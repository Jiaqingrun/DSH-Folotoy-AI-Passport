#!/usr/bin/env python3
"""Collect advisory compliance/smoothness signals from firmware C/C++ sources.

This is a signal collector, not an audit verdict. It cannot prove memory safety,
LVGL locking, frame cadence, or legal compliance. Every hit must be reviewed in
context; clean output is not a passed audit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".h", ".cc", ".cpp", ".cxx", ".hpp"}
SKIP_DIRS = {
    ".git", ".agents", ".venv", "build", "managed_components",
    "node_modules", "__pycache__", "venv",
}
PATTERNS = (
    ("unsafe-call", re.compile(r"\b(strcpy|strcat|sprintf|vsprintf|gets|system|popen)\s*\("), "high"),
    ("secret-like-literal", re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret|bearer)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{8,}"), "high"),
    ("heap-call", re.compile(r"\b(malloc|calloc|realloc|free)\s*\("), "review"),
    ("blocking-delay", re.compile(r"\b(vTaskDelay|sleep|usleep|esp_rom_delay_us)\s*\("), "review"),
    ("full-redraw", re.compile(r"lv_obj_invalidate\s*\(\s*lv_screen_active\s*\("), "review"),
    ("open-marker", re.compile(r"\b(TODO|FIXME|XXX)\b"), "note"),
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def _scan_file(path: Path, root: Path) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    findings: list[dict[str, object]] = []
    relative = str(path.relative_to(root))
    for line_number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern, severity in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            findings.append({
                "kind": kind,
                "severity": severity,
                "file": relative,
                "line": line_number,
                "snippet": line.strip()[:240],
            })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scan_code.py",
        description="Collect advisory compliance/smoothness signals from C/C++ sources.",
    )
    parser.add_argument("--root", default="", help="firmware project root (default: current directory)")
    parser.add_argument("--include-tests", action="store_true", help="also scan the tests/ directory")
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    args = parser.parse_args(argv)

    _configure_stdio()
    root = Path(args.root).expanduser().absolute() if args.root else Path.cwd().absolute()
    if not root.is_dir():
        print(f"root not found: {root}", file=sys.stderr)
        return 2

    findings: list[dict[str, object]] = []
    files_scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name for name in dirnames
            if name not in SKIP_DIRS and not (name == "tests" and not args.include_tests)
        ]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            files_scanned += 1
            findings.extend(_scan_file(path, root))

    counts: dict[str, int] = {}
    for finding in findings:
        counts[str(finding["kind"])] = counts.get(str(finding["kind"]), 0) + 1
    report = {
        "root": str(root),
        "advisory": "Signals only; review every hit in context and run build/device gates.",
        "files_scanned": files_scanned,
        "finding_count": len(findings),
        "counts": counts,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"files scanned: {files_scanned}")
    print(f"signals: {len(findings)}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")
    print("advisory only: clean output is not a passed audit")
    for finding in findings[:50]:
        print(f"{finding['file']}:{finding['line']}: [{finding['kind']}] {finding['snippet']}")
    if len(findings) > 50:
        print(f"... {len(findings) - 50} more; rerun with --json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
