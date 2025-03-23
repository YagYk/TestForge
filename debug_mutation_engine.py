import os
import tempfile
import uuid
from mutation_engine import MutationEngine

# Function to create a simple Python file
def create_test_file(code, filename=None):
    if filename is None:
        fd, filename = tempfile.mkstemp(suffix='.py')
        os.close(fd)
    
    with open(filename, 'w') as f:
        f.write(code)
    
    return filename

# Complex test code
test_code = """
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

# Simple test code for comparison
simple_code = """
def add(a, b):
    return a + b
"""

# Create a temporary directory for the mutation engine
temp_dir = os.path.join(tempfile.gettempdir(), f"mutation_test_{uuid.uuid4().hex}")
os.makedirs(temp_dir, exist_ok=True)
print(f"Created temp directory: {temp_dir}")

# Create test files
complex_file = os.path.join(temp_dir, "complex.py")
simple_file = os.path.join(temp_dir, "simple.py")

create_test_file(test_code, complex_file)
create_test_file(simple_code, simple_file)

print(f"Created test files: {complex_file} and {simple_file}")

# Initialize the mutation engine
mutation_engine = MutationEngine(temp_dir)

# Debug the mutation generation for both files
print("\n=== Testing Simple Code ===")
simple_mutations = mutation_engine.generate_mutations(simple_file)
print(f"Generated {len(simple_mutations)} mutations for simple code")
for i, mutation in enumerate(simple_mutations):
    print(f"\nMutation {i+1}:")
    print(f"  Line number: {mutation.get('line_number', 'Unknown')}")
    print(f"  Original code: {mutation.get('original_code', 'Unknown')}")
    print(f"  Mutated code: {mutation.get('mutated_code', 'Unknown')}")
    print(f"  Description: {mutation.get('mutation_description', 'Unknown')}")

print("\n=== Testing Complex Code ===")
complex_mutations = mutation_engine.generate_mutations(complex_file)
print(f"Generated {len(complex_mutations)} mutations for complex code")
for i, mutation in enumerate(complex_mutations):
    print(f"\nMutation {i+1}:")
    print(f"  Line number: {mutation.get('line_number', 'Unknown')}")
    print(f"  Original code: {mutation.get('original_code', 'Unknown')}")
    print(f"  Mutated code: {mutation.get('mutated_code', 'Unknown')}")
    print(f"  Description: {mutation.get('mutation_description', 'Unknown')}")

# Clean up
print("\nCleaning up...")
for file in [complex_file, simple_file]:
    if os.path.exists(file):
        os.remove(file)
        print(f"Removed {file}")

# Try to remove the temp directory
try:
    os.rmdir(temp_dir)
    print(f"Removed directory {temp_dir}")
except:
    print(f"Could not remove directory {temp_dir} (it may not be empty)") 