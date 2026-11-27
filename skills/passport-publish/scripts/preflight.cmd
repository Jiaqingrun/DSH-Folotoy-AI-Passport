@echo off
rem Thin launcher: cmd wrapper around preflight.py.
rem Use this when PowerShell execution policy blocks preflight.ps1.
setlocal
chcp 65001 >nul 2>nul
set "PYSCRIPT=%~dp0preflight.py"
if not exist "%PYSCRIPT%" goto :nopy
if defined PYTHON goto :runenv
set "PY="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
    where python >nul 2>nul
    if not errorlevel 1 set "PY=python"
)
if not defined PY (
    where python3 >nul 2>nul
    if not errorlevel 1 set "PY=python3"
)
if not defined PY goto :nopython
%PY% "%PYSCRIPT%" %*
exit /b %ERRORLEVEL%

:runenv
"%PYTHON%" "%PYSCRIPT%" %*
exit /b %ERRORLEVEL%

:nopython
echo python 3.10+ not found (install Python or set PYTHON) 1>&2
exit /b 127

:nopy
echo missing script: %PYSCRIPT% 1>&2
exit /b 127
