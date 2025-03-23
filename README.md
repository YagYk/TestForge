# TestForge - Mutation-Guided AI Test Generator

TestForge is a comprehensive testing platform that leverages mutation testing and AI to help developers create more robust test suites. It automatically generates mutations in your code and uses AI to create tests that can detect these mutations.

## Features

- **Mutation Testing**: Automatically generates mutations in your code to simulate bugs
- **AI-Powered Test Generation**: Uses Google Gemini API to create intelligent tests that can detect mutations
- **GitHub Integration**: Test code directly from GitHub repositories
- **Intuitive UI**: Modern web interface for visualizing test results and mutation coverage
- **Session Management**: Save and retrieve test results with unique session IDs

## Project Structure

```
TestForge/
├── Frontend/              # React frontend application
│   ├── src/               # Source code
│   ├── public/            # Public assets
│   └── build/             # Production build
├── app.py                 # Flask backend application
├── mutation_engine.py     # Mutation generation engine
├── test_generator.py      # AI test generation using Gemini API
├── test_executor.py       # Test execution and result collection
├── debug_api.py           # API debugging tool
├── server_manager.py      # Server management script
├── apply_spline_fix.bat   # Script to fix common issues (Windows)
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Quick Start (Windows)

For Windows users, we provide a quick start script that handles both the backend and frontend setup:

```bash
# Just double-click on this file
apply_spline_fix.bat
```

This script:
1. Installs required dependencies
2. Fixes common issues with 3D components
3. Starts both the backend and frontend servers

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/username/TestForge.git
   cd TestForge
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Run the backend server:
   ```bash
   python app.py
   ```

Alternatively, use the server manager to start the backend:
```bash
python server_manager.py start
```

### Frontend Setup

1. Navigate to the Frontend directory:
   ```bash
   cd Frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. For production, build the frontend:
   ```bash
   npm run build
   ```

## Using the Application

1. **Home Page**: Visit the home page to access the testing form.
2. **Custom Code Testing**: Enter your Python code and optionally provide custom tests.
3. **GitHub Repository Testing**: Provide a GitHub repository URL and optionally specify a target file.
4. **Test Results**: View detailed results including mutation detection rates, test coverage, and mutation details.

## API Documentation

The backend provides the following API endpoints:

- `GET /api/health`: Check API health and dependencies
- `POST /api/test-custom`: Test custom Python code
- `POST /api/test-github`: Test code from a GitHub repository
- `GET /api/run-tests`: Run a demo test
- `GET /api/results/<session_id>`: Retrieve results for a specific session

## Troubleshooting

### Automated Fixes

We provide several scripts to automatically fix common issues:

1. **Server Management**:
   ```bash
   # Start both backend and frontend
   python server_manager.py all
   
   # Check server status
   python server_manager.py check
   
   # Restart just the backend
   python server_manager.py restart
   ```

2. **3D Component/Chunk Loading Errors**:
   ```bash
   # For Windows users
   Frontend/fix_spline_errors.bat
   
   # For all platforms
   cd Frontend
   node fix_chunk_error.js
   ```

### Backend Issues

1. **API Connection Errors**:
   - Ensure the Flask server is running
   - Check for CORS issues in the browser console
   - Run `python debug_api.py` to test API functionality
   - Try using the improved API service that tries multiple endpoints

2. **Gemini API Issues**:
   - Verify your API key is correct in the `.env` file
   - Check internet connectivity
   - If issues persist, the system will fall back to basic test templates

3. **Mutation Testing Failures**:
   - Ensure your Python code is syntactically correct
   - Check for library dependencies required by your code

### Frontend Issues

1. **Chunk Loading Errors / 3D Component Issues**:
   - Use our automatic fix scripts (see above)
   - If errors persist, you can disable the 3D components by creating a `.env` file in the Frontend directory with:
     ```
     REACT_APP_DISABLE_SPLINE=true
     ```

2. **Build Errors**:
   - Ensure all dependencies are installed with `npm install`
   - Check for JavaScript errors in the browser console
   - Try clearing browser cache and reloading
   - Use the config-overrides.js file to customize webpack configuration

3. **API Connection**:
   - Check the API status indicator in the UI
   - Verify the API URL configuration in `config.js`
   - Try the retry button in the Test Form component
   - Increase request timeout if needed

## Development and Extension

To extend TestForge with new features:

1. **Custom Mutation Operators**: Add new mutation operators in `mutation_engine.py`
2. **Test Generation Strategies**: Enhance test templates in `test_generator.py`
3. **Frontend Components**: Add or modify React components in the Frontend directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name (@yourgithub)

## Acknowledgements

- Google Gemini API for AI-powered test generation
- React and Material-UI for the frontend interface
- Flask for the backend API