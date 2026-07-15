@echo off
REM Double-click to open LockIn Study — the theory app (networks, memory, Linux, CMD).
REM No code to run here: you read the lesson, then explain it in the Workbench and the
REM AI grades your answer. Needs Python 3 (python.org/downloads — tick "Add to PATH").
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py lockin_lab.py theory
  goto :end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python lockin_lab.py theory
  goto :end
)
echo [!] Python was not found. Install it from https://www.python.org/downloads/
echo     and tick "Add python.exe to PATH", then run this again.
pause
:end
if %errorlevel% neq 0 pause
