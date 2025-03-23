from flask import Flask, request, jsonify, send_from_directory
import os
import tempfile
import uuid
import shutil
import time
import logging
from werkzeug.utils import secure_filename
from flask_cors import CORS
import sys

# Import your components
from mutation_engine import MutationEngine
from test_generator import TestGenerator
from test_executor import TestExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='Frontend/build')

# Configure CORS for your frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3004", "methods": ["GET", "POST", "OPTIONS"]}})

# Dictionary to store sessions and their results
sessions = {}

# Create a temporary directory for all files
TEMP_DIR = tempfile.mkdtemp()
logger.info(f"Created temporary directory: {TEMP_DIR}")

# Cleanup temporary directory on exit
import atexit
def cleanup():
    logger.info(f"Cleaning up temporary directory: {TEMP_DIR}")
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
atexit.register(cleanup)

# Serve the frontend React app (including Spline)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    Serve the frontend React app from Frontend/build.
    Supports SPA routing by falling back to index.html.
    """
    static_folder = app.static_folder
    if not os.path.exists(static_folder):
        logger.error(f"Static folder '{static_folder}' not found. Ensure React build exists.")
        return jsonify({"error": "Frontend build not found. Run 'npm run build' in your React project and move to Frontend/build."}), 500

    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """
    Check if the API and its dependencies are working.
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3004'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

    has_gemini_key = bool(os.getenv("GEMINI_API_KEY"))
    response_data = {
        "status": "ok",
        "dependencies": {
            "gemini_api_key": "available" if has_gemini_key else "missing"
        },
        "server_info": {
            "flask_version": Flask.__version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "client_ip": request.remote_addr
        },
        "message": "API is running" if has_gemini_key else "API is running but Gemini API key is missing"
    }
    logger.info(f"Health check: {response_data}")
    return jsonify(response_data)

@app.route('/api/test-custom', methods=['POST', 'OPTIONS'])
def test_custom():
    """
    Run mutation testing on custom Python code.
    Request JSON: {"code": "...", "custom_tests": "...", "generate_ai_tests": true}
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3004'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

    try:
        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"error": "Missing required parameter: code"}), 400

        session_id = str(uuid.uuid4())
        session_dir = os.path.join(TEMP_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        code_path = os.path.join(session_dir, "source.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(data["code"])

        mutation_engine = MutationEngine(session_dir)
        test_generator = TestGenerator(os.getenv("GEMINI_API_KEY"))
        test_executor = TestExecutor(session_dir)

        mutations = mutation_engine.generate_mutations(code_path)
        logger.info(f"Generated {len(mutations)} mutations for session {session_id}")

        tests = []
        if "custom_tests" in data and data["custom_tests"]:
            tests.append({"name": "Custom Test", "code": data["custom_tests"], "source": "custom"})

        generate_ai_tests = data.get("generate_ai_tests", True)
        if generate_ai_tests:
            for idx, mutation in enumerate(mutations):
                test_code = test_generator.generate_test(
                    data["code"],
                    mutation.get("mutated_full_code", data["code"]),
                    mutation.get("description", f"Mutation {idx}")
                )
                tests.append({"name": f"Generated Test {idx}", "code": test_code, "source": "ai", "target_mutation": idx})

        results = test_executor.run_tests(code_path, mutations, tests)
        results["session_id"] = session_id
        results["timestamp"] = time.time()

        sessions[session_id] = results
        return jsonify(results)

    except Exception as e:
        logger.exception(f"Error in test-custom: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-github', methods=['POST', 'OPTIONS'])
def test_github():
    """
    Run mutation testing on a GitHub repository.
    Request JSON: {"repo_url": "...", "target_file": "...", "custom_tests": "...", "generate_ai_tests": true}
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3004'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

    try:
        data = request.get_json()
        if not data or "repo_url" not in data:
            return jsonify({"error": "Missing required parameter: repo_url"}), 400

        session_id = str(uuid.uuid4())
        session_dir = os.path.join(TEMP_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        mutation_engine = MutationEngine(session_dir)
        test_generator = TestGenerator(os.getenv("GEMINI_API_KEY"))
        test_executor = TestExecutor(session_dir)

        repo_dir = mutation_engine.clone_github_repo(data["repo_url"])
        logger.info(f"Cloned repository to {repo_dir} for session {session_id}")

        python_files = ([os.path.join(repo_dir, data["target_file"])] 
                       if "target_file" in data and data["target_file"] 
                       else mutation_engine.find_python_files(repo_dir))
        
        if not python_files:
            return jsonify({"error": "No Python files found in repository"}), 400

        all_results = []
        for code_path in python_files[:5]:
            try:
                with open(code_path, "r", encoding="utf-8") as f:
                    code = f.read()

                mutations = mutation_engine.generate_mutations(code_path)
                logger.info(f"Generated {len(mutations)} mutations for file {code_path}")

                tests = []
                if "custom_tests" in data and data["custom_tests"]:
                    tests.append({"name": "Custom Test", "code": data["custom_tests"], "source": "custom"})

                generate_ai_tests = data.get("generate_ai_tests", True)
                if generate_ai_tests:
                    for idx, mutation in enumerate(mutations):
                        test_code = test_generator.generate_test(
                            code,
                            mutation.get("mutated_full_code", code),
                            mutation.get("description", f"Mutation {idx}")
                        )
                        tests.append({"name": f"Generated Test {idx}", "code": test_code, "source": "ai", "target_mutation": idx})

                file_results = test_executor.run_tests(code_path, mutations, tests)
                file_results["file_path"] = os.path.relpath(code_path, repo_dir)
                all_results.append(file_results)
            except Exception as e:
                logger.exception(f"Error processing file {code_path}: {str(e)}")
                all_results.append({"file_path": os.path.relpath(code_path, repo_dir), "error": str(e)})

        results = {
            "session_id": session_id,
            "timestamp": time.time(),
            "repo_url": data["repo_url"],
            "files_processed": len(all_results),
            "results": all_results
        }
        sessions[session_id] = results
        return jsonify(results)

    except Exception as e:
        logger.exception(f"Error in test-github: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/run-tests', methods=['GET', 'OPTIONS'])
def run_demo_test():
    """
    Run a demo test with sample code.
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3004'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

    sample_code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b
"""
    sample_request = {"code": sample_code, "generate_ai_tests": True}
    request._cached_json = (sample_request, {})
    return test_custom()

@app.route('/api/results/<session_id>', methods=['GET', 'OPTIONS'])
def get_results(session_id):
    """
    Get results from a previous test session.
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3004'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

    if session_id not in sessions:
        return jsonify({"error": f"Session {session_id} not found"}), 404
    return jsonify(sessions[session_id])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)