@echo off
echo =================================
echo TestForge Spline Error Fix Script
echo =================================
echo.
echo This script will fix chunk loading errors and restart your application.
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed or not in your PATH.
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo Changing to Frontend directory...
cd Frontend

echo.
echo Installing react-app-rewired to fix chunk loading issues...
call npm install --save-dev react-app-rewired

echo.
echo Cleaning build directory...
if exist "build" (
    rmdir /s /q build
    echo Build directory cleaned.
)

echo.
echo Updating the package.json scripts...
node -e "const fs = require('fs'); const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8')); if (pkg.scripts && pkg.scripts.start) { pkg.scripts.start = pkg.scripts.start.replace('react-scripts', 'react-app-rewired'); } if (pkg.scripts && pkg.scripts.build) { pkg.scripts.build = pkg.scripts.build.replace('react-scripts', 'react-app-rewired'); } fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));"
echo Package.json updated.

echo.
echo Running npm install to ensure all dependencies are installed...
call npm install

echo.
echo Starting the application...
echo.
echo 1. First, we'll make sure the backend is running
cd ..
python server_manager.py restart
echo.
echo 2. Now we'll start the frontend
cd Frontend
start cmd /k npm start

echo.
echo If you still encounter issues:
echo 1. Try running "npm run build" instead of "npm start"
echo 2. Check the console for any errors
echo 3. Make sure the backend is running at http://localhost:5000
echo.

echo Press any key to exit this window...
pause >nul 