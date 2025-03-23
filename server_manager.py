#!/usr/bin/env python
"""
Server Manager for TestForge
----------------------------
This script helps to manage the TestForge Flask server.
It can start, stop, and check the status of the server.
"""

import os
import sys
import time
import json
import signal
import subprocess
import requests
from urllib.parse import urlparse
import socket
import webbrowser
import threading
import platform

# Configuration
DEFAULT_PORT = 5000
FRONTEND_PORT = 3000
SERVER_SCRIPT = "app.py"
SERVER_URL = f"http://localhost:{DEFAULT_PORT}"
HEALTH_ENDPOINT = f"{SERVER_URL}/api/health"
PROCESS_NAME = "python app.py"
STATUS_FILE = ".server_status.json"
TIMEOUT = 10  # seconds

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_free_port(start_port, max_attempts=10):
    """Find a free port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    return None

def check_server_status():
    """Check if the server is running and responding."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        return False, {"error": f"Server responded with status code: {response.status_code}"}
    except requests.RequestException as e:
        return False, {"error": f"Cannot connect to server: {str(e)}"}

def save_process_info(pid):
    """Save process information to a file."""
    with open(STATUS_FILE, 'w') as f:
        json.dump({
            "pid": pid,
            "started_at": time.time(),
            "url": SERVER_URL
        }, f)

def load_process_info():
    """Load process information from file."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return None

def is_process_running(pid):
    """Check if a process with the given PID is running."""
    if platform.system() == "Windows":
        try:
            # On Windows, check with tasklist
            output = subprocess.check_output(["tasklist", "/FI", f"PID eq {pid}"], text=True)
            return str(pid) in output
        except subprocess.SubprocessError:
            return False
    else:
        try:
            # On Unix-based systems, send signal 0 to the process
            os.kill(pid, 0)
            return True
        except OSError:
            return False

def start_server(port=DEFAULT_PORT, wait_for_server=True):
    """Start the Flask server."""
    # Check if server is already running
    is_running, data = check_server_status()
    if is_running:
        print(f"Server is already running at {SERVER_URL}")
        return True

    # Check if port is in use
    if is_port_in_use(port):
        free_port = get_free_port(port)
        if free_port:
            print(f"Port {port} is in use. Using port {free_port} instead.")
            port = free_port
        else:
            print(f"Port {port} is in use and no free ports found.")
            return False

    # Start the server as a subprocess
    print(f"Starting server on port {port}...")
    
    command = [sys.executable, SERVER_SCRIPT]
    
    # Use different subprocess creation based on OS
    if platform.system() == "Windows":
        # On Windows, we need to create a new console window
        process = subprocess.Popen(
            command,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # On Unix-based systems, use standard Popen
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Save process info
    save_process_info(process.pid)
    
    # Wait for server to start responding
    if wait_for_server:
        print("Waiting for server to start...")
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            is_running, data = check_server_status()
            if is_running:
                print(f"Server started successfully at {SERVER_URL}")
                print(f"API Status: {data.get('status', 'unknown')}")
                return True
            time.sleep(0.5)
        
        print(f"Warning: Server did not respond within {TIMEOUT} seconds.")
        print("The server might still be starting up. Check the server console for errors.")
        return False
    
    return True

def stop_server():
    """Stop the Flask server."""
    # Load process info
    process_info = load_process_info()
    if not process_info:
        print("No server process information found.")
        return False
    
    pid = process_info.get("pid")
    if not pid:
        print("No process ID found.")
        return False
    
    # Check if process is running
    if not is_process_running(pid):
        print(f"Process with PID {pid} is not running.")
        if os.path.exists(STATUS_FILE):
            os.remove(STATUS_FILE)
        return False
    
    # Stop the process
    print(f"Stopping server process (PID: {pid})...")
    try:
        if platform.system() == "Windows":
            # On Windows, use taskkill
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
        else:
            # On Unix-based systems, send SIGTERM
            os.kill(pid, signal.SIGTERM)
        
        # Wait for process to terminate
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            if not is_process_running(pid):
                print("Server stopped successfully.")
                if os.path.exists(STATUS_FILE):
                    os.remove(STATUS_FILE)
                return True
            time.sleep(0.5)
        
        print("Warning: Failed to stop server gracefully. Trying force kill...")
        
        # Force kill if process still running
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGKILL)
        
        if os.path.exists(STATUS_FILE):
            os.remove(STATUS_FILE)
        
        print("Server force stopped.")
        return True
    
    except (subprocess.SubprocessError, OSError) as e:
        print(f"Error stopping server: {str(e)}")
        return False

def start_frontend():
    """Start the React frontend."""
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    
    try:
        # Check if we're in the right directory
        if not os.path.isdir("Frontend"):
            print("Frontend directory not found. Make sure you're running this script from the project root.")
            return False
        
        # Change to Frontend directory
        os.chdir("Frontend")
        
        print("Starting React frontend...")
        
        # Start the frontend as a subprocess
        if platform.system() == "Windows":
            process = subprocess.Popen(
                [npm_cmd, "start"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(
                [npm_cmd, "start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Go back to original directory
        os.chdir("..")
        
        print(f"Frontend starting at http://localhost:{FRONTEND_PORT}")
        return True
    
    except Exception as e:
        print(f"Error starting frontend: {str(e)}")
        # Go back to original directory in case of error
        try:
            os.chdir("..")
        except:
            pass
        return False

def open_browser():
    """Open browser to the frontend URL."""
    # Wait a bit for the frontend to start
    time.sleep(5)
    frontend_url = f"http://localhost:{FRONTEND_PORT}"
    print(f"Opening browser to {frontend_url}")
    webbrowser.open(frontend_url)

def start_all():
    """Start both backend and frontend."""
    # Start backend
    if not start_server(wait_for_server=False):
        print("Failed to start backend server.")
        return False
    
    # Start frontend
    if not start_frontend():
        print("Failed to start frontend.")
        return False
    
    # Start a thread to open the browser
    threading.Thread(target=open_browser).start()
    
    return True

def print_help():
    """Print help information."""
    print("TestForge Server Manager")
    print("=======================")
    print("Usage: python server_manager.py [command]")
    print("\nCommands:")
    print("  start       - Start the Flask server")
    print("  stop        - Stop the Flask server")
    print("  restart     - Restart the Flask server")
    print("  check       - Check if the server is running")
    print("  frontend    - Start the React frontend")
    print("  all         - Start both backend and frontend")
    print("  help        - Show this help information")
    print("\nExamples:")
    print("  python server_manager.py start")
    print("  python server_manager.py check")
    print("  python server_manager.py all")

def main():
    """Main function to parse command line arguments and execute commands."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_server()
    
    elif command == "stop":
        stop_server()
    
    elif command == "restart":
        stop_server()
        time.sleep(1)
        start_server()
    
    elif command == "check":
        is_running, data = check_server_status()
        if is_running:
            print(f"Server is running at {SERVER_URL}")
            print(f"Status: {json.dumps(data, indent=2)}")
        else:
            print(f"Server is not running. Error: {data.get('error', 'Unknown error')}")
    
    elif command == "frontend":
        start_frontend()
    
    elif command == "all":
        start_all()
    
    elif command == "help":
        print_help()
    
    else:
        print(f"Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    main() 