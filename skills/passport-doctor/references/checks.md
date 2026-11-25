# Doctor checks

PASS/WARN/FAIL lines expected from doctor.py (doctor.sh/doctor.ps1 are launchers):

- PASS DSH version <version> (or WARN if not detectable)
- PASS python <major.minor> (3.10+)
- PASS git <version>
- PASS skill <name> for all 9 skills
- WARN publisher skill not installed (expected when publish is unavailable)
- PASS publisher --help when --publisher is set
- PASS root/firmware/cover when --root is supplied

FAIL means fix before publishing; WARN means the environment can start but publish may stop.
