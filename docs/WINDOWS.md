# Windows notes

Status: the bundle's scripts are implemented with a Python core plus PowerShell
launchers. The GitHub Actions smoke test passes on `windows-latest`, but
**Windows has not yet been tested on a real desktop/device**. Treat this page as
the acceptance checklist, not as a verified Windows support statement.

## Requirements

- Windows 10/11 with PowerShell 5.1 or newer.
- Python 3.10+ from python.org, installed with the `py` launcher; `py -3 --version`
  must work.
- Git for Windows (`git --version`).
- DSH 0.2.2-rc.5 or newer.
- The official `folotoy-ai-passport-publisher` skill installed separately.

The bundle does not require WSL or Git Bash for its own scripts. The official
ESP-IDF setup skill may still recommend WSL or the ESP-IDF PowerShell terminal
for building firmware; that is a toolchain requirement, not a bundle script
requirement.

## Run the bundle checks

Use `py -3` and the `.py` entry points directly; this also avoids PowerShell
execution-policy issues:

```powershell
py -3 <base>\scripts\doctor.py --publisher <publisher.py> `
  --root <project> --firmware <firmware.bin> --cover <cover.png>

py -3 <base>\scripts\preflight.py --root <project> `
  --firmware <firmware.bin> --cover <cover.png> --publisher <publisher.py>

py -3 <base>\scripts\publish.py --publisher <publisher.py> `
  --firmware <firmware.bin> --cover <cover.png> `
  --title-zh "<title>" --description-zh "<desc>" `
  --instructions-zh-file <instructions.md> --dry-run
```

The `.ps1` launchers (`doctor.ps1`, `preflight.ps1`, `publish.ps1`) perform the
same job and locate `py -3` automatically. If execution policy blocks them:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <base>\scripts\doctor.ps1
```

Prefer the direct `py -3 ...py` form in automated runs.

## Safety behavior

- `publish.py` defaults to dry-run.
- It never adds `--auto`.
- Only `--execute --confirmed` runs `submit`; `--confirmed` alone only changes the
  printed dry-run command.
- It never reads, prints, or stores authorization codes or tokens.

## Acceptance checklist on Windows

1. `py -3 --version` is 3.10+.
2. `py -3 <base>\scripts\doctor.py` prints `PASS python` and all 8 skill lines.
3. The scanner returns the same class/hash as on macOS for 余烬.
4. `preflight.py` produces the same PASS/FAIL lines as macOS, including the
   tracked-modification gate.
5. `publish.py --dry-run` shows one command line, contains `--execute`-equivalent
   `submit` arguments, and contains no `--auto`.
6. `publish.py --execute --confirmed` with a fake publisher runs only local
   validation/submit arguments before a real upload is attempted.
7. `.ps1` launchers work under both Windows PowerShell 5.1 and PowerShell 7.
8. A real `publisher.py validate` succeeds, and a real `submit` is attempted only
   after manual authorization.

Until this checklist passes, report "Windows compatibility implemented, not yet
validated on Windows", not "Windows supported".
