# Job Rocket Deployment Guide for cPanel Hosting

## 🚀 Deployment Steps for jobrocket.co.za

### 1. File Structure on cPanel Server
```
public_html/
├── index.html (React build)
├── static/ (React assets)
├── api/ (FastAPI backend)
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── uploads/ (user uploaded files)
│   ├── cvs/
│   └── images/
└── .htaccess (URL rewriting)
```

### 2. Environment Configuration

**Backend (.env file):**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=jobrocket
JWT_SECRET=your-production-secret-key
BASE_URL=https://jobrocket.co.za
CORS_ORIGINS=https://jobrocket.co.za,https://www.jobrocket.co.za
PAYFAST_MERCHANT_ID=your-production-merchant-id
PAYFAST_MERCHANT_KEY=your-production-merchant-key
PAYFAST_PASSPHRASE=your-production-passphrase
PAYFAST_SANDBOX=False
UPLOAD_PATH=/home/yourusername/public_html/uploads
```

**Frontend (built into static files):**
- REACT_APP_BACKEND_URL=https://jobrocket.co.za
- All API calls will go to jobrocket.co.za/api/*

### 3. Required Updates Before Deployment

1. **Update MongoDB Connection:**
   - Install MongoDB on your server
   - Update MONGO_URL with your server's MongoDB connection string
   - Import existing data (covered in Phase 2)

2. **Update File Paths:**
   - Change UPLOAD_PATH to your actual cPanel path
   - Usually: `/home/yourusername/public_html/uploads`

3. **Production Security:**
   - Generate new JWT_SECRET (use: `python -c "import secrets; print(secrets.token_urlsafe(32))")`)
   - Update Payfast credentials to production values
   - Set PAYFAST_SANDBOX=False

### 4. Build Commands

**Frontend Build:**
```bash
cd frontend
npm run build
# Copy build files to public_html/
```

**Backend Deployment:**
```bash
cd backend
pip install -r requirements.txt
# Copy files to public_html/api/
```

### 5. .htaccess Configuration

Create `/public_html/.htaccess`:
```apache
RewriteEngine On

# API routes to Python backend
RewriteRule ^api/(.*)$ /api/server.py/$1 [L,QSA]

# React Router - redirect all non-API routes to index.html
RewriteCond %{REQUEST_URI} !^/api/
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Enable CORS
Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization"
```

### 6. MongoDB Setup on cPanel

**If MongoDB is not available on shared hosting:**
- Consider upgrading to VPS
- Or use MongoDB Atlas (cloud database)
- Update MONGO_URL to Atlas connection string

### 7. File Permissions

Set appropriate permissions:
```bash
chmod 755 public_html/api/
chmod 644 public_html/api/*.py
chmod 600 public_html/api/.env
chmod 755 public_html/uploads/
```

### 8. Testing Checklist

After deployment:
- [ ] Visit https://jobrocket.co.za (should load React app)
- [ ] Test API: https://jobrocket.co.za/api/packages
- [ ] Test authentication (login/register)
- [ ] Test file uploads
- [ ] Test job posting
- [ ] Test CV search
- [ ] Test payment integration

### 9. Common Issues & Solutions

**Issue: 500 Error on API calls**
- Check Python path in cPanel
- Verify requirements.txt dependencies installed
- Check .env file permissions and values

**Issue: CORS Errors**
- Verify .htaccess CORS headers
- Check CORS_ORIGINS in .env

**Issue: File Upload Errors**
- Verify UPLOAD_PATH exists and is writable
- Check file permissions on uploads directory

**Issue: MongoDB Connection**
- Verify MongoDB is running
- Check MONGO_URL connection string
- Ensure database name matches

### 10. Post-Deployment

After successful deployment:
- Update DNS if needed
- Set up SSL certificate
- Configure backup strategy
- Monitor logs for errors
- Test all functionality thoroughly

---

**Next Phase:** Database migration from current MongoDB to your server's MongoDB (or MySQL conversion)