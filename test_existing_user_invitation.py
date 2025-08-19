#!/usr/bin/env python3
"""
Test invitation acceptance by existing users
"""

import requests
import json

BASE_URL = "https://jobrocket.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_existing_user_invitation_acceptance():
    """Test invitation acceptance by an existing user"""
    
    # Step 1: Login as recruiter to create invitation
    recruiter_login = {
        "email": "lisa.martinez@techcorp.demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=recruiter_login, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Recruiter login failed: {response.status_code}")
        return False
    
    recruiter_token = response.json()["access_token"]
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {recruiter_token}"
    print("✅ Recruiter logged in")
    
    # Step 2: Create invitation for existing user (another demo user)
    invitation_data = {
        "email": "david.wilson@innovate.demo",  # Existing demo user
        "first_name": "David",
        "last_name": "Wilson",
        "role": "manager",
        "branch_ids": []
    }
    
    response = requests.post(f"{BASE_URL}/company/invite", json=invitation_data, headers=auth_headers)
    if response.status_code != 200:
        print(f"❌ Create invitation failed: {response.status_code} - {response.text}")
        return False
    
    invitation_result = response.json()
    invitation_token = invitation_result["invitation_token"]
    print(f"✅ Invitation created for existing user")
    
    # Step 3: Login as the invited existing user
    existing_user_login = {
        "email": "david.wilson@innovate.demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=existing_user_login, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Existing user login failed: {response.status_code}")
        return False
    
    existing_user_token = response.json()["access_token"]
    existing_user_headers = HEADERS.copy()
    existing_user_headers["Authorization"] = f"Bearer {existing_user_token}"
    print("✅ Existing user logged in")
    
    # Step 4: Accept invitation using authenticated route
    response = requests.post(f"{BASE_URL}/invitations/{invitation_token}/accept", headers=existing_user_headers)
    if response.status_code == 200:
        print("✅ Existing user accepted invitation successfully")
        return True
    else:
        print(f"❌ Invitation acceptance failed: {response.status_code} - {response.text}")
        return False

def test_company_member_listing():
    """Test viewing company members after invitation acceptance"""
    
    # Login as recruiter
    recruiter_login = {
        "email": "lisa.martinez@techcorp.demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=recruiter_login, headers=HEADERS)
    if response.status_code != 200:
        return False
    
    recruiter_token = response.json()["access_token"]
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {recruiter_token}"
    
    # Get company members
    response = requests.get(f"{BASE_URL}/company/members", headers=auth_headers)
    if response.status_code == 200:
        members = response.json()
        print(f"✅ Found {len(members)} company members")
        
        for member in members:
            user = member.get("user", {})
            print(f"   - {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')} ({member.get('role', 'N/A')})")
        
        return True
    else:
        print(f"❌ Failed to get company members: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Existing User Invitation Acceptance")
    print("=" * 50)
    
    success1 = test_existing_user_invitation_acceptance()
    success2 = test_company_member_listing()
    
    if success1 and success2:
        print("\n🎉 Existing user invitation flow works!")
    else:
        print("\n💥 Some issues with existing user invitation flow")