import os
import ast
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

# Check AST parsing - direct AST check
for file_path, file_name in [(simple_file, "Simple"), (complex_file, "Complex")]:
    print(f"\n=== Checking AST for {file_name} Code ===")
    with open(file_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        print(f"Successfully parsed AST")
        
        # Count function definitions
        function_count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_count += 1
                print(f"Found function: {node.name}, line {node.lineno}-{node.end_lineno}")
                
                # Get function body lines
                func_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                print(f"Function source ({len(func_lines)} lines):")
                for i, line in enumerate(func_lines):
                    print(f"  {node.lineno+i}: {line}")
        
        print(f"Total functions found: {function_count}")
        
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")

# Debug with a custom version of the _apply_mutations method to see what's happening
def debug_apply_mutations(source_file, func_source, start_line):
    print(f"\n=== Debug Apply Mutations ===")
    print(f"Source file: {source_file}")
    print(f"Function source length: {len(func_source)} characters")
    print(f"Start line: {start_line}")
    
    mutations = []
    lines = func_source.splitlines()
    print(f"Function has {len(lines)} lines")
    
    # Read the full file content
    with open(source_file, 'r') as f:
        full_content = f.read()
    
    print("Checking for patterns to match...")
    # Define a subset of mutation operators for testing
    operators = [
        # Arithmetic operators
        (r'(\W)(\+)(\W)', r'\1-\3', "Change + to -"),
        (r'(\W)(-)(\W)', r'\1+\3', "Change - to +"),
        # Relational operators
        (r'(\W)(==)(\W)', r'\1!=\3', "Change == to !="),
        # Boolean literals
        (r'(\W)(True)(\W)', r'\1False\3', "Change True to False"),
    ]
    
    found_mutations = False
    
    # Apply mutations to each line
    for i, line in enumerate(lines):
        line_number = start_line + i
        
        print(f"Checking line {line_number}: {line}")
        
        for pattern, replacement, description in operators:
            # Skip comment and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            import re
            # Check for match without substituting
            if re.search(pattern, line):
                print(f"  MATCH FOUND: {pattern} matches in line: {line}")
                found_mutations = True
                
                # Apply the mutation
                mutated_line = re.sub(pattern, replacement, line)
                
                # Skip if mutation didn't change anything
                if mutated_line == line:
                    print(f"  WARNING: Mutation didn't change anything")
                    continue
                
                print(f"  Original: {line}")
                print(f"  Mutated: {mutated_line}")
                print(f"  Description: {description}")
    
    if not found_mutations:
        print("No pattern matches found in any lines")
        
        # Check for basic mutations like return statements
        for i, line in enumerate(lines):
            if "return " in line and not line.strip().startswith('#'):
                print(f"Found return statement in line {start_line + i}: {line}")
                print("This should have created a basic mutation")
    
    # Check if we would create a forced mutation
    if not found_mutations:
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                print(f"Would create forced mutation on first non-empty line {start_line + i}: {line}")
                break
    
    return mutations

# Initialize the mutation engine
mutation_engine = MutationEngine(temp_dir)

# Debug the apply mutations method directly
for file_path, file_name in [(simple_file, "Simple"), (complex_file, "Complex")]:
    print(f"\n=== Testing {file_name} Code with Custom Debug ===")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse the code
    try:
        tree = ast.parse(content)
        
        # Find functions to mutate
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get function source
                func_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                func_source = '\n'.join(func_lines)
                
                # Call our debug version
                debug_apply_mutations(file_path, func_source, node.lineno)
                
    except SyntaxError:
        print(f"Syntax error in {file_path}. Skipping mutation.")

# Now try the actual mutation engine
print("\n=== Testing with actual MutationEngine ===")
simple_mutations = mutation_engine.generate_mutations(simple_file)
print(f"Generated {len(simple_mutations)} mutations for simple code")

complex_mutations = mutation_engine.generate_mutations(complex_file)
print(f"Generated {len(complex_mutations)} mutations for complex code")

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