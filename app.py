#!/usr/bin/env python3
"""
Flask Application for Diving Admin
Initializes the Flask app with SQLAlchemy database
"""

from flask import Flask
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

@app.route('/')
def home():
    return '''
    <html>
        <head><title>Diving Admin</title></head>
        <body>
            <h1>Welcome to Diving Admin</h1>
            <p>App is running on port 8000</p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)