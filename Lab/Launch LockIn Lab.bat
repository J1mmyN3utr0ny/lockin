@echo off
REM Double-click to open LockIn Lab (the cyber Virtual Environment).
REM Needs Python 3 (python.org/downloads — tick "Add to PATH" during install).
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py lockin_lab.py
  goto :end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python lockin_lab.py
  goto :end
)
echo [!] Python was not found. Install it from https://www.python.org/downloads/
echo     and tick "Add python.exe to PATH", then run this again.
pause
:end
if %errorlevel% neq 0 pause
