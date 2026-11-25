# Self-audit: 0.2.1

Date: 2026-11-25
Scope: DSH bundle `dsh-folotoy-ai-passport@0.2.1` in this repository
Auditor: AI Passport agent (self-audit; not an independent security review)

## Checks run

| Check | Command | Result |
| --- | --- | --- |
| Python compile | `python3 -m compileall -q skills tests` | PASS |
| Cover policy tests | `python3 -m unittest discover -s tests -v` | PASS (7 tests) |
| Package manifest | `npm pack --dry-run` | PASS; 45 entries, no `__pycache__` |
| Doctor | `python3 skills/passport-doctor/scripts/doctor.py` | PASS (publisher path warnings expected) |
| Project scanner | `python3 skills/passport-router/scripts/scan_project.py --root . --json` | PASS; class C is expected for the bundle, not an app |
| Whitespace | `git diff --check` | PASS |
| Credential/path scan | ripgrep over credentials, tokens, `/Users/qr` | No secrets or local absolute paths found |
| Dangerous-call scan | ripgrep over `eval`/`exec`/`os.system`/`system()` | No such calls in bundle scripts |

## Findings

1. **Medium — cover generation is not bundled.** The first-upload policy requires
   a finished 3:4 render, but this bundle has no image model. It therefore uses
   the image tooling available in the session and stops with instructions if
   rendering is unavailable or unfinished. The reference prompt and visual
   checks are in `skills/passport-publish/references/cover-render.md`.
2. **Low — update cover discovery can be ambiguous.** When several exact 3:4
   images whose names contain `cover` exist under `--root`, the wrapper prefers
   `cover*`, then shallower paths. Use `--previous-cover` to bind the exact file.
3. **Low — real Windows remains unverified.** The Python tests and PowerShell
   launchers run in CI on `windows-latest`; no real Windows desktop or device was
   used. This does not change the existing beta boundary.
4. **Informational — publisher validation not executed.** A real `publisher.py
   validate` needs a real merged firmware and cover, which are not part of this
   repository. The wrapper was tested with a fake publisher to verify command
   construction and cover policy only.

## Verdict

The four requested defaults are implemented in the persona, router, develop,
publish, and device-test guidance, and the update-cover rule is enforced and
tested in `publish.py`. No blocking finding was found in this self-audit. Real
store acceptance, Windows hardware, and actual cover generation remain
unverified and must be reported as such.
