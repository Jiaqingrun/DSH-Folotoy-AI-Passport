# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Version bumped to `0.2.3`; CI step renamed to regression tests.

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
