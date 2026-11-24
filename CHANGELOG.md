# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
