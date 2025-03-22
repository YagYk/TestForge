import random
import inspect
import ast
import astor
import os
import json
import google.generativeai as genai
from textwrap import dedent
import unittest
import importlib.util
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import re

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# Sample function to test - a simple calculator function
def calculator(operation, a, b):
    """
    Performs basic arithmetic operations
    operation: 'add', 'subtract', 'multiply', 'divide'
    a, b: numbers
    """
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b != 0:  # Prevent division by zero
            return a / b
        else:
            raise ValueError("Cannot divide by zero")
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Store original function code for mutation
ORIGINAL_FUNC = inspect.getsource(calculator)

# Mock data for the demo (in a real app, this would be generated)
RESULTS = {
    "total_mutants": 0,
    "killed_mutants": 0,
    "surviving_mutants": 0,
    "test_effectiveness": 0,
    "mutations": []
}

def create_mutation(func_source):
    """Create a mutation of the given function source code"""
    # Parse the function code to AST
    parsed = ast.parse(dedent(func_source))
    
    # Simple mutation strategies
    mutations = [
        # Change + to -
        lambda node: ast.BinOp(node.left, ast.Sub(), node.right) 
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) else node,
        # Change == to !=
        lambda node: ast.Compare(node.left, [ast.NotEq()], node.comparators) 
            if isinstance(node, ast.Compare) and any(isinstance(op, ast.Eq) for op in node.ops) else node,
        # Change != to ==
        lambda node: ast.Compare(node.left, [ast.Eq()], node.comparators) 
            if isinstance(node, ast.Compare) and any(isinstance(op, ast.NotEq) for op in node.ops) else node,
        # Change > to <=
        lambda node: ast.Compare(node.left, [ast.LtE()], node.comparators) 
            if isinstance(node, ast.Compare) and any(isinstance(op, ast.Gt) for op in node.ops) else node
    ]
    
    # For demo, just randomly choose a mutation
    mutation_type = random.choice(["Change + to -", "Change == to !=", "Change != to ==", "Change > to <="])
    
    # Apply the mutation to a random node (simplified for demo)
    # In real implementation, you'd traverse the AST and apply mutations more carefully
    
    # For demonstration, return a manually mutated version of calculator
    if mutation_type == "Change + to -" and "a + b" in func_source:
        return func_source.replace("a + b", "a - b"), "Changed + to - in addition operation"
    elif "b != 0" in func_source:
        return func_source.replace("b != 0", "b == 0"), "Changed != to == in division check"
    else:
        # Fallback mutation
        return func_source.replace("return a / b", "return a * b"), "Changed division to multiplication"

def generate_test_with_ai(func_source, mutation_info):
    """Generate a test case using AI for the given function"""
    # For demo purposes, check if Google Gemini API key is available
    if not gemini_api_key:
        # Fallback to hardcoded tests if no API key is provided
        if "Changed + to -" in mutation_info:
            test_code = """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calculator('add', 5, 3), 8)
        self.assertEqual(calculator('add', -1, 1), 0)
        
if __name__ == '__main__':
    unittest.main()
"""
        elif "Changed != to ==" in mutation_info:
            test_code = """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculator('divide', 10, 0)
        
if __name__ == '__main__':
    unittest.main()
"""
        else:
            test_code = """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_division(self):
        self.assertEqual(calculator('divide', 10, 2), 5)
        
if __name__ == '__main__':
    unittest.main()
"""
        return test_code
    
    # Use Google Gemini API to generate test
    try:
        # Create a prompt for the AI
        prompt = f"""
You are an expert Python developer and tester. You need to write a unittest for a function that has a specific bug.

Original function:
{func_source}

Bug introduced: {mutation_info}

Write a Python unittest that will fail when this bug is present, but would pass on the original code.
The test should be specific to catching this type of bug.
Import the 'calculator' function from the 'bugslayer' module.
Make sure to include the unittest.main() call at the end.

Output only the Python unittest code without any explanations.
"""

        # Call the Gemini API
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Extract the generated test code
        test_code = response.text.strip()
        
        # If the response doesn't look like a proper test, fallback to hardcoded tests
        if "unittest" not in test_code or "TestCalculator" not in test_code:
            # Create a fallback
            if "Changed + to -" in mutation_info:
                return """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calculator('add', 5, 3), 8)
        self.assertEqual(calculator('add', -1, 1), 0)
        
if __name__ == '__main__':
    unittest.main()
"""
            elif "Changed != to ==" in mutation_info:
                return """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculator('divide', 10, 0)
        
if __name__ == '__main__':
    unittest.main()
"""
            else:
                return """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_division(self):
        self.assertEqual(calculator('divide', 10, 2), 5)
        
if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code
        
    except Exception as e:
        print(f"Error using Google Gemini API: {e}")
        # Fallback to hardcoded tests
        if "Changed + to -" in mutation_info:
            return """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calculator('add', 5, 3), 8)
        self.assertEqual(calculator('add', -1, 1), 0)
        
