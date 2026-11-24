# AI Passport

Unofficial agent preset for FoloToy AI Passport projects. Not affiliated with FoloToy; it cannot approve a store submission.

## What it does

- Classifies a project as A (official gate + firmware + cover), B (at least one publishable artifact but not a full gate), or C (no firmware binary and no cover).
- Includes the official MIT skills for build, debug, develop, device test, and setup.
- Adds router, publish, and doctor skills plus read-only scan/preflight/publish scripts.
- Prepares a store submission with manual authorization; it never stores codes or tokens.

## Requirements

- DSH 0.2.2-rc.5 or newer.
- Python 3.10+ for bundled scripts (`python3` on macOS/Linux, `py -3` on Windows).
- The official `folotoy-ai-passport-publisher` skill, installed separately; it is not bundled (the official zip has no LICENSE).
- A cover image that already exists; this bundle does not generate images.

## Limits

- No automatic authorization, no `--auto` default, no browser automation.
- No device tests, no image generation, no guarantee of store approval.
- macOS/Linux use `*.sh`/`*.py`; Windows use `*.ps1`/`py -3 *.py` (PowerShell 5.1+).
- Windows support is implemented by the Python scripts and PowerShell launchers; the official ESP-IDF setup skill may still recommend WSL for some toolchains. Windows is not yet tested.
- Windows PowerShell execution policy can block `.ps1`; call `py -3 <script>.py` directly or use `powershell -ExecutionPolicy Bypass -File <script>.ps1`.
- Windows acceptance checklist: `docs/WINDOWS.md`.
- The publisher skill's own license/terms apply; do not redistribute it with this bundle.
