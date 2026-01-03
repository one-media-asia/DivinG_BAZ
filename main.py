#!/usr/bin/env python3
"""
Diving Admin Desktop Application
Launches the Flask web app and opens it in the default browser.
"""

import sys
import os
import threading
import time
import webbrowser
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def open_browser():
    """Open the web app in browser after a short delay"""
    time.sleep(2)  # Wait for Flask to start
    webbrowser.open('http://127.0.0.1:5001')

def main():
    """Main entry point for the desktop application"""
    try:
        # Import the Flask app
        from app import app, db

        # Create database tables
        with app.app_context():
            db.create_all()

        # Start browser in a separate thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Run the Flask app
        print("Starting Diving Admin...")
        print("Opening browser at http://127.0.0.1:5001")
        app.run(host='127.0.0.1', port=5001, debug=False)

    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()