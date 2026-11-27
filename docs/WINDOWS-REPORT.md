# Windows adaptation report

Date: 2026-11-26
Bundle: `dsh-folotoy-ai-passport` 0.2.4 (initial report); 0.2.5 field patch
Test machine: Windows 11 Home China, PowerShell 5.1.26100, Python 3.13.5,
DSH Desktop 0.2.2-rc.5 (Electron 44.7.0, Node 24.21.0, pnpm 11.28.5), console
code page 936.

This page records what was found while installing and running the bundle on a real
Windows machine, what was changed, and what is still unverified.

The initial Windows run came from the 0.2.3 handoff package. The 0.2.4 changes
were later field-tested on 2026-11-27 (see the field update below); the historical
section retains the original 33-test macOS review context.

## 2026-11-27 field rerun (0.2.4 + patch)

A second pass was run on the same Windows 11 machine under the DSH user `30339`
(not the qrssh preview account):

- Environment: Windows 11 Home China `10.0.26300`, zh-CN, code page 936;
  PowerShell 5.1.26100 + pwsh 7.7.0; Python 3.13.5; Git 2.56.1;
  DSH Desktop 0.2.2-rc.5.
- Install: local link at `C:\Users\30339\DSH-plugins\DSH-Folotoy-AI-Passport`;
  `application: applied`, `warnings: []`, version 0.2.4.
