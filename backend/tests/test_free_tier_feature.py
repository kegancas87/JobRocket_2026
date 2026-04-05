"""
Test Free Tier Feature - Testing the following:
1. /api/tiers endpoint should return only purchasable tiers (NOT 'free')
2. /api/billing endpoint should work for free tier accounts
3. /api/auth/me should return correct tier_id for recruiters
4. New recruiter registration should start with 'free' tier
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://recruiter-dash-build.preview.emergentagent.com"

# Test credentials
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"
ADMIN_EMAIL = "admin@jobrocket.co.za"
ADMIN_PASSWORD = "admin123"


class TestFreeTierFeature:
    """Tests for free tier implementation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login(self, email, password):
        """Helper to login and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return response.json()
        return None
    
    # Test 1: /api/tiers should NOT include 'free' tier
    def test_tiers_endpoint_excludes_free(self):
        """Test that /api/tiers returns only purchasable tiers (NOT 'free')"""
        response = self.session.get(f"{BASE_URL}/api/tiers")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        tiers = response.json()
        assert isinstance(tiers, list), "Expected list of tiers"
        assert len(tiers) > 0, "Expected at least one tier"
        
        # Check that 'free' tier is NOT in the list
        tier_ids = [t.get("id") for t in tiers]
        assert "free" not in tier_ids, f"'free' tier should NOT be in /api/tiers. Found tiers: {tier_ids}"
        
        # Verify expected purchasable tiers are present
        expected_tiers = ["starter", "growth", "pro", "enterprise"]
        for expected in expected_tiers:
            assert expected in tier_ids, f"Expected tier '{expected}' not found in {tier_ids}"
        
        print(f"✓ /api/tiers correctly excludes 'free' tier. Returned tiers: {tier_ids}")
    
    # Test 2: /api/billing should work for existing recruiter (with active tier)
    def test_billing_endpoint_for_active_tier(self):
        """Test that /api/billing works for recruiter with active tier"""
        login_result = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert login_result is not None, "Failed to login as recruiter"
        
        response = self.session.get(f"{BASE_URL}/api/billing")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        billing = response.json()
        assert "tier_id" in billing, "Expected tier_id in billing response"
        assert "tier_name" in billing, "Expected tier_name in billing response"
        
        # Existing recruiter should have an active tier (could be starter, growth, pro, or enterprise)
        valid_tiers = ["starter", "growth", "pro", "enterprise"]
        assert billing.get("tier_id") in valid_tiers, f"Expected tier_id to be one of {valid_tiers}, got '{billing.get('tier_id')}'"
        
        print(f"✓ /api/billing works for active tier. tier_id: {billing.get('tier_id')}, tier_name: {billing.get('tier_name')}")
    
    # Test 3: /api/auth/me should return correct tier_id for recruiter
    def test_auth_me_returns_tier_for_recruiter(self):
        """Test that /api/auth/me returns tier_id for recruiter"""
        login_result = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert login_result is not None, "Failed to login as recruiter"
        
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        user_data = response.json()
        assert "account" in user_data, "Expected 'account' in user data for recruiter"
        
        account = user_data.get("account", {})
        tier_id = account.get("tier_id")
        
        # Existing test recruiter should have a valid tier
        valid_tiers = ["starter", "growth", "pro", "enterprise"]
        assert tier_id in valid_tiers, f"Expected tier_id to be one of {valid_tiers}, got '{tier_id}'"
        
        print(f"✓ /api/auth/me returns tier_id: {tier_id}")
    
    # Test 4: Register new recruiter and verify they get 'free' tier
    def test_new_recruiter_gets_free_tier(self):
        """Test that newly registered recruiter gets 'free' tier (not 'starter')"""
        # Generate unique email for test
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test_recruiter_{unique_id}@test.com"
        
        # Register new recruiter
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "Recruiter",
            "role": "recruiter",
            "company_name": f"Test Company {unique_id}"
        })
        
        assert register_response.status_code == 200, f"Registration failed: {register_response.status_code}: {register_response.text}"
        
        # Get token from registration response
        reg_data = register_response.json()
        token = reg_data.get("access_token")
        assert token, "No access token in registration response"
        
        # Update session with new token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get user profile to check tier
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200, f"Failed to get user profile: {me_response.status_code}: {me_response.text}"
        
        user_data = me_response.json()
        account = user_data.get("account", {})
        tier_id = account.get("tier_id")
        
        # New recruiter should have 'free' tier
        assert tier_id == "free", f"Expected new recruiter to have 'free' tier, got '{tier_id}'"
        
        print(f"✓ New recruiter correctly assigned 'free' tier. Email: {test_email}, tier_id: {tier_id}")
    
    # Test 5: /api/billing should work for free tier accounts (return tier_id: 'free')
    def test_billing_endpoint_for_free_tier(self):
        """Test that /api/billing works for free tier accounts"""
        # Register a new recruiter (will have free tier)
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"test_billing_free_{unique_id}@test.com"
        
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "BillingFree",
            "role": "recruiter",
            "company_name": f"Test Billing Company {unique_id}"
        })
        
        assert register_response.status_code == 200, f"Registration failed: {register_response.status_code}"
        
        token = register_response.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Now test billing endpoint
        billing_response = self.session.get(f"{BASE_URL}/api/billing")
        
        # Should NOT return error - should work for free tier
        assert billing_response.status_code == 200, f"Billing endpoint failed for free tier: {billing_response.status_code}: {billing_response.text}"
        
        billing_data = billing_response.json()
        tier_id = billing_data.get("tier_id")
        
        # Should return 'free' tier
        assert tier_id == "free", f"Expected billing to return tier_id 'free', got '{tier_id}'"
        
        print(f"✓ /api/billing works for free tier accounts. tier_id: {tier_id}")


class TestAdminFreeTierOption:
    """Tests for admin ability to set free tier"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login_admin(self):
        """Login as admin"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return True
        return False
    
    def test_admin_can_access_accounts(self):
        """Test that admin can access accounts list"""
        logged_in = self.login_admin()
        assert logged_in, "Failed to login as admin"
        
        response = self.session.get(f"{BASE_URL}/api/admin/stats")
        
        assert response.status_code == 200, f"Admin stats failed: {response.status_code}: {response.text}"
        
        data = response.json()
        assert "accounts" in data, "Expected 'accounts' in admin stats"
        
        print(f"✓ Admin can access accounts. Found {len(data.get('accounts', []))} accounts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
