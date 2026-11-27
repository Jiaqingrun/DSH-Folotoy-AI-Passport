"""Tests for platform-specific static gate ordering and fallback."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "passport-publish" / "scripts" / "preflight.py"


def _load():
    spec = importlib.util.spec_from_file_location("preflight_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StaticGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "tools").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _touch(self, name: str) -> None:
        (self.root / "tools" / name).write_text("exit 0\n", encoding="utf-8")

    def test_windows_prefers_ps1_then_cmd_then_sh(self) -> None:
        for name in ("validate.sh", "validate.ps1", "validate.cmd"):
            self._touch(name)
        module = _load()
        self.assertEqual(
            module._static_order(self.root, "nt"),
            ["validate.ps1", "validate.cmd", "validate.sh"],
        )

    def test_posix_prefers_sh_then_ps1_then_cmd(self) -> None:
        for name in ("validate.sh", "validate.ps1", "validate.cmd"):
            self._touch(name)
        module = _load()
        self.assertEqual(
            module._static_order(self.root, "posix"),
            ["validate.sh", "validate.ps1", "validate.cmd"],
        )

    def test_missing_powershell_falls_back_to_bash(self) -> None:
        for name in ("validate.ps1", "validate.sh"):
            self._touch(name)
        module = _load()
        real_which = module.shutil.which

        def fake_which(name: str):
            if name in {"pwsh", "powershell"}:
                return None
            if name == "bash":
                return "/bin/bash"
            return real_which(name)

        with patch.object(module.shutil, "which", side_effect=fake_which), patch.object(
            module, "_run", return_value=subprocess.CompletedProcess([], 0, "", "")
        ) as run:
            ok, message = module._run_static(self.root, "nt")
        self.assertTrue(ok, message)
        self.assertEqual(message, "static checks")
        self.assertEqual(run.call_args.args[0][0], "/bin/bash")

    def test_no_gate_reports_skip(self) -> None:
        module = _load()
        ok, message = module._run_static(self.root, "nt")
        self.assertFalse(ok)
        self.assertIn("not found", message)

    def test_long_path_retries_without_cwd(self) -> None:
        self._touch("validate.ps1")
        module = _load()
        cwds: list[Path | None] = []

        def fake_run(command, cwd=None, timeout=30):
            cwds.append(cwd)
            if len(cwds) == 1:
                raise NotADirectoryError(20, "directory name is invalid")
            return subprocess.CompletedProcess(command, 0, "", "")

        with patch.object(
            module.shutil, "which", side_effect=lambda name: "C:/pwsh.exe" if name in {"pwsh", "powershell"} else None
        ), patch.object(module, "_run", side_effect=fake_run):
            ok, message = module._run_static(self.root, "nt")
        self.assertTrue(ok, message)
        self.assertEqual(message, "static checks")
        self.assertEqual(cwds, [self.root, None])


if __name__ == "__main__":
    unittest.main()
