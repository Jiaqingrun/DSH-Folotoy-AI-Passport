"""Regression tests for the publish wrapper's cover policy.

Run with: python -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "skills" / "passport-publish" / "scripts" / "publish.py"


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


class PublishCoverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.publisher = self.root / "publisher.py"
        self.publisher.write_text(
            "import sys\n"
            "if '--help' in sys.argv:\n"
            "    print('fake publisher')\n"
            "    raise SystemExit(0)\n"
            "if 'validate' in sys.argv or 'submit' in sys.argv:\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(0)\n",
            encoding="utf-8",
        )
        self.firmware = self.root / "firmware.bin"
        self.firmware.write_bytes(b"\x00" * 4096)
        self.instructions = self.root / "instructions.md"
        self.instructions.write_text("操作说明\n", encoding="utf-8")
        self.changelog = self.root / "changelog.md"
        self.changelog.write_text("本次更新\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_publish(self, *extra: str) -> subprocess.CompletedProcess[str]:
        common = [
            sys.executable,
            str(PUBLISH),
            "--publisher",
            str(self.publisher),
            "--firmware",
            str(self.firmware),
            "--title-zh",
            "测试应用",
            "--description-zh",
            "测试说明",
            "--instructions-zh-file",
            str(self.instructions),
            "--root",
            str(self.root),
            "--dry-run",
        ]
        return subprocess.run(
            [*common, *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_new_upload_with_cover(self) -> None:
        cover = self.root / "game-cover.png"
        _png(cover, 30, 40)
        result = self.run_publish("--cover", str(cover))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--cover", result.stdout)

    def test_new_upload_without_cover_fails(self) -> None:
        result = self.run_publish()
        self.assertEqual(result.returncode, 2)
        self.assertIn("first upload requires a generated portrait 3:4 render cover", result.stderr)

    def test_update_without_cover_preserves_exact_3x4(self) -> None:
        cover = self.root / "old-cover.png"
        _png(cover, 30, 40)
        result = self.run_publish(
            "--project-id", "1943",
            "--changelog-zh-file", str(self.changelog),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cover: preserving", result.stderr)
        self.assertIn(str(cover), result.stdout)
        self.assertNotIn("--cover " + str(self.root / "new-cover.png"), result.stdout)

    def test_update_without_cover_or_candidate_fails(self) -> None:
        result = self.run_publish(
            "--project-id", "1943",
            "--changelog-zh-file", str(self.changelog),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("update needs the existing published cover", result.stderr)

    def test_update_ignores_non_3x4_cover(self) -> None:
        _png(self.root / "wrong-cover.png", 30, 30)
        result = self.run_publish(
            "--project-id", "1943",
            "--changelog-zh-file", str(self.changelog),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("update needs the existing published cover", result.stderr)

    def test_update_explicit_new_cover_is_allowed(self) -> None:
        cover = self.root / "new-cover.png"
        _png(cover, 30, 40)
        result = self.run_publish(
            "--project-id", "1943",
            "--changelog-zh-file", str(self.changelog),
            "--cover", str(cover),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(cover), result.stdout)

    def test_previous_cover_is_update_only(self) -> None:
        cover = self.root / "old-cover.png"
        _png(cover, 30, 40)
        result = self.run_publish("--previous-cover", str(cover))
        self.assertEqual(result.returncode, 2)
        self.assertIn("--previous-cover is only valid for an update", result.stderr)


if __name__ == "__main__":
    unittest.main()
