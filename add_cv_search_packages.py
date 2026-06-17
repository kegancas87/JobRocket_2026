#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Add the current directory to Python path to import server modules
sys.path.append('/app/backend')

async def add_cv_search_packages():
    """Add CV search packages to recruiter users for testing"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/job_portal')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.job_portal
    
    print("🔍 Adding CV Search Packages to Recruiter Users...")
    
    try:
        # Find all recruiter users - try known recruiter IDs
        known_recruiter_id = "3c513e33-ddc3-41a8-8b43-245fc88af257"  # lisa.martinez@techcorp.demo
        
        # Try to find this specific recruiter
        recruiter = await db.users.find_one({"id": known_recruiter_id})
        
        if recruiter:
            recruiters = [recruiter]
            print(f"✅ Found known recruiter: {recruiter.get('email', 'No email')}")
        else:
            # Fallback: try to find any users with role recruiter
            all_users = await db.users.find({}).to_list(None)
            recruiters = [user for user in all_users if user.get('role') == 'recruiter']
            print(f"📊 Found {len(recruiters)} recruiters from {len(all_users)} total users")
        
        print(f"📊 Processing {len(recruiters)} recruiter users")
        
        # CV Search packages to add
        packages_to_add = [
            {
                "package_type": "cv_search",
                "name": "CV Search - 10 Searches",
                "description": "Search through candidate CVs with 10 search credits",
                "price": 499.00,
                "currency": "ZAR",
                "job_listings": 0,
                "cv_searches": 10,
                "duration_days": 30,
                "features": ["10 CV searches", "Advanced filtering", "Contact candidates"]
            },
            {
                "package_type": "cv_search_unlimited",
                "name": "CV Search - Unlimited",
                "description": "Unlimited CV searches for one month",
                "price": 999.00,
                "currency": "ZAR", 
                "job_listings": 0,
                "cv_searches": None,  # Unlimited
                "duration_days": 30,
                "features": ["Unlimited CV searches", "Advanced filtering", "Contact candidates", "Priority support"]
            }
        ]
        
        added_count = 0
        
        for recruiter in recruiters:
            recruiter_id = recruiter["id"]
            email = recruiter.get("email", "No email")
            
            print(f"\n👤 Processing recruiter: {email} ({recruiter_id})")
            
            # Check if user already has CV search packages
            existing_packages = await db.user_packages.find({
                "user_id": recruiter_id,
                "package.package_type": {"$in": ["cv_search", "cv_search_unlimited"]}
            }).to_list(None)
            
            if existing_packages:
                print(f"   ⚠️  Already has {len(existing_packages)} CV search package(s), skipping...")
                continue
            
            # Add both CV search packages for testing
            for package_data in packages_to_add:
                user_package = {
                    "id": str(uuid.uuid4()),
                    "user_id": recruiter_id,
                    "package": package_data,
                    "is_active": True,
                    "purchase_date": datetime.utcnow(),
                    "expiry_date": datetime.utcnow() + timedelta(days=package_data["duration_days"]),
                    "job_listings_remaining": package_data["job_listings"],
                    "cv_searches_remaining": package_data["cv_searches"],
                    "created_at": datetime.utcnow()
                }
                
                # Insert the user package
                result = await db.user_packages.insert_one(user_package)
                
                if result.inserted_id:
                    print(f"   ✅ Added {package_data['name']}")
                    added_count += 1
                else:
                    print(f"   ❌ Failed to add {package_data['name']}")
        
        print(f"\n🎉 Successfully added {added_count} CV search packages to recruiter users!")
        
        # Summary
        total_packages = await db.user_packages.count_documents({
            "package.package_type": {"$in": ["cv_search", "cv_search_unlimited"]}
        })
        print(f"📊 Total CV search packages in database: {total_packages}")
        
        # Show some example packages
        print("\n📋 Sample CV search packages:")
        sample_packages = await db.user_packages.find({
            "package.package_type": {"$in": ["cv_search", "cv_search_unlimited"]}
        }).limit(3).to_list(3)
        
        for pkg in sample_packages:
            user = await db.users.find_one({"id": pkg["user_id"]})
            user_email = user.get("email", "Unknown") if user else "Unknown"
            print(f"   • {pkg['package']['name']} - {user_email} - {pkg['cv_searches_remaining'] or 'Unlimited'} searches")
            
    except Exception as e:
        print(f"❌ Error adding CV search packages: {str(e)}")
        return False
    
    finally:
        client.close()
    
    return True

async def main():
    """Main function"""
    print("🚀 CV Search Package Setup Script")
    print("=" * 50)
    
    success = await add_cv_search_packages()
    
    if success:
        print("\n✅ CV search packages setup completed successfully!")
        print("🔍 Recruiters can now access CV search functionality")
    else:
        print("\n❌ Setup failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())