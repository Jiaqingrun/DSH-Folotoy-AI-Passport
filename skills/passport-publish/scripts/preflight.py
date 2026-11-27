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
from collections.abc import Callable
from pathlib import Path


def _configure_stdio() -> None:
    """Emit UTF-8 even when stdout is a pipe (Windows ANSI code pages mangle it)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def _run(command: list[str], cwd: Path | None = None, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _size(path: Path) -> int:
    return path.stat().st_size


def _static_candidates(
    root: Path, platform_name: str | None = None
) -> list[tuple[Path, Callable[[], tuple[list[str] | None, str]]]]:
    """Return existing static-gate candidates in platform order.

    On Windows, `tools/validate.sh` is a poor first choice: bash may be absent and
    Git Bash/WSL can mangle `C:\\...` arguments. Prefer the project's PowerShell
    or cmd gate there. Tests use `platform_name` to check both orders on one host.
    """
    sh_script = root / "tools" / "validate.sh"
    ps_script = root / "tools" / "validate.ps1"
    cmd_script = root / "tools" / "validate.cmd"

    def via_bash() -> tuple[list[str] | None, str]:
        bash = shutil.which("bash")
        if not bash:
            return None, f"static check skipped: bash not found for {sh_script}"
        return [bash, str(sh_script), "--static"], ""

    def via_powershell() -> tuple[list[str] | None, str]:
        pwsh = shutil.which("pwsh") or shutil.which("powershell")
        if not pwsh:
            return None, f"static check skipped: PowerShell not found for {ps_script}"
        return (
            [
                pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(ps_script), "-Static",
            ],
            "",
        )

    def via_cmd() -> tuple[list[str] | None, str]:
        comspec = os.environ.get("COMSPEC") or "cmd.exe"
        return [comspec, "/c", str(cmd_script), "--static"], ""

    candidates: list[tuple[Path, Callable[[], tuple[list[str] | None, str]]]] = [
        (ps_script, via_powershell),
        (cmd_script, via_cmd),
        (sh_script, via_bash),
    ]
    if (platform_name or os.name) != "nt":
        candidates = [
            (sh_script, via_bash),
            (ps_script, via_powershell),
            (cmd_script, via_cmd),
        ]
    return [(script, runner) for script, runner in candidates if script.is_file()]


def _static_order(root: Path, platform_name: str | None = None) -> list[str]:
    """Return existing gate filenames in the order they would be tried."""
    return [script.name for script, _ in _static_candidates(root, platform_name)]


def _run_static(root: Path, platform_name: str | None = None) -> tuple[bool, str]:
    """Run the first available project static gate; fall back if its runner is missing."""
    candidates = _static_candidates(root, platform_name)
    if not candidates:
        return (False, "static check skipped: tools/validate.sh, .ps1, or .cmd not found")

    command: list[str] | None = None
    label = ""
    skipped: list[str] = []
    for script, runner in candidates:
        command, reason = runner()
        label = script.name
        if command is not None:
            break
        skipped.append(reason)

    if command is None:
        return (False, "; ".join(skipped))

    try:
        proc = _run(command, cwd=root)
    except NotADirectoryError:
        # Windows cannot give a >260-character directory to CreateProcess as the
        # child working directory (WinError 267). The gate still runs from its
        # absolute path, so retry without cwd instead of failing the check.
        try:
            proc = _run(command, cwd=None)
        except (OSError, subprocess.SubprocessError) as exc:
            return (False, f"static checks failed: {exc}")
    except (OSError, subprocess.SubprocessError) as exc:
        return (False, f"static checks failed: {exc}")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return (False, f"static checks failed ({label}): {detail[0] if detail else 'exit ' + str(proc.returncode)}")
    return (True, "static checks")


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
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
        bad("git missing (install Git for Windows: winget install --id Git.Git -e)")

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
