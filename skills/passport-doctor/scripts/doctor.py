#!/usr/bin/env python3
"""Read-only environment doctor for the AI Passport DSH bundle.

Cross-platform replacement for doctor.sh. Keep this file the single source of
truth; doctor.sh and doctor.ps1 only locate a Python 3.10+ interpreter.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_NAMES = (
    "passport-build",
    "passport-code-audit",
    "passport-debug",
    "passport-develop",
    "passport-device-test",
    "passport-setup",
    "passport-router",
    "passport-publish",
    "passport-doctor",
)


def _configure_stdio() -> None:
    """Emit UTF-8 even when stdout is a pipe.

    On a Chinese/Japanese Windows install Python falls back to the ANSI code page
    (cp936/cp932) for pipes. That mangles non-ASCII paths for the caller and
    raises UnicodeEncodeError for names the code page cannot represent.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def _run(command: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _desktop_version(dsh_home: Path) -> str:
    """Read the DSH Desktop version from its runtime manifest.

    DSH Desktop keeps the CLI off PATH (it lives under resources/runtime/cli/bin),
    so `shutil.which("dsh")` finds nothing even though a version is installed.
    """
    runtimes = dsh_home / "dsh-runtimes"
    if not runtimes.is_dir():
        return ""
    for runtime in sorted(runtimes.iterdir()):
        manifest = runtime / "runtime.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        version = data.get("desktopVersion") if isinstance(data, dict) else None
        if isinstance(version, str) and version.strip():
            return version.strip()
    return ""


def _first_line(text: str) -> str:
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def _publisher_skill_candidates(dsh_home: Path) -> list[Path]:
    """Likely locations of the official publisher skill.

    The bundle must not ship the publisher, and it is not always installed under
    ``$DSH_HOME/skills``: a manual clone such as ``C:\\folotoy-publisher\\...`` is
    common. Checking only the DSH home reported "not installed" on a machine that
    had already published successfully, which is worse than reporting nothing.
    """
    candidates: list[Path] = []
    explicit = os.environ.get("FOLOTOY_PUBLISHER_DIR", "").strip()
    if explicit:
        candidates.append(Path(explicit).expanduser() / "SKILL.md")
    candidates.extend(
        (
            dsh_home / "skills" / "folotoy-ai-passport-publisher" / "SKILL.md",
            dsh_home / "skills" / "folotoy" / "folotoy-ai-passport-publisher" / "SKILL.md",
            Path.home() / "folotoy-publisher" / "folotoy-ai-passport-publisher" / "SKILL.md",
        )
    )
    if os.name == "nt":
        candidates.append(Path("C:/folotoy-publisher/folotoy-ai-passport-publisher/SKILL.md"))
        candidates.append(
            Path(os.environ.get("ProgramFiles", "C:/Program Files"))
            / "folotoy-publisher"
            / "folotoy-ai-passport-publisher"
            / "SKILL.md"
        )
    else:
        candidates.append(Path("/opt/folotoy-publisher/folotoy-ai-passport-publisher/SKILL.md"))
        candidates.append(
            Path("/usr/local/share/folotoy-publisher/folotoy-ai-passport-publisher/SKILL.md")
        )
    return candidates


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        prog="doctor.py",
        description="Read-only environment checks for the AI Passport bundle.",
    )
    parser.add_argument("--publisher", default=os.environ.get("PUBLISHER", ""))
    parser.add_argument("--root", default="")
    parser.add_argument("--firmware", default="")
    parser.add_argument("--cover", default="")
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    skills_dir = script_dir.parent.parent
    dsh_home = Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh")).expanduser()

    failed = False

    def ok(message: str) -> None:
        print(f"PASS {message}")

    def warn(message: str) -> None:
        print(f"WARN {message}")

    def bad(message: str) -> None:
        nonlocal failed
        failed = True
        print(f"FAIL {message}")

    # DSH version: explicit DSH_VERSION wins; then the CLI; then DSH Desktop's manifest.
    version = os.environ.get("DSH_VERSION", "").strip()
    if not version:
        dsh = os.environ.get("DSH_CLI", "").strip() or shutil.which("dsh")
        if dsh:
            try:
                proc = _run([dsh, "--version"])
                line = _first_line(proc.stdout or proc.stderr)
                version = line.split()[-1] if line else ""
            except (OSError, subprocess.SubprocessError):
                version = ""
    if not version:
        version = _desktop_version(dsh_home)
    if version:
        ok(f"DSH version {version}")
    else:
        warn("DSH version not detectable (set DSH_VERSION or DSH_CLI)")

    if sys.version_info >= (3, 10):
        ok(f"python {sys.version_info.major}.{sys.version_info.minor} ({sys.executable})")
    else:
        bad(f"python is older than 3.10 ({sys.executable})")

    git = shutil.which("git")
    if git:
        try:
            proc = _run([git, "--version"])
            ok(_first_line(proc.stdout or proc.stderr) or "git available")
        except (OSError, subprocess.SubprocessError):
            bad("git found but --version failed")
    else:
        bad("git missing (install Git for Windows: winget install --id Git.Git -e)")

    for name in SKILL_NAMES:
        if (skills_dir / name / "SKILL.md").is_file():
            ok(f"skill {name}")
        else:
            bad(f"skill {name} missing")

    publisher_skill = ""
    for candidate in _publisher_skill_candidates(dsh_home):
        if candidate.is_file():
            publisher_skill = str(candidate)
            break
    if publisher_skill:
        warn(f"publisher skill found outside this bundle: {publisher_skill}")
    else:
        warn(
            "publisher not found in standard locations "
            "(install it, set FOLOTOY_PUBLISHER_DIR, or pass --publisher <path>)"
        )

    publisher = args.publisher.strip()
    if publisher:
        publisher_path = Path(publisher).expanduser()
        if not publisher_path.is_file():
            bad(f"publisher path not found: {publisher_path}")
        else:
            try:
                proc = _run([sys.executable, str(publisher_path), "--help"])
                if proc.returncode == 0:
                    ok("publisher --help")
                else:
                    detail = _first_line(proc.stderr or proc.stdout)
                    bad(f"publisher --help failed: {detail or 'exit ' + str(proc.returncode)}")
            except (OSError, subprocess.SubprocessError) as exc:
                bad(f"publisher --help failed: {exc}")
    else:
        if publisher_skill:
            hint = Path(publisher_skill).parent / "scripts" / "publisher.py"
            warn(f'publisher path not set (pass --publisher "{hint}" to validate it)')
        else:
            warn("publisher path not set (--publisher or PUBLISHER)")

    root = args.root.strip()
    if root:
        root_path = Path(root).expanduser()
        if root_path.is_dir():
            ok(f"root {root_path}")
        else:
            bad(f"root missing: {root_path}")
        firmware = args.firmware.strip()
        cover = args.cover.strip()
        if firmware and Path(firmware).expanduser().is_file():
            ok(f"firmware {Path(firmware).expanduser()}")
        else:
            bad("firmware missing")
        if cover and Path(cover).expanduser().is_file():
            ok(f"cover {Path(cover).expanduser()}")
        else:
            bad("cover missing")
    else:
        warn("no --root; project checks skipped")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
