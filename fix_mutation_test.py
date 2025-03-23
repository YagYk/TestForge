import os
import tempfile
import requests
import json
import re

def create_source_code_file(code):
    """Create a temporary file with the source code."""
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(code.encode('utf-8'))
        return f.name

def create_mutations(source_file):
    """Create mutations for the given source file."""
    # Read the source file
    with open(source_file, 'r') as f:
        content = f.read()
    
    mutations = []
    lines = content.splitlines()
    
    # Define mutation operators
    operators = [
        # Arithmetic operators
        (r'(\W)(\+)(\W)', r'\1-\3', "Change + to -"),
        (r'(\W)(-)(\W)', r'\1+\3', "Change - to +"),
        (r'(\W)(\*)(\W)', r'\1/\3', "Change * to /"),
        (r'(\W)(/)(\W)', r'\1*\3', "Change / to *"),
        # Relational operators
        (r'(\W)(==)(\W)', r'\1!=\3', "Change == to !="),
        (r'(\W)(!=)(\W)', r'\1==\3', "Change != to =="),
        (r'(\W)(>)(\W)', r'\1<=\3', "Change > to <="),
        (r'(\W)(<)(\W)', r'\1>=\3', "Change < to >="),
        (r'(\W)(>=)(\W)', r'\1<\3', "Change >= to <"),
        (r'(\W)(<=)(\W)', r'\1>\3', "Change <= to >"),
        # Boolean literals
        (r'(\W)(True)(\W)', r'\1False\3', "Change True to False"),
        (r'(\W)(False)(\W)', r'\1True\3', "Change False to True"),
    ]
    
    # Apply mutations to each line
    for i, line in enumerate(lines):
        line_number = i + 1
        
        # Skip comment and empty lines
        if line.strip().startswith('#') or not line.strip():
            continue
        
        # Check if the line contains a return statement
        if "return " in line and not line.strip().startswith('#'):
            # Create a basic mutation for the return statement
            mutated_line = line.replace("return ", "return 'MUTATED_' + str(")
            # Check if there's a value after return
            if not line.strip().endswith("return"):
                mutated_line += ")"
            
            mutation = {
                "line_number": line_number,
                "original_code": line.strip(),
                "mutated_code": mutated_line.strip(),
                "mutation_description": "Force mutation: change return value",
            }
            mutations.append(mutation)
        
        # Try standard operators
        for pattern, replacement, description in operators:
            # Try to find matches for the pattern
            if re.search(pattern, line):
                # Apply the mutation
                mutated_line = re.sub(pattern, replacement, line)
                
                # Skip if mutation didn't change anything
                if mutated_line == line:
                    continue
                
                # Create the mutation record
                mutation = {
                    "line_number": line_number,
                    "original_code": line.strip(),
                    "mutated_code": mutated_line.strip(),
                    "mutation_description": description,
                }
                
                mutations.append(mutation)
    
    # If no mutations found, create a forced mutation
    if not mutations:
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                line_number = i + 1
                mutated_line = line + " # FORCED MUTATION"
                
                mutation = {
                    "line_number": line_number,
                    "original_code": line.strip(),
                    "mutated_code": mutated_line.strip(),
                    "mutation_description": "Forced mutation for simple code",
                }
                mutations.append(mutation)
                break
    
    return mutations

def send_custom_mutations_to_api(code, tests, mutations):
    """Send custom mutations to the API."""
    payload = {
        "code": code,
        "custom_tests": tests,
        "generate_ai_tests": True,
        "mutations": mutations  # Add the custom mutations
    }
    
    response = requests.post(
        "http://localhost:5000/api/test-custom",
        json=payload,
        timeout=30
    )
    
    return response

def main():
    """Main function."""
    # Simple test code
    simple_code = """
def add(a, b):
    return a + b
"""
    
    # Complex test code
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
    
    # Custom tests
    simple_tests = """
import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
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
    
    # Test simple code
    print("Testing simple code...")
    simple_file = create_source_code_file(simple_code)
    simple_mutations = create_mutations(simple_file)
    print(f"Generated {len(simple_mutations)} mutations for simple code")
    
    for i, mutation in enumerate(simple_mutations):
        print(f"\nMutation {i+1}:")
        print(f"  Line: {mutation['line_number']}")
        print(f"  Original: {mutation['original_code']}")
        print(f"  Mutated: {mutation['mutated_code']}")
        print(f"  Description: {mutation['mutation_description']}")
    
    # Test complex code
    print("\nTesting complex code...")
    complex_file = create_source_code_file(complex_code)
    complex_mutations = create_mutations(complex_file)
    print(f"Generated {len(complex_mutations)} mutations for complex code")
    
    for i, mutation in enumerate(complex_mutations):
        print(f"\nMutation {i+1}:")
        print(f"  Line: {mutation['line_number']}")
        print(f"  Original: {mutation['original_code']}")
        print(f"  Mutated: {mutation['mutated_code']}")
        print(f"  Description: {mutation['mutation_description']}")
    
    # Send to API with custom mutations
    print("\nSending to API with custom mutations...")
    response = send_custom_mutations_to_api(complex_code, complex_tests, complex_mutations)
    
    print(f"Status Code: {response.status_code}")
    
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
            print("\nNo mutations were returned!")
    else:
        print(f"Error response: {response.text}")
    
    # Clean up
    os.remove(simple_file)
    os.remove(complex_file)

if __name__ == "__main__":
    main() 