@echo off
REM Byte-Sized Business Boost - Auto-start Script for Windows

echo 🌟 Starting Byte-Sized Business Boost...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.6 or higher.
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 Flask not found. Installing dependencies...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies. Please run: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed!
    echo.
)

REM Start the Flask application
echo 🚀 Starting web server...
echo 📍 Open your browser to: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

python app.py

pause

