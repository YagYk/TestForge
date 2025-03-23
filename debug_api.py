#!/usr/bin/env python3
"""
Debug script to test and validate API connectivity
"""
import os
import sys
import json
import requests
from urllib.parse import urljoin

# Default API URL
API_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    endpoint = urljoin(API_URL, "/api/health")
    print(f"Testing health endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"Status code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if Gemini API key is available
            if "dependencies" in data and "gemini_api_key" in data["dependencies"]:
                print(f"Gemini API key status: {data['dependencies']['gemini_api_key']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def test_demo():
    """Test the demo test endpoint"""
    endpoint = urljoin(API_URL, "/api/run-tests")
    print(f"Testing demo endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"Status code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            # Pretty print the first part of the response
            print(f"Response summary:")
            print(f"  Total mutations: {data.get('total_mutations', 'N/A')}")
            print(f"  Tests passed original: {data.get('tests_passed_original', 'N/A')}")
            print(f"  Mutations detected: {data.get('tests_detected_mutations', 'N/A')}")
            print(f"  Detection rate: {data.get('mutation_detection_rate', 'N/A')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def test_custom_code():
    """Test the custom code endpoint with a simple example"""
    endpoint = urljoin(API_URL, "/api/test-custom")
    print(f"Testing custom code endpoint: {endpoint}")
    
    test_data = {
        "code": "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError('Cannot divide by zero')\n    return a / b",
        "custom_tests": "import unittest\n\nclass TestMath(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(1, 2), 3)\n    \n    def test_divide(self):\n        self.assertEqual(divide(6, 2), 3)",
        "generate_ai_tests": True
    }
    
    try:
        response = requests.post(
            endpoint, 
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            # Pretty print the first part of the response
            print(f"Response summary:")
            print(f"  Total mutations: {data.get('total_mutations', 'N/A')}")
            print(f"  Tests passed original: {data.get('tests_passed_original', 'N/A')}")
            print(f"  Mutations detected: {data.get('tests_detected_mutations', 'N/A')}")
            print(f"  Detection rate: {data.get('mutation_detection_rate', 'N/A')}")
            
            # Check session ID
            if "session_id" in data:
                print(f"  Session ID: {data['session_id']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def main():
    """Main function"""
    print("API Debug Tool")
    print("==============")
    
    # Check health
    print("\n1. Checking API health...")
    if not test_health():
        print("Health check failed. Make sure the API server is running.")
        return
    
    # Check demo
    print("\n2. Testing demo endpoint...")
    test_demo()
    
    # Test custom code
    print("\n3. Testing custom code endpoint...")
    test_custom_code()
    
    print("\nTests completed.")

if __name__ == "__main__":
    # Check if custom API URL is provided
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    
    main() 