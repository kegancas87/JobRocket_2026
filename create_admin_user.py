#!/usr/bin/env python3
"""
Create an admin user for testing discount codes
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'jobrocket')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if admin user already exists
    existing_admin = await db.users.find_one({"email": "admin@jobrocket.com"})
    if existing_admin:
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": "admin@jobrocket.com",
        "password_hash": pwd_context.hash("admin123"),
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.users.insert_one(admin_data)
    print("Admin user created successfully!")
    print("Email: admin@jobrocket.com")
    print("Password: admin123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())