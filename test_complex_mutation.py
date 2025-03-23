import requests
import json
import tempfile
import os

# Define a complex function that should trigger mutations
code = """
def calculate_discount(price, customer_type, years_of_membership):
    \"\"\"Calculate discount based on price, customer type and membership years.\"\"\"
    base_discount = 0.0
    
    if customer_type == "premium":
        base_discount = 0.15
    elif customer_type == "gold":
        base_discount = 0.10
    elif customer_type == "silver":
        base_discount = 0.05
    
    loyalty_bonus = min(years_of_membership * 0.01, 0.1)
    total_discount = base_discount + loyalty_bonus
    
    if price > 1000:
        total_discount += 0.05
        
    final_price = price * (1 - total_discount)
    return round(final_price, 2)
"""

# Define test code for the function
test_code = """
import unittest

class TestDiscount(unittest.TestCase):
    def test_premium_customer(self):
        # Test a premium customer with 5 years membership
        result = calculate_discount(500, "premium", 5)
        self.assertEqual(result, 400.0)
        
    def test_gold_customer(self):
        # Test a gold customer with 2 years membership
        result = calculate_discount(300, "gold", 2)
        self.assertEqual(result, 264.0)
        
    def test_high_price_discount(self):
        # Test additional discount for high-priced items
        result = calculate_discount(1200, "silver", 3)
        self.assertEqual(result, 1044.0)
        
    def test_loyalty_cap(self):
        # Test that loyalty bonus is capped at 10%
        result = calculate_discount(500, "silver", 15)
        self.assertEqual(result, 425.0)
        
if __name__ == "__main__":
    unittest.main()
"""

print("Testing API with complex function...")
print(f"Source code length: {len(code)} characters")
print(f"Test code length: {len(test_code)} characters")

# Create a temporary file with our code
with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
    source_file_path = temp_file.name
    temp_file.write(code)
    print(f"Created temporary file: {source_file_path}")

try:
    # Create the payload
    payload = {
        "code": code,
        "custom_tests": test_code,
        "generate_ai_tests": True,  # Enable AI test generation
        "source_file_path": source_file_path  # Add the file path
    }
    
    # Send the request to the test-custom endpoint
    response = requests.post(
        "http://localhost:5000/api/test-custom",
        json=payload,
        timeout=60  # Longer timeout for AI processing
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n=== Mutation Testing Results ===")
        print(f"Total mutations: {result.get('total_mutations', 0)}")
        print(f"Tests passed on original: {result.get('tests_passed_original', 0)}")
        print(f"Mutation detection rate: {result.get('mutation_detection_rate', 0):.2f}%")
        
        # Print mutation details
        if result.get("mutation_results"):
            print("\n=== Mutations Generated ===")
            for i, mutation in enumerate(result.get("mutation_results", [])):
                print(f"\nMutation {i+1}:")
                print(f"  Description: {mutation.get('mutation_description', 'Unknown')}")
                print(f"  Line: {mutation.get('line_number', 'Unknown')}")
                print(f"  Original: {mutation.get('original_code', 'Unknown')}")
                print(f"  Mutated: {mutation.get('mutated_code', 'Unknown')}")
                print(f"  Detected: {'Yes' if mutation.get('was_detected', False) else 'No'}")
        else:
            print("\nNo mutations were generated!")
            
        # Print AI test details
        if result.get("test_details"):
            print("\n=== Tests ===")
            for i, test in enumerate(result.get("test_details", [])):
                print(f"\nTest {i+1}: {test.get('name', 'Unknown')}")
                print(f"  Source: {test.get('source', 'Unknown')}")
                print(f"  Passes original: {'Yes' if test.get('passes_original', False) else 'No'}")
                print(f"  Detected mutations: {test.get('detection_count', 0)}")
        else:
            print("\nNo test details were provided!")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    # Clean up temporary file
    if os.path.exists(source_file_path):
        os.unlink(source_file_path)
        print(f"Deleted temporary file: {source_file_path}") 