"""
JobRocket - Database Initialization Script
Sets up collections, indexes, and seeds initial tier data
Run this once when setting up a fresh database
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']


async def drop_old_collections(db):
    """Drop collections that are being replaced"""
    old_collections = [
        "user_packages",  # Replaced by account-level subscriptions
        "company_branches",  # Will be part of account
        "company_members",  # Replaced by account user management
        # Keep these but they'll be cleared:
        # "users", "jobs", "job_applications", "payments", "discount_codes"
    ]
    
    for coll in old_collections:
        try:
            await db.drop_collection(coll)
            print(f"  Dropped collection: {coll}")
        except Exception as e:
            print(f"  Could not drop {coll}: {e}")


async def clear_existing_data(db):
    """Clear data from existing collections for fresh start"""
    collections_to_clear = [
        "users",
        "jobs", 
        "job_applications",
        "payments",
        "discount_codes",
        "team_invitations",
    ]
    
    for coll in collections_to_clear:
        try:
            result = await db[coll].delete_many({})
            print(f"  Cleared {result.deleted_count} documents from {coll}")
        except Exception as e:
            print(f"  Could not clear {coll}: {e}")


async def create_collections(db):
    """Create new collections"""
    new_collections = [
        "accounts",
        "account_addons",
        "tiers",
        "addons",
    ]
    
    existing = await db.list_collection_names()
    
    for coll in new_collections:
        if coll not in existing:
            await db.create_collection(coll)
            print(f"  Created collection: {coll}")
        else:
            print(f"  Collection exists: {coll}")


async def create_indexes(db):
    """Create database indexes for performance"""
    
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("account_id")
    await db.users.create_index("role")
    print("  Created users indexes")
    
    # Accounts indexes
    await db.accounts.create_index("owner_user_id", unique=True)
    await db.accounts.create_index("tier_id")
    await db.accounts.create_index("subscription_status")
    print("  Created accounts indexes")
    
    # Account addons indexes
    await db.account_addons.create_index("account_id")
    await db.account_addons.create_index([("account_id", 1), ("addon_id", 1)])
    print("  Created account_addons indexes")
    
    # Jobs indexes
    await db.jobs.create_index("account_id")
    await db.jobs.create_index("posted_by")
    await db.jobs.create_index("is_active")
    await db.jobs.create_index("posted_date")
    await db.jobs.create_index([("is_active", 1), ("posted_date", -1)])
    print("  Created jobs indexes")
    
    # Job applications indexes
    await db.job_applications.create_index("job_id")
    await db.job_applications.create_index("applicant_id")
    await db.job_applications.create_index("account_id")
    await db.job_applications.create_index("status")
    print("  Created job_applications indexes")
    
    # Payments indexes
    await db.payments.create_index("account_id")
    await db.payments.create_index("user_id")
    await db.payments.create_index("status")
    await db.payments.create_index("provider_reference")
    print("  Created payments indexes")
    
    # Team invitations indexes
    await db.team_invitations.create_index("account_id")
    await db.team_invitations.create_index("email")
    await db.team_invitations.create_index("invitation_token", unique=True)
    await db.team_invitations.create_index("status")
    print("  Created team_invitations indexes")
    
    # Discount codes indexes
    await db.discount_codes.create_index("code", unique=True)
    await db.discount_codes.create_index("status")
    print("  Created discount_codes indexes")


async def seed_tiers(db):
    """Seed tier definitions into database"""
    from models.tiers import TIER_CONFIG
    from models.enums import TierId
    
    # Clear existing tiers
    await db.tiers.delete_many({})
    
    for tier_id, config in TIER_CONFIG.items():
        tier_doc = {
            "id": tier_id.value,
            "name": config["name"],
            "price_monthly": config["price_monthly"],
            "price_annually": config.get("price_annually"),
            "currency": config["currency"],
            "included_users": config["included_users"],
            "extra_user_price": config["extra_user_price"],
            "multi_user_access": config["multi_user_access"],
            "role_based_permissions": config["role_based_permissions"],
            "company_profile_level": config["company_profile_level"].value,
            "features": [f.value for f in config["features"]],
            "available_addons": [a.value for a in config["available_addons"]],
            "display_order": config["display_order"],
            "is_active": config["is_active"],
            "created_at": datetime.utcnow(),
        }
        await db.tiers.insert_one(tier_doc)
        print(f"  Seeded tier: {config['name']}")


async def seed_addons(db):
    """Seed add-on definitions into database"""
    from models.tiers import ADDON_CONFIG
    
    # Clear existing addons
    await db.addons.delete_many({})
    
    for addon_id, config in ADDON_CONFIG.items():
        addon_doc = {
            "id": addon_id.value,
            "name": config["name"],
            "description": config["description"],
            "feature_id": config["feature_id"].value,
            "price_monthly": config.get("price_monthly"),
            "price_once": config.get("price_once"),
            "is_recurring": config["is_recurring"],
            "available_tiers": [t.value for t in config["available_tiers"]],
            "is_active": config["is_active"],
            "created_at": datetime.utcnow(),
        }
        await db.addons.insert_one(addon_doc)
        print(f"  Seeded addon: {config['name']}")


async def main():
    """Main initialization function"""
    print("=" * 60)
    print("JobRocket Database Initialization")
    print("=" * 60)
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"\nConnected to database: {db_name}")
    
    print("\n1. Dropping old collections...")
    await drop_old_collections(db)
    
    print("\n2. Clearing existing data (fresh start)...")
    await clear_existing_data(db)
    
    print("\n3. Creating new collections...")
    await create_collections(db)
    
    print("\n4. Creating indexes...")
    await create_indexes(db)
    
    print("\n5. Seeding tier definitions...")
    await seed_tiers(db)
    
    print("\n6. Seeding add-on definitions...")
    await seed_addons(db)
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    
    # Summary
    print("\nCollection summary:")
    collections = await db.list_collection_names()
    for coll in sorted(collections):
        count = await db[coll].count_documents({})
        print(f"  {coll}: {count} documents")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
