# JobRocket Production Deployment Guide

## Server Requirements

- **OS**: Ubuntu 20.04+ or similar Linux
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 20GB+ SSD
- **Software**: 
  - Python 3.9+
  - Node.js 18+
  - MongoDB 6.0+
  - Nginx
  - PM2 or systemd for process management

---

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx mongodb

# Install PM2 globally
sudo npm install -g pm2

# Create application directory
sudo mkdir -p /var/www/jobrocket
sudo chown $USER:$USER /var/www/jobrocket
```

---

## Step 2: MongoDB Setup

```bash
# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Secure MongoDB (run mongo shell)
mongosh

# In mongo shell:
use admin
db.createUser({
  user: "jobrocketadmin",
  pwd: "YOUR_SECURE_PASSWORD",
  roles: ["root"]
})
exit
```

Update `/etc/mongod.conf` to enable authentication:
```yaml
security:
  authorization: enabled
```

Then restart: `sudo systemctl restart mongod`

---

## Step 3: Upload Application Files

Upload the `/app/backend` and `/app/frontend` directories to `/var/www/jobrocket/`

---

## Step 4: Backend Setup

```bash
cd /var/www/jobrocket/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads/{cvs,profile_pictures,documents,images}
chmod -R 755 uploads
```

### Update backend/.env for production:
- Update `MONGO_URL` if you added authentication:
  ```
  MONGO_URL=mongodb://jobrocketadmin:YOUR_SECURE_PASSWORD@localhost:27017
  ```

---

## Step 5: Frontend Build

```bash
cd /var/www/jobrocket/frontend

# Install dependencies
npm install

# Build for production
npm run build

# The build output will be in /var/www/jobrocket/frontend/build/
```

---

## Step 6: Nginx Configuration

Create `/etc/nginx/sites-available/jobrocket`:

```nginx
server {
    listen 80;
    server_name jobrocket.co.za www.jobrocket.co.za;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name jobrocket.co.za www.jobrocket.co.za;

    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/jobrocket.co.za/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jobrocket.co.za/privkey.pem;

    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    # Frontend - Serve React build
    root /var/www/jobrocket/frontend/build;
    index index.html;

    # Frontend routes (React Router)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy to Backend
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        client_max_body_size 50M;
    }

    # Uploads - Static file serving
    location /api/uploads {
        alias /var/www/jobrocket/uploads;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/jobrocket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 7: SSL Certificate (Let's Encrypt)

```bash
sudo certbot --nginx -d jobrocket.co.za -d www.jobrocket.co.za
```

---

## Step 8: Start Backend with PM2

```bash
cd /var/www/jobrocket/backend
source venv/bin/activate

# Start with PM2
pm2 start "uvicorn server:app --host 0.0.0.0 --port 8001" --name jobrocket-api

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

---

## Step 9: Setup Billing Scheduler (Cron Job)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 6 AM):
0 6 * * * cd /var/www/jobrocket/backend && /var/www/jobrocket/backend/venv/bin/python -m tasks.billing_scheduler >> /var/log/jobrocket-billing.log 2>&1
```

---

## Step 10: Seed Initial Data

```bash
cd /var/www/jobrocket/backend
source venv/bin/activate
python init_db.py
```

---

## Security Checklist

- [ ] MongoDB authentication enabled
- [ ] Firewall configured (UFW):
  ```bash
  sudo ufw allow 22    # SSH
  sudo ufw allow 80    # HTTP
  sudo ufw allow 443   # HTTPS
  sudo ufw enable
  ```
- [ ] SSL certificate installed
- [ ] `.env` files have correct permissions: `chmod 600 .env`
- [ ] Uploads directory permissions: `chmod 755 uploads`
- [ ] Regular backups configured for MongoDB

---

## Monitoring

```bash
# Check backend status
pm2 status

# View backend logs
pm2 logs jobrocket-api

# Monitor resources
pm2 monit
```

---

## Troubleshooting

### Backend not starting
```bash
cd /var/www/jobrocket/backend
source venv/bin/activate
python -c "from server import app; print('OK')"
```

### MongoDB connection issues
```bash
mongosh --eval "db.adminCommand('ping')"
```

### Nginx issues
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

---

## Important Notes

1. **NEVER commit `.env` files to git**
2. **Backup your database regularly**
3. **Keep your JWT_SECRET safe - changing it logs out all users**
4. **PayFast is in PRODUCTION mode - real payments will be processed**
5. **Test thoroughly before going live**

---

## Support Contacts

- MongoDB: https://www.mongodb.com/docs/
- Nginx: https://nginx.org/en/docs/
- PayFast: https://developers.payfast.co.za/
- Let's Encrypt: https://certbot.eff.org/
