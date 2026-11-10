@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [MAH DailyDesk] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 goto error
)
echo [MAH DailyDesk] Installing or checking dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo [MAH DailyDesk] Launching...
".venv\Scripts\python.exe" main.py
if errorlevel 1 goto error
exit /b 0
:error
echo.
echo Failed. Make sure Python is installed, internet is available for first-time setup,
echo and run this file again. See README.md for detailed steps.
pause
exit /b 1