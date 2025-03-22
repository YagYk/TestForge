from flask import Flask, render_template, jsonify, request
import bugslayer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    # Run the mutation testing process
    results = bugslayer.run_mutation_testing()
    return jsonify(results)

@app.route('/api/custom-tests', methods=['POST'])
def run_custom_tests():
    # Get the custom code and function name from the request
    data = request.json
    custom_code = data.get('code_input', '')
    function_name = data.get('function_name', 'calculator')
    
    app.logger.info(f"Running custom tests for function: {function_name}")
    
    # Run the custom code mutation testing
    results = bugslayer.run_custom_mutation_testing(custom_code, function_name)
    
    app.logger.info(f"Custom tests completed with {results.get('total_mutants', 0)} mutations")
    
    # Also fetch the latest results to update the main view
    latest_results = bugslayer.get_results()
    app.logger.info(f"Latest results: {latest_results.get('total_mutants', 0)} mutations")
    
    return jsonify(results)

@app.route('/api/github-tests', methods=['POST'])
def run_github_tests():
    # Get the GitHub repository details from the request
    data = request.json
    repo_url = data.get('repo_url', '').strip()
    file_path = data.get('file_path', '').strip()
    function_name = data.get('function_name', '').strip()
    
    app.logger.info(f"Running GitHub tests for repo: {repo_url}, file: {file_path}, function: {function_name}")
    
    # Validate inputs
    if not repo_url:
        return jsonify({
            "error": "Repository URL is required",
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        })
    
    if not file_path:
        return jsonify({
            "error": "File path is required",
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        })
    
    if not function_name:
        return jsonify({
            "error": "Function name is required",
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        })
    
    # Validate GitHub URL format
    if not (repo_url.startswith('https://github.com/') or 
            repo_url.startswith('http://github.com/') or
            repo_url.startswith('git@github.com:')):
        return jsonify({
            "error": "Invalid GitHub URL format. Please use https://github.com/username/repo or git@github.com:username/repo",
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        })
    
    try:
        # Run the GitHub repository testing
        results = bugslayer.run_github_repo_testing(repo_url, file_path, function_name)
        
        app.logger.info(f"GitHub tests completed with {results.get('total_mutants', 0)} mutations")
        
        # Also fetch the latest results to update the main view
        latest_results = bugslayer.get_results()
        app.logger.info(f"Latest results: {latest_results.get('total_mutants', 0)} mutations")
        
        return jsonify(results)
    except Exception as e:
        # Log the error
        app.logger.error(f"Error processing GitHub repository: {str(e)}")
        return jsonify({
            "error": f"Failed to process GitHub repository: {str(e)}",
            "total_mutants": 0,
            "killed_mutants": 0,
            "surviving_mutants": 0,
            "test_effectiveness": 0,
            "mutations": []
        })

@app.route('/api/results')
def get_results():
    # Get the current results
    results = bugslayer.get_results()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 