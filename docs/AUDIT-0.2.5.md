# Self-audit: 0.2.5 (Windows field fixes)

Date: 2026-11-27
Scope: the Windows field patch (`windows-field-fixes.patch`, baseline 0.2.4)
plus the one regression test missing from that patch.
Auditor: AI Passport agent on macOS (self-audit; not an independent security review)

## Inputs reviewed

- `MAC-HANDOFF.md` from the Windows machine: field evidence, two defects, and
  the action list for the Mac side.
- `windows-field-fixes.patch`: reviewed hunk-by-hunk, applied with
  `git apply --check` then `git apply`.
- `docs/WINDOWS-REPORT.md`: historical 0.2.4 report, extended with the
  2026-11-27 field rerun.
- Windows field report and evidence under
  `H:\桌面\FAP-0.2.4-Windows-Final-Test\evidence\20261126-194531\` (not copied
  into the repository).

## Patch review

The patch is narrow and applies cleanly to the 0.2.4 baseline:

| Change | Verdict |
| --- | --- |
| `doctor.py`: `_publisher_skill_candidates()`, explicit/standard/platform locations, actionable hint | Correct direction; 3 tests pass; no publisher is bundled |
| `preflight.py`: catch `NotADirectoryError` and retry static gate with `cwd=None` | Works for the field >260-character case; **cwd is intentionally dropped**, so gates that rely on the process cwd are now a documented limitation |
| `tests/test_doctor_publisher.py` (3 tests) | Pass on macOS and exercised the explicit/standard/platform branches |

The field patch did not include a regression test for the long-path retry. I added
`test_long_path_retries_without_cwd` to `tests/test_preflight_static.py`; it
asserts the first call uses the project root and the retry uses `cwd=None`.
Suite is now **37 tests** on macOS. The Windows patch run was **36 tests**; the
only post-patch change is that test and documentation, so the shipped Python code
is the same code that was field-tested.

## Checks run on this Mac

| Check | Command | Result |
| --- | --- | --- |
| Patch apply | `git apply --check windows-field-fixes.patch` | PASS |
| Python compile | `python3 -m compileall -q skills tests` | PASS |
| Full test suite | `python3 -m unittest discover -s tests -v` | PASS (37 tests) |
| Doctor | `python3 skills/passport-doctor/scripts/doctor.py` | PASS; 9 skills; publisher warning expected when absent |
| Package manifest | `npm pack --dry-run` | PASS; 61 entries, no `__pycache__` |
| Whitespace | `git diff --check` | PASS (to re-check after doc edits) |
| Windows field evidence | `MAC-HANDOFF.md` + `docs/WINDOWS-REPORT.md` | Recorded, not independently rerun on Windows by this audit |

## Findings closed from 0.2.4

1. **Git end-to-end (0.2.4 finding 2)** — closed by the Windows field run:
   real repository, Chinese path, Chinese remote, `gitRoot`/`remote` intact,
   `dirty` false→true (`B5-*`).
2. **Real device / publishing (0.2.4 finding 3)** — closed **for the 0.2.3
   adaptation** (build, flash, 8 real screenshots, submit, project 2749,
   revision 6901, approved/published). **0.2.4** was only dry-run/validate
   tested; `publish.py` is byte-for-byte unchanged from 0.2.3, but do not call
   the 0.2.3 submission a 0.2.4 field test.
3. **Single-machine (0.2.4 finding 1)** — accepted scope: one Windows 11 machine
   fully exercised; the user explicitly will not provide a second one. Do not
   claim multi-machine coverage.
4. **Long path / UNC / PowerShell 7 (0.2.4 finding 5)** — field-tested: 324-char
   class-A scan passed; `preflight` failed before P1 and passed after; UNC path
   passed; `pwsh 7.7.0` doctor passed. `LongPathsEnabled=0` remains unverified.
5. **P1 — long-path static gate** — fixed in this patch and covered by the new
   regression test.
6. **P2 — doctor publisher false negative** — fixed in this patch; the warning
   now names `FOLOTOY_PUBLISHER_DIR` and the `--publisher` remedy.

## Remaining risks / not verified

- **P1 cwd fallback:** the retry runs the gate with `cwd=None`; a gate that
  depends on the process cwd instead of `$PSScriptRoot`/absolute paths could see
  a different directory. The field gate passed, but this is not a general
  guarantee. `FAP-0.2.4` fixtures use absolute script paths.
- **`FOLOTOY_PUBLISHER_DIR` contract:** it must point at the skill directory
  containing `SKILL.md`, not at `scripts/`. Not documented in the patch itself;
  documented here.
- **`agentPreset` header mismatch (DSH-side):** Windows reported a session whose
  header says `agentPreset: standard` while the actual system prompt is AI
  PASSPORT and the router base directory is the bundle. This repository does not
  write that header; needs DSH-side confirmation. Do not fix it in the bundle.
- **0.2.5 not re-run on Windows:** only the plan/test/docs changed after the
  Windows 36-test run. Treat 0.2.5 as "field patch + test/docs", not as a new
  Windows validation round.
- **Not verified:** multi-machine Windows, `LongPathsEnabled=0`, DSH restart /
  long-running stability, concurrent sessions, store review policy, other
  devices.

## Verdict

The two field defects are real and fixed; the patch is suitable to ship as
0.2.5 with the added regression test. Windows is still a **compatibility beta
exercised on one Windows 11 machine**: installation, scripts, Git, CJK/emoji,
long path, UNC, and PowerShell 7 are field-tested; real-device/publish evidence
belongs to the 0.2.3 adaptation; multi-machine and `LongPathsEnabled=0` remain
`Unverified`.
