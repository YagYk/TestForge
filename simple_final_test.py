import requests
import json

# Simple code example
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

payload = {
    "code": code,
    "custom_tests": custom_tests,
    "generate_ai_tests": True
}

print("Testing API with simple add function...")
try:
    response = requests.post(
        "http://localhost:5000/api/test-custom",
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Total mutations: {result.get('total_mutations', 0)}")
        if result.get("mutation_results"):
            print("Mutations found!")
            with open("mutations.json", "w") as f:
                json.dump(result, f, indent=2)
            print("Results saved to mutations.json")
        else:
            print("No mutations found")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}") 