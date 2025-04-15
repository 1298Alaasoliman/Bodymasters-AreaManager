@echo off
echo ======================================
echo    Area Manager Connection Fixer
echo ======================================
echo.

echo Checking for processes using ports...
netstat -ano | findstr :5000
netstat -ano | findstr :8000
netstat -ano | findstr :8080
netstat -ano | findstr :3000

echo.
echo Attempting to free up ports...
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
echo Resetting network connections...
ipconfig /flushdns
netsh winsock reset

echo.
echo Connection fix complete. Please try starting the application again.
echo Press any key to exit...
pause > nul
