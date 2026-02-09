"""
Backend API Tests for Multi-Tenant SaaS Recruitment Platform
Tests: Tiers, Pricing, Payments, Account Dashboard, Authentication
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_CREDS = {"email": "admin@jobrocket.co.za", "password": "admin123"}
RECRUITER_STARTER = {"email": "hr@techcorp.co.za", "password": "demo123"}
RECRUITER_GROWTH = {"email": "talent@innovatedigital.co.za", "password": "demo123"}
RECRUITER_PRO = {"email": "careers@fintechsa.co.za", "password": "demo123"}
RECRUITER_ENTERPRISE = {"email": "admin@globalrecruit.co.za", "password": "demo123"}


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        print(f"✓ Health check passed - version: {data['version']}")


class TestTiersEndpoint:
    """Tests for /api/tiers endpoint - Pricing page data"""
    
    def test_get_all_tiers(self):
        """Test GET /api/tiers returns all 4 subscription tiers"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        assert len(tiers) == 4, f"Expected 4 tiers, got {len(tiers)}"
        
        tier_ids = [t["id"] for t in tiers]
        assert "starter" in tier_ids
        assert "growth" in tier_ids
        assert "pro" in tier_ids
        assert "enterprise" in tier_ids
        print(f"✓ All 4 tiers returned: {tier_ids}")
    
    def test_starter_tier_pricing(self):
        """Test Starter tier has correct price R6,899 and 1 user"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        starter = next((t for t in tiers if t["id"] == "starter"), None)
        
        assert starter is not None, "Starter tier not found"
        assert starter["price_monthly"] == 6899, f"Expected R6,899, got R{starter['price_monthly']}"
        assert starter["included_users"] == 1, f"Expected 1 user, got {starter['included_users']}"
        assert starter["name"] == "Starter"
        print(f"✓ Starter tier: R{starter['price_monthly']}/month, {starter['included_users']} user")
    
    def test_growth_tier_pricing(self):
        """Test Growth tier has correct price R10,499 and 2 users"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        growth = next((t for t in tiers if t["id"] == "growth"), None)
        
        assert growth is not None, "Growth tier not found"
        assert growth["price_monthly"] == 10499, f"Expected R10,499, got R{growth['price_monthly']}"
        assert growth["included_users"] == 2, f"Expected 2 users, got {growth['included_users']}"
        assert growth["name"] == "Growth"
        print(f"✓ Growth tier: R{growth['price_monthly']}/month, {growth['included_users']} users")
    
    def test_pro_tier_pricing(self):
        """Test Pro tier has correct price R19,999 and 3 users"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        pro = next((t for t in tiers if t["id"] == "pro"), None)
        
        assert pro is not None, "Pro tier not found"
        assert pro["price_monthly"] == 19999, f"Expected R19,999, got R{pro['price_monthly']}"
        assert pro["included_users"] == 3, f"Expected 3 users, got {pro['included_users']}"
        assert pro["name"] == "Pro"
        print(f"✓ Pro tier: R{pro['price_monthly']}/month, {pro['included_users']} users")
    
    def test_enterprise_tier_pricing(self):
        """Test Enterprise tier has correct price R39,999 and 5 users"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        enterprise = next((t for t in tiers if t["id"] == "enterprise"), None)
        
        assert enterprise is not None, "Enterprise tier not found"
        assert enterprise["price_monthly"] == 39999, f"Expected R39,999, got R{enterprise['price_monthly']}"
        assert enterprise["included_users"] == 5, f"Expected 5 users, got {enterprise['included_users']}"
        assert enterprise["name"] == "Enterprise"
        print(f"✓ Enterprise tier: R{enterprise['price_monthly']}/month, {enterprise['included_users']} users")
    
    def test_tier_features_included(self):
        """Test that tiers include features array"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        for tier in tiers:
            assert "features" in tier, f"Tier {tier['id']} missing features"
            assert isinstance(tier["features"], list), f"Tier {tier['id']} features should be a list"
            assert len(tier["features"]) > 0, f"Tier {tier['id']} should have at least one feature"
        print("✓ All tiers have features array")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_admin_login(self):
        """Test admin user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == ADMIN_CREDS["email"]
        print(f"✓ Admin login successful: {data['user']['email']}")
    
    def test_recruiter_login(self):
        """Test recruiter user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_STARTER)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "recruiter"
        assert data["user"]["account_id"] is not None
        print(f"✓ Recruiter login successful: {data['user']['email']}")
    
    def test_invalid_login(self):
        """Test invalid credentials return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly returns 401")


