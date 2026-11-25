"""Tests for the advisory firmware source scanner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "passport-code-audit" / "scripts" / "scan_code.py"


class ScanCodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "main").mkdir()
        (self.root / "build").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_tool(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_collects_expected_signals(self) -> None:
        (self.root / "main" / "app.c").write_text(
            'void f(void) { strcpy(dst, src); void *p = malloc(10); vTaskDelay(1); }\n'
            '// TODO: fix\n'
            'const char *api_key = "abcdef1234567890";\n',
            encoding="utf-8",
        )
        (self.root / "build" / "ignored.c").write_text("strcpy(a,b);\n", encoding="utf-8")
        result = self.run_tool("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["files_scanned"], 1)
        self.assertGreaterEqual(data["counts"].get("unsafe-call", 0), 1)
        self.assertGreaterEqual(data["counts"].get("heap-call", 0), 1)
        self.assertGreaterEqual(data["counts"].get("blocking-delay", 0), 1)
        self.assertGreaterEqual(data["counts"].get("secret-like-literal", 0), 1)
        self.assertGreaterEqual(data["counts"].get("open-marker", 0), 1)
        self.assertIn("advisory", json.dumps(data))

    def test_clean_source_has_no_signals(self) -> None:
        (self.root / "main" / "app.c").write_text(
            "static int add(int a, int b) { return a + b; }\n", encoding="utf-8"
        )
        result = self.run_tool("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["finding_count"], 0)
        self.assertEqual(data["counts"], {})

    def test_invalid_root_fails(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root / "missing")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("root not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
