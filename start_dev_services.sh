#!/bin/bash

# Detect OS
OS=$(uname)

# Function to clean up processes on exit
cleanup() {
    echo "Stopping Flask and React servers..."
    kill $FLASK_PID $REACT_PID
    exit 0
}

# Trap Ctrl+C (SIGINT) to cleanup before exiting
trap cleanup SIGINT

# Activate virtual environment
if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    source venv/bin/activate
elif [[ "$OS" == "CYGWIN"* || "$OS" == "MINGW"* || "$OS" == "MSYS"* ]]; then
    source venv/Scripts/activate
else
    echo "Unsupported OS"
    exit 1
fi

# Start Flask app and capture logs
cd flask_backend/ham_sandwich_cuts || exit
export FLASK_APP=app.py 
export FLASK_ENV=development
flask run 2>&1 | tee flask_output.log &  # Capture and display output
FLASK_PID=$!

# Start React app
cd ../../UI/visualising_ham_sandwich || exit
npm run dev & 
REACT_PID=$!

echo "Flask and React applications started successfully!"
echo "Press Ctrl+C to stop both."

# Wait to keep the script running and detect Ctrl+C
wait
