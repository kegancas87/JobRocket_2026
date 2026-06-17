# 🚀 Job Rocket Deployment Instructions

## Quick Deployment Steps:

### 1. Upload Files to cPanel
- Upload all files from this folder to your `public_html` directory
- Ensure file structure matches the guide

### 2. Update Configuration
- Edit `api/.env` with your actual server details
- Generate new JWT_SECRET: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Update MongoDB connection string
- Add production Payfast credentials

### 3. Set Permissions
```bash
chmod 755 api/
chmod 644 api/*.py
chmod 600 api/.env
chmod 755 uploads/
chmod 777 uploads/cvs/
chmod 777 uploads/images/
```

### 4. Install Python Dependencies
In cPanel Terminal or SSH:
```bash
cd public_html/api
pip install -r requirements.txt
```

### 5. Setup Database
- Import existing MongoDB data (see deployment_guide.md)
- Or run fresh installation

### 6. Test Deployment
- Visit: https://jobrocket.co.za
- Test API: https://jobrocket.co.za/api/packages
- Check all functionality

## Need Help?
See `deployment_guide.md` for detailed instructions.
