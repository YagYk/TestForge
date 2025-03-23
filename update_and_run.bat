@echo off
echo =====================================
echo TestForge Update and Run Script
echo =====================================
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

echo Step 1: Installing frontend dependencies...
cd Frontend
call npm install
echo.

echo Step 2: Ensuring config-overrides.js exists...
if not exist "config-overrides.js" (
    echo Creating config-overrides.js file...
    echo // Custom override for webpack to fix chunk loading errors > config-overrides.js
    echo const webpack = require('webpack'); >> config-overrides.js
    echo. >> config-overrides.js
    echo module.exports = function override(config, env) { >> config-overrides.js
    echo   // Add environment variables to the build >> config-overrides.js
    echo   config.plugins.push( >> config-overrides.js
    echo     new webpack.DefinePlugin({ >> config-overrides.js
    echo       'process.env.REACT_APP_DISABLE_SPLINE': JSON.stringify(process.env.REACT_APP_DISABLE_SPLINE) >> config-overrides.js
    echo     }) >> config-overrides.js
    echo   ); >> config-overrides.js
    echo. >> config-overrides.js
    echo   // Modify chunking strategy >> config-overrides.js
    echo   if (config.optimization ^&^& config.optimization.splitChunks) { >> config-overrides.js
    echo     config.optimization.splitChunks.cacheGroups = { >> config-overrides.js
    echo       ...config.optimization.splitChunks.cacheGroups, >> config-overrides.js
    echo       // Prevent Splinetool from being split into chunks >> config-overrides.js
    echo       splineVendors: { >> config-overrides.js
    echo         test: /[\\\/]node_modules[\\\/](@splinetool)[\\\/]/, >> config-overrides.js
    echo         name: 'spline-vendors', >> config-overrides.js
    echo         chunks: 'all', >> config-overrides.js
    echo         enforce: true, >> config-overrides.js
    echo         priority: 10, >> config-overrides.js
    echo       }, >> config-overrides.js
    echo     }; >> config-overrides.js
    echo   } >> config-overrides.js
    echo. >> config-overrides.js
    echo   // Add resolver fallbacks for problematic modules >> config-overrides.js
    echo   if (!config.resolve) config.resolve = {}; >> config-overrides.js
    echo   if (!config.resolve.fallback) config.resolve.fallback = {}; >> config-overrides.js
    echo. >> config-overrides.js
    echo   config.resolve.fallback = { >> config-overrides.js
    echo     ...config.resolve.fallback, >> config-overrides.js
    echo     fs: false, >> config-overrides.js
    echo     path: false, >> config-overrides.js
    echo     crypto: false, >> config-overrides.js
    echo     stream: false, >> config-overrides.js
    echo     zlib: false, >> config-overrides.js
    echo   }; >> config-overrides.js
    echo. >> config-overrides.js
    echo   // Return the modified config >> config-overrides.js
    echo   return config; >> config-overrides.js
    echo }; >> config-overrides.js
) else (
    echo config-overrides.js already exists.
)
echo.

echo Step 3: Ensuring .env file exists...
if not exist ".env" (
    echo Creating .env file...
    echo # Fix chunk loading errors by modifying webpack configuration > .env
    echo GENERATE_SOURCEMAP=false >> .env
    echo INLINE_RUNTIME_CHUNK=false >> .env
    echo. >> .env
    echo # Skip including unnecessary chunks and optimize build >> .env
    echo # The specific flag that fixes the splinetool/runtime/opentype.js chunk error >> .env
    echo REACT_APP_DISABLE_SPLINE=true >> .env
) else (
    echo .env file already exists.
)
echo.

echo Step 4: Going back to project root...
cd ..
echo.

echo Step 5: Starting the backend server...
start cmd /k python app.py
echo.

echo Waiting for the backend to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

echo Step 6: Starting the frontend server...
cd Frontend
start cmd /k npm start
echo.

echo =====================================
echo All done! The application should open in your browser shortly.
echo - Backend: http://localhost:5000
echo - Frontend: http://localhost:3000
echo.
echo If you encounter any issues:
echo 1. Check the terminal windows for error messages
echo 2. Make sure both servers are running
echo 3. Try refreshing your browser
echo =====================================

pause 