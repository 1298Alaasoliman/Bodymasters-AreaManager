@echo off
echo ======================================
echo    Starting Area Manager Application
echo ======================================
echo.

set /p PORT="Enter port number (default: 5000): "

if "%PORT%"=="" set PORT=5000

echo Starting server on port %PORT%...
echo.

python -c "from production import app, start_server; start_server(%PORT%)"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error starting the application. Please check the logs.
    echo Press any key to exit...
    pause > nul
    exit /b %ERRORLEVEL%
)

echo.
echo Application is running on port %PORT%!
echo Please access it through your browser at http://127.0.0.1:%PORT%
echo.
echo Press Ctrl+C to stop the server when you're done.
