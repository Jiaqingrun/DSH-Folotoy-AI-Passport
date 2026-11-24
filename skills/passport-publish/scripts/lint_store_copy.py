#!/usr/bin/env python3
"""Bounded copy linter for AI Passport store submissions."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAX_INSTRUCTIONS = 8000
MAX_CHANGELOG = 4000
CJK = re.compile(r"[\u4e00-\u9fff]")
PLACEHOLDERS = ("<TODO>", "TODO", "Lorem ipsum", "xxx", "待补充")
TOKENLIKE = re.compile(
    r"(?i)(?:token|secret|api[_-]?key|password)\s*[:=]\s*[A-Za-z0-9_\-]{8,}"
)


def read_text(path: str | None) -> tuple[str | None, str | None]:
    if not path:
        return None, None
    target = Path(path)
    if not target.is_file():
        return None, f"missing: {path}"
    try:
        return target.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as error:
        return None, f"not UTF-8: {path}: {error}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instructions-zh", required=True)
    parser.add_argument("--instructions-en")
    parser.add_argument("--changelog-zh")
    parser.add_argument("--changelog-en")
    parser.add_argument("--require-changelog", action="store_true")
    args = parser.parse_args()

    checks: list[dict[str, object]] = []
    ok = True

    def check(name: str, condition: bool, detail: str) -> None:
        nonlocal ok
        checks.append({"check": name, "ok": bool(condition), "detail": detail})
        if not condition:
            ok = False

    zh, error = read_text(args.instructions_zh)
    check("instructions-zh-readable", error is None and zh is not None, error or "utf-8")
    if zh is not None:
        check("instructions-zh-chinese", bool(CJK.search(zh)), f"{len(CJK.findall(zh))} CJK chars")
        check("instructions-zh-length", 1 <= len(zh) <= MAX_INSTRUCTIONS,
              f"{len(zh)} chars (max {MAX_INSTRUCTIONS})")
        placeholder = next((item for item in PLACEHOLDERS if item in zh), None)
        check("instructions-zh-placeholders", placeholder is None,
              f"placeholder: {placeholder}" if placeholder else "no placeholder")
        check("instructions-zh-tokenlike", not TOKENLIKE.search(zh), "no token-like assignment")

    optional = (
        ("instructions-en", args.instructions_en, MAX_INSTRUCTIONS),
        ("changelog-zh", args.changelog_zh, MAX_CHANGELOG),
        ("changelog-en", args.changelog_en, MAX_CHANGELOG),
    )
    for label, path, limit in optional:
        if not path:
            continue
        text, error = read_text(path)
        check(f"{label}-readable", error is None and text is not None, error or "utf-8")
        if text is None:
            continue
        check(f"{label}-length", len(text) <= limit, f"{len(text)} chars (max {limit})")
        placeholder = next((item for item in PLACEHOLDERS if item in text), None)
        check(f"{label}-placeholders", placeholder is None,
              f"placeholder: {placeholder}" if placeholder else "no placeholder")
        check(f"{label}-tokenlike", not TOKENLIKE.search(text), "no token-like assignment")

    if args.require_changelog and not args.changelog_zh:
        check("changelog-zh-required", False, "update requires --changelog-zh")

    for item in checks:
        print(("PASS " if item["ok"] else "FAIL ") + str(item["check"]) + ": " + str(item["detail"]))
    print(json.dumps({"ok": ok, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
