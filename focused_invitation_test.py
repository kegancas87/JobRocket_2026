#!/usr/bin/env python3
"""
Focused test for invitation registration with unique email
"""

import requests
import json
import uuid
from datetime import datetime

BASE_URL = "https://seeker-profile-v2.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

def test_invitation_registration_flow():
    """Test the complete invitation registration flow with unique email"""
    
    # Step 1: Login as recruiter
    login_data = {
        "email": "lisa.martinez@techcorp.demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Recruiter login failed: {response.status_code} - {response.text}")
        return False
    
    login_result = response.json()
    recruiter_token = login_result["access_token"]
    print(f"✅ Recruiter logged in successfully")
    
    # Step 2: Create invitation with unique email
    unique_email = f"test.user.{uuid.uuid4().hex[:8]}@example.com"
    invitation_data = {
        "email": unique_email,
        "first_name": "Test",
        "last_name": "User",
        "role": "recruiter",
        "branch_ids": []
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {recruiter_token}"
    
    response = requests.post(f"{BASE_URL}/company/invite", json=invitation_data, headers=auth_headers)
    if response.status_code != 200:
        print(f"❌ Create invitation failed: {response.status_code} - {response.text}")
        return False
    
    invitation_result = response.json()
    invitation_token = invitation_result["invitation_token"]
    print(f"✅ Invitation created with token: {invitation_token[:20]}...")
    
    # Step 3: Get invitation details (public endpoint)
    response = requests.get(f"{BASE_URL}/public/invitations/{invitation_token}", headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Get invitation details failed: {response.status_code} - {response.text}")
        return False
    
    invitation_details = response.json()
    print(f"✅ Retrieved invitation details for: {invitation_details['company_name']}")
    print(f"   Role: {invitation_details['role']}")
    print(f"   Expires: {invitation_details['expires_at']}")
    
    # Step 4: Register via invitation
    registration_data = {
        "email": unique_email,  # Must match invitation email
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/public/invitations/{invitation_token}/register", json=registration_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Registration via invitation failed: {response.status_code} - {response.text}")
        return False
    
    registration_result = response.json()
    new_user_token = registration_result["access_token"]
    new_user = registration_result["user"]
    print(f"✅ User registered successfully via invitation")
    print(f"   User ID: {new_user['id']}")
    print(f"   Email: {new_user['email']}")
    print(f"   Role: {new_user['role']}")
    
    # Step 5: Verify the invitation is now accepted
    response = requests.get(f"{BASE_URL}/company/invitations", headers=auth_headers)
    if response.status_code == 200:
        invitations = response.json()
        for inv in invitations:
            if inv["invitation_token"] == invitation_token:
                print(f"✅ Invitation status: {inv['status']}")
                if inv['status'] == 'accepted':
                    print("✅ Invitation correctly marked as accepted")
                else:
                    print(f"⚠️  Expected 'accepted', got '{inv['status']}'")
                break
    
    # Step 6: Verify new user can login
    new_login_data = {
        "email": unique_email,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=new_login_data, headers=HEADERS)
    if response.status_code == 200:
        print("✅ New user can login successfully")
        return True
    else:
        print(f"❌ New user login failed: {response.status_code} - {response.text}")
        return False

def test_invitation_edge_cases():
    """Test edge cases and error conditions"""
    
    # Login as recruiter first
    login_data = {
        "email": "lisa.martinez@techcorp.demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
    if response.status_code != 200:
        return False
    
    recruiter_token = response.json()["access_token"]
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {recruiter_token}"
    
    print("\n🧪 Testing Edge Cases:")
    
    # Test 1: Invalid email format
    invalid_invitation = {
        "email": "invalid-email-format",
        "first_name": "Test",
        "last_name": "User",
        "role": "recruiter"
    }
    
    response = requests.post(f"{BASE_URL}/company/invite", json=invalid_invitation, headers=auth_headers)
    if response.status_code >= 400:
        print("✅ Invalid email format properly rejected")
    else:
        print(f"❌ Invalid email should be rejected, got: {response.status_code}")
    
    # Test 2: Missing required fields
    incomplete_invitation = {
        "email": "test@example.com"
        # Missing first_name, last_name
    }
    
    response = requests.post(f"{BASE_URL}/company/invite", json=incomplete_invitation, headers=auth_headers)
    if response.status_code >= 400:
        print("✅ Incomplete invitation properly rejected")
    else:
        print(f"❌ Incomplete invitation should be rejected, got: {response.status_code}")
    
    # Test 3: Invalid role
    invalid_role_invitation = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "invalid_role"
    }
    
    response = requests.post(f"{BASE_URL}/company/invite", json=invalid_role_invitation, headers=auth_headers)
    if response.status_code >= 400:
        print("✅ Invalid role properly rejected")
    else:
        print(f"❌ Invalid role should be rejected, got: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing Invitation Registration Flow")
    print("=" * 50)
    
    success = test_invitation_registration_flow()
    test_invitation_edge_cases()
    
    if success:
        print("\n🎉 Invitation registration flow works correctly!")
    else:
        print("\n💥 Invitation registration flow has issues")