class TestAccountEndpoint:
    """Tests for /api/account endpoint - Recruiter account details"""
    
    @pytest.fixture
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_STARTER)
        return response.json()["access_token"]
    
    def test_get_account_requires_auth(self):
        """Test /api/account requires authentication"""
        response = requests.get(f"{BASE_URL}/api/account")
        assert response.status_code in [401, 403]
        print("✓ Account endpoint requires authentication")
    
    def test_get_account_with_auth(self, recruiter_token):
        """Test /api/account returns account details for authenticated recruiter"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "tier_id" in data
        assert "tier_name" in data
        assert "subscription_status" in data
        assert "features" in data
        print(f"✓ Account details returned: {data['name']} ({data['tier_name']})")
    
    def test_admin_cannot_access_account(self):
        """Test admin user cannot access /api/account (no account_id)"""
        # Login as admin
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        admin_token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        # Admin should get 403 because they don't have an account_id
        assert response.status_code == 403
        print("✓ Admin correctly denied access to /api/account")


class TestPaymentSubscription:
    """Tests for /api/payments/subscription endpoint"""
    
    @pytest.fixture
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_STARTER)
        return response.json()["access_token"]
    
    def test_subscription_requires_auth(self):
        """Test subscription endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/payments/subscription", json={
            "tier_id": "growth",
            "billing_cycle": "monthly"
        })
        assert response.status_code in [401, 403]
        print("✓ Subscription endpoint requires authentication")
    
    def test_initiate_subscription_payment(self, recruiter_token):
        """Test initiating subscription payment returns Payfast data"""
        headers = {
            "Authorization": f"Bearer {recruiter_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(f"{BASE_URL}/api/payments/subscription", 
            headers=headers,
            json={"tier_id": "growth", "billing_cycle": "monthly"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "payment_id" in data
        assert "payfast_url" in data
        assert "payfast_data" in data
        
        # Verify Payfast data structure
        payfast_data = data["payfast_data"]
        assert "merchant_id" in payfast_data
        assert "merchant_key" in payfast_data
        assert "return_url" in payfast_data
        assert "cancel_url" in payfast_data
        assert "amount" in payfast_data
        assert "signature" in payfast_data
        
        # Verify amount matches Growth tier
        assert payfast_data["amount"] == "10499.00", f"Expected 10499.00, got {payfast_data['amount']}"
        print(f"✓ Subscription payment initiated: {data['payment_id']}")
        print(f"  Amount: R{payfast_data['amount']}")
        print(f"  Return URL: {payfast_data['return_url']}")
    
    def test_subscription_payment_correct_tier_amount(self, recruiter_token):
        """Test subscription payment uses correct tier amount"""
        headers = {
            "Authorization": f"Bearer {recruiter_token}",
            "Content-Type": "application/json"
        }
        
        # Test Pro tier
        response = requests.post(f"{BASE_URL}/api/payments/subscription", 
            headers=headers,
            json={"tier_id": "pro", "billing_cycle": "monthly"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payfast_data"]["amount"] == "19999.00"
        print(f"✓ Pro tier payment amount correct: R{data['payfast_data']['amount']}")


class TestPublicEndpoints:
    """Tests for public endpoints (no auth required)"""
    
    def test_public_jobs_no_auth(self):
        """Test /api/public/jobs accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/public/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        print(f"✓ Public jobs accessible: {data['total']} jobs found")
    
    def test_tiers_no_auth(self):
        """Test /api/tiers accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/tiers")
        assert response.status_code == 200
        
        tiers = response.json()
        assert len(tiers) == 4
        print("✓ Tiers endpoint accessible without auth")


class TestRecruitersByTier:
    """Test different recruiter accounts by tier"""
    
    def test_starter_recruiter_account(self):
        """Test Starter tier recruiter account"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_STARTER)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        account_response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        assert account_response.status_code == 200
        
        account = account_response.json()
        assert account["tier_id"] == "starter"
        assert account["tier_name"] == "Starter"
        print(f"✓ Starter recruiter: {account['name']} - {account['tier_name']}")
    
    def test_growth_recruiter_account(self):
        """Test Growth tier recruiter account"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_GROWTH)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        account_response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        assert account_response.status_code == 200
        
        account = account_response.json()
        assert account["tier_id"] == "growth"
        assert account["tier_name"] == "Growth"
        print(f"✓ Growth recruiter: {account['name']} - {account['tier_name']}")
    
    def test_pro_recruiter_account(self):
        """Test Pro tier recruiter account"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_PRO)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        account_response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        assert account_response.status_code == 200
        
        account = account_response.json()
        assert account["tier_id"] == "pro"
        assert account["tier_name"] == "Pro"
        print(f"✓ Pro recruiter: {account['name']} - {account['tier_name']}")
    
    def test_enterprise_recruiter_account(self):
        """Test Enterprise tier recruiter account"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_ENTERPRISE)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        account_response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        assert account_response.status_code == 200
        
        account = account_response.json()
        assert account["tier_id"] == "enterprise"
        assert account["tier_name"] == "Enterprise"
        print(f"✓ Enterprise recruiter: {account['name']} - {account['tier_name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
