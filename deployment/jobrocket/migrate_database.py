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
