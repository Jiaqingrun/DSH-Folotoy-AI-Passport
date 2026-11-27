# Self-audit: 0.2.4 (historical)

> The Windows field patch and 0.2.5 release are audited in
> [`AUDIT-0.2.5.md`](AUDIT-0.2.5.md). This file records the original 0.2.4
> macOS review; the 33-test count below is historical.

Date: 2026-11-26
Scope: Windows adaptation integrated from the user-provided 0.2.3 handoff
package, plus the local preflight-fallback fix.
Auditor: AI Passport agent (self-audit; not an independent security review)

## Inputs reviewed

- `HANDOFF.md`: explained the Windows machine, changed files, expected 27 tests,
  and the items that could not be tested on Windows.
- `DSH-Folotoy-AI-Passport-0.2.3-windows-adapted.zip`: extracted and compared
  file-by-file with the repository; the complete bundle and the unified diff
  were inspected, not blindly overwritten.
- `docs/WINDOWS-REPORT.md`: integrated as the run record, with provenance
  clarified.

The handoff-only `HANDOFF.md` and `windows-adaptation.diff` were **not** added to
the repository; they describe the transfer, not the product.

## Checks run on this Mac

| Check | Command | Result |
| --- | --- | --- |
| Python compile | `python3 -m compileall -q skills tests` | PASS |
| Full test suite | `python3 -m unittest discover -s tests -v` | PASS (33 tests) |
| Doctor | `python3 skills/passport-doctor/scripts/doctor.py` | PASS; 9 skills, publisher warnings expected |
| Package manifest | `npm pack --dry-run` | PASS; 60 entries, no `__pycache__` |
| Command launchers in package | `npm pack --dry-run --json` | PASS; all three `.cmd` files included |
| Whitespace | `git diff --check` | PASS |
| Local-path scan | ripgrep for the current user's home path | No hard-coded paths |
| Secret scan | ripgrep for credential-like literals | Only a deliberate test fixture; no real secret |
| Static gate tests | `tests/test_preflight_static.py` | PASS (4 tests; platform order and fallback) |
| Portability guards | `tests/test_windows_portability.py` | PASS (9 tests; UTF-8/launcher shape/probe) |
| Scanner Windows gate | `tests/test_scan_project.py` | PASS (1 test; `.ps1`/`.cmd` class-A gate) |
| XPro harness preview | `FAP-0.2.4-Windows-Final-Test` | PASS (Windows 11, Python 3.12.7, Git 2.56.1; DSH profile not installed under preview user) |
| GitHub Actions Windows job | `.github/workflows/validate.yml` | NOT RUN (new `.cmd` smoke step; no push in this review) |

## Windows evidence from the handoff

The provided run was on Windows 11 Home China, PowerShell 5.1.26100, Python
3.13.5, DSH Desktop 0.2.2-rc.5, console code page 936. It reports:

- bundle installed with `application: applied`, `warnings: []`;
- `preset-ai-passport` enabled and active;
- doctor: 9/9 skills PASS, DSH version PASS;
- scanner: correct UTF-8 for CJK and emoji paths;
- preflight: runs `tools/validate.ps1` with `-ExecutionPolicy Bypass`;
- `publish.py --dry-run`: one command line, no `--auto`;
- `.cmd` works under the default Restricted policy; `.ps1` works with Bypass;
- 27 tests passed.

I did **not** independently rerun this on Windows. The 33-test macOS suite
includes four tests added during this review; those four were not part of the
Windows handoff run.

## Findings

1. **Medium — single Windows machine, not independently reproduced.** The
   adaptation is supported by the handoff's real Windows 11 run, but this review
   ran on macOS. Do not describe it as multi-machine Windows validation.
2. **Medium — Git end-to-end was not run on the Windows machine.** Git was not
   installed there; the decoding mechanism was tested, but real `gitRoot`,
   `remote`, dirty-gate and path behavior remain unverified on Windows.
3. **Medium — real device and publishing were not tested.** Firmware flashing,
   `FAP_SCREENSHOT_V1`, the official publisher validation/submission, and the
   actual firmware build remain outside scope.
4. **Low — `.cmd` sets the console code page to 65001 for its run.** This is not
   a machine-wide setting, but a parent console can observe it when the wrapper
   is called from an existing shell. The tested handoff run used it successfully.
5. **Low — long paths, UNC/network paths, and PowerShell 7 are unverified.** The
   `\\?\` long-path prefix is still not implemented.
6. **Fixed during this review — scanner ignored `.ps1`/`.cmd` gate.** A Windows project with `AGENTS.md` and `tools/validate.ps1` was classified B/C instead of A because `signals.validate` only checked `validate.sh`. It now accepts all three gate names; regression test added.
7. **Fixed during this review — launchers trusted a broken `py.exe`.** On the XPro machine `py.exe` is on PATH but has no registered CPython; every `.cmd`/`.ps1` tried `py -3` and failed. Launchers now probe and fall back to `python`. The Windows harness preview passed after the fix.
8. **Fixed during this review — `preflight.py --static` fallback.** The handoff
   version returned a skip when the first existing gate's runner was absent
   (for example a `.ps1` without PowerShell) instead of trying the next gate.
   It now falls through and has four regression tests.

## Verdict

The Windows adaptation is integrated, the 33-test macOS suite and package shape pass,
and the handoff's single-machine Windows evidence is recorded. Windows is still
a compatibility beta: Git end-to-end, a second Windows machine, PowerShell 7,
long/UNC paths, real devices, and store publication remain `Unverified`.
