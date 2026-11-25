"""Regression tests for the project-folder rename helper."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "passport-develop" / "scripts" / "rename_project.py"


class RenameProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.app = self.base / "placeholder-app"
        self.app.mkdir()
        (self.app / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.16)\n", encoding="utf-8")
        (self.app / "main").mkdir()
        (self.app / "main" / "app.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_tool(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.app), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dry_run_does_not_rename(self) -> None:
        result = self.run_tool("--name", "Star Dust")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dry-run", result.stdout)
        self.assertTrue(self.app.is_dir())
        self.assertFalse((self.base / "star-dust").exists())

    def test_apply_renames_to_slug(self) -> None:
        result = self.run_tool("--name", "Star Dust", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.base / "star-dust"
        self.assertTrue(target.is_dir())
        self.assertFalse(self.app.exists())
        self.assertTrue((target / "main" / "app.c").is_file())


    def test_reports_next_cwd_when_run_inside_project(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", ".", "--name", "Star Dust", "--apply"],
            cwd=str(self.app),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("next cwd:", result.stdout)
        self.assertTrue((self.base / "star-dust").is_dir())

    def test_apply_keeps_unicode_name(self) -> None:
        result = self.run_tool("--name", "星尘冒险", "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.base / "星尘冒险").is_dir())

    def test_existing_target_is_refused(self) -> None:
        (self.base / "star-dust").mkdir()
        result = self.run_tool("--name", "Star Dust", "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("target already exists", result.stderr)
        self.assertTrue(self.app.is_dir())

    def test_bundle_is_refused(self) -> None:
        (self.app / "package.json").write_text(
            json.dumps({"name": "fake-bundle", "dsh": {"bundle": {"patch": "./cordis.patch.yml"}}}),
            encoding="utf-8",
        )
        (self.app / "cordis.patch.yml").write_text("- insert: []\n", encoding="utf-8")
        result = self.run_tool("--name", "Star Dust", "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("DSH bundle/profile", result.stderr)
        self.assertTrue(self.app.is_dir())

    def test_linked_worktree_is_refused(self) -> None:
        (self.app / ".git").write_text("gitdir: /tmp/elsewhere\n", encoding="utf-8")
        result = self.run_tool("--name", "Star Dust", "--apply")
        self.assertEqual(result.returncode, 2)
        self.assertIn("linked git worktree", result.stderr)
        self.assertTrue(self.app.is_dir())

    def test_unchanged_when_already_matching(self) -> None:
        app = self.base / "star-dust"
        self.app.rename(app)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(app), "--name", "Star Dust", "--apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status: unchanged", result.stdout)
        self.assertTrue(app.is_dir())

    def test_json_record(self) -> None:
        result = self.run_tool("--name", "Star Dust", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "dry-run")
        self.assertTrue(data["new"].endswith("star-dust"))


if __name__ == "__main__":
    unittest.main()
