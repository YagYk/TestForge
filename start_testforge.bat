@echo off
echo TestForge Launcher
echo =================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: npm is not installed or not in your PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Starting TestForge using server manager...
echo.

REM Run the server manager with the "all" command
python server_manager.py all

if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to start TestForge.
    echo.
    echo Manual steps:
    echo 1. Start the backend server: python app.py
    echo 2. In a separate terminal, start the frontend: cd Frontend ^&^& npm start
    echo.
    echo If issues persist, check for errors in the console output.
)

echo.
echo Press any key to close this window...
pause >nul 