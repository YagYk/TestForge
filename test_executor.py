import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Tuple

class TestExecutor:
    """
    A class to execute tests against original and mutated code and collect results
    """
    
    def __init__(self, temp_dir: str):
        """
        Initialize the test executor
        
        Args:
            temp_dir: Path to temporary directory for test files
        """
        self.temp_dir = temp_dir
        # Make sure the directory for test files exists
        os.makedirs(os.path.join(self.temp_dir, "tests"), exist_ok=True)
        
    def run_tests(self, 
                 code_file: str, 
                 mutations: List[Dict[str, Any]], 
                 tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run all tests against original and mutated code
        
        Args:
            code_file: Path to the original code file
            mutations: List of mutation dictionaries
            tests: List of test dictionaries
            
        Returns:
            Dictionary with test results
        """
        results = {
            "original_code": self._read_file(code_file),
            "total_mutations": len(mutations),
            "total_tests": len(tests),
            "tests_passed_original": 0,
            "tests_detected_mutations": 0,
            "mutation_detection_rate": 0.0,
            "mutation_results": [],
        }
        
        # Run tests against the original code first
        for test_idx, test_info in enumerate(tests):
            test_file = os.path.join(self.temp_dir, "tests", f"test_{test_idx}.py")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_info["code"])
            
            # Run the test against the original code
            original_success = self._run_single_test(test_file, code_file)
            test_info["passes_original"] = original_success
            
            if original_success:
                results["tests_passed_original"] += 1
        
        # Create mutation results
        for mutation_idx, mutation in enumerate(mutations):
            # Create the mutated code file
            mutated_file = os.path.join(self.temp_dir, f"mutated_{mutation_idx}.py")
            self._create_mutated_file(code_file, mutated_file, mutation)
            
            mutation_result = {
                "mutation_id": mutation_idx,
                "mutation_description": mutation.get("description", "Unknown mutation"),
                "line_number": mutation.get("line", 0),
                "original_code": mutation.get("original_code", ""),
                "mutated_code": mutation.get("mutated_code", ""),
                "detected_by_tests": [],
                "was_detected": False
            }
            
            # Run each test against this mutation
            for test_idx, test_info in enumerate(tests):
                # Only run tests that passed against the original code
                if not test_info.get("passes_original", False):
                    continue
                    
                test_file = os.path.join(self.temp_dir, "tests", f"test_{test_idx}.py")
                mutated_success = self._run_single_test(test_file, mutated_file)
                
                # If the test fails on the mutation but passed on the original,
                # it has detected the mutation
                if not mutated_success:
                    mutation_result["detected_by_tests"].append(test_idx)
                    mutation_result["was_detected"] = True
                    test_info["detected_mutations"] = test_info.get("detected_mutations", []) + [mutation_idx]
            
            results["mutation_results"].append(mutation_result)
            if mutation_result["was_detected"]:
                results["tests_detected_mutations"] += 1
        
        # Calculate detection rate
        if len(mutations) > 0:
            results["mutation_detection_rate"] = results["tests_detected_mutations"] / len(mutations) * 100
        
        # Add test details to the results
        results["test_details"] = []
        for test_idx, test_info in enumerate(tests):
            results["test_details"].append({
                "test_id": test_idx,
                "name": test_info.get("name", f"Test {test_idx}"),
                "passes_original": test_info.get("passes_original", False),
                "detected_mutations": test_info.get("detected_mutations", []),
                "detection_count": len(test_info.get("detected_mutations", [])),
            })
        
        return results
    
    def _create_mutated_file(self, original_file: str, mutated_file: str, mutation: Dict[str, Any]) -> None:
        """
        Create a file with the mutated code
        
        Args:
            original_file: Path to the original code file
            mutated_file: Path where the mutated file should be created
            mutation: Dictionary with mutation details
        """
        with open(original_file, "r", encoding="utf-8") as f:
            original_code = f.read()
        
        # Check if we have a specific mutation to apply
        if "line" in mutation and "original_code" in mutation and "mutated_code" in mutation:
            lines = original_code.splitlines()
            line_index = mutation["line"] - 1  # Convert to 0-based indexing
            
            if 0 <= line_index < len(lines):
                original_line = lines[line_index]
                mutated_line = original_line.replace(mutation["original_code"], mutation["mutated_code"])
                lines[line_index] = mutated_line
                
                with open(mutated_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                return
        
        # If we couldn't apply the specific mutation, just copy the original
        with open(mutated_file, "w", encoding="utf-8") as f:
            f.write(original_code)
    
    def _run_single_test(self, test_file: str, code_file: str) -> bool:
        """
        Run a single test against a code file
        
        Args:
            test_file: Path to the test file
            code_file: Path to the code file to test
            
        Returns:
            True if the test passes, False otherwise
        """
        # Get the directory of the code file
        code_dir = os.path.dirname(code_file)
        
        # Create environment with path set to include the code directory
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{code_dir}:{env.get('PYTHONPATH', '')}"
        
        try:
            # Try to run the test with unittest
            result = subprocess.run(
                [sys.executable, test_file],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5  # Prevent infinite loops
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"Test timed out: {test_file}")
            return False
        except Exception as e:
            print(f"Error running test {test_file}: {e}")
            return False
    
    def _read_file(self, file_path: str) -> str:
        """
        Read the contents of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Contents of the file as a string
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return "" 