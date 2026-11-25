# Self-audit: 0.2.2

Date: 2026-11-25
Scope: DSH bundle `dsh-folotoy-ai-passport@0.2.2` in this repository
Auditor: AI Passport agent (self-audit; not an independent security review)

## Checks run

| Check | Command | Result |
| --- | --- | --- |
| Python compile | `python3 -m compileall -q skills tests` | PASS |
| Full test suite | `python3 -m unittest discover -s tests -v` | PASS (16 tests) |
| Package manifest | `npm pack --dry-run` | PASS; 47 entries, no `__pycache__` |
| Bundle rename guard | `rename_project.py --root . --name renamed-bundle` | PASS (refused: DSH bundle/profile) |
| Doctor | `python3 skills/passport-doctor/scripts/doctor.py` | PASS; publisher warnings expected |
| Project scanner | `python3 skills/passport-router/scripts/scan_project.py --root . --json` | PASS; class C is expected for the bundle |
| Whitespace | `git diff --check` | PASS |
| Dangerous-call scan | ripgrep for `eval`/`exec`/`os.system`/`system()` | No such calls in bundle scripts |
| Local-path scan | ripgrep for the current user's home path | No hard-coded local paths in source or docs |

## Findings

1. **Medium — rename is intentionally conservative.** The helper refuses a DSH
   bundle/profile, linked worktree, symlink, home directory, filesystem root, or
   existing target. A user who needs one of those renamed must do it manually
   with a separate decision; the agent must stop rather than force it.
2. **Low — active-cwd rename needs a follow-up.** When the app root is the
   session cwd, the helper moves itself to the parent before renaming and reports
   `next cwd`. The agent must switch the session to that path and recheck Git
   state; otherwise later relative commands can target a stale directory.
3. **Low — Windows real desktop not manually tested.** The test suite and
   PowerShell launcher path run on `windows-latest`; no real Windows desktop or
   device was used for this change. The existing beta boundary remains.
4. **Informational — no real project was renamed by this audit.** Rename tests
   use temporary app directories and do not touch any user project.

## Verdict

The folder-follows-firmware-name rule is implemented in the persona, develop
guidance (zh/en), README, and a tested helper. All local checks pass. The helper
is deliberately allowed to refuse unsafe targets, and that refusal is part of
the design rather than a failure to bypass.
