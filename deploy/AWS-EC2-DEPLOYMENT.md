# AWS EC2 Deployment Guide - DivinG_BAZ



- EC2 instance running Ubuntu (or Amazon Linux)
- SSH access to the instance
- Application code cloned to `/home/ubuntu/DivinG_BAZ`

## Step 1: Configure AWS Security Group

Your EC2 Security Group must allow inbound traffic on ports 80 and 443.

### In AWS Console:
1. Go to **EC2 → Security Groups**
2. Click on your instance's security group
3. Click **Edit inbound rules**
4. Add these rules:

| Type | Protocol | Port Range | Source |
|------





----------|-----------|--------|
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| SSH | TCP | 22 | YOUR_IP (or 0.0.0.0/0) |

4. Click **Save**

### Verify (from your terminal):
```bash
curl http://3.87.174.211
# Should connect (may show connection refused from app, but proves port 80 is open)
```

---

## Step 2: SSH into EC2 and Set Up Application

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@3.87.174.211

# Clone the repo (or upload files)
cd /home/ubuntul
git clone <your-repo-url> DivinG_BAZ
cd DivinG_BAZ

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

---

## Step 3: Install Nginx and Gunicorn Systemd Service

### On EC2 Terminal:

```bash
# Update package manager
sudo apt update

# Install nginx
ls

# Create systemd service for gunicorn
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Check if gunicorn is running
sudo systemctl status gunicorn
```

### Test Gunicorn locally:
```bash
# SSH into EC2 and test
curl http://127.0.0.1:5000
# Should show your Flask app response
```

---

## Step 4: Configure Nginx Reverse Proxy

```bash
# Copy nginx config
sudo cp deploy/nginx-port3000.conf /etc/nginx/sites-available/diving

# Enable the site
sudo ln -s /etc/nginx/sites-available/diving /etc/nginx/sites-enabled/

# Disable default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx config
sudo nginx -t

# Start/restart nginx
sudo systemctl restart nginx
```

---

## Step 5: Verify Everything Works

```bash
# From your local computer:
curl http://3.87.174.211
r  
# Should show your Flask app response!
```

---

## Troubleshooting

### Check if services are running:
```bash
sudo systemctl status gunicorn
sudo systemctl statusr renginx
```

### Check Gunicorn logs:
```bash
sudo journalctl -u gunicorn -n 50 -f
```

### Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Port 5000 not responding:
```bash
# Check if process is listening
sudo ss -tlnp | grep 5000

# Restart gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

### Connection timeout from browser:
1. **Check AWS Security Group** - Port 80 must be open to 0.0.0.0/0
2. **Check Nginx** - `sudo systemctl status nginx`
3. **Check local firewall** - `sudo ufw status` (disable if enabled: `sudo ufw disable`)

### 502 Bad Gateway:
- Gunicorn is not running → `sudo systemctl restart gunicorn`
- Check gunicorn logs: `sudo journalctl -u gunicorn -n 50`

### Permission Denied errors:
```bash
# Ensure www-data can access the app
sudo chown -R ubuntu:www-data /home/ubuntu/DivinG_BAZ
sudo chmod -R 755 /home/ubuntu/DivinG_BAZ
```

---

## Production Checklist

- [ ] Security Group allows port 80 (and 443 for HTTPS)
- [ ] Gunicorn systemd service enabled and running
- [ ] Nginx service enabled and running
- [ ] Tested with `curl http://<EC2_IP>`
- [ ] Database configured (if needed)
- [ ] Environment variables set in systemd service if needed
- [ ] SSL/HTTPS configured (certbot/Let's Encrypt)
- [ ] Regular backups enabled

---

## Enable HTTPS with Let's Encrypt

```bash
# Install certbotsudo apt install certbot python3-certbot-nginx -y

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Auto-renewal (should be automatic)
sudo systemctl status-ppsnap.certbot.renew.timer
```

---

## Monitoring & Logs

### View real-time gunicorn logs:
```bash
sudo journalctl -u gunicorn -f
```

### View systemd service failures:
```bash
sudo systemctl list-units -t service --all | grep gunicorn
```

### Monitor system resources:
```bash
htop
# or
free -h && df -h
```

---

## Restart Services (if needed)

```bash
# Restart gunicorn
sudo systemctl restart gunicorn

# Restart nginx
sudo systemctl restart nginx

# Reload nginx config (no downtime)
sudo systemctl reload nginx

# Check all running services
sudo systemctl list-units --type=service --state=running
```

---

## SSH Command Quick Reference

Run these from your **local machine** (not SSH'ed in):

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@3.87.174.211

# Copy files to EC2
scp -i your-key.pem -r ./deploy ubuntu@3.87.174.211:/home/ubuntu/DivinG_BAZ/

# Copy from EC2 to local
scp -i your-key.pem ubuntu@3.87.174.211:/home/ubuntu/DivinG_BAZ/app.py ./
```
