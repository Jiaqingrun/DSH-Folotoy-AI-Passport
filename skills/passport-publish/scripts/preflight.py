#!/usr/bin/env python3
"""Read-only preflight checks for an AI Passport publish.

Cross-platform replacement for preflight.sh. The shell and PowerShell files are
thin launchers; this file is the single source of truth.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _run(command: list[str], cwd: Path | None = None, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _size(path: Path) -> int:
    return path.stat().st_size


def _run_static(root: Path) -> tuple[bool, str]:
    """Run the project's static validation when a supported entry point exists."""
    checks: list[tuple[str, list[str] | None]] = []
    sh_script = root / "tools" / "validate.sh"
    ps_script = root / "tools" / "validate.ps1"
    cmd_script = root / "tools" / "validate.cmd"

    if sh_script.is_file():
        bash = shutil.which("bash")
        if bash:
            checks.append((f"bash {sh_script}", [bash, str(sh_script), "--static"]))
        else:
            return (False, f"static check skipped: bash not found for {sh_script}")
    elif ps_script.is_file():
        pwsh = shutil.which("pwsh") or shutil.which("powershell")
        if pwsh:
            checks.append((f"powershell {ps_script}", [pwsh, "-NoProfile", "-File", str(ps_script), "-Static"]))
        else:
            return (False, f"static check skipped: PowerShell not found for {ps_script}")
    elif cmd_script.is_file():
        comspec = os.environ.get("COMSPEC") or "cmd.exe"
        checks.append((f"cmd {cmd_script}", [comspec, "/c", str(cmd_script), "--static"]))
    else:
        return (False, "static check skipped: tools/validate.sh, .ps1, or .cmd not found")

    for label, command in checks:
        if command is None:
            continue
        try:
            proc = _run(command, cwd=root)
        except (OSError, subprocess.SubprocessError) as exc:
            return (False, f"static checks failed: {exc}")
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip().splitlines()
            return (False, f"static checks failed ({label}): {detail[0] if detail else 'exit ' + str(proc.returncode)}")
    return (True, "static checks")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="preflight.py",
        description="Check files, publisher, size limits, and git state before publishing.",
    )
    parser.add_argument("--root", default="")
    parser.add_argument("--firmware", default="")
    parser.add_argument("--cover", default="")
    parser.add_argument("--publisher", default=os.environ.get("PUBLISHER", ""))
    parser.add_argument("--static", action="store_true")
    args = parser.parse_args(argv)

    failed = False

    def ok(message: str) -> None:
        print(f"PASS {message}")

    def bad(message: str) -> None:
        nonlocal failed
        failed = True
        print(f"FAIL {message}")

    root = Path(args.root).expanduser() if args.root else Path()
    firmware = Path(args.firmware).expanduser() if args.firmware else Path()
    cover = Path(args.cover).expanduser() if args.cover else Path()

    if args.root and root.is_dir():
        ok(f"root {root}")
    else:
        bad("root missing")

    if args.firmware and firmware.is_file():
        ok(f"firmware {firmware}")
    else:
        bad("firmware missing")

    if args.cover and cover.is_file():
        ok(f"cover {cover}")
    else:
        bad("cover missing")

    if sys.version_info >= (3, 10):
        ok(f"python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        bad("python is older than 3.10")

    git = shutil.which("git")
    if git:
        try:
            proc = _run([git, "--version"])
            first = next((line.strip() for line in (proc.stdout or proc.stderr).splitlines() if line.strip()), "")
            ok(first or "git available")
        except (OSError, subprocess.SubprocessError):
            bad("git found but --version failed")
    else:
        bad("git missing")

    publisher = Path(args.publisher).expanduser() if args.publisher else None
    if publisher and publisher.is_file():
        try:
            proc = _run([sys.executable, str(publisher), "--help"])
            if proc.returncode == 0:
                ok("publisher help")
            else:
                detail = next((line.strip() for line in (proc.stderr or proc.stdout).splitlines() if line.strip()), "")
                bad(f"publisher --help failed: {detail or 'exit ' + str(proc.returncode)}")
        except (OSError, subprocess.SubprocessError) as exc:
            bad(f"publisher --help failed: {exc}")
    else:
        bad("publisher path not set (--publisher or PUBLISHER)")

    if args.firmware and firmware.is_file():
        size = _size(firmware)
        if size <= 8 * 1024 * 1024:
            ok(f"firmware {size}B <= 8MiB")
        else:
            bad(f"firmware {size}B > 8MiB")

    if args.cover and cover.is_file():
        size = _size(cover)
        if size <= 10 * 1024 * 1024:
            ok(f"cover {size}B <= 10MiB")
        else:
            bad(f"cover {size}B > 10MiB")

    if args.root and root.is_dir() and git:
        try:
            inside = _run([git, "-C", str(root), "rev-parse", "--is-inside-work-tree"])
            if inside.returncode == 0:
                status = _run([git, "-C", str(root), "status", "--porcelain", "--untracked-files=no"])
                dirty = len([line for line in status.stdout.splitlines() if line.strip()])
                if dirty == 0:
                    ok("git tracked clean")
                else:
                    bad(f"git has {dirty} tracked modifications")
        except (OSError, subprocess.SubprocessError) as exc:
            bad(f"git check failed: {exc}")

    if args.static and args.root and root.is_dir():
        passed, message = _run_static(root)
        if passed:
            ok(message)
        elif message.startswith("static check skipped"):
            print(f"WARN {message}")
        else:
            bad(message)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
