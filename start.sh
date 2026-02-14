#!/bin/bash
# Chrysalis Connect - Auto-start Script

echo "🌟 Starting Chrysalis Connect..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.6 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Determine pip command
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Flask not found. Installing dependencies..."
    $PIP_CMD install -q -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please run: pip install -r requirements.txt"
        exit 1
    fi
    echo "✅ Dependencies installed!"
    echo ""
fi

# Start the Flask application
echo "🚀 Starting web server..."
echo "📍 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python3 app.py

