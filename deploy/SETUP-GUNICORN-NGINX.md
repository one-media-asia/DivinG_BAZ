# DivinG_BAZ - Gunicorn & Nginx Setup Guide

## Overview
This guide covers setting up **Gunicorn** (WSGI application server) and **Nginx** (reverse proxy) for the DivinG_BAZ Flask application.

- **Gunicorn** runs on port 3000
- **Nginx** listens on port 80 and reverse proxies to port 3000

## Installation Status

✅ **Gunicorn**: Already installed (added to requirements.txt)
✅ **Nginx**: Already installed via Homebrew

## Quick Start

### 1. 


From the project root directory:

```bash





```

Or use the provided script:

```bash
cd deploy/



bash run-gunicorn.sh
```

### 2. Configure & Start Nginx

Copy the nginx configuration:

```bash
sudo cp deploy/nginx-port3000.conf /usr/local/etc/nginx/servers/diving.conf
```

Start nginx:

```bas```

Or restart if already running:

```bash
sudo brew services restart nginx
```

### 3. Test the Setup

Visit http://localhost in your browser. Requests should:
- Hit nginx on port 80
- Get proxied to gunicorn on port 3000
- Return your Flask app response

## Configuration Files

- **nginx-port3000.conf**: Nginx reverse proxy configuration (port 80 → 3000)
- **run-gunicorn.sh**: Bash script to start gunicorn

## Nginx Management

Check nginx status:
```bash
sudo brew services list | grep nginx
```

Stop nginx:
```bash
sudo brew services stop nginx
```

View nginx error logs:
```bash
tail -f /usr/local/var/log/nginx/error.log
```

View nginx access logs:
```bash
tail -f /usr/local/var/log/nginx/access.log
```

## Running Gunicorn Continuously

### Option 1: Background Process

```bash
nohup gunicorn --workers 3 --bind 127.0.0.1:3000 app:app > gunicorn.log 2>&1 &
```

### Option 2: Using launchd (macOS)

Create `/Library/LaunchDaemons/com.divingbaz.gunicorn.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.divingbaz.gunicorn</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/OneMedia/GHOST/DivinG_BAZ/.venv/bin/gunicorn</string>
        <string>--workers</string>
        <string>3</string>
        <string>--bind</string>
        <string>127.0.0.1:3000</string>
        <string>app:app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/OneMedia/GHOST/DivinG_BAZ</string>
    <key>StandardOutPath</key>
    <string>/var/log/gunicorn.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/gunicorn-error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then load it:
```bash
sudo launchctl load /Library/LaunchDaemons/com.divingbaz.gunicorn.plist
```

### Option 3: Using screen/tmux

```bash
screen -S gunicorn -d -m bash -c 'gunicorn --workers 3 --bind 127.0.0.1:3000 app:app'
```

## Troubleshooting

**Port 3000 already in use:**
```bash
lsof -i :3000
# Kill the process: kill -9 <PID>
```

**Port 80 requires sudo:**
If you want to run gunicorn on port 80 instead of 3000, you'd need to run as root, which isn't recommended. Keep it on 3000 and use nginx as the reverse proxy (current setup).

**Nginx not picking up config:**
Verify the config syntax:
```bash
sudo nginx -t
```

## Performance Tuning

Adjust the number of workers based on CPU cores:
```bash
gunicorn --workers $(nproc) --bind 127.0.0.1:3000 app:app
```

For 4 CPU cores, try: `--workers 9` (formula: 2 * cores + 1)

## Security Notes

- Nginx is the public-facing server (handles port 80)
-  (local loopback) for security
- Add firewall rules to only allow traffic to port 80/443
