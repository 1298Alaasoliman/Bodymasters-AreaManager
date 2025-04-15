@echo off
echo ======================================
echo    Starting Simple Flask Server
echo ======================================
echo.

set PORT=5000

echo Starting server on port %PORT%...
echo.

venv\Scripts\activate

python simple_server.py %PORT%

echo.
echo Application is running on port %PORT%!
echo Please access it through your browser at http://127.0.0.1:%PORT%
echo.
echo Press Ctrl+C to stop the server when you're done.






