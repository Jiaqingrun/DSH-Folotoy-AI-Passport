# AI Passport

Unofficial agent preset for FoloToy AI Passport projects. Not affiliated with FoloToy; it cannot approve a store submission.

## What it does

- Classifies a project as A (official gate + firmware + cover), B (at least one publishable artifact but not a full gate), or C (no firmware binary and no cover).
- Includes the official MIT skills for build, debug, develop, device test, and setup.
- Adds router, publish, and doctor skills plus read-only scan/preflight/publish scripts.
- Prepares a store submission with manual authorization; it never stores codes or tokens.
- Defaults to AI Passport firmware when an app/game request names no platform.
- Requires all three function buttons to have distinct, logical roles.
- Requires a generated 3:4 render cover for a first upload; updates preserve the published cover.
- Renames the app's project root folder when its firmware/app name is finalized or changed; refuses DSH bundles, linked worktrees, symlinks, home/root, and existing targets.

## Requirements

- DSH 0.2.2-rc.5 or newer.
- Python 3.10+ for bundled scripts (`python3` on macOS/Linux, `py -3` on Windows).
- The official `folotoy-ai-passport-publisher` skill, installed separately; it is not bundled (the official zip has no LICENSE).
- A finished portrait 3:4 render for a first upload. Use available image
  tooling; the bundle does not include an image-generation model. An update
  reuses the published cover by default.

## Limits

- No automatic authorization, no `--auto` default, no browser automation.
- No device tests, no bundled image-generation model, and no guarantee of store
  approval. First-upload cover rendering depends on the image tooling available
  in the current session; if it is unavailable or unfinished, the workflow must
  stop and ask rather than upload a placeholder.
- macOS/Linux use `*.sh`/`*.py`; Windows use `*.ps1`/`py -3 *.py` (PowerShell 5.1+).
- Windows support is implemented by the Python scripts and PowerShell launchers; the official ESP-IDF setup skill may still recommend WSL for some toolchains. Windows is not yet tested.
- Windows PowerShell execution policy can block `.ps1`; call `py -3 <script>.py` directly or use `powershell -ExecutionPolicy Bypass -File <script>.ps1`.
- Windows acceptance checklist: `docs/WINDOWS.md`.
- The publisher skill's own license/terms apply; do not redistribute it with this bundle.
