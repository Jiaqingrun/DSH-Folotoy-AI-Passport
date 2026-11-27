# Windows notes

Status: the bundle's scripts are implemented with a Python core plus PowerShell
and cmd launchers. The GitHub Actions workflow includes a `windows-latest`
smoke test (including the new `.cmd` launcher); it was not rerun in this review.
A 2026-11-27 field run on one Windows 11 (zh-CN) machine with PowerShell 5.1,
pwsh 7.7.0, Python 3.13.5, Git 2.56.1, and DSH Desktop 0.2.2-rc.5 exercised the
installation, 9 skills, doctor, scanner, preflight, Git end-to-end, CJK/emoji,
`.cmd` Restricted, `.ps1` Bypass, 324-character path, UNC, and publish dry-run
paths. The 0.2.3 adaptation also completed a real build, flash, 8 real-screen
captures, and a community submission (approved/published); the 0.2.4 run only
revalidated the publish chain. Multi-machine coverage and
`LongPathsEnabled=0` remain unverified — see `docs/WINDOWS-REPORT.md`.

## Requirements

- Windows 10/11 with PowerShell 5.1 or newer.
- Python 3.10+ from python.org; `python --version` or `py -3 --version` must work.
  The launchers probe `py -3` first and fall back to `python` (a `py.exe` with no
  registered interpreter is a known broken state).
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
same job. They probe `py -3 -c "import sys"` and fall back to `python` when
`py.exe` exists without a registered interpreter. Windows client defaults to the
`Restricted` execution policy, which refuses to run any `.ps1` file, so either
bypass it explicitly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <base>\scripts\doctor.ps1
```

or use the `.cmd` launchers (`doctor.cmd`, `preflight.cmd`, `publish.cmd`), which
run under the default policy. Prefer the direct `py -3 ...py` form in automated
runs.

## Encoding behavior

Windows consoles and pipes default to the ANSI code page (cp936 on Chinese
installs, cp932 on Japanese), not UTF-8. Every Python entry point forces UTF-8 on
stdout/stderr and decodes subprocess output as UTF-8, so:

- non-ASCII project paths survive a `--json` round trip;
- a path containing a character the code page cannot represent no longer raises
  `UnicodeEncodeError`;
- the `.ps1` launchers switch `[Console]::OutputEncoding` to UTF-8 for the call
  and restore it afterwards;
- the `.cmd` launchers run `chcp 65001`.

A consumer that reads these scripts' output itself must decode UTF-8.

## Safety behavior

- `publish.py` defaults to dry-run.
- It never adds `--auto`.
- Only `--execute --confirmed` runs `submit`; `--confirmed` alone only changes the
  printed dry-run command.
- It never reads, prints, or stores authorization codes or tokens.

## Acceptance checklist on Windows

1. `py -3 --version` is 3.10+.
2. `py -3 <base>\scripts\doctor.py` prints `PASS python` and all 9 skill lines.
3. The scanner returns the same class/hash as on macOS for 余烬, and repo-relative
   paths are POSIX-style (`skills/x/y`) on both platforms.
4. `preflight.py` produces the same PASS/FAIL lines as macOS, including the
   tracked-modification gate.
5. `publish.py --dry-run` shows one command line, contains `--execute`-equivalent
   `submit` arguments, and contains no `--auto`.
6. `publish.py --execute --confirmed` with a fake publisher runs only local
   validation/submit arguments before a real upload is attempted.
7. `.ps1` launchers work under both Windows PowerShell 5.1 and PowerShell 7 when
   run with `-ExecutionPolicy Bypass`, and `.cmd` launchers work under the default
   `Restricted` policy.
8. A project path containing CJK and emoji survives `--json` unchanged; the
   captured bytes decode as UTF-8.
9. A real `publisher.py validate` succeeds, and a real `submit` is attempted only
   after manual authorization.

Until the remaining checklist items pass, report "Windows compatibility beta,
exercised on one Windows machine; multi-machine and LongPathsEnabled=0 remain
unverified", not "Windows fully supported". The 0.2.3 field run's device/publish
evidence is not a 0.2.4 device/publish test.

## Known field limitation: paths over 260 characters

`preflight.py --static` retries with `cwd=None` when Windows refuses a
>260-character project root as the child process working directory
(`[WinError 267]`). The gate script itself is still passed by absolute path, so
gates that use `$PSScriptRoot`/absolute paths work; a gate that depends on the
process cwd could see a different directory. The field `validate.ps1` passed, but
this is not a blanket guarantee for arbitrary third-party gates. See
`docs/AUDIT-0.2.5.md`.
