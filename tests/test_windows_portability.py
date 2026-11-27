"""Windows portability guards for the bundle's entry points and launchers.

These tests encode the Windows findings that are easy to regress:

- Python must force UTF-8 on stdout, otherwise a piped call on a cp936/cp932
  console either mangles non-ASCII paths or dies with UnicodeEncodeError.
- Subprocess output must be decoded as UTF-8 explicitly, not with the ANSI code
  page that ``text=True`` picks on Windows.
- The PowerShell launchers must switch the console to UTF-8 around the call.
- Every ``.ps1`` needs a ``.cmd`` twin, because the Windows default execution
  policy (Restricted) refuses to run any ``.ps1`` at all.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ENTRY_POINTS = {
    "doctor": ROOT / "skills" / "passport-doctor" / "scripts" / "doctor.py",
    "scan_project": ROOT / "skills" / "passport-router" / "scripts" / "scan_project.py",
    "preflight": ROOT / "skills" / "passport-publish" / "scripts" / "preflight.py",
    "publish": ROOT / "skills" / "passport-publish" / "scripts" / "publish.py",
    "lint_store_copy": ROOT / "skills" / "passport-publish" / "scripts" / "lint_store_copy.py",
    "scan_code": ROOT / "skills" / "passport-code-audit" / "scripts" / "scan_code.py",
    "rename_project": ROOT / "skills" / "passport-develop" / "scripts" / "rename_project.py",
}

LAUNCHER_DIRS = (
    ROOT / "skills" / "passport-doctor" / "scripts",
    ROOT / "skills" / "passport-publish" / "scripts",
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StdioTests(unittest.TestCase):
    def test_every_entry_point_forces_utf8_stdout(self) -> None:
        for name, path in ENTRY_POINTS.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertIn("def _configure_stdio", text)
                self.assertIn('reconfigure(encoding="utf-8"', text)
                # defined once, called at least once
                self.assertGreaterEqual(text.count("_configure_stdio"), 2)

    def test_no_implicit_ansi_subprocess_decoding(self) -> None:
        for name, path in ENTRY_POINTS.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertNotIn("text=True", text)

    def test_subprocess_callers_decode_utf8_explicitly(self) -> None:
        for name in ("doctor", "scan_project", "preflight"):
            text = ENTRY_POINTS[name].read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertIn('encoding="utf-8"', text)


class LauncherTests(unittest.TestCase):
    def test_powershell_launcher_switches_console_to_utf8(self) -> None:
        for directory in LAUNCHER_DIRS:
            for script in sorted(directory.glob("*.ps1")):
                text = script.read_text(encoding="utf-8")
                with self.subTest(launcher=script.name):
                    self.assertIn("[Console]::OutputEncoding", text)
                    self.assertIn("UTF8Encoding", text)
                    for line in text.splitlines():
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            continue
                        self.assertNotIn(
                            "$ErrorActionPreference",
                            stripped,
                            f"{script.name} must not override error handling around the native call",
                        )

    def test_cmd_launcher_exists_and_stays_ascii(self) -> None:
        for directory in LAUNCHER_DIRS:
            for script in sorted(directory.glob("*.ps1")):
                cmd = script.with_suffix(".cmd")
                with self.subTest(launcher=cmd.name):
                    self.assertTrue(cmd.is_file(), f"{cmd.name} missing")
                    data = cmd.read_bytes()
                    self.assertTrue(all(byte < 128 for byte in data), "cmd launcher must stay ASCII")

    def test_launcher_pairs_match_python_entry_points(self) -> None:
        for directory in LAUNCHER_DIRS:
            for cmd in sorted(directory.glob("*.cmd")):
                with self.subTest(launcher=cmd.name):
                    self.assertTrue(cmd.with_suffix(".py").is_file())

    def test_launchers_probe_py_before_trusting_it(self) -> None:
        for directory in LAUNCHER_DIRS:
            for cmd in sorted(directory.glob("*.cmd")):
                text = cmd.read_text(encoding="utf-8")
                with self.subTest(launcher=cmd.name):
                    self.assertIn('py -3 -c "import sys"', text)
            for ps1 in sorted(directory.glob("*.ps1")):
                text = ps1.read_text(encoding="utf-8")
                with self.subTest(launcher=ps1.name):
                    self.assertIn('& py -3 -c "import sys"', text)


class DoctorDetectionTests(unittest.TestCase):
    def test_desktop_version_comes_from_runtime_manifest(self) -> None:
        module = _load("doctor_under_test", ENTRY_POINTS["doctor"])
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            runtime = home / "dsh-runtimes" / "dsh-primary-runtime"
            runtime.mkdir(parents=True)
            (runtime / "runtime.json").write_text(
                json.dumps({"desktopVersion": "0.2.2-rc.5"}), encoding="utf-8"
            )
            self.assertEqual(module._desktop_version(home), "0.2.2-rc.5")
            self.assertEqual(module._desktop_version(home / "missing"), "")

    def test_desktop_version_tolerates_broken_manifest(self) -> None:
        module = _load("doctor_under_test_broken", ENTRY_POINTS["doctor"])
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            runtime = home / "dsh-runtimes" / "broken"
            runtime.mkdir(parents=True)
            (runtime / "runtime.json").write_text("{not json", encoding="utf-8")
            self.assertEqual(module._desktop_version(home), "")


if __name__ == "__main__":
    unittest.main()
