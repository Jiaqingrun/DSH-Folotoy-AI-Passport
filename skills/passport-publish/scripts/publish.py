#!/usr/bin/env python3
"""Prepare or run a FoloToy AI Passport publisher submission.

Cross-platform replacement for publish.sh. It never invokes --auto, never reads
authorization codes, and defaults to dry-run. publish.sh/publish.ps1 are thin
launchers around this file.

Cover default policy:
- New upload: --cover is required; it must be a finished portrait 3:4 render.
- Update (--project-id): omit --cover to preserve the published cover. The
  wrapper finds the exact 3:4 cover under --root, or uses --previous-cover, and
  reuses those same bytes because the publisher requires a complete revision.
"""

from __future__ import annotations

import argparse
import os
import shlex
import struct
import subprocess
import sys
from pathlib import Path


USAGE = """\
publish.py --publisher PY --firmware BIN \\
  [--cover IMG | --previous-cover IMG] \\
  --title-zh TEXT --description-zh TEXT --instructions-zh-file FILE \\
  [--project-id ID] [--root DIR] [--changelog-zh-file FILE] [--source-url URL] \\
  [--image IMG ...] [--title-en TEXT --description-en TEXT \\
   --instructions-en-file FILE --changelog-en-file FILE] \\
  [--dry-run] [--confirmed] [--execute]

New upload: --cover is required; generate a finished portrait 3:4 render first.
Update: omit --cover to preserve the existing published cover (use --root or
--previous-cover). Pass --cover only when the user explicitly wants a new cover.

Default is dry-run: prints the exact command and exits 0.
--execute actually runs submit; --confirmed adds --confirmed (upload after preview).
--auto is deliberately not supported.
"""

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
SKIP_DIRS = {
    ".git",
    ".agents",
    ".venv",
    "__pycache__",
    "build",
    "managed_components",
    "node_modules",
    "venv",
}


