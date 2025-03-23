import requests
import json
import traceback

# Simple test code
code = """
def add(a, b):
    return a + b
"""

# Simple test
custom_tests = """
import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
"""

payload = {
    "code": code,
    "custom_tests": custom_tests,
    "generate_ai_tests": False
}

print("Sending request to API...")
try:
    # Make sure we're sending the right content type
    headers = {"Content-Type": "application/json"}
    
    # Send a POST request
    response = requests.post(
        "http://localhost:5000/api/test-custom",
        data=json.dumps(payload),  # Explicitly use json.dumps
        headers=headers,
        timeout=10
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    # Try to parse the response
    try:
        result = response.json()
        print("Response JSON:")
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError:
        print("Could not decode JSON response")
        print("Raw response:")
        print(response.text[:200])
        
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc() 