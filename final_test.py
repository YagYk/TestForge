import requests
import json

# Test function
def test_api_with_code(name, code, tests, save_results=True):
    print(f"Testing API with {name}...")
    
    payload = {
        "code": code,
        "custom_tests": tests,
        "generate_ai_tests": True
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/test-custom",
            json=payload,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Basic summary
            print("\n=== Mutation Testing Results ===")
            print(f"Total mutations: {result.get('total_mutations', 0)}")
            print(f"Tests passed on original: {result.get('tests_passed_original', 0)}")
            print(f"Mutation detection rate: {result.get('mutation_detection_rate', 0):.2f}%")
            
            # Save detailed results to file if requested
            if save_results:
                filename = f"{name.lower().replace(' ', '_')}_results.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Detailed results saved to {filename}")
                
                # Print summary of mutations
                if result.get("mutation_results"):
                    print(f"\nGenerated {len(result.get('mutation_results', []))} mutations:")
                    for i, mutation in enumerate(result.get("mutation_results", [])[:3]):  # Only show first 3
                        print(f"  {i+1}. {mutation.get('mutation_description', 'Unknown')} (Line {mutation.get('line_number', 'Unknown')})")
                    if len(result.get("mutation_results", [])) > 3:
                        print(f"  ... and {len(result.get('mutation_results', [])) - 3} more (see {filename})")
                else:
                    print("\nNo mutations were generated!")
            else:
                # Print full results
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
            
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Simple code example
simple_code = """
def add(a, b):
    return a + b
"""

simple_tests = """
import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
"""

# Complex code example
complex_code = """
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

complex_tests = """
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

# Run tests
test_api_with_code("Simple Add Function", simple_code, simple_tests)

print("\n" + "="*50)

test_api_with_code("Complex Discount Function", complex_code, complex_tests) 