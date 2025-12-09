#!/usr/bin/env python3
"""
Byte-Sized Business Boost - Auto-start Script
Automatically installs dependencies and starts the web server.
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is 3.6 or higher."""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Checking dependencies...")
    
    try:
        import flask
        print("✅ Flask is already installed!")
        return True
    except ImportError:
        print("📦 Flask not found. Installing dependencies...")
        
        try:
            # Try pip3 first, then pip
            pip_cmd = 'pip3' if sys.platform != 'win32' else 'pip'
            subprocess.check_call([pip_cmd, 'install', '-q', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies.")
            print("   Please run manually: pip install -r requirements.txt")
            return False
        except FileNotFoundError:
            print("❌ pip not found. Please install pip.")
            return False

def start_server():
    """Start the Flask development server."""
    print("\n" + "="*60)
    print("🌟 BYTE-SIZED BUSINESS BOOST")
    print("="*60)
    print("\n🚀 Starting web server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server\n")
    print("-"*60 + "\n")
    
    # Import and run the app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main function."""
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies if needed
    if not install_dependencies():
        sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for supporting local businesses!")
        sys.exit(0)

