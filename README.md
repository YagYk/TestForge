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






- Your Name (@yourgithub)

## Acknowledgements

- Google Gemini API for AI-powered test generation
- React and Material-UI for the frontend interface
- Flask for the backend API
