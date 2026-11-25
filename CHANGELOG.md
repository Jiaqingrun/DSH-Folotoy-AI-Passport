# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
