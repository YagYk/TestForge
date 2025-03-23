@echo off
echo Checking if Flask Server is running...
python server_manager.py check
if errorlevel 1 (
    echo Flask server is not running.
    echo Would you like to start it now? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        python server_manager.py start
    )
) else (
    echo Server is running!
)
pause 