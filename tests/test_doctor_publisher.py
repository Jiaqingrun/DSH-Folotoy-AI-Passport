"""Field guard: doctor must find the official publisher outside ``$DSH_HOME/skills``.

The bundle never ships the publisher, and a manual clone such as
``C:\\folotoy-publisher\\folotoy-ai-passport-publisher`` is a normal install on
Windows. Reporting "publisher skill not installed" there is misleading, and it is
what made a published project look unpublished during the 0.2.4 validation.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCTOR = ROOT / "skills" / "passport-doctor" / "scripts" / "doctor.py"


def _load():
    spec = importlib.util.spec_from_file_location("doctor_publisher_under_test", DOCTOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PublisherProbeTests(unittest.TestCase):
    def test_explicit_directory_takes_priority(self) -> None:
        module = _load()
        with tempfile.TemporaryDirectory() as temp:
            publisher = Path(temp) / "folotoy-ai-passport-publisher"
            publisher.mkdir()
            (publisher / "SKILL.md").write_text("---\nname: fixture\n---\n", encoding="utf-8")
            os.environ["FOLOTOY_PUBLISHER_DIR"] = str(publisher)
            try:
                candidates = module._publisher_skill_candidates(Path(temp) / "dsh-home")
            finally:
                os.environ.pop("FOLOTOY_PUBLISHER_DIR", None)
            self.assertEqual(Path(candidates[0]), publisher / "SKILL.md")
            self.assertTrue(Path(candidates[0]).is_file())

    def test_standard_and_platform_locations_are_checked(self) -> None:
        module = _load()
        candidates = [
            str(path).replace("\\", "/")
            for path in module._publisher_skill_candidates(Path("C:/dsh"))
        ]
        self.assertTrue(
            any("dsh/skills/folotoy-ai-passport-publisher/SKILL.md" in item for item in candidates)
        )
        if os.name == "nt":
            expected = "C:/folotoy-publisher/folotoy-ai-passport-publisher/SKILL.md"
        else:
            expected = "/opt/folotoy-publisher/folotoy-ai-passport-publisher/SKILL.md"
        self.assertIn(expected, candidates)

    def test_home_clone_is_checked(self) -> None:
        module = _load()
        candidates = [str(path) for path in module._publisher_skill_candidates(Path("C:/dsh"))]
        self.assertTrue(any("folotoy-publisher" in item for item in candidates))


if __name__ == "__main__":
    unittest.main()
