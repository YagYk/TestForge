import os
import google.generativeai as genai
from typing import Optional, Dict, Any

class TestGenerator:
    """
    A class to generate test cases using Google Gemini API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the test generator
        
        Args:
            api_key: Google Gemini API key (optional, can also use environment variable)
        """
        # Use the provided API key or get from environment
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # Configure the Gemini API if a key is available
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            print("Warning: No Gemini API key provided. Test generation will use fallback methods.")
    
    def generate_test(self, original_code: str, mutated_code: str, mutation_description: str) -> str:
        """
        Generate a test case that can detect the mutation
        
        Args:
            original_code: The original Python code
            mutated_code: The mutated Python code
            mutation_description: Description of the mutation
            
        Returns:
            Generated test code as a string
        """
        if not self.api_key:
            return self._generate_fallback_test(original_code, mutation_description)
        
        try:
            # Create a prompt for the API
            prompt = self._create_prompt(original_code, mutated_code, mutation_description)
            
            # Call the Gemini API
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Extract the generated test code
            test_code = response.text
            
            # Clean up the response if it contains markdown code blocks
            if "```python" in test_code:
                code_blocks = test_code.split("```")
                for block in code_blocks:
                    if block.startswith("python\n"):
                        test_code = block[7:]  # Remove "python\n"
                        break
                    elif not block.strip().startswith(('python', 'markdown')):
                        test_code = block
                        break
            
            # If the response doesn't look like a proper test
            if "import unittest" not in test_code and "import pytest" not in test_code:
                return self._generate_fallback_test(original_code, mutation_description)
            
            return test_code
            
        except Exception as e:
            print(f"Error using Google Gemini API: {e}")
            # Fallback to template-based tests
            return self._generate_fallback_test(original_code, mutation_description)
    
    def _create_prompt(self, original_code: str, mutated_code: str, mutation_description: str) -> str:
        """
        Create a prompt for the Gemini API
        
        Args:
            original_code: The original Python code
            mutated_code: The mutated Python code
            mutation_description: Description of the mutation
            
        Returns:
            Prompt string
        """
        return f"""
You are an expert Python developer and tester. I need to create a test that can detect a specific bug introduced by a mutation.

Original code:
```python
{original_code}
```

Mutated code (with the bug):
```python
{mutated_code}
```

Mutation description: {mutation_description}

Generate a Python test case that will pass when run against the original code but will fail when run against the mutated code. 
The test should specifically target the mutation described.

Please follow these guidelines:
1. Use the unittest framework
2. The test should only focus on testing the specific mutation
3. Make the test as simple as possible while ensuring it will detect the mutation
4. Don't include any explanations in your response, just the pure Python test code
5. Include appropriate import statements
6. Make sure all imports and function calls are correctly qualified
7. Use relative imports if needed (assume both the code and test are in the same package)

Return ONLY the Python test code without any additional explanations.
"""

    def _generate_fallback_test(self, code: str, mutation_description: str) -> str:
        """
        Generate a fallback test case when the API is not available
        
        Args:
            code: The original Python code
            mutation_description: Description of the mutation
            
        Returns:
            Generated test code as a string
        """
        # Extract function/class name from the code (very basic extraction)
        import re
        import ast
        
        try:
            # Parse the code to get function/class names
            tree = ast.parse(code)
            
            # Find the first function or class definition
            target_name = ""
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    target_name = node.name
                    break
                elif isinstance(node, ast.ClassDef):
                    target_name = node.name
                    break
            
            # If we found a name, create a test for it
            if target_name:
                # Create a basic test template
                if "Change + to -" in mutation_description or "Change - to +" in mutation_description:
                    return self._create_arithmetic_test_template(target_name)
                elif "Change == to !=" in mutation_description or "Change != to ==" in mutation_description:
                    return self._create_equality_test_template(target_name)
                elif "Change > to <=" in mutation_description or "Change < to >=" in mutation_description:
                    return self._create_comparison_test_template(target_name)
                else:
                    return self._create_general_test_template(target_name)
            else:
                # If we couldn't find a name, create a generic test
                return self._create_general_test_template("target_function")
                
        except SyntaxError:
            # If we couldn't parse the code, create a generic test
            return self._create_general_test_template("target_function")
    
    def _create_arithmetic_test_template(self, function_name: str) -> str:
        """Create a test template for arithmetic mutations"""
        return f"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function or class to test - adjust the import path as needed
try:
    from source import {function_name}
except ImportError:
    # If that fails, try importing directly
    try:
        exec("from {function_name} import {function_name}")
    except ImportError:
        # Last resort: try to import from the filename
        module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        exec(f"from {{module_name}} import {function_name}")

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_arithmetic_operation(self):
        # Test positive values
        self.assertEqual({function_name}(5, 3), 8)
        
        # Test negative values
        self.assertEqual({function_name}(-2, -3), -5)
        
        # Test mixed values
        self.assertEqual({function_name}(-1, 5), 4)

if __name__ == '__main__':
    unittest.main()
"""
    
    def _create_equality_test_template(self, function_name: str) -> str:
        """Create a test template for equality mutations"""
        return f"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function or class to test - adjust the import path as needed
try:
    from source import {function_name}
except ImportError:
    # If that fails, try importing directly
    try:
        exec("from {function_name} import {function_name}")
    except ImportError:
        # Last resort: try to import from the filename
        module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        exec(f"from {{module_name}} import {function_name}")

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_equality_condition(self):
        # Test when condition should be true
        self.assertTrue({function_name}(10, 10))
        
        # Test when condition should be false
        self.assertFalse({function_name}(5, 10))

if __name__ == '__main__':
    unittest.main()
"""
    
    def _create_comparison_test_template(self, function_name: str) -> str:
        """Create a test template for comparison mutations"""
        return f"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function or class to test - adjust the import path as needed
try:
    from source import {function_name}
except ImportError:
    # If that fails, try importing directly
    try:
        exec("from {function_name} import {function_name}")
    except ImportError:
        # Last resort: try to import from the filename
        module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        exec(f"from {{module_name}} import {function_name}")

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_comparison_operation(self):
        # Test value greater than threshold
        self.assertTrue({function_name}(15, 10))
        
        # Test value equal to threshold
        self.assertFalse({function_name}(10, 10))
        
        # Test value less than threshold
        self.assertFalse({function_name}(5, 10))

if __name__ == '__main__':
    unittest.main()
"""
    
    def _create_general_test_template(self, function_name: str) -> str:
        """Create a general test template"""
        return f"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function or class to test - adjust the import path as needed
try:
    from source import {function_name}
except ImportError:
    # If that fails, try importing directly
    try:
        exec("from {function_name} import {function_name}")
    except ImportError:
        # Last resort: try to import from the filename
        module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
        exec(f"from {{module_name}} import {function_name}")

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_function_behavior(self):
        # Test with sample inputs - adjust these based on the expected function behavior
        # These are placeholder assertions that will likely need to be modified
        result = {function_name}(10, 5)
        self.assertIsNotNone(result)
        
        # Add more specific tests based on the function's expected behavior

if __name__ == '__main__':
    unittest.main()
""" 