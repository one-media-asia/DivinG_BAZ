#!/bin/bash
# Script to run gunicorn on port 3000

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# Run gunicorn
cd "$PROJECT_DIR"
echo "Starting gunicorn on port 5000..."
## Prefer an activated venv's gunicorn, fall back to module run
if command -v gunicorn >/dev/null 2>&1; then
    exec gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 90 app:app
else
    exec python3 -m gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 90 app:app
fi
