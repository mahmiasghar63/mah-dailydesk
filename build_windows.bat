@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Please run run_windows.bat first to set up the environment.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install "pyinstaller>=6,<7"
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name "MAH-DailyDesk" main.py
if errorlevel 1 goto error
echo.
echo Windows app created in dist\MAH-DailyDesk\
echo Copy the ENTIRE folder, not just the EXE. Test before publishing.
pause
exit /b 0
:error
echo Windows build failed. Check the error output above.
pause
exit /b 1