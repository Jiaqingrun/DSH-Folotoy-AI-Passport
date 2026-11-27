#requires -Version 5.1
# Thin launcher: Windows PowerShell wrapper around doctor.py.
#
# Two Windows-specific details:
#   1. Python emits UTF-8, so this console is switched to UTF-8 for the call.
#      Without it, Chinese/Japanese path output is shown as mojibake on a
#      cp936/cp932 console.
#   2. Do not set $ErrorActionPreference = 'Stop' here. Python writes normal
#      diagnostics to stderr, and under 'Stop' that becomes a terminating
#      NativeCommandError that masks the real exit code.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $here 'doctor.py'

if (-not (Test-Path -LiteralPath $pyScript)) {
    [Console]::Error.WriteLine("missing script: $pyScript")
    exit 127
}

$savedEncoding = $null
try {
    $savedEncoding = [Console]::OutputEncoding
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
}
catch { }
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)

$pyExe = $null
$pyPrefix = @()
try {
    if ($env:PYTHON) {
        $pyExe = $env:PYTHON
    }
    elseif (Get-Command py -ErrorAction SilentlyContinue) {
        # `py.exe` can exist with no registered CPython (for example a launcher
        # left behind after an interpreter was removed). Probe before trusting it.
        & py -3 -c "import sys" 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $pyExe = 'py'
            $pyPrefix = @('-3')
        }
    }
    if (-not $pyExe -and (Get-Command python -ErrorAction SilentlyContinue)) {
        $pyExe = 'python'
    }
    if (-not $pyExe -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
        $pyExe = 'python3'
    }
    if (-not $pyExe) {
        [Console]::Error.WriteLine('python 3.10+ not found (install Python or set PYTHON)')
        exit 127
    }
    & $pyExe @pyPrefix $pyScript @args
    $code = $LASTEXITCODE
}
finally {
    if ($null -ne $savedEncoding) {
        try { [Console]::OutputEncoding = $savedEncoding } catch { }
    }
}
if ($null -eq $code) { $code = 1 }
exit $code
