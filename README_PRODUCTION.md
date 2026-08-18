# SANTINEL Production Deployment Guide

## Quick Start

### Prerequisites
- Ubuntu 20.04 LTS or similar Linux server
- Docker (recommended) or native Python 3.10+
- PostgreSQL 14+
- Node.js 18+
- SSL certificate (Let's Encrypt)

### 1. Clone Repository

```bash
git clone https://github.com/santinel/santinel.git
cd santinel
```

### 2. Set Up Environment

```bash
# Create production environment file
cp .env.production.example .env.production

# Edit with your values
nano .env.production

# Set strict permissions
chmod 600 .env.production
```

### 3. Database Setup

```bash
# Create database
createdb santinel_prod

# Run migrations
psql -U postgres -d santinel_prod -f schema.sql

# Verify
psql -U postgres -d santinel_prod -c "SELECT 1"
```

### 4. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python migrate_data.py

# Test backend
python backend/fastapi_backend.py
# Should show: Uvicorn running on http://0.0.0.0:8002
```

### 5. Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Build for production
npm run build

# Output goes to dist/
ls dist/
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx

sudo certbot certonly --standalone -d santinel.io -d www.santinel.io

# Certificate at: /etc/letsencrypt/live/santinel.io/fullchain.pem
# Private key at: /etc/letsencrypt/live/santinel.io/privkey.pem

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 7. Nginx Configuration

```bash
# Create config
sudo nano /etc/nginx/sites-available/santinel

# Paste this:

server {
    listen 80;
    listen [::]:80;
    server_name santinel.io www.santinel.io;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name santinel.io www.santinel.io;
    
    ssl_certificate /etc/letsencrypt/live/santinel.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/santinel.io/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Frontend
    location / {
        root /var/www/santinel/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api/ {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/santinel /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### 8. Systemd Service (Backend)

```bash
# Create service file
sudo nano /etc/systemd/system/santinel-backend.service

# Paste:

[Unit]
Description=SANTINEL Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=santinel
WorkingDirectory=/home/santinel/santinel
Environment="PATH=/home/santinel/santinel/venv/bin"
ExecStart=/home/santinel/santinel/venv/bin/python backend/fastapi_backend.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable & start
sudo systemctl daemon-reload
sudo systemctl enable santinel-backend
sudo systemctl start santinel-backend

# Check status
sudo systemctl status santinel-backend
```

### 9. Monitoring Setup

```bash
# Install Sentry CLI
pip install sentry-cli

# Configure Sentry DSN in .env.production
# Get from: https://sentry.io/

# Test error logging
curl http://localhost:8002/api/v1/health
```

### 10. Backup Script

```bash
# Create backup script
nano /home/santinel/backup-santinel.sh

# Paste:

#!/bin/bash
BACKUP_DIR="/home/santinel/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/santinel_prod_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -U postgres -d santinel_prod > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"

# Make executable
chmod +x /home/santinel/backup-santinel.sh

# Add to crontab (daily at 2 AM)
# crontab -e
# 0 2 * * * /home/santinel/backup-santinel.sh
```

## Verification

### Health Checks

```bash
# Backend
curl https://santinel.io/api/v1/health

# Should return:
# {
#   "status": "SANTINEL Backend v3.0-PHASE4...",
#   "database": "Connected",
#   "cache": "Enabled",
#   "auth": "JWT enabled"
# }

# Frontend
curl https://santinel.io/

# Should return HTML (index.html)
```

### Database

```bash
# Connect to database
psql -U postgres -d santinel_prod

# Check tables
\dt

# Check sessions
SELECT COUNT(*) FROM sessions;
```

### Logs

```bash
# Backend logs
sudo journalctl -u santinel-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Backend not responding
```bash
sudo systemctl restart santinel-backend
sudo journalctl -u santinel-backend -n 50
```

### Database connection error
```bash
pg_isready
psql -U postgres -d santinel_prod -c "SELECT 1"
```

### SSL certificate expired
```bash
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

### High memory usage
```bash
free -h
ps aux --sort=-%mem | head -10
```

## Performance Tuning

### PostgreSQL
```bash
# Edit /etc/postgresql/14/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 64MB
```

### Nginx
```bash
# Increase worker connections in /etc/nginx/nginx.conf
worker_connections 2048;
```

### Python
```bash
# Use gunicorn instead of uvicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8002 backend.fastapi_backend:app
```

## Security Hardening

```bash
# Fail2ban (rate limiting)
sudo apt-get install fail2ban

# UFW (firewall)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Regular updates
sudo apt-get update
sudo apt-get upgrade
```

## Support

For issues, see:
- Backend logs: `journalctl -u santinel-backend`
- Error tracking: Sentry dashboard
- Database: `psql -U postgres -d santinel_prod`

---

**Deployment completed:** August 18, 2026