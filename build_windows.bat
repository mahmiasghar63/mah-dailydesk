@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Please run run_windows.bat first to set up the environment.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install "pyinstaller>=6,<7" "Pillow>=10,<12"
if errorlevel 1 goto error
".venv\Scripts\python.exe" tools\create_icon.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name "MAH-DailyDesk" --icon "assets\MAH-DailyDesk.ico" main.py
if errorlevel 1 goto error
echo.
echo Windows app created in dist\MAH-DailyDesk\
echo Keep the entire folder and test the EXE before sharing it.
pause
exit /b 0
:error
echo Windows build failed. Check the output above.
pause
exit /b 1