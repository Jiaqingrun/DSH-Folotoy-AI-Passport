---
name: passport-doctor
description: Diagnose a broken AI Passport agent environment, including missing skills, publisher CLI, Python, git, firmware/cover, or DSH version. Use when a check fails or before the first publish.
whenToUse: The user reports a missing tool, a failed preflight, an unknown skill, or asks "why can't it publish".
---

# Diagnose the environment

Run `<base>/scripts/doctor.py` first. It is read-only and prints PASS/FAIL lines. The `references/checks.md` file records the expected PASS lines and their commands.

Cross-platform invocation:

- macOS/Linux: `python3 <base>/scripts/doctor.py ...` or `<base>/scripts/doctor.sh ...`
- Windows PowerShell: `py -3 <base>\scripts\doctor.py ...`, `<base>\scripts\doctor.cmd ...`,
  or `<base>\scripts\doctor.ps1 ...` with `-ExecutionPolicy Bypass` (the Windows
  default policy is Restricted and refuses any `.ps1`).

Check and report, in this order:

1. DSH version is at least 0.2.2-rc.5 (the bundle's `engines.dsh`).
2. `python --version` / `py -3 --version` is 3.10+.
3. `git --version` works.
4. All 9 bundled skills are in the catalog: the FoloToy skill set plus router, publish, code-audit, and doctor.
5. The official `folotoy-ai-passport-publisher` skill exists; if not, give the install instruction, do not bundle it.
6. The publisher script responds to `--help`.
7. The target project has a firmware candidate and a cover candidate; run the scanner if unsure.
8. The cover opens with `read_image` and is 3:4.

Do not print environment variables that may contain tokens. Do not run `authorize`, `submit`, or any network upload in this skill.
