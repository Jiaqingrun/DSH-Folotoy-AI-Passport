# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.5] - 2026-11-27

### Added

- `tests/test_doctor_publisher.py` (3 tests) covering explicit,
  `$DSH_HOME/skills`, home-clone, and platform-specific publisher locations.
- `test_long_path_retries_without_cwd` for the Windows >260-character static
  gate. Total suite: 37 tests.

### Fixed

- Windows field P1: `preflight.py --static` failed with `[WinError 267]` when the
  project root exceeded 260 characters. It now retries the gate without a
  `cwd` after `NotADirectoryError`; the gate is invoked by absolute path.
- Windows field P2: `doctor.py` reported "publisher skill not installed" when the
  official publisher was installed outside `$DSH_HOME/skills`. It now checks
  `FOLOTOY_PUBLISHER_DIR`, the DSH home, `~/folotoy-publisher`, and platform
  locations, and gives a `--publisher` hint when found.

### Notes

- The 0.2.3 adaptation completed a real build, flash, 8 real-screen captures,
  and a community submission (project 2749, revision 6901, approved/published).
  The 0.2.4 validation only exercised the publish dry-run; do not conflate them.
- The Windows field run had 42 harness checks PASS and 36 tests after applying
  the patch. The 37th test is the new P1 regression test; the shipped Python code
  is the field-tested code.

## [0.2.4] - 2026-11-26

### Added

- `.cmd` launchers (`doctor.cmd`, `preflight.cmd`, `publish.cmd`) that run under
  the Windows default `Restricted` execution policy, where every `.ps1` is
  refused.
- `tests/test_windows_portability.py` (9 tests) guarding UTF-8 stdio, explicit
  UTF-8 subprocess decoding, the launcher pairs, and DSH Desktop version
  detection.
- `tests/test_preflight_static.py` (4 tests) for Windows/POSIX static-gate order
  and fallback when PowerShell/bash is unavailable. Total suite: 33 tests.

### Fixed

- Windows: `doctor.py`, `scan_project.py`, `preflight.py`, and
  `lint_store_copy.py` now force UTF-8 on stdout/stderr. Before, a piped call on a
  cp936/cp932 console produced mojibake for non-ASCII paths and raised
  `UnicodeEncodeError` for names outside the code page (for example a project
  folder containing an emoji).
- Windows: subprocess output from `git` is decoded as UTF-8 with replacement
  instead of the ANSI code page, which could raise `UnicodeDecodeError`.
- Windows: `doctor.py` finds the DSH version from
  `%USERPROFILE%\.dsh\dsh-runtimes\*\runtime.json`, because DSH Desktop does not
  put `dsh` on `PATH`. `DSH_CLI` is honoured as an override.
- Windows: `scan_project.py` reports repo-relative paths in POSIX form so cards
  are byte-comparable with macOS, and directory skipping/firmware detection is
  case-insensitive (Windows editors capitalize `Build`). Its class-A gate now
  recognises `tools/validate.ps1` and `tools/validate.cmd` as well as `.sh`.
- Windows: `preflight.py --static` prefers the project's `validate.ps1` /`.cmd`
  and runs PowerShell with `-ExecutionPolicy Bypass`; if the preferred runner is
  absent it now falls through to the next available gate instead of skipping.
  Previously a project that shipped `validate.sh` plus `validate.ps1` was skipped
  whenever `bash` was missing.
- Windows: `rename_project.py` retries a rename that fails because another
  program holds the folder open (WinError 32), and reports what to close.
- Windows: the `.ps1` launchers switch `[Console]::OutputEncoding` to UTF-8 and no
  longer set `$ErrorActionPreference = 'Stop'` around the native call, which used
  to turn Python's stderr diagnostics into a terminating `NativeCommandError`.
- Docs: `INSTALL-WINDOWS.md` claimed 8 skills (there are 9), told testers to run
  `.ps1` directly although the default policy blocks it, and omitted the Git
  install command and the UTF-8/`python3` caveats.
- Windows: the `.cmd`/`.ps1` launchers now probe `py -3 -c "import sys"` and fall
  back to `python` when `py.exe` exists but has no registered interpreter (the
  state on the XPro validation machine). Regression test added.
- Windows: real Windows 11 / PowerShell 5.1 / Python 3.13.5 installation run is
  recorded in `docs/WINDOWS-REPORT.md`; Git end-to-end and real-device tests
  remain unverified.

## [0.2.3] - 2026-11-25

### Added

- Real-screen-first visual verification: the agent prefers a running-firmware
  framebuffer capture over mockups, simulators, photos, source review, or stale
  images; it opens the actual PNG, compares every changed screen/state, fixes
  the firmware, and recaptures.
