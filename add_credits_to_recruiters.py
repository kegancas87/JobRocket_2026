#!/usr/bin/env python3
"""
Script to add job listing credits to recruiter accounts for testing
"""

import asyncio
import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'jobrocket')

async def add_credits_to_recruiters():
    """Add job listing credits to all recruiter accounts"""
    
    client = AsyncMongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Find all recruiter users
        recruiters = await db.users.find({"role": "recruiter"}).to_list(None)
        
        print(f"Found {len(recruiters)} recruiter accounts")
        
        for recruiter in recruiters:
            user_id = recruiter['id']
            email = recruiter.get('email', 'Unknown')
            
            # Add 10 job listing credits to each recruiter
            credits_to_add = 10
            
            # Update user's job credits
            result = await db.users.update_one(
                {"id": user_id},
                {
                    "$inc": {"job_credits": credits_to_add},
                    "$set": {"credits_updated": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Added {credits_to_add} job credits to {email}")
                
                # Also create a fake payment record for tracking
                payment_record = {
                    "id": f"test_payment_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "user_id": user_id,
                    "package_id": "test_package",
                    "amount": 0.0,
                    "final_amount": 0.0,
                    "currency": "ZAR",
                    "payment_method": "admin_grant",
                    "status": "completed",
                    "created_date": datetime.utcnow(),
                    "completed_date": datetime.utcnow(),
                    "description": f"Admin granted {credits_to_add} job credits for testing"
                }
                
                await db.payments.insert_one(payment_record)
                print(f"   📝 Created payment record for tracking")
            else:
                print(f"❌ Failed to add credits to {email}")
        
        print(f"\n🎉 Successfully added credits to all recruiter accounts!")
        print(f"Each recruiter now has 10+ job listing credits for testing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

async def main():
    print("🚀 Adding Job Credits to Recruiter Accounts")
    print("=" * 50)
    await add_credits_to_recruiters()

if __name__ == "__main__":
    asyncio.run(main())