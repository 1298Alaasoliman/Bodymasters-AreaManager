@echo off
echo ======================================
echo    Starting Area Manager Application
echo ======================================
echo.

:: تشغيل التطبيق مع محاولة المنافذ المختلفة تلقائياً
echo The application will try ports 5000, 8000, and 3000 automatically.
echo Please wait while the server starts...
echo.

python production.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting the application. Please check the logs.
    echo Press any key to exit...
    pause > nul
    exit /b %ERRORLEVEL%
)

echo.
echo Application is running! Please access it through your browser.
echo.
echo Press Ctrl+C to stop the server when you're done.

