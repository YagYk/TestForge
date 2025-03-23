import requests
import json
import sys
import traceback

print("Starting complex test script")

# Define a more complex piece of code to be tested
code = """
def calculate_statistics(numbers):
    '''
    Calculate basic statistics for a list of numbers.
    
    Args:
        numbers: A list of numbers
        
    Returns:
        Dictionary with mean, median, min, max and count
    '''
    if not numbers:
        return {"mean": 0, "median": 0, "min": 0, "max": 0, "count": 0}
    
    # Calculate stats
    count = len(numbers)
    mean = sum(numbers) / count
    
    # Sort for median and min/max
    sorted_nums = sorted(numbers)
    if count % 2 == 0:
        # Even number of items
        median = (sorted_nums[count//2 - 1] + sorted_nums[count//2]) / 2
    else:
        # Odd number of items
        median = sorted_nums[count//2]
    
    return {
        "mean": mean,
        "median": median,
        "min": sorted_nums[0],
        "max": sorted_nums[-1],
        "count": count
    }
"""

print("Defined source code")

# Basic test cases for the function
custom_tests = """
import unittest

class TestStatistics(unittest.TestCase):
    def test_basic_stats(self):
        result = calculate_statistics([1, 2, 3, 4, 5])
        self.assertEqual(result["mean"], 3)
        self.assertEqual(result["median"], 3)
        self.assertEqual(result["min"], 1)
        self.assertEqual(result["max"], 5)
        self.assertEqual(result["count"], 5)
    
    def test_empty_list(self):
        result = calculate_statistics([])
        self.assertEqual(result["mean"], 0)
        self.assertEqual(result["median"], 0)
        self.assertEqual(result["min"], 0)
        self.assertEqual(result["max"], 0)
        self.assertEqual(result["count"], 0)

if __name__ == '__main__':
    unittest.main()
"""

print("Defined test code")

# Create the payload
payload = {
    "code": code,
    "custom_tests": custom_tests,
    "generate_ai_tests": False  # Set to False to speed up the test
}

print("Payload size:", len(json.dumps(payload)))

# Send the request to the API
print("Sending request to /api/test-custom endpoint...")
try:
    print("Making POST request...")
    response = requests.post(
        "http://localhost:5000/api/test-custom",
        json=payload,
        timeout=30  # Add a timeout
    )
    
    # Print the results
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    
    if response.status_code == 200:
        print("Parsing JSON response...")
        try:
            result = response.json()
            print("Successfully parsed JSON")
            
            # Print a summary
            print("\n=== Mutation Testing Results ===")
            print(f"Total mutations: {result.get('total_mutations', 0)}")
            print(f"Tests passed on original: {result.get('tests_passed_original', 0)}")
            print(f"Mutations detected: {result.get('tests_detected_mutations', 0)}")
            print(f"Detection rate: {result.get('mutation_detection_rate', 0):.2f}%")
            
            # Print mutation details
            print("\n=== Mutation Details ===")
            for mutation in result.get("mutation_results", []):
                print(f"\nMutation {mutation.get('mutation_id', 'Unknown')}:")
                print(f"  Description: {mutation.get('mutation_description', 'No description')}")
                print(f"  Line: {mutation.get('line_number', 'Unknown')}")
                print(f"  Original code: {mutation.get('original_code', 'Unknown')}")
                print(f"  Mutated code: {mutation.get('mutated_code', 'Unknown')}")
                print(f"  Detected: {'Yes' if mutation.get('was_detected', False) else 'No'}")
            
            # Print test details
            print("\n=== Test Details ===")
            for test in result.get("test_details", []):
                print(f"\nTest {test.get('test_id', 'Unknown')}: {test.get('name', 'Unknown')}")
                print(f"  Passes original: {test.get('passes_original', False)}")
                print(f"  Detected mutations: {test.get('detected_mutations', [])}")
                print(f"  Detection count: {test.get('detection_count', 0)}")
        except json.JSONDecodeError as e:
            print("Failed to parse JSON response")
            print("JSON Error:", str(e))
            print("Raw response:", response.text[:500])
    else:
        print(f"Error Response: {response.text[:500]}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()

print("Script completed.") 