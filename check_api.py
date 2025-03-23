#!/usr/bin/env python
"""
TestForge API Connectivity Check Tool
-------------------------------------
This script tests connectivity to the TestForge backend API
and provides diagnostic information.
"""

import requests
import json
import sys
import platform
import socket
import time
import subprocess
import os
from urllib.parse import urlparse

# Configuration
API_ENDPOINTS = [
    "http://localhost:5000/api/health",
    "http://127.0.0.1:5000/api/health",
    "http://localhost:8000/api/health",
    "http://localhost:3001/api/health",
    "/api/health"
]

def check_port(host, port):
    """Check if a port is open on a host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, socket.error):
            return False

def get_system_info():
    """Collect system information for diagnostics."""
    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "network": {
            "hostname": socket.gethostname(),
        }
    }
    
    # Try to get IP addresses
    try:
        info["network"]["ip_addresses"] = socket.gethostbyname_ex(socket.gethostname())[2]
    except:
        info["network"]["ip_addresses"] = ["Unable to determine"]
    
    # Check if common ports are open
    info["ports"] = {
        "5000": check_port("localhost", 5000),
        "3000": check_port("localhost", 3000),
        "8000": check_port("localhost", 8000),
        "3001": check_port("localhost", 3001)
    }
    
    return info

def check_server_process():
    """Check if the Flask server process is running."""
    is_running = False
    pid = None
    
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output("tasklist /FI \"IMAGENAME eq python.exe\" /FO CSV", shell=True).decode()
            lines = output.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if 'app.py' in line or 'flask' in line.lower():
                    is_running = True
                    try:
                        pid = line.split(',')[1].strip('"')
                    except:
                        pid = "Unknown"
                    break
        except:
            pass
    else:
        try:
            output = subprocess.check_output(["ps", "-ef"]).decode()
            lines = output.split('\n')
            for line in lines:
                if 'app.py' in line or 'flask' in line:
                    is_running = True
                    pid = line.split()[1]
                    break
        except:
            pass
    
    return {"running": is_running, "pid": pid}

def check_api_endpoints():
    """Test connectivity to all API endpoints."""
    results = []
    
    for endpoint in API_ENDPOINTS:
        try:
            print(f"Testing endpoint: {endpoint}")
            start_time = time.time()
            response = requests.get(endpoint, timeout=5)
            elapsed = time.time() - start_time
            
            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time": f"{elapsed:.2f}s",
                "success": response.status_code == 200,
                "headers": dict(response.headers)
            }
            
            if response.status_code == 200:
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = "Unable to parse JSON response"
            
            results.append(result)
            
            if result["success"]:
                print(f"  ✓ Success! Status: {response.status_code}, Time: {elapsed:.2f}s")
            else:
                print(f"  ✗ Failed! Status: {response.status_code}, Time: {elapsed:.2f}s")
                
        except requests.RequestException as e:
            results.append({
                "endpoint": endpoint,
                "error": str(e),
                "success": False
            })
            print(f"  ✗ Error: {str(e)}")
    
    return results

def check_cors_headers(endpoint):
    """Check if CORS headers are properly configured."""
    try:
        response = requests.options(endpoint, headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }, timeout=5)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        return {
            "status_code": response.status_code,
            "cors_headers": cors_headers,
            "success": "Access-Control-Allow-Origin" in response.headers
        }
    except requests.RequestException as e:
        return {
            "error": str(e),
            "success": False
        }

def check_server_status():
    """Check if server_manager.py exists and try to use it to check server status."""
    if os.path.exists("server_manager.py"):
        try:
            output = subprocess.check_output([sys.executable, "server_manager.py", "check"], stderr=subprocess.STDOUT, text=True)
            return {
                "exists": True,
                "output": output,
                "success": "Server is running" in output
            }
        except subprocess.CalledProcessError as e:
            return {
                "exists": True,
                "error": e.output,
                "success": False
            }
    else:
        return {
            "exists": False,
            "success": False
        }

def main():
    """Run all diagnostics and print results."""
    print("TestForge API Connectivity Check")
    print("================================")
    print()
    
    # Check system information
    print("System Information:")
    print("-----------------")
    system_info = get_system_info()
    print(f"Platform: {system_info['platform']}")
    print(f"Python: {system_info['python_version'].split()[0]}")
    print(f"Hostname: {system_info['network']['hostname']}")
    print(f"IP Addresses: {', '.join(system_info['network']['ip_addresses'])}")
    print()
    
    # Check open ports
    print("Port Status:")
    print("-----------")
    for port, is_open in system_info["ports"].items():
        status = "OPEN" if is_open else "CLOSED"
        print(f"Port {port}: {status}")
    print()
    
    # Check server process
    print("Flask Server Process:")
    print("-------------------")
    process_info = check_server_process()
    if process_info["running"]:
        print(f"Status: RUNNING (PID: {process_info['pid']})")
    else:
        print("Status: NOT RUNNING")
    print()
    
    # Check server_manager.py
    print("Server Manager Check:")
    print("-------------------")
    manager_status = check_server_status()
    if manager_status["exists"]:
        print("server_manager.py: EXISTS")
        if manager_status.get("success", False):
            print("Status: RUNNING")
            if "output" in manager_status:
                print(f"Details: {manager_status['output'].strip()}")
        else:
            print("Status: ERROR")
            if "error" in manager_status:
                print(f"Error: {manager_status['error'].strip()}")
    else:
        print("server_manager.py: NOT FOUND")
    print()
    
    # Check API endpoints
    print("API Endpoint Tests:")
    print("-----------------")
    api_results = check_api_endpoints()
    working_endpoints = [r for r in api_results if r.get("success", False)]
    if working_endpoints:
        print(f"\n✓ Found {len(working_endpoints)} working endpoint(s)!")
        first_working = working_endpoints[0]
        print(f"  First working endpoint: {first_working['endpoint']}")
        
        # Check CORS for the working endpoint
        print("\nCORS Headers Check:")
        print("----------------")
        cors_check = check_cors_headers(first_working['endpoint'])
        if cors_check.get("success", False):
            print("✓ CORS headers are configured correctly!")
            print(f"  Origin: {cors_check['cors_headers']['Access-Control-Allow-Origin']}")
            print(f"  Methods: {cors_check['cors_headers']['Access-Control-Allow-Methods']}")
        else:
            print("✗ CORS headers are missing or misconfigured!")
            if "error" in cors_check:
                print(f"  Error: {cors_check['error']}")
            else:
                print(f"  Headers: {cors_check.get('cors_headers', {})}")
    else:
        print("\n✗ No working endpoints found!")
    
    # Print detailed diagnostic information
    print("\nDetailed Diagnostic Information:")
    print("-------------------------------")
    diagnostic_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system_info": system_info,
        "server_process": process_info,
        "server_manager": manager_status,
        "api_tests": api_results
    }
    
    # Save diagnostic information to file
    with open("api_diagnostic.json", "w") as f:
        json.dump(diagnostic_data, f, indent=2)
    print(f"Full diagnostic information saved to api_diagnostic.json")
    
    print("\nSuggested Actions:")
    print("-----------------")
    if not process_info["running"]:
        print("1. Start the Flask server: python app.py")
        print("   Or use: python server_manager.py start")
    elif not any(r.get("success", False) for r in api_results):
        print("1. The server is running but all API requests failed.")
        print("   Check if the server is listening on the correct port and address.")
        print("   Try: python server_manager.py restart")
    else:
        print("1. API is accessible on at least one endpoint.")
        for endpoint in working_endpoints:
            print(f"   Working endpoint: {endpoint['endpoint']}")
        
        if not cors_check.get("success", False) and working_endpoints:
            print("\n2. CORS issues detected. Make sure CORS is properly configured in app.py.")
            print("   The browser may block API requests from your frontend.")
    
    print("\nNext steps for frontend:")
    print("1. Make sure the React app is using one of the working endpoints")
    print("2. Check browser console for CORS errors")
    print("3. If using the fix_chunk_error.js script, ensure it's properly applied")
    print("4. Try: cd Frontend && npm start")

if __name__ == "__main__":
    main() 