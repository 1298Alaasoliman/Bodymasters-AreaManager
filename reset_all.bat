@echo off
echo ======================================
echo    Complete System Reset
echo ======================================
echo.

echo Stopping all Python processes...
taskkill /F /IM python.exe /T
taskkill /F /IM pythonw.exe /T

echo.
echo Clearing all ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    echo Found process using port 5000: %%a
    taskkill /F /PID %%a
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Found process using port 8000: %%a
    taskkill /F /PID %%a
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    echo Found process using port 8080: %%a
    taskkill /F /PID %%a
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo Found process using port 3000: %%a
    taskkill /F /PID %%a
)

echo.
echo Resetting network...
ipconfig /release
ipconfig /renew
ipconfig /flushdns
netsh winsock reset

echo.
echo System reset complete. Please restart your computer before running the application again.
echo Press any key to exit...
pause > nul
