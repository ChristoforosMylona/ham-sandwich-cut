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
    source flask_backend/venv/bin/activate
elif [[ "$OS" == "CYGWIN"* || "$OS" == "MINGW"* || "$OS" == "MSYS"* ]]; then
    source flask_backend/venv/Scripts/activate
else
    echo "Unsupported OS"
    exit 1
fi

# Install Flask dependencies from requirements.txt
echo "Installing Flask dependencies..."
pip install -r flask_backend/ham_sandwich_cuts/requirements.txt

# Start Flask app in production mode
cd flask_backend/ham_sandwich_cuts || exit
export FLASK_APP=app.py  # Adjust if needed
export FLASK_ENV=production

# For Linux and Mac, use Gunicorn. For Windows, use Waitress.
if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    gunicorn -b 0.0.0.0:5000 app:app --workers 3 &  # Run Flask in production mode using Gunicorn
elif [[ "$OS" == "CYGWIN"* || "$OS" == "MINGW"* || "$OS" == "MSYS"* ]]; then
    # Run Flask with Waitress on Windows
    waitress-serve --listen=0.0.0.0:5000 app:app &  
fi
FLASK_PID=$!

# Start React app in production mode
cd ../../UI/visualising_ham_sandwich || exit
npm install  # Install React dependencies if not already installed
npm run build  # Build the React app for production

# For Linux/Mac, use Nginx to serve React on the desired port (5173)
if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    echo "Starting React app using Nginx on port 5173..."
    # Stop any running Nginx processes to prevent conflicts
    sudo nginx -s stop 2>/dev/null
    sudo nginx -c /etc/nginx/nginx.conf &  # Ensure Nginx is running with the correct config
    sudo nginx -g "daemon off;"  # Ensure Nginx keeps running
# For Windows, use a Python HTTP server to serve React on port 5173
elif [[ "$OS" == "CYGWIN"* || "$OS" == "MINGW"* || "$OS" == "MSYS"* ]]; then
    echo "Starting React app using local server (Windows) on port 5173..."
    python -m http.server 5173 --bind 0.0.0.0 &  # Simple HTTP server for serving React on Windows
fi
REACT_PID=$!

echo "Flask and React applications started successfully in production mode!"
echo "Flask is running at http://127.0.0.1:5000"
echo "React is running at http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both."

# Wait to keep the script running and detect Ctrl+C
wait
