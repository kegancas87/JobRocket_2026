#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import bcrypt

async def create_admin_user():
    """Create admin@jobrocket.co.za as administrator"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/job_portal')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.job_portal
    
    print("👑 Creating Administrator User...")
    print("=" * 40)
    
    admin_email = "admin@jobrocket.co.za"
    admin_password = "admin123"
    
    try:
        # Check if admin already exists
        existing_admin = await db.users.find_one({"email": admin_email})
        if existing_admin:
            print(f"⚠️  Admin user {admin_email} already exists!")
            print(f"   Current role: {existing_admin.get('role', 'Unknown')}")
            return
        
        # Hash password
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
        
        # Create admin user document
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password_hash": hashed_password.decode('utf-8'),
            "first_name": "Job Rocket",
            "last_name": "Administrator",
            "role": "admin",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "admin_permissions": {
                "user_management": True,
                "discount_codes": True,
                "analytics": True,
                "system_settings": True,
                "platform_management": True
            }
        }
        
        # Insert admin user
        result = await db.users.insert_one(admin_user)
        
        if result.inserted_id:
            print(f"✅ Successfully created admin user!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   Role: admin")
            print(f"   ID: {admin_user['id']}")
            
            # Verify the admin was created
            verify_admin = await db.users.find_one({"email": admin_email})
            if verify_admin and verify_admin.get("role") == "admin":
                print(f"✅ Verification successful - admin user is ready!")
            else:
                print(f"❌ Verification failed - please check database")
                
        else:
            print(f"❌ Failed to create admin user in database")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        
    finally:
        client.close()

async def main():
    print("🚀 Job Rocket - Admin User Creation Script")
    print("=" * 50)
    
    await create_admin_user()
    
    print("\n🎉 Admin user creation complete!")
    print("\n💡 You can now login with:")
    print("   Email: admin@jobrocket.co.za")
    print("   Password: admin123")

if __name__ == "__main__":
    asyncio.run(main())