- `passport-code-audit` skill for a strict post-implementation audit of project
  and security compliance plus runtime smoothness, with a blocking P0/P1 rule.
- Advisory `scan_code.py` signal collector for unsafe calls, heap calls,
  blocking delays, full redraws, secret-like literals, and open markers.
- Bilingual real-screen capture reference and bilingual compliance/smoothness
  checklists.
- Three scanner regression tests; total suite is now 19 tests.

### Changed

- `passport-develop`, `passport-device-test`, the persona, README, doctor, and
  design notes now require real-pixel verification and the completion audit.
- Version bumped to `0.2.4`; CI step renamed to regression tests; API-compatible
  with 0.2.3.

## [0.2.2] - 2026-11-25

### Added

- Project-folder rename policy: when a firmware/app name is finalized or
  changed, rename that app's project root to the normalized name automatically.
- `skills/passport-develop/scripts/rename_project.py`, a dry-run-by-default
  helper that preserves Unicode names, normalizes unsafe punctuation, prefixes
  Windows-reserved names, and refuses DSH bundles/profiles, linked worktrees,
  symlinks, home/root, and existing targets.
- Nine regression tests for the rename helper (dry-run, apply, Unicode,
  existing target, bundle refusal, worktree refusal, unchanged, JSON record).
- Persona, develop skill (zh/en), README, and design notes document the rename
  rule and cwd refresh.
- Self-audit record: `docs/AUDIT-0.2.2.md`.

### Changed

- Version bumped to `0.2.2`.

## [0.2.1] - 2026-11-25

### Added

- Default target rule: an unspecified "create an app/game" request means
  FoloToy AI Passport firmware, not a desktop/web/mobile app.
- Full-button rule: every application/game must give UP/DOWN/OK distinct,
  logical short/long/double roles with truthful on-screen hints.
- First-upload cover policy: generate a portrait 3:4 render of the actual
  finished app/game; stop if rendering is unavailable or unfinished.
- Update cover policy: preserve the published cover by default. `publish.py`
  finds the existing exact 3:4 cover under `--root`, or accepts
  `--previous-cover`, and reuses it; `--cover` is only for an intentional change.
- Regression tests for the new-upload guard, update cover preservation, explicit
  cover replacement, and `--previous-cover` validity; CI now runs them.
- Self-audit record: `docs/AUDIT-0.2.1.md`.

### Changed

- `publish.py` no longer treats a cover as mandatory input for updates; it
  requires one for a new upload and explains how to generate it.
- Agent persona, router, develop, publish, and device-test guidance now include
  the target, button, and cover defaults.
- Version bumped to `0.2.1`.
- Fixed a Windows `UnicodeEncodeError` when the dry-run printed a Chinese submit
  command on a cp1252 console; stdio now uses UTF-8 with replacement.

## [0.2.0] - 2026-11-24

### Added

- Windows-compatible Python entry points for doctor, preflight, and publish.
- PowerShell launchers (`doctor.ps1`, `preflight.ps1`, `publish.ps1`) that locate
  `py -3`, `python3`, or `python`.
- Cross-platform wrappers keep the existing `.sh` entry points for macOS/Linux.
- `INSTALL-WINDOWS.md` with a group-testing checklist and feedback template.
- `docs/WINDOWS.md` with the Windows acceptance checklist and known limitations.
- Repository metadata, bilingual README, changelog, contribution guide, security
  policy, code of conduct, and a cross-platform smoke-test workflow that passes
  on Ubuntu and Windows.
- Package name `dsh-folotoy-ai-passport` for a public repository while remaining
  locally installable as a DSH bundle.

### Changed

- Canonical script logic moved to Python; `.sh` files are thin launchers.
- `passport-doctor` and `passport-publish` documentation now shows both
  macOS/Linux and Windows commands.
- `passport-router` documentation shows `python3` and `py -3` forms.
- Agent persona includes an explicit platform rule: `python3` + `.sh` on
  macOS/Linux, `py -3` + `.ps1` on Windows.

### Security

- `publish.py` remains dry-run by default and never adds `--auto`.
- No authorization codes, tokens, cookies, firmware binaries, or publisher skill
  are included.

## [0.1.0] - 2026-11-24

### Added

- Initial DSH agent preset/bundle for FoloToy AI Passport projects.
- Eight skills: router, setup, build, debug, develop, device-test, publish, doctor.
- Local DSH installation, session-level skill discovery, and macOS regression
  tests.
- Publishing preflight, dry-run, and controlled-submission wrapper with explicit
  manual confirmation.
