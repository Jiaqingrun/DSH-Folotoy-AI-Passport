#!/usr/bin/env python3
"""Prepare or run a FoloToy AI Passport publisher submission.

Cross-platform replacement for publish.sh. It never invokes --auto, never reads
authorization codes, and defaults to dry-run. publish.sh/publish.ps1 are thin
launchers around this file.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path


USAGE = """\
publish.py --publisher PY --firmware BIN --cover IMG \\
  --title-zh TEXT --description-zh TEXT --instructions-zh-file FILE \\
  [--project-id ID] [--changelog-zh-file FILE] [--source-url URL] \\
  [--image IMG ...] [--title-en TEXT --description-en TEXT --instructions-en-file FILE --changelog-en-file FILE] \\
  [--dry-run] [--confirmed] [--execute]

Default is dry-run: prints the exact command and exits 0.
--execute actually runs submit; --confirmed adds --confirmed (upload after preview).
--auto is deliberately not supported.
"""


def _fail(message: str, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def _display(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


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

    publisher = Path(args.publisher).expanduser() if args.publisher else None
    firmware = Path(args.firmware).expanduser() if args.firmware else None
    cover = Path(args.cover).expanduser() if args.cover else None
    instructions_zh = Path(args.instructions_zh_file).expanduser() if args.instructions_zh_file else None

    if not publisher or not publisher.is_file():
        return _fail("missing publisher")
    if not firmware or not firmware.is_file():
        return _fail("missing firmware")
    if not cover or not cover.is_file():
        return _fail("missing cover")
    if not args.title_zh:
        return _fail("missing --title-zh")
    if not args.description_zh:
        return _fail("missing --description-zh")
    if not instructions_zh or not instructions_zh.is_file():
        return _fail("missing --instructions-zh-file")

    changelog_zh = Path(args.changelog_zh_file).expanduser() if args.changelog_zh_file else None
    if args.project_id and (not changelog_zh or not changelog_zh.is_file()):
        return _fail("update requires --changelog-zh-file")

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
