import os
import ast
import uuid
import random
import tempfile
import subprocess
import shutil
import re
from pathlib import Path
import git
from typing import List, Dict, Any, Union, Optional

class MutationEngine:
    """
    A class to handle code mutation using mutmut or custom mutation strategies
    """
    
    def __init__(self, temp_dir: str):
        """
        Initialize the mutation engine
        
        Args:
            temp_dir: Path to store temporary files
        """
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        # Add debug flag
        self.debug = True
    
    def generate_mutations(self, source_file: str) -> List[Dict[str, Any]]:
        """
        Generate mutations for the given source file
        
        Args:
            source_file: Path to the Python source file
            
        Returns:
            List of mutation details including original and mutated code
        """
        try:
            # Attempt to use mutmut if available
            if self.debug:
                print(f"Attempting to generate mutations for {source_file}")
            return self._generate_mutations_with_mutmut(source_file)
        except (ImportError, subprocess.CalledProcessError) as e:
            print(f"Falling back to custom mutation engine: {e}")
            # Fallback to custom implementation
            return self._generate_mutations_custom(source_file)
    
    def _generate_mutations_with_mutmut(self, source_file: str) -> List[Dict[str, Any]]:
        """
        Generate mutations using mutmut
        
        Args:
            source_file: Path to the Python source file
            
        Returns:
            List of mutation details
        """
        try:
            # Create a temporary directory for mutmut to work in
            work_dir = os.path.dirname(os.path.abspath(source_file))
            
            # Run mutmut to find mutations
            result = subprocess.run(
                ["mutmut", "run", "--paths-to-mutate", source_file],
                cwd=work_dir,
                text=True,
                capture_output=True,
                check=False
            )
            
            # Check if there were any mutations generated
            if "No surviving mutants found" in result.stdout or "No valid mutants found" in result.stdout:
                return []
            
            # Run mutmut show to get the mutations
            show_result = subprocess.run(
                ["mutmut", "show"],
                cwd=work_dir,
                text=True,
                capture_output=True,
                check=False
            )
            
            # Parse the output to get mutation details
            mutations = []
            mutation_id_pattern = r"mutmut (\d+)"
            mutation_blocks = show_result.stdout.split("--- Starting mutation ---")
            
            for block in mutation_blocks[1:]:  # Skip the first empty block
                match = re.search(mutation_id_pattern, block)
                if not match:
                    continue
                
                mutation_id = match.group(1)
                
                # Extract line number
                line_number_pattern = r"File: .*?:(\d+)"
                line_match = re.search(line_number_pattern, block)
                line_number = int(line_match.group(1)) if line_match else 0
                
                # Extract original and mutated code
                original_code = ""
                mutated_code = ""
                
                # Get full file content
                with open(source_file, 'r') as f:
                    file_content = f.read()
                
                # Run mutmut show for this specific mutation to see the diff
                show_mutation = subprocess.run(
                    ["mutmut", "show", mutation_id],
                    cwd=work_dir,
                    text=True,
                    capture_output=True,
                    check=False
                )
                
                # Parse diff to extract changes
                diff_lines = show_mutation.stdout.splitlines()
                mutation_type = "Unknown mutation"
                
                for i, line in enumerate(diff_lines):
                    if line.startswith("--- ") and i+1 < len(diff_lines) and diff_lines[i+1].startswith("+++ "):
                        # Skip the filename lines
                        continue
                    if line.startswith("-") and not line.startswith("--- "):
                        original_code += line[1:] + "\n"
                    elif line.startswith("+") and not line.startswith("+++ "):
                        mutated_code += line[1:] + "\n"
                    elif "mutmut #" in line:
                        mutation_type = line.strip()
                
                # Apply the mutation to get the full mutated file
                # This is a simplified approach - in a real implementation, you'd need more robust patching
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(file_content)
                
                # Run mutmut apply to get the mutated file
                apply_result = subprocess.run(
                    ["mutmut", "apply", mutation_id],
                    cwd=work_dir,
                    text=True,
                    capture_output=True,
                    check=False
                )
                
                # Read the mutated file
                with open(source_file, 'r') as f:
                    mutated_content = f.read()
                
                # Reset the file to its original state
                with open(source_file, 'w') as f:
                    f.write(file_content)
                
                mutations.append({
                    'id': f"mutmut-{mutation_id}",
                    'source_file': source_file,
                    'line_number': line_number,
                    'original_code': original_code.strip() or "Unable to extract original code",
                    'mutated_code': mutated_content,
                    'mutation_type': mutation_type
                })
            
            return mutations
            
        except Exception as e:
            print(f"Error using mutmut: {e}")
            # Fallback to custom implementation if mutmut fails
            return self._generate_mutations_custom(source_file)
    
    def _generate_mutations_custom(self, source_file: str) -> List[Dict[str, Any]]:
        """
        Generate mutations using custom implementation
        
        Args:
            source_file: Path to the Python source file
            
        Returns:
            List of mutation details
        """
        mutations = []
        
        # Read the source file
        with open(source_file, 'r') as f:
            content = f.read()
        
        if self.debug:
            print(f"File content length: {len(content)}")
        
        # Parse the code
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"Syntax error in {source_file}. Skipping mutation.")
            return []
        
        # Find functions and methods to mutate
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get function source
                func_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                func_source = '\n'.join(func_lines)
                
                if self.debug:
                    print(f"Found function {node.name} at lines {node.lineno}-{node.end_lineno}")
                    print(f"Function source: {func_source[:100]}...")
                
                # Define mutation operators
                new_mutations = self._apply_mutations(source_file, func_source, node.lineno)
                if self.debug:
                    print(f"Generated {len(new_mutations)} mutations for function {node.name}")
                
                mutations.extend(new_mutations)
        
        if self.debug:
            print(f"Total mutations generated: {len(mutations)}")
            
        return mutations
    
    def _apply_mutations(self, source_file: str, func_source: str, start_line: int) -> List[Dict[str, Any]]:
        """
        Apply various mutation operators to the function source
        
        Args:
            source_file: Original source file path
            func_source: Function source code to mutate
            start_line: Starting line number of the function
            
        Returns:
            List of mutations
        """
        mutations = []
        lines = func_source.splitlines()
        
        if self.debug:
            print(f"Applying mutations to function starting at line {start_line}")
            print(f"Function has {len(lines)} lines")
        
        # Read the full file content
        with open(source_file, 'r') as f:
            full_content = f.read()
        
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
            # Logical operators
            (r'(\W)(and)(\W)', r'\1or\3', "Change and to or"),
            (r'(\W)(or)(\W)', r'\1and\3', "Change or to and"),
            # Boolean literals
            (r'(\W)(True)(\W)', r'\1False\3', "Change True to False"),
            (r'(\W)(False)(\W)', r'\1True\3', "Change False to True"),
            # Add basic mutations for function calls and returns
            (r'(\s*)(return\s+)(.+?)([\n;])', r'\1return None\4', "Replace return value with None"),
            (r'(\s*)(return\s+)(\w+)([\n;])', r'\1return not \3\4', "Negate return value"),
        ]
        
        # Create a separate list for return statement mutations
        return_mutations = []
        
        # Check each line for return statements
        for i, line in enumerate(lines):
            line_number = start_line + i
            
            # Skip comment and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Check for return statement
            if "return " in line and not line.strip().startswith('#'):
                # Create a basic mutation for the return statement
                orig_line = line
                
                if self.debug:
                    print(f"Found return statement: {line} at line {line_number}")
                
                # Create a modified version of the full file content with a 'MUTATED' return
                file_lines = full_content.splitlines()
                mutated_line = line.replace("return ", "return 'MUTATED_' + str(")
                # Check if there's a value after return
                if not line.strip().endswith("return"):
                    mutated_line += ")"
                file_lines[line_number-1] = mutated_line
                mutated_content = "\n".join(file_lines)
                
                mutation = {
                    "mutation_id": str(uuid.uuid4()),
                    "line_number": line_number,
                    "original_code": orig_line.strip(),
                    "mutated_code": mutated_line.strip(),
                    "mutation_description": "Force mutation: change return value",
                    "mutated_full_code": mutated_content,
                    "was_detected": False
                }
                return_mutations.append(mutation)
                if self.debug:
                    print(f"Created return mutation: {mutation['mutated_code']}")
        
        # Apply standard mutation operators to each line
        for i, line in enumerate(lines):
            line_number = start_line + i
            
            # Skip comment and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            for pattern, replacement, description in operators:
                # Try to find matches for the pattern
                if re.search(pattern, line):
                    if self.debug:
                        print(f"Found pattern match: {pattern} in line {line_number}: {line}")
                    
                    # Apply the mutation
                    mutated_line = re.sub(pattern, replacement, line)
                    
                    # Skip if mutation didn't change anything
                    if mutated_line == line:
                        continue
                    
                    # Create a modified version of the full file content
                    file_lines = full_content.splitlines()
                    file_lines[line_number-1] = mutated_line
                    mutated_content = "\n".join(file_lines)
                    
                    # Create the mutation record
                    mutation = {
                        "mutation_id": str(uuid.uuid4()),
                        "line_number": line_number,
                        "original_code": line.strip(),
                        "mutated_code": mutated_line.strip(),
                        "mutation_description": description,
                        "mutated_full_code": mutated_content,
                        "was_detected": False
                    }
                    
                    mutations.append(mutation)
                    if self.debug:
                        print(f"Created mutation: {description} at line {line_number}")
        
        # If no standard mutations were found, use the return mutations
        if not mutations and return_mutations:
            if self.debug:
                print("No regular mutations found, using return mutations")
            mutations = return_mutations
            
        # If still no mutations, create a simple forced mutation on the first non-empty line
        if not mutations:
            if self.debug:
                print("No mutations found, creating forced mutation")
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#'):
                    line_number = start_line + i
                    mutated_line = line + " # FORCED MUTATION"
                    
                    # Create a modified version of the full file content
                    file_lines = full_content.splitlines()
                    file_lines[line_number-1] = mutated_line
                    mutated_content = "\n".join(file_lines)
                    
                    mutation = {
                        "mutation_id": str(uuid.uuid4()),
                        "line_number": line_number,
                        "original_code": line.strip(),
                        "mutated_code": mutated_line.strip(),
                        "mutation_description": "Forced mutation for simple code",
                        "mutated_full_code": mutated_content,
                        "was_detected": False
                    }
                    mutations.append(mutation)
                    if self.debug:
                        print(f"Created forced mutation at line {line_number}: {mutated_line}")
                    break
        
        if self.debug:
            print(f"Returning {len(mutations)} mutations")
            
        return mutations
    
    def clone_github_repo(self, repo_url: str, branch: str = 'main', target_dir: Optional[str] = None) -> str:
        """
        Clone a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to clone (default: main)
            target_dir: Target directory for the clone (default: a temporary directory)
            
        Returns:
            Path to the cloned repository
        """
        if target_dir is None:
            target_dir = os.path.join(self.temp_dir, f"github_{uuid.uuid4().hex}")
        
        os.makedirs(target_dir, exist_ok=True)
        
        # Clone the repository
        repo = git.Repo.clone_from(repo_url, target_dir, branch=branch)
        
        return target_dir
    
    def find_python_files(self, directory: str) -> List[str]:
        """
        Find all Python files in a directory (recursively)
        
        Args:
            directory: Directory to search
            
        Returns:
            List of Python file paths
        """
        python_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files 