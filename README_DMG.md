# Diving Admin - macOS Application

Your Flask-based diving administration app has been successfully packaged as a macOS application!

## Files Created:
- `Diving Admin.app` - The macOS application bundle
- `Diving_Admin.dmg` - The distributable disk image file

## Installation:
1. Double-click `Diving_Admin.dmg` to mount the disk image
2. Drag `Diving Admin.app` to your Applications folder
3. Eject the disk image

## Usage:
- Double-click `Diving Admin.app` to launch the application
- The app will automatically start the Flask server and open your default web browser
- The web interface will be available at `http://127.0.0.1:5001`

## Features:
- Self-contained application with all dependencies included
- SQLite database for data persistence
- User authentication and role management
- Dive site management, diver profiles, equipment tracking, and certifications

## Notes:
- First run may take a moment to start as the database is initialized
- The application runs a local web server - no internet connection required
- Data is stored locally in the application's data directory

## Troubleshooting:
- If the app doesn't start, check that port 5001 is not in use by another application
- You can force quit the app from Activity Monitor if needed