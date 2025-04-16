#!/bin/bash

# Detect OS
OS=$(uname)

# Function to clean up processes on exit
cleanup() {
    echo "Stopping Flask and React servers..."
    kill $FLASK_PID $REACT_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C (SIGINT) to cleanup before exiting
trap cleanup SIGINT

# Set virtual environment path
VENV_PATH="venv"

# Try to find a working Python 3 executable
if python3 -c "import sys; exit(0) if sys.version_info >= (3,0) else exit(1)" 2>/dev/null; then
    PYTHON_CMD=python3
elif python -c "import sys; exit(0) if sys.version_info >= (3,0) else exit(1)" 2>/dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Could not find a working Python 3 installation."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -f "$VENV_PATH/bin/activate" && ! -f "$VENV_PATH/Scripts/activate" ]]; then
    echo "Creating virtual environment at $VENV_PATH using $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_PATH" || {
        echo "❌ Failed to create virtual environment."
        exit 1
    }
fi

# Activate virtual environment
if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    source "$VENV_PATH/bin/activate"
elif [[ "$OS" == "CYGWIN"* || "$OS" == "MINGW"* || "$OS" == "MSYS"* ]]; then
    source "$VENV_PATH/Scripts/activate"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

# Install Python dependencies
REQ_FILE="flask_backend/ham_sandwich_cuts/requirements.txt"
if [[ -f "$REQ_FILE" ]]; then
    echo "Installing Python dependencies from $REQ_FILE..."
    pip install -r "$REQ_FILE"
else
    echo "⚠️  requirements.txt not found at $REQ_FILE — skipping install."
fi

# Start Flask app and capture logs
cd flask_backend/ham_sandwich_cuts || exit
export FLASK_APP=app.py 
export FLASK_ENV=development
flask run 2>&1 | tee flask_output.log &
FLASK_PID=$!

# Start React app
cd ../../UI/visualising_ham_sandwich || exit
npm install  # Ensure dependencies are installed
npm run dev &
REACT_PID=$!

echo ""
echo "🚀 Flask and React applications started successfully!"
echo "📦 Flask: http://127.0.0.1:5000"
echo "🖼️ React: http://127.0.0.1:5173"
echo "🛑 Press Ctrl+C to stop both."

# Wait to keep the script running and detect Ctrl+C
wait