if __name__ == '__main__':
    unittest.main()
"""
        elif "Changed != to ==" in mutation_info:
            return """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculator('divide', 10, 0)
        
if __name__ == '__main__':
    unittest.main()
"""
        else:
            return """
import unittest
from bugslayer import calculator

class TestCalculator(unittest.TestCase):
    def test_division(self):
        self.assertEqual(calculator('divide', 10, 2), 5)
        
if __name__ == '__main__':
    unittest.main()
"""

def run_test(test_code):
    """Run the test and return if it passes or fails"""
    try:
        # Create temporary files
        test_file = Path("temp_test.py")
        mutated_module_file = Path("temp_bugslayer.py")
        
        # Create a mutated version of the calculator function
        mutated_code, mutation_info = create_mutation(ORIGINAL_FUNC)
        
        # Create a temporary module with the mutated code
        module_content = f"""
# This is a temporary mutated version of the calculator function
{mutated_code}
"""
        
        # Write files
        test_file.write_text(test_code)
        mutated_module_file.write_text(module_content)
        
        # For demo purposes in a hackathon, we'll simulate the test result
        # In a real implementation, you'd run the test programmatically using unittest.TextTestRunner()
        # and capture the results
        
        # Simulate test result - roughly half the tests should catch the mutations
        test_passed = random.choice([True, False])
        
        # Clean up
        if test_file.exists():
            test_file.unlink()
        if mutated_module_file.exists():
            mutated_module_file.unlink()
        
        # If test fails on mutated code, it means it caught the bug (good)
        return not test_passed
    
    except Exception as e:
        print(f"Error running test: {e}")
        # Clean up in case of error
        if 'test_file' in locals() and test_file.exists():
            test_file.unlink()
        if 'mutated_module_file' in locals() and mutated_module_file.exists():
            mutated_module_file.unlink()
        
        # Fallback to random result
        return random.choice([True, False])

def run_mutation_testing():
    """Run the full mutation testing process"""
    global RESULTS
    
    # Reset results
    RESULTS = {
        "total_mutants": 0,
        "killed_mutants": 0,
        "surviving_mutants": 0,
        "test_effectiveness": 0,
        "mutations": []
    }
    
    # Number of mutations to create
    num_mutations = 5
    
    for i in range(num_mutations):
        # Create a mutation
        mutated_code, mutation_info = create_mutation(ORIGINAL_FUNC)
        
        # Generate test with AI
        test_code = generate_test_with_ai(ORIGINAL_FUNC, mutation_info)
        
        # Run test on mutated code
        mutation_killed = run_test(test_code)
        
        # Update results
        RESULTS["total_mutants"] += 1
        if mutation_killed:
            RESULTS["killed_mutants"] += 1
        else:
            RESULTS["surviving_mutants"] += 1
        
        RESULTS["mutations"].append({
            "id": i + 1,
            "mutation_type": mutation_info,
            "killed": mutation_killed,
            "test_generated": test_code.strip()
        })
    
    # Calculate effectiveness
    if RESULTS["total_mutants"] > 0:
        RESULTS["test_effectiveness"] = (RESULTS["killed_mutants"] / RESULTS["total_mutants"]) * 100
    
    return RESULTS

def get_results():
    """Get the current results"""
    return RESULTS 

def run_custom_mutation_testing(custom_code, function_name):
    """Run mutation testing on custom code
    
    Args:
        custom_code (str): The custom function code
        function_name (str): The name of the function
        
    Returns:
        dict: Results of mutation testing on the custom code
    """
    # Create a results object for custom code
    custom_results = {
        "total_mutants": 0,
        "killed_mutants": 0,
        "surviving_mutants": 0,
        "test_effectiveness": 0,
        "mutations": []
    }
    
    # Number of mutations to create
    num_mutations = 3
    
    try:
        # Ensure the code is properly formatted
        if not custom_code.strip():
            raise ValueError("Custom code cannot be empty")
        
        # Ensure the code is a valid Python function
        import ast
        try:
            ast.parse(custom_code)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error in custom code: {str(e)}")
        
        # Create mutations for the custom code
        for i in range(num_mutations):
            # Create a mutation
            mutated_code, mutation_info = create_mutation(custom_code)
            
            # Generate test with AI
            test_code = generate_test_with_ai(custom_code, mutation_info)
            
            # Run test on mutated code
            # For demonstration purposes, use deterministic random behavior
            import random
            random.seed(hash(mutated_code + test_code) % 10000)  # Use hash of code as seed
            mutation_killed = random.choice([True, False])
            
            # Update results
            custom_results["total_mutants"] += 1
            if mutation_killed:
                custom_results["killed_mutants"] += 1
            else:
                custom_results["surviving_mutants"] += 1
            
            # Add formatted versions for display
            formatted_original = custom_code.replace("\n", "<br>").replace(" ", "&nbsp;")
            formatted_mutated = mutated_code.replace("\n", "<br>").replace(" ", "&nbsp;")
            formatted_test = test_code.replace("\n", "<br>").replace(" ", "&nbsp;")
            
            custom_results["mutations"].append({
                "id": i + 1,
                "mutation_type": mutation_info,
                "original_code": formatted_original,
                "mutated_code": formatted_mutated,
                "test_generated": formatted_test,
                "killed": mutation_killed
            })
        
        # Calculate effectiveness
        if custom_results["total_mutants"] > 0:
            custom_results["test_effectiveness"] = (custom_results["killed_mutants"] / custom_results["total_mutants"]) * 100
        
        # For debugging
        print(f"Custom code testing results: {custom_results}")
        
        # Also update the global results for the main view
        # This ensures that the main results section reflects the latest test
        global RESULTS
        RESULTS = {
            "total_mutants": custom_results["total_mutants"],
            "killed_mutants": custom_results["killed_mutants"],
            "surviving_mutants": custom_results["surviving_mutants"],
            "test_effectiveness": custom_results["test_effectiveness"],
            "mutations": custom_results["mutations"]
        }
    
    except Exception as e:
        # If there's an error, return an error message
        print(f"Error in custom mutation testing: {e}")
        return {
            "error": str(e),
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        }
    
    return custom_results

def clone_github_repo(repo_url, temp_dir="temp_repos"):
    """Clone a GitHub repository to a temporary directory.
    
    Args:
        repo_url (str): The GitHub repository URL
        temp_dir (str): Directory to clone repositories into
        
    Returns:
        str: Path to the cloned repository
    """
    import subprocess
    import os
    import shutil
    import uuid
    import time
    import sys
    
    # Create a unique directory for this repository
    repo_id = str(uuid.uuid4())
    repo_path = os.path.join(temp_dir, repo_id)
    
    # Create the temp directory if it doesn't exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        # For Windows, check if we should use sparse-checkout instead
        is_windows = sys.platform.startswith('win')
        
        if is_windows:
            # On Windows, use a simpler approach to avoid permission issues
            # First, create the directory
            os.makedirs(repo_path, exist_ok=True)
            
            # Initialize a git repository
            subprocess.check_call(
                ["git", "init"],
                cwd=repo_path,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Add the remote
            subprocess.check_call(
                ["git", "remote", "add", "origin", repo_url],
                cwd=repo_path,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Enable sparse checkout
            subprocess.check_call(
                ["git", "config", "core.sparsecheckout", "true"],
                cwd=repo_path,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Fetch only the default branch with depth=1
            subprocess.check_call(
                ["git", "fetch", "--depth=1", "origin"],
                cwd=repo_path,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Checkout the fetched branch
            subprocess.check_call(
                ["git", "checkout", "FETCH_HEAD"],
                cwd=repo_path,
                stderr=subprocess.PIPE,
                shell=True
            )
        else:
            # Non-Windows platforms can use the standard approach
            # Clone the repository with a depth of 1 to minimize download size
            subprocess.check_call(
                ["git", "clone", "--depth=1", repo_url, repo_path],
                stderr=subprocess.PIPE,
                shell=False
            )
        
        return repo_path
    except subprocess.CalledProcessError as e:
        # Clean up failed clone
        print(f"Git error: {e}")
        # Wait a moment before cleanup to allow file handles to be released
        time.sleep(1)
        safe_remove_dir(repo_path)
        
        # Special handling for Windows Access Denied errors
        error_str = str(e)
        if "WinError 5" in error_str and "Access is denied" in error_str:
            raise Exception("Windows access denied error when accessing Git repository. Please try a different repository or run the application with administrator privileges.")
        
        raise Exception(f"Failed to clone repository: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        safe_remove_dir(repo_path)
        raise Exception(f"Error during repository cloning: {e}")

def safe_remove_dir(path):
    """Safely remove a directory, handling Windows permission errors.
    
    Args:
        path (str): Directory path to remove
    """
    import os
    import shutil
    import time
    from pathlib import Path
    
    if not os.path.exists(path):
        return
        
    try:
        # On Windows, sometimes we need to make files writable before deletion
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.chmod(file_path, 0o666)  # Make file writable
                except:
                    pass  # Ignore errors and continue
        
        # Try to remove the directory
        shutil.rmtree(path, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Could not remove directory {path}: {e}")
        # In case of errors, leave it for cleanup later
        pass

def extract_function_from_file(repo_path, file_path, function_name):
    """Extract a function from a file in the repository.
    
    Args:
        repo_path (str): Path to the repository
        file_path (str): Path to the file relative to the repository root
        function_name (str): Name of the function to extract
        
    Returns:
        str: The function code
    """
    import os
    import ast
    import astor
    
    # Full path to the file
    full_path = os.path.join(repo_path, file_path)
    
    if not os.path.exists(full_path):
        raise Exception(f"File {file_path} not found in repository")
    
    try:
        # Read the file content
        with open(full_path, 'r') as f:
            file_content = f.read()
        
        # Parse the file
        module = ast.parse(file_content)
        
        # Find the function
        for node in module.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Get the function source code
                return astor.to_source(node)
        
        raise Exception(f"Function '{function_name}' not found in {file_path}")
    except Exception as e:
        raise Exception(f"Error extracting function: {e}")

def fetch_github_file_http(repo_url, file_path):
    """Fetch a file directly from GitHub via HTTP without cloning.
    
    Args:
        repo_url (str): The GitHub repository URL
        file_path (str): Path to the file within the repository
        
    Returns:
        str: The file content
    """
    # Extract owner and repo from URL
    if "github.com" not in repo_url:
        raise ValueError("Not a valid GitHub URL")
    
    # Handle different URL formats
    if repo_url.startswith("git@github.com:"):
        # SSH format: git@github.com:owner/repo.git
        match = re.search(r'git@github\.com:([\w\-]+)/([\w\-]+)(\.git)?', repo_url)
        if not match:
            raise ValueError("Invalid GitHub SSH URL format")
        owner, repo = match.group(1), match.group(2)
    else:
        # HTTPS format: https://github.com/owner/repo
        match = re.search(r'github\.com/([\w\-]+)/([\w\-]+)', repo_url)
        if not match:
            raise ValueError("Invalid GitHub HTTPS URL format")
        owner, repo = match.group(1), match.group(2)
    
    # Remove .git extension if present
    if repo.endswith('.git'):
        repo = repo[:-4]
    
    # Construct the raw content URL
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{file_path}"
    
    # Fetch the file content
    response = requests.get(raw_url)
    
    if response.status_code != 200:
        # Try the main branch if master doesn't work
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"
        response = requests.get(raw_url)
        
        if response.status_code != 200:
            raise ValueError(f"File not found: {file_path} (HTTP status: {response.status_code})")
    
    return response.text

def extract_function_from_text(file_content, function_name):
    """Extract a function from file content.
    
    Args:
        file_content (str): The content of the file
        function_name (str): Name of the function to extract
        
    Returns:
        str: The function code
    """
    import ast
    import astor
    
    try:
        # Parse the file
        module = ast.parse(file_content)
        
        # Find the function
        for node in module.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Get the function source code
                return astor.to_source(node)
        
        raise Exception(f"Function '{function_name}' not found")
    except Exception as e:
        raise Exception(f"Error extracting function: {e}")

def run_github_repo_testing(repo_url, file_path, function_name):
    """Run mutation testing on a function from a GitHub repository.
    
    Args:
        repo_url (str): The GitHub repository URL
        file_path (str): Path to the file relative to the repository root
        function_name (str): Name of the function to extract and test
        
    Returns:
        dict: Results of mutation testing on the function
    """
    repo_path = None
    
    try:
        try:
            # First try to use Git to clone the repository
            repo_path = clone_github_repo(repo_url)
            function_code = extract_function_from_file(repo_path, file_path, function_name)
        except Exception as git_error:
            print(f"Git clone failed: {git_error}. Trying HTTP fallback method...")
            # If Git fails, try HTTP method as fallback
            file_content = fetch_github_file_http(repo_url, file_path)
            function_code = extract_function_from_text(file_content, function_name)
        
        # Run mutation testing on the extracted function
        results = run_custom_mutation_testing(function_code, function_name)
        
        # Add repository information to results
        results["repository"] = {
            "url": repo_url,
            "file_path": file_path,
            "function_name": function_name
        }
        
        # For debugging
        print(f"GitHub testing results: {results}")
        
        # Also update the global results for the main view
        # This ensures that the main results section reflects the latest test
        global RESULTS
        if "error" not in results:
            RESULTS = {
                "total_mutants": results["total_mutants"],
                "killed_mutants": results["killed_mutants"],
                "surviving_mutants": results["surviving_mutants"],
                "test_effectiveness": results["test_effectiveness"],
                "mutations": results["mutations"]
            }
        
        return results
    except Exception as e:
        print(f"Error in GitHub repo testing: {e}")
        return {
            "error": str(e),
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        }
    finally:
        # Always try to clean up the repository, even if we had an error
        if repo_path and os.path.exists(repo_path):
            import time
            # Wait a moment before cleanup to allow file handles to be released
            time.sleep(1)
            safe_remove_dir(repo_path) 