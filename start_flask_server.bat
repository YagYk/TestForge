@echo off
echo Starting Flask Server for TestForge...
python server_manager.py start
if errorlevel 1 (
    echo Failed to start Flask server.
    pause
) else (
    echo Server started successfully!
    echo You can close this window after you're done using the server.
    pause
) 