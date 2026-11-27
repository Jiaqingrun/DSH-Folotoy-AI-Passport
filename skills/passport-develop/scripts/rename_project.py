#!/usr/bin/env python3
"""Rename an AI Passport application's project folder to its final name.

Default is a dry run. --apply performs the rename. The helper refuses ambiguous
or unsafe targets instead of guessing:

- DSH bundles/profiles are never renamed.
- A linked git worktree (root/.git is a file) is not renamed.
- Symlinks, filesystem roots, the home directory, and an existing target are
  refused.
- Only the app's own project root is renamed; parent/other projects are not.

The final name is normalized to a filesystem-safe slug. Unicode letters/numbers
are preserved (Chinese app names are valid); spaces and shell/path punctuation
become hyphens. Windows-reserved device names get an `app-` prefix.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import uuid
from pathlib import Path


WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _fail(message: str, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def _slugify(name: str) -> str | None:
    text = unicodedata.normalize("NFKC", name).strip()
    if not text:
        return None
    chars: list[str] = []
    for char in text:
        if char.isalnum() or char in "-_":
            chars.append(char)
        else:
            chars.append("-")
    slug = re.sub(r"-{2,}", "-", "".join(chars)).strip("-_.")
    slug = slug.lower()
    if not slug:
        return None
    if slug.upper() in WINDOWS_RESERVED:
        slug = "app-" + slug
    if len(slug) > 80:
        slug = slug[:80].rstrip("-_.")
    return slug or None


def _is_dsh_bundle(root: Path) -> bool:
    package = root / "package.json"
    if not package.is_file():
        return False
    if (root / "cordis.patch.yml").is_file():
        return True
    try:
        data = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    dsh = data.get("dsh") if isinstance(data, dict) else None
    return isinstance(dsh, dict) and any(key in dsh for key in ("bundle", "profile", "plugin"))


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _rename_with_retry(source: Path, target: Path, attempts: int = 6) -> None:
    """Rename, retrying while Windows reports the directory as busy.

    Windows refuses to rename a directory that any process holds open (an editor,
    a terminal cwd, an indexer, a virus scanner) with WinError 32/5. On macOS the
    same call usually succeeds, so a single attempt is not enough here.
    """
    delay = 0.15
    for attempt in range(attempts):
        try:
            source.rename(target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 2.0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rename_project.py",
        description="Rename the current AI Passport app folder to its final name (dry-run by default).",
    )
    parser.add_argument("--root", default="", help="app project root (default: current directory)")
    parser.add_argument("--name", required=True, help="final firmware/app name")
    parser.add_argument("--apply", action="store_true", help="perform the rename; default is dry-run")
    parser.add_argument("--json", action="store_true", help="emit a JSON record")
    args = parser.parse_args(argv)

    _configure_stdio()

    root = Path(args.root).expanduser().absolute() if args.root else Path.cwd().absolute()
    if not root.exists():
        return _fail(f"root not found: {root}")
    if root.is_symlink():
        return _fail(f"refusing to rename a symlink: {root}")
    if not root.is_dir():
        return _fail(f"root is not a directory: {root}")
    if root.parent == root:
        return _fail("refusing to rename a filesystem root")
    if root == Path.home().absolute():
        return _fail("refusing to rename the home directory")
    if _is_dsh_bundle(root):
        return _fail("refusing to rename a DSH bundle/profile; this is not an app project")

    git_meta = root / ".git"
    if git_meta.is_file() or git_meta.is_symlink():
        return _fail("refusing to rename a linked git worktree")

    slug = _slugify(args.name)
    if slug is None:
        return _fail(f"cannot derive a folder name from: {args.name!r}")

    target = root.parent / slug
    cwd_inside = _inside(Path.cwd().absolute(), root)
    status = "unchanged"
    if target != root:
        if target.exists():
            try:
                same = root.samefile(target)
            except OSError:
                same = False
            if not same:
                return _fail(f"target already exists: {target}")
            status = "renamed-case-only"
        else:
            status = "renamed"
        if args.apply:
            try:
                if cwd_inside:
                    os.chdir(root.parent)
                if status == "renamed-case-only":
                    temporary = root.parent / f".rename-{uuid.uuid4().hex}"
                    _rename_with_retry(root, temporary)
                    _rename_with_retry(temporary, target)
                else:
                    _rename_with_retry(root, target)
            except PermissionError as exc:
                return _fail(
                    f"rename failed, the folder is held open by another program: {exc}\n"
                    "close editors, terminals, and Explorer windows showing it, then retry"
                )
            except OSError as exc:
                return _fail(f"rename failed: {exc}")
            if not target.is_dir():
                return _fail(f"rename did not complete as expected: {root} -> {target}")
            if status == "renamed" and root.exists():
                return _fail(f"old path still exists after rename: {root}")
        else:
            status = "dry-run"

    new_root = target if target != root else root
    record = {
        "status": status,
        "old": str(root),
        "new": str(new_root),
        "slug": slug,
        "cwd_inside_old": cwd_inside,
        "next_cwd": str(new_root) if cwd_inside else str(Path.cwd()),
    }
    if args.json:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    else:
        print(f"status: {status}")
        print(f"old: {root}")
        print(f"new: {new_root}")
        if cwd_inside and status != "dry-run":
            print(f"next cwd: {new_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
