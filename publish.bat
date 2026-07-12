@echo off
REM ============================================================
REM  LockIn - one-tap publish. Double-click after any change.
REM  (First time ever? Run setup-github.bat instead.)
REM  Optional: drag-run from a terminal with your own message:
REM      publish.bat Improve workout logger
REM ============================================================
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [!] Git is not installed. Run setup-github.bat first.
  pause
  exit /b 1
)

git add -A

set msg=%*
if "%msg%"=="" set msg=Update LockIn (%date% %time%)

git commit -m "%msg%"
git push

echo.
echo  Published. GitHub Pages refreshes in about a minute -
echo  then just reopen the app on your phone (it may need one
echo  close + reopen to pick up the new version).
pause
