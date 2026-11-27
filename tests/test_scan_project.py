"""Regression tests for Windows static-gate detection in the project scanner."""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "skills" / "passport-router" / "scripts" / "scan_project.py"


def _png(path: Path, width: int, height: int) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + (b"\x00\x00\x00" * width) for _ in range(height))
    data = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(data)


class ScannerGateTests(unittest.TestCase):
    def test_windows_gate_detected(self) -> None:
        for gate in ("validate.ps1", "validate.cmd"):
            with self.subTest(gate=gate), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "项目🎮"
                (root / "tools").mkdir(parents=True)
                (root / "build").mkdir()
                (root / "firmware").mkdir()
                (root / "AGENTS.md").write_text("# project\n", encoding="utf-8")
                (root / "tools" / gate).write_text("exit 0\n", encoding="utf-8")
                (root / "build" / "firmware-full.bin").write_bytes(b"\x00" * 64)
                _png(root / "cover-game.png", 30, 40)

                result = subprocess.run(
                    [sys.executable, str(SCANNER), "--root", str(root), "--json"],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                card = json.loads(result.stdout)
                self.assertEqual(card["class"], "A")
                self.assertTrue(card["signals"]["validate"])
                self.assertEqual(card["firmware"][0]["path"], "build/firmware-full.bin")


if __name__ == "__main__":
    unittest.main()
