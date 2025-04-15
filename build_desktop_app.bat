@echo off
echo ======================================
echo    Building Desktop Application
echo ======================================
echo.

pyinstaller --onefile --windowed --icon=app.ico desktop_app.py

echo.
echo Build complete! The executable file is in the dist folder.
echo Press any key to exit...
pause > nul
