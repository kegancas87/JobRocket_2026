#!/bin/bash

# Job Rocket Production Deployment Script for jobrocket.co.za

echo "🚀 Job Rocket Production Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="jobrocket.co.za"
PROJECT_NAME="jobrocket"

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo -e "   Domain: ${GREEN}$DOMAIN${NC}"
echo -e "   Project: ${GREEN}$PROJECT_NAME${NC}"
echo ""

# Step 1: Build Frontend
echo -e "${YELLOW}📦 Step 1: Building React Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Building production React app..."
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend build successful!${NC}"
else
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi

cd ..

# Step 2: Prepare Backend
echo -e "${YELLOW}📦 Step 2: Preparing Backend...${NC}"

# Create deployment directory
mkdir -p deployment/$PROJECT_NAME
mkdir -p deployment/$PROJECT_NAME/api
mkdir -p deployment/$PROJECT_NAME/uploads
mkdir -p deployment/$PROJECT_NAME/uploads/cvs
mkdir -p deployment/$PROJECT_NAME/uploads/images

# Copy frontend build
echo "Copying frontend build files..."
cp -r frontend/build/* deployment/$PROJECT_NAME/

# Copy backend files
echo "Copying backend files..."
cp backend/server.py deployment/$PROJECT_NAME/api/
cp backend/requirements.txt deployment/$PROJECT_NAME/api/
cp backend/.env deployment/$PROJECT_NAME/api/.env.example

# Copy configuration files
cp .htaccess deployment/$PROJECT_NAME/
cp deployment_guide.md deployment/$PROJECT_NAME/

echo -e "${GREEN}✅ Files copied successfully!${NC}"

# Step 3: Create production .env template
echo -e "${YELLOW}📝 Step 3: Creating production environment template...${NC}"

cat > deployment/$PROJECT_NAME/api/.env << EOL
# MongoDB Configuration (UPDATE FOR YOUR SERVER)
MONGO_URL=mongodb://localhost:27017
DB_NAME=jobrocket

# Security (GENERATE NEW SECRET)
JWT_SECRET=REPLACE_WITH_NEW_SECRET

# Production Configuration
BASE_URL=https://$DOMAIN
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Payfast Production Configuration (UPDATE WITH REAL CREDENTIALS)
PAYFAST_MERCHANT_ID=your_production_merchant_id
PAYFAST_MERCHANT_KEY=your_production_merchant_key
PAYFAST_PASSPHRASE=your_production_passphrase
PAYFAST_SANDBOX=False

# File Upload Configuration (UPDATE PATH)
UPLOAD_PATH=/home/yourusername/public_html/uploads
MAX_FILE_SIZE=10485760
EOL

# Step 4: Create deployment instructions
echo -e "${YELLOW}📋 Step 4: Creating deployment instructions...${NC}"

cat > deployment/$PROJECT_NAME/DEPLOYMENT_INSTRUCTIONS.md << 'EOL'
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
EOL

# Step 5: Create database migration script
echo -e "${YELLOW}💾 Step 5: Creating database migration helper...${NC}"

cat > deployment/$PROJECT_NAME/migrate_database.py << 'EOL'
#!/usr/bin/env python3
"""
Database Migration Helper for Job Rocket
Run this script to export/import MongoDB data
"""

import os
import sys
from pymongo import MongoClient
import json
from datetime import datetime

def export_current_db():
    """Export current database to JSON files"""
    print("🔄 Exporting current database...")
    
    # Connect to current database
    client = MongoClient('mongodb://localhost:27017')
    db = client['job_portal']  # Current database name
    
    collections = ['users', 'jobs', 'user_packages', 'payments', 'company_members', 'applications']
    
    export_dir = 'db_export'
    os.makedirs(export_dir, exist_ok=True)
    
    for collection_name in collections:
        collection = db[collection_name]
        documents = list(collection.find())
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        filename = f"{export_dir}/{collection_name}.json"
        with open(filename, 'w') as f:
            json.dump(documents, f, default=str, indent=2)
        
        print(f"✅ Exported {len(documents)} documents from {collection_name}")
    
    print(f"📁 Database exported to {export_dir}/ directory")

def import_to_new_db():
    """Import data to new database"""
    print("🔄 Importing to new database...")
    
    # Connect to new database
    client = MongoClient('mongodb://localhost:27017')
    db = client['jobrocket']  # New database name
    
    export_dir = 'db_export'
    
    if not os.path.exists(export_dir):
        print("❌ No export directory found. Run export first.")
        return
    
    for filename in os.listdir(export_dir):
        if filename.endswith('.json'):
            collection_name = filename.replace('.json', '')
            
            with open(f"{export_dir}/{filename}", 'r') as f:
                documents = json.load(f)
            
            if documents:
                collection = db[collection_name]
                collection.insert_many(documents)
                print(f"✅ Imported {len(documents)} documents to {collection_name}")
    
    print("🎉 Database import completed!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_database.py [export|import]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "export":
        export_current_db()
    elif action == "import":
        import_to_new_db()
    else:
        print("Invalid action. Use 'export' or 'import'")
EOL

# Step 6: Create deployment package
echo -e "${YELLOW}📦 Step 6: Creating deployment package...${NC}"

cd deployment
tar -czf ${PROJECT_NAME}_production_$(date +%Y%m%d_%H%M%S).tar.gz $PROJECT_NAME/
cd ..

echo -e "${GREEN}🎉 Deployment package created successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "1. Extract the deployment package"
echo -e "2. Upload files to your cPanel hosting"
echo -e "3. Follow DEPLOYMENT_INSTRUCTIONS.md"
echo -e "4. Update .env with your server details"
echo -e "5. Test the deployment"
echo ""
echo -e "${YELLOW}📁 Files ready in: ${NC}deployment/$PROJECT_NAME/"
echo -e "${YELLOW}📦 Package: ${NC}deployment/${PROJECT_NAME}_production_*.tar.gz"
echo ""
echo -e "${GREEN}🚀 Ready for deployment to $DOMAIN!${NC}"