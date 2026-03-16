#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import requests

# Add the current directory to Python path to import server modules
sys.path.append('/app/backend')

async def add_cv_packages_to_demo_recruiters():
    """Add different CV search packages to demo recruiter users for testing"""
    
    print("📦 Adding CV Search Packages to Demo Recruiter Users...")
    print("=" * 60)
    
    # Demo recruiters and their package assignments
    demo_recruiters = [
        {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123",
            "package_type": "cv_search_10",
            "package_name": "10 CV Searches",
            "credits": 10
        },
        {
            "email": "david.wilson@innovate.demo", 
            "password": "demo123",
            "package_type": "cv_search_20",
            "package_name": "20 CV Searches", 
            "credits": 20
        }
    ]
    
    base_url = "https://jobs-dashboard-3.preview.emergentagent.com/api"
    
    try:
        added_count = 0
        
        for recruiter_info in demo_recruiters:
            print(f"\n👤 Processing recruiter: {recruiter_info['email']}")
            
            # Step 1: Login to get user token and ID
            login_data = {
                "email": recruiter_info["email"],
                "password": recruiter_info["password"]
            }
            
            try:
                response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=30)
                
                if response.status_code != 200:
                    print(f"   ❌ Login failed: {response.status_code} - {response.text}")
                    continue
                
                login_result = response.json()
                token = login_result["access_token"]
                user_id = login_result["user"]["id"]
                user_role = login_result["user"]["role"]
                
                print(f"   ✅ Logged in successfully")
                print(f"      📍 User ID: {user_id}")
                print(f"      🎭 Role: {user_role}")
                
                if user_role != "recruiter":
                    print(f"   ⚠️  User is not a recruiter, skipping...")
                    continue
                
                # Step 2: Check existing packages
                headers = {"Authorization": f"Bearer {token}"}
                packages_response = requests.get(f"{base_url}/my-packages", headers=headers, timeout=30)
                
                if packages_response.status_code == 200:
                    existing_packages = packages_response.json()
                    cv_packages = [pkg for pkg in existing_packages 
                                 if pkg.get('package', {}).get('package_type', '').startswith('cv_search')]
                    
                    if cv_packages:
                        print(f"   ⚠️  Already has {len(cv_packages)} CV search package(s), skipping...")
                        for pkg in cv_packages:
                            package_info = pkg.get('package', {})
                            remaining = pkg.get('user_package', {}).get('cv_searches_remaining', 'unlimited')
                            print(f"      • {package_info.get('name', 'Unknown')} - {remaining} searches remaining")
                        continue
                
                # Step 3: Purchase the assigned CV search package
                print(f"   💳 Purchasing {recruiter_info['package_name']}...")
                
                # Initiate payment
                payment_response = requests.post(
                    f"{base_url}/payments/initiate?package_type={recruiter_info['package_type']}", 
                    headers=headers,
                    timeout=30
                )
                
                if payment_response.status_code != 200:
                    print(f"   ❌ Payment initiation failed: {payment_response.status_code} - {payment_response.text}")
                    continue
                
                payment_result = payment_response.json()
                payment_id = payment_result.get("payment_id")
                
                if not payment_id:
                    print(f"   ❌ No payment ID returned")
                    continue
                
                print(f"   ✅ Payment initiated: {payment_id}")
                
                # Complete payment with mock reference
                complete_response = requests.post(
                    f"{base_url}/payments/{payment_id}/complete?payment_reference=TEST_{recruiter_info['package_type'].upper()}_{int(datetime.utcnow().timestamp())}",
                    headers=headers,
                    timeout=30
                )
                
                if complete_response.status_code != 200:
                    print(f"   ❌ Payment completion failed: {complete_response.status_code} - {complete_response.text}")
                    continue
                
                complete_result = complete_response.json()
                print(f"   ✅ Payment completed successfully!")
                print(f"      📦 Package activated: {complete_result.get('package_activated')}")
                print(f"      🔍 CV searches remaining: {complete_result.get('cv_searches_remaining', 'unlimited')}")
                
                added_count += 1
                
            except requests.RequestException as e:
                print(f"   ❌ Request failed for {recruiter_info['email']}: {str(e)}")
                continue
            
            except Exception as e:
                print(f"   ❌ Error processing {recruiter_info['email']}: {str(e)}")
                continue
        
        print(f"\n🎉 Successfully added CV search packages to {added_count} demo recruiter users!")
        
        # Verify packages were added
        print(f"\n📋 Verification - Checking all demo recruiter packages:")
        
        for recruiter_info in demo_recruiters:
            try:
                # Login again to check packages
                response = requests.post(f"{base_url}/auth/login", json={
                    "email": recruiter_info["email"],
                    "password": recruiter_info["password"]
                }, timeout=30)
                
                if response.status_code == 200:
                    token = response.json()["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    packages_response = requests.get(f"{base_url}/my-packages", headers=headers, timeout=30)
                    if packages_response.status_code == 200:
                        packages = packages_response.json()
                        cv_packages = [pkg for pkg in packages 
                                     if pkg.get('package', {}).get('package_type', '').startswith('cv_search')]
                        
                        print(f"   • {recruiter_info['email']}:")
                        if cv_packages:
                            for pkg in cv_packages:
                                package_info = pkg.get('package', {})
                                user_package = pkg.get('user_package', {})
                                remaining = user_package.get('cv_searches_remaining', 'unlimited')
                                is_active = user_package.get('is_active', False)
                                print(f"     ✅ {package_info.get('name', 'Unknown')} - {remaining} searches - {'Active' if is_active else 'Inactive'}")
                        else:
                            print(f"     ❌ No CV search packages found")
                            
            except Exception as e:
                print(f"   ❌ Verification failed for {recruiter_info['email']}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        return False
    
    return True

async def main():
    """Main function"""
    print("🚀 CV Search Package Assignment Script for Demo Users")
    print("=" * 60)
    
    success = await add_cv_packages_to_demo_recruiters()
    
    if success:
        print("\n✅ CV search packages assignment completed!")
        print("\n🔍 Demo Recruiter Testing Setup:")
        print("   📧 lisa.martinez@techcorp.demo - 10 CV Searches")
        print("   📧 david.wilson@innovate.demo - 20 CV Searches")
        print("\n💡 You can now test CV search functionality with different credit limits!")
    else:
        print("\n❌ Assignment failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())