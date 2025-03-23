# Flask Server Guide for TestForge

This guide explains how to start, verify, and manage the Flask server that powers the TestForge application's backend API.

## Prerequisites

Before starting the server, make sure you have:

1. Python installed (version 3.6 or higher recommended)
2. Required packages installed:
   ```
   pip install flask flask-cors requests
   ```
3. If you want to use AI test generation, a Gemini API key should be set as an environment variable:
   ```
   set GEMINI_API_KEY=your_api_key_here
   ```

## Quick Start

The easiest way to start the Flask server is to double-click the `start_flask_server.bat` file in the TestForge directory. This will:

1. Start the Flask server in a new console window
2. Verify that the server is running correctly
3. Show next steps

## Verifying the Server

To check if the Flask server is already running:

1. Double-click the `check_flask_server.bat` file
2. It will tell you if the server is running or not
3. If not running, it will offer to start it for you

## Manual Commands

If you prefer to use the command line directly:

### Starting the Server

```
python server_manager.py start
```

### Checking Server Status

```
python server_manager.py check
```

### Starting the Server Directly

If you want to see all server logs directly in the console:

```
python app.py
```

## Troubleshooting

If you're having issues with the Flask server:

1. **Port already in use**: If port 5000 is already in use by another application, the server won't start. You can either:
   - Close the other application using port 5000
   - Modify the Flask app to use a different port:
     ```python
     # In app.py, change the port number
     app.run(host='0.0.0.0', port=5001)  # Change 5000 to 5001 or another free port
     ```

2. **Connection refused**: This usually means the server isn't running. Start it using one of the methods above.

3. **CORS issues**: If your frontend can't connect to the API, check the CORS configuration in `app.py`. The current configuration should allow requests from localhost on various ports.

4. **Missing dependencies**: If you see errors about missing modules, install them using pip:
   ```
   pip install flask flask-cors requests
   ```

## Connecting from the Frontend

Once the Flask server is running:

1. Start your React frontend:
   ```
   cd Frontend
   npm start
   ```

2. Open your browser to the frontend URL (usually http://localhost:3000)

3. Use the debug mode in the TestForm component to verify the API connection:
   - Click "Show Debug Info"
   - Click "Test API Service" or "Test Direct Fetch"
   - Check the connection info displayed

## Advanced: Production Deployment

For production deployment:

1. Use a production-ready WSGI server like Gunicorn or uWSGI instead of Flask's development server
2. Set up proper error handling and logging
3. Configure CORS to only allow requests from your production frontend domain
4. Consider containerizing the application with Docker for easier deployment

---

If you need additional help, please refer to the Flask documentation at https://flask.palletsprojects.com/ 