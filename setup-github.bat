@echo off
REM ============================================================
REM  LockIn - FIRST-TIME publish setup (run this exactly once).
REM  Prerequisites (5 min, see PUBLISH.md for pictures):
REM    1. Install Git: https://git-scm.com/download/win
REM    2. Create a free account at https://github.com
REM    3. On GitHub click "+" -> "New repository", name it: lockin
REM       (leave EVERYTHING unticked), press "Create repository",
REM       and copy the URL it shows, e.g. https://github.com/YOURNAME/lockin.git
REM ============================================================
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [!] Git is not installed. Get it from https://git-scm.com/download/win and run me again.
  pause
  exit /b 1
)

if not exist ".git" (
  git init
  git branch -M main
)

git add -A
git commit -m "LockIn v1 - summer goal system app"

set /p REPO=Paste your GitHub repo URL here and press Enter:
git remote remove origin >nul 2>nul
git remote add origin %REPO%
git push -u origin main

echo.
echo ============================================================
echo  Done! Last step (once, on the GitHub website):
echo    repo page -^> Settings -^> Pages -^> Branch: main / root -^> Save
echo  Your app will be live at:  https://YOURNAME.github.io/lockin/
echo  Open that on your phone in Chrome -^> menu -^> Add to Home screen
echo.
echo  From now on, after any change, just double-click publish.bat
echo ============================================================
pause
