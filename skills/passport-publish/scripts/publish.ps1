#requires -Version 5.1
# Thin launcher: Windows PowerShell wrapper around publish.py.
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $here 'publish.py'

if ($env:PYTHON) {
    & $env:PYTHON $pyScript @args
    exit $LASTEXITCODE
}
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $pyScript @args
    exit $LASTEXITCODE
}
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $pyScript @args
    exit $LASTEXITCODE
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $pyScript @args
    exit $LASTEXITCODE
}
[Console]::Error.WriteLine('python 3.10+ not found (install Python or set PYTHON)')
exit 127
