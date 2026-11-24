#!/usr/bin/env python3
"""Read-only project card scanner for FoloToy AI Passport projects."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", ".direnv", "managed_components"}


def git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=10, check=False,
        )
        return proc.stdout.strip() if proc.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            data = handle.read(65536)
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", data[6:10])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X":
            return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
        if kind == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
            return (
                int.from_bytes(data[26:28], "little") & 0x3FFF,
                int.from_bytes(data[28:30], "little") & 0x3FFF,
            )
        if kind == b"VP8L" and data[20] == 0x2F:
            bits = int.from_bytes(data[21:25], "little")
            return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
    if data[:2] == b"\xff\xd8":
        index = 2
        while index + 9 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            index += 2
            if marker in (0xD8, 0xD9):
                continue
            if index + 2 > len(data):
                break
            length = int.from_bytes(data[index:index + 2], "big")
            if length < 2:
                break
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                height = int.from_bytes(data[index + 3:index + 5], "big")
                width = int.from_bytes(data[index + 5:index + 7], "big")
                return width, height
            index += length
    return None


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        base = Path(dirpath)
        for name in filenames:
            yield base / name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"FAIL root is not a directory: {root}", file=sys.stderr)
        return 1

    git_root = git(root, "rev-parse", "--show-toplevel")
    remote = git(root, "remote", "get-url", "origin")
    dirty = git(root, "status", "--porcelain", "--untracked-files=no")
    untracked = git(root, "ls-files", "--others", "--exclude-standard")

    files = list(walk(root))
    firmware = []
    for path in files:
        lower = path.name.lower()
        if not lower.endswith(".bin"):
            continue
        if "build" not in path.parts and "publish" not in path.parts:
            continue
        if "build" in path.parts:
            after_build = path.parts[path.parts.index("build") + 1:]
            if "firmware" in after_build:
                continue  # skip historical build/firmware/<sha>/... copies
        if not any(token in lower for token in ("full", "merged", "firmware")):
            continue
        firmware.append({
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    covers = []
    for path in files:
        lower = path.name.lower()
        if not lower.startswith("cover") and "cover" not in lower:
            continue
        if path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        size = image_size(path)
        covers.append({
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "width": size[0] if size else None,
            "height": size[1] if size else None,
        })

    signals = {
        "agents": (root / "AGENTS.md").is_file(),
        "project": (root / "PROJECT.md").is_file(),
        "validate": (root / "tools/validate.sh").is_file(),
        "check_repo": (root / "tools/check_repo.py").is_file(),
        "cmake": (root / "CMakeLists.txt").is_file(),
        "idf": (root / "sdkconfig").is_file() or (root / "sdkconfig.defaults").is_file(),
        "main": (root / "main").is_dir(),
        "firmware_dir": (root / "firmware").is_dir(),
    }

    gate = signals["agents"] and signals["validate"]
    firmware_ok = bool(firmware) and (signals["cmake"] or signals["idf"] or signals["firmware_dir"])
    cover_ok = any(item["width"] == 3 * item["height"] // 4 for item in covers if item["width"] and item["height"])
    klass = "A" if gate and firmware_ok and cover_ok else "B" if firmware_ok or cover_ok else "C"

    missing = []
    if not gate:
        missing.append("AGENTS.md + tools/validate.sh gate")
    if not firmware_ok:
        missing.append("firmware binary")
    if not cover_ok:
        missing.append("exact 3:4 cover")

    card = {
        "root": str(root),
        "gitRoot": git_root,
        "remote": remote,
        "dirty": bool(dirty),
        "untracked": bool(untracked),
        "class": klass,
        "signals": signals,
        "firmware": firmware,
        "covers": covers,
        "missing": missing,
    }
    if args.json:
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(f"class={klass} root={root}")
        print(f"firmware={len(firmware)} covers={len(covers)} dirty={bool(dirty)} untracked={bool(untracked)}")
        print("missing=" + (", ".join(missing) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