def _configure_stdio() -> None:
    """Avoid cp1252 crashes when a Windows console prints UTF-8 copy."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def _fail(message: str, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def _display(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def _image_size(path: Path) -> tuple[int, int] | None:
    """Read image dimensions without an image library, cross-platform."""
    try:
        with path.open("rb") as handle:
            head = handle.read(32)
            if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 24:
                width, height = struct.unpack(">II", head[16:24])
                return width, height

            if head[:2] == b"\xff\xd8":
                handle.seek(0)
                data = handle.read(262144)
                index = 2
                while index + 9 < len(data):
                    if data[index] != 0xFF:
                        index += 1
                        continue
                    marker = data[index + 1]
                    if marker in (0xD8, 0xD9):
                        index += 2
                        continue
                    if 0xD0 <= marker <= 0xD7:
                        index += 2
                        continue
                    length = int.from_bytes(data[index + 2:index + 4], "big")
                    if length < 2:
                        return None
                    if marker in {
                        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
                    }:
                        height = int.from_bytes(data[index + 5:index + 7], "big")
                        width = int.from_bytes(data[index + 7:index + 9], "big")
                        return width, height
                    index += 2 + length
                return None

            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                handle.seek(0)
                data = handle.read(32)
                chunk = data[12:16]
                if chunk == b"VP8X" and len(data) >= 30:
                    width = 1 + int.from_bytes(data[24:27], "little")
                    height = 1 + int.from_bytes(data[27:30], "little")
                    return width, height
                if chunk == b"VP8 " and len(data) >= 30:
                    width = int.from_bytes(data[26:28], "little") & 0x3FFF
                    height = int.from_bytes(data[28:30], "little") & 0x3FFF
                    return width, height
                if chunk == b"VP8L" and len(data) >= 25:
                    bits = int.from_bytes(data[21:25], "little")
                    width = (bits & 0x3FFF) + 1
                    height = ((bits >> 14) & 0x3FFF) + 1
                    return width, height
    except OSError:
        return None
    return None


def _is_portrait_3x4(width: int, height: int) -> bool:
    return width > 0 and height > 0 and width * 4 == height * 3


def _cover_rank(path: Path, root: Path) -> tuple[int, int, str]:
    name = path.name.lower()
    if name.startswith("cover"):
        rank = 0
    elif "cover" in name:
        rank = 1
    else:
        rank = 2
    try:
        depth = len(path.relative_to(root).parts)
    except ValueError:
        depth = 99
    return rank, depth, str(path).lower()


def _find_published_cover(root: Path) -> Path | None:
    """Find one exact 3:4 image whose name contains 'cover' under root."""
    if not root.is_dir():
        return None
    candidates: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        try:
            depth = len(current.relative_to(root).parts)
        except ValueError:
            depth = 99
        dirnames[:] = [
            name for name in dirnames
            if name not in SKIP_DIRS and not name.startswith(".git")
        ]
        if depth >= 6:
            dirnames[:] = []
        for name in filenames:
            if "cover" not in name.lower():
                continue
            if Path(name).suffix.lower() not in IMAGE_SUFFIXES:
                continue
            candidate = current / name
            size = _image_size(candidate)
            if size and _is_portrait_3x4(*size):
                candidates.append(candidate)
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: _cover_rank(item, root))[0]


def _preserved_cover(root: Path, explicit: str) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            return None
        size = _image_size(path)
        if size and not _is_portrait_3x4(*size):
            return None
        return path
    return _find_published_cover(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="publish.py",
        usage=USAGE,
        add_help=True,
    )
    parser.add_argument("--publisher", default="")
    parser.add_argument("--project-id", default="")
    parser.add_argument("--firmware", default="")
    parser.add_argument("--cover", default="")
    parser.add_argument("--previous-cover", default="")
    parser.add_argument("--root", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--title-zh", default="")
    parser.add_argument("--description-zh", default="")
    parser.add_argument("--instructions-zh-file", default="")
    parser.add_argument("--changelog-zh-file", default="")
    parser.add_argument("--title-en", default="")
    parser.add_argument("--description-en", default="")
    parser.add_argument("--instructions-en-file", default="")
    parser.add_argument("--changelog-en-file", default="")
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--dry-run", dest="execute", action="store_const", const=False)
    parser.add_argument("--confirmed", action="store_true")
    parser.add_argument("--execute", dest="execute", action="store_const", const=True)
    parser.set_defaults(execute=False)
    args = parser.parse_args(argv)

    _configure_stdio()

    publisher = Path(args.publisher).expanduser() if args.publisher else None
    firmware = Path(args.firmware).expanduser() if args.firmware else None
    root = Path(args.root).expanduser() if args.root else Path.cwd()

    if not publisher or not publisher.is_file():
        return _fail("missing publisher")
    if not firmware or not firmware.is_file():
        return _fail("missing firmware")
    if args.root and not root.is_dir():
        return _fail(f"root not found: {root}")
    if args.cover and args.previous_cover:
        return _fail("use --cover or --previous-cover, not both")
    if args.previous_cover and not args.project_id:
        return _fail("--previous-cover is only valid for an update (--project-id)")
    if not args.title_zh:
        return _fail("missing --title-zh")
    if not args.description_zh:
        return _fail("missing --description-zh")
    instructions_zh = Path(args.instructions_zh_file).expanduser() if args.instructions_zh_file else None
    if not instructions_zh or not instructions_zh.is_file():
        return _fail("missing --instructions-zh-file")

    changelog_zh = Path(args.changelog_zh_file).expanduser() if args.changelog_zh_file else None
    if args.project_id and (not changelog_zh or not changelog_zh.is_file()):
        return _fail("update requires --changelog-zh-file")

    if args.cover:
        cover = Path(args.cover).expanduser()
        if not cover.is_file():
            return _fail(f"cover not found: {cover}")
    elif args.project_id:
        cover = _preserved_cover(root, args.previous_cover)
        if cover is None:
            return _fail(
                "update needs the existing published cover; pass --previous-cover <img>, "
                "place the exact 3:4 cover under --root, or pass --cover only for an intentional change"
            )
        print(f"cover: preserving {cover}", file=sys.stderr)
    else:
        return _fail(
            "first upload requires a generated portrait 3:4 render cover; "
            "generate and inspect it, then pass --cover <img>"
        )

    if len(args.image) > 4:
        return _fail("at most 4 --image values")
    images: list[Path] = []
    for raw in args.image:
        image = Path(raw).expanduser()
        if not image.is_file():
            return _fail(f"extra image not found: {image}")
        images.append(image)

    python = sys.executable
    validate_cmd = [
        python,
        str(publisher),
        "validate",
        "--kind",
        "firmware",
        "--firmware",
        str(firmware),
        "--cover",
        str(cover),
    ]
    validated = subprocess.run(validate_cmd, check=False)
    if validated.returncode != 0:
        return validated.returncode

    command: list[str] = [
        python,
        str(publisher),
        "submit",
        "--title-zh",
        args.title_zh,
        "--description-zh",
        args.description_zh,
        "--instructions-zh-file",
        str(instructions_zh),
        "--cover",
        str(cover),
        "--kind",
        "firmware",
        "--firmware",
        str(firmware),
    ]

    if args.project_id:
        command += ["--project-id", args.project_id]
    if changelog_zh:
        command += ["--changelog-zh-file", str(changelog_zh)]
    if args.source_url:
        command += ["--source-url", args.source_url]
    if args.title_en:
        command += ["--title-en", args.title_en]
    if args.description_en:
        command += ["--description-en", args.description_en]
    if args.instructions_en_file:
        command += ["--instructions-en-file", str(Path(args.instructions_en_file).expanduser())]
    if args.changelog_en_file:
        command += ["--changelog-en-file", str(Path(args.changelog_en_file).expanduser())]
    for image in images:
        command += ["--image", str(image)]
    if args.confirmed:
        command += ["--confirmed"]

    if not args.execute:
        print(_display(command))
        return 0

    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
