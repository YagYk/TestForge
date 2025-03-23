import requests
import json

# Test accessing the root endpoint
try:
    response = requests.get("http://localhost:5000/")
    print(f"Root Status Code: {response.status_code}")
    
    # Try to find all API endpoints in the HTML
    content = response.text.lower()
    api_routes = []
    for line in content.split('\n'):
        if '/api/' in line:
            api_routes.append(line.strip())
    
    if api_routes:
        print("Found potential API routes:")
        for route in api_routes:
            print(f"  - {route}")
    else:
        print("No API routes found in the HTML")
except Exception as e:
    print(f"Exception accessing root: {e}")

# Define the test code and test cases
code = """
def add(a, b):
    return a + b
"""

custom_tests = """
import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
"""

# Create the payload
payload = {
    "code": code,
    "custom_tests": custom_tests,
    "generate_ai_tests": False
}

# Try different endpoints
endpoints = [
    "/api/test-custom",
    "/test-custom",
    "/api/analyze"  # From our Testforge implementation
]

for endpoint in endpoints:
    print(f"\nTrying endpoint: {endpoint}")
    try:
        response = requests.post(
            f"http://localhost:5000{endpoint}",
            json=payload
        )
        
        # Print the results
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                print(json.dumps(result, indent=2))
            except:
                print(f"Response: {response.text[:100]}...")
        else:
            print(f"Error: {response.text[:100]}...")
    except Exception as e:
        print(f"Exception: {e}") 