- Harness: **42 checks, 42 PASS / 0 FAIL / 0 WARN / 0 SKIP**, `FINAL: PASS`.
  Evidence: `H:\桌面\FAP-0.2.4-Windows-Final-Test\evidence\20261126-194531\`.
- DSH: `preset-ai-passport` enabled/active; a new AI Passport session returned
  the AI PASSPORT persona, the bundle's `passport-router` base directory, and all
  9 passport skills.
- Git end-to-end: a real repo with a Chinese path and Chinese remote kept
  `gitRoot`/`remote` intact; `dirty` changed false → true.
- Long path: a 324-character class-A project scanned normally; `preflight`
  failed **before** the P1 fix with `[WinError 267]` and passed **after** it.
- UNC: `\\localhost\C$\...` scanned class A and passed the static gate.
- PowerShell 7: `pwsh -NoProfile -File doctor.ps1` exited 0 with 9 skills and no
  `NativeCommandError`.
- Publish: real `publisher.py validate` passed; update dry-run preserved the
  existing 3:4 cover and contained `--project-id 2749`, with no `--auto` or
  `--confirmed`.
- Real end-to-end (0.2.3 adaptation, separate session): ESP-IDF 5.5.3 build
  produced a 707,248-byte full image; the device was flashed; 8 real 240×320
  screenshots were captured; project **2749** / revision **6901**
  (`community-e8527287`) was submitted and **approved/published**. This is
  **0.2.3** evidence, not a 0.2.4 publish.

The field patch (`windows-field-fixes.patch`) fixed P1 (long-path static gate)
and P2 (doctor publisher false negative). After applying it, Windows ran **36
tests**; this Mac added one P1 regression test and now runs **37**. The Python
code that ships in 0.2.5 is the field-tested code; only the test and docs changed
after the Windows run.

Still not verified: a second Windows machine (`LongPathsEnabled=0`), DSH restart
/ long-running stability, concurrent sessions, store review rules, and device
models other than the field device. The P1 retry drops `cwd` for the child, so a
gate that relies on the process cwd rather than absolute paths could behave
differently (see `docs/AUDIT-0.2.5.md`).

## Installation result (historical 0.2.4 run)

- Installed from the repository root at `C:\DSH\plugins\DSH-Folotoy-AI-Passport`.
- `plugin_manager action=install_bundle` returned `application: applied` and
  `warnings: []`; the profile records
  `"dsh-folotoy-ai-passport": "link:C:/DSH/plugins/DSH-Folotoy-AI-Passport"` and a
  junction under `node_modules`.
- `preset-ai-passport` is `enabled: true`, `fiberPhase: active`.
- `doctor.py`: DSH version PASS, python PASS, 9/9 skills PASS. Git is not
  installed on this machine, so `git` is FAIL — an environment gap, not a bundle
  defect.

## Fixed

| # | Symptom on Windows | Cause | Fix |
|---|---|---|---|
| 1 | `--json` output shows mojibake for CJK paths; a folder containing an emoji raises `UnicodeEncodeError: 'gbk' codec can't encode character '\U0001f3ae'` | `doctor.py`, `scan_project.py`, `preflight.py`, `lint_store_copy.py` printed with the ANSI code page when stdout was a pipe | `_configure_stdio()` forces UTF-8 with `errors="replace"` in all four |
| 2 | Every `.ps1` launcher is refused: `因为在此系统上禁止运行脚本` | Windows client default execution policy is `Restricted`; the docs told testers to run `.ps1` directly | added `doctor.cmd` / `preflight.cmd` / `publish.cmd`; `.ps1` now documented as needing `-ExecutionPolicy Bypass` |
| 3 | `preflight.py --static` silently skipped a project gate that existed | it preferred `tools/validate.sh`, and `bash` is absent unless Git Bash/WSL is installed, so the run ended as `WARN static check skipped` even though `tools/validate.ps1` existed | on Windows the order is `.ps1` → `.cmd` → `.sh`, and PowerShell runs with `-ExecutionPolicy Bypass` |
| 4 | `git` output decoded as cp936 could raise `UnicodeDecodeError` | `subprocess.run(..., text=True)` uses the locale encoding for pipes | `encoding="utf-8", errors="replace"` in `doctor.py`, `scan_project.py`, `preflight.py` |
| 5 | `doctor.py` always printed `WARN DSH version not detectable` | DSH Desktop keeps `dsh` off `PATH` (it lives under `resources\runtime\cli\bin`) | fall back to `%USERPROFILE%\.dsh\dsh-runtimes\*\runtime.json` → `desktopVersion`; `DSH_CLI` override |
| 6 | Scanner cards differ between Windows and macOS | `str(path.relative_to(root))` emits `\` on Windows | `_relative()` returns `as_posix()` |
| 7 | `Build/` (capitalized) was not skipped; firmware under it was not found | `SKIP_DIRS` and the `"build"` marker were compared case-sensitively | `casefold()` comparisons |
| 8 | `.ps1` launchers turned Python's stderr into `NativeCommandError` noise | `$ErrorActionPreference = 'Stop'` around a native call | removed; launchers now capture `$LASTEXITCODE` and restore console encoding |
| 9 | `rename_project.py --apply` fails with "另一个程序正在使用此文件" | Windows refuses to rename a directory held open (WinError 32) | retry with backoff (6 attempts, 0.15 s → 2 s) and a message naming what to close |
| 10 | Docs: "8 个技能" but there are 9; no Git install command; `python3` in English skills | documentation drift | `INSTALL-WINDOWS.md`, `docs/WINDOWS.md`, `README.md`, `CHANGELOG.md`, and 7 `SKILL.md` files updated |
| 11 | Scanner classified a Windows project as B/C even with `tools/validate.ps1` | class-A gate only looked for `tools/validate.sh` | gate now accepts `.sh`, `.ps1`, or `.cmd`; regression test added |
| 12 | Every `.cmd`/`.ps1` launcher failed on XPro: `py.exe` exists but `py -3` has no installed Python | launchers trusted `where py` without probing it | probe `py -3 -c "import sys"` and fall back to `python`; regression test added |

## Regression evidence

```
python -m compileall -q skills tests        exit 0
python -m unittest discover -s tests        27 tests, OK  (Windows handoff: 19 existing + 8 new)
python -m unittest discover -s tests        33 tests, OK  (macOS revalidation: +6 preflight/scanner/launcher tests)
doctor.py                                   9/9 skills PASS, DSH 0.2.2-rc.5 PASS, git FAIL (not installed)
scan_project.py --root .                    class C, exit 0
scan_project.py --root <CJK path>           correct UTF-8
scan_project.py --root <emoji path>         correct UTF-8 (previously UnicodeEncodeError)
preflight.py --root <fixture> --static      PASS static checks (runs tools/validate.ps1)
publish.py --dry-run                        one command line, no --auto, Chinese intact
doctor.cmd                                  works under the default Restricted policy
doctor.ps1                                  works with -ExecutionPolicy Bypass
```

## Still unverified (historical 0.2.4 report; see field update above)

- Git-dependent end-to-end paths (`gitRoot`, `remote`, dirty gate): Git is not
  installed on this machine, so only the decoding mechanism was verified — a
  UTF-8 child process under `text=True` raises `UnicodeDecodeError: 'gbk' codec
  can't decode byte 0xad`, and under `encoding="utf-8"` decodes to
  `refs/heads/中文分支`.
- Firmware build/flash with the official ESP-IDF toolchain (out of scope here).
- The official `folotoy-ai-passport-publisher` skill; only the dry-run path ran.
- Real device capture (`FAP_SCREENSHOT_V1`) and store submission.
- PowerShell 7 (`pwsh` exists? not on this machine), UNC paths, network drives, and
  paths longer than `MAX_PATH`.
- DSH Web (browser) hosts; only DSH Desktop was exercised.

## What not to do

- Do not drop the `.sh` launchers or make the bundle depend on bash/WSL.
- Do not lower the `git missing` FAIL to WARN; keep the gate, add a remedy hint.
- Do not relax `publish.py`'s dry-run default or add `--auto`.
- Do not fork the Python logic per platform; keep one implementation plus thin
  launchers.
- Do not add third-party Python dependencies or change `engines.dsh`.
- Do not change the system-wide code page or `git config`; the `.cmd` launchers only set the console code page for their run.
