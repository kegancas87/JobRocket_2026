#!/usr/bin/env python3
"""
Script to add unlimited packages to specific recruiter and admin users
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'jobrocket')

def add_unlimited_packages():
    """Add unlimited packages to specific users"""
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Target users
    target_users = [
        'lisa.martinez@techcorp.demo',
        'david.wilson@innovate.demo', 
        'emma.davis@dataflow.demo',
        'admin@jobrocket.com'
    ]
    
    try:
        print("🚀 Adding Unlimited Packages to Target Users")
        print("=" * 50)
        
        for email in target_users:
            # Find user by email
            user = db.users.find_one({"email": email})
            
            if not user:
                print(f"❌ User not found: {email}")
                continue
                
            user_id = user['id']
            user_role = user.get('role', 'unknown')
            current_credits = user.get('job_credits', 0)
            current_cv_searches = user.get('cv_search_credits', 0)
            
            print(f"\n📋 Processing: {email} ({user_role})")
            print(f"   Current job credits: {current_credits}")
            print(f"   Current CV search credits: {current_cv_searches}")
            
            # Set unlimited credits (very high numbers)
            unlimited_job_credits = 9999
            unlimited_cv_credits = 9999
            
            # Update user with unlimited packages
            update_result = db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "job_credits": unlimited_job_credits,
                        "cv_search_credits": unlimited_cv_credits,
                        "package_type": "unlimited",
                        "package_status": "active",
                        "package_expires": datetime.utcnow() + timedelta(days=365),  # 1 year
                        "credits_updated": datetime.utcnow(),
                        "unlimited_package": True
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print(f"✅ Added unlimited package to {email}")
                print(f"   Job credits: {unlimited_job_credits}")
                print(f"   CV search credits: {unlimited_cv_credits}")
                print(f"   Package expires: {(datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%d')}")
                
                # Create payment record for tracking
                payment_record = {
                    "id": f"unlimited_grant_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "user_id": user_id,
                    "package_id": "unlimited_package",
                    "package_type": "unlimited_listings", 
                    "amount": 0.0,
                    "final_amount": 0.0,
                    "currency": "ZAR",
                    "payment_method": "admin_grant",
                    "status": "completed",
                    "created_date": datetime.utcnow(),
                    "completed_date": datetime.utcnow(),
                    "description": f"Admin granted unlimited package to {email}",
                    "credits_granted": {
                        "job_credits": unlimited_job_credits,
                        "cv_search_credits": unlimited_cv_credits
                    }
                }
                
                db.payments.insert_one(payment_record)
                print(f"   📝 Created payment record for tracking")
                
                # Also create a user package record
                user_package = {
                    "id": f"package_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "user_id": user_id,
                    "package_type": "unlimited_listings",
                    "job_credits": unlimited_job_credits,
                    "cv_search_credits": unlimited_cv_credits,
                    "purchase_date": datetime.utcnow(),
                    "expiry_date": datetime.utcnow() + timedelta(days=365),
                    "status": "active",
                    "payment_id": payment_record["id"]
                }
                
                db.user_packages.insert_one(user_package)
                print(f"   📦 Created user package record")
                
            else:
                print(f"❌ Failed to update {email}")
        
        print(f"\n🎉 Successfully added unlimited packages to target users!")
        print(f"All specified users now have:")
        print(f"  • 9,999 job listing credits")
        print(f"  • 9,999 CV search credits") 
        print(f"  • 1-year expiration")
        print(f"  • Active unlimited package status")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

def main():
    add_unlimited_packages()

if __name__ == "__main__":
    main()