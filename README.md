# Bug Slayer AI: Mutation-Guided AI Test Generator

An AI-powered tool that automatically finds hidden bugs in your code by generating smart test cases based on mutation testing.

## Project Overview

Bug Slayer AI uses mutation testing principles combined with AI to automatically generate test cases that can catch potential bugs in your code:

1. **Mutation Testing**: We intentionally introduce bugs (mutations) into your code
2. **AI Test Generation**: AI automatically creates test cases to catch these mutations
3. **Results Dashboard**: See which mutants were "killed" vs "survived"

## Demo Features

- Simple calculator function with mutated versions
- AI-generated test cases to catch the mutations
- Interactive web dashboard showing test results

## Quick Start

### Setup

1. Clone this repository
```
git clone <repository-url>
cd bug-slayer-ai
```

2. Set up a virtual environment
```
# On Windows
python -m venv myenv
myenv\Scripts\activate

# On macOS/Linux
python3 -m venv myenv
source myenv/bin/activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Set up your OpenAI API key (optional for demo)
```
# On Windows
set OPENAI_API_KEY=your-api-key

# On macOS/Linux
export OPENAI_API_KEY=your-api-key
```

### Running the Application

1. Start the Flask server
```
python app.py
```

2. Open your browser and go to http://127.0.0.1:5000

3. Click "Run Test Generation" to see the AI in action!

## How It Works

1. We have a simple calculator function in `bugslayer.py`
2. When you click "Run Test Generation":
   - We create mutated versions of the code (e.g., change + to -)
   - AI generates test cases to try to catch these mutations
   - Results show which mutations were caught vs. missed

## Future Development

This is an MVP (Minimum Viable Product) for demonstration purposes. Future enhancements could include:

- Integration with real codebases
- Support for multiple programming languages
- More sophisticated mutation strategies
- Advanced AI prompt engineering
- CI/CD integration

## Tech Stack

- Python
- Flask
- OpenAI API
- Bootstrap
- JavaScript

## Contributing

This is a hackathon project. Feel free to fork and extend!