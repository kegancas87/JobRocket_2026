"""
Test Billing Cycle Enforcement Features
- Admin subscription overview endpoint
- Admin account reactivation endpoint
- /api/auth/me subscription_status and grace_days_remaining
- Payment webhook handling for recurring ITN (COMPLETE and FAILED)
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from iteration_12.json
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"
ADMIN_EMAIL = "admin@jobrocket.co.za"
ADMIN_PASSWORD = "admin123"


class TestBillingCycleEnforcement:
    """Tests for billing cycle enforcement features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_recruiter_token(self):
        """Login as recruiter and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def get_admin_token(self):
        """Login as admin and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    # ============================================
    # Test 1: Admin subscription-overview endpoint
    # ============================================
    def test_admin_subscription_overview_returns_status_counts(self):
        """GET /api/admin/subscription-overview returns status_counts, grace_period_accounts, suspended_accounts"""
        token = self.get_admin_token()
        assert token is not None, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/subscription-overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify status_counts structure
        assert "status_counts" in data, "Response missing status_counts"
        status_counts = data["status_counts"]
        assert "active" in status_counts, "status_counts missing 'active'"
        assert "trial" in status_counts, "status_counts missing 'trial'"
        assert "past_due" in status_counts, "status_counts missing 'past_due'"
        assert "inactive" in status_counts, "status_counts missing 'inactive'"
        assert "free" in status_counts, "status_counts missing 'free'"
        assert "pending" in status_counts, "status_counts missing 'pending'"
        
        # Verify grace_period_accounts and suspended_accounts are lists
        assert "grace_period_accounts" in data, "Response missing grace_period_accounts"
        assert "suspended_accounts" in data, "Response missing suspended_accounts"
        assert isinstance(data["grace_period_accounts"], list), "grace_period_accounts should be a list"
        assert isinstance(data["suspended_accounts"], list), "suspended_accounts should be a list"
        
        print(f"✓ Admin subscription overview: {status_counts}")
        print(f"  Grace period accounts: {len(data['grace_period_accounts'])}")
        print(f"  Suspended accounts: {len(data['suspended_accounts'])}")
    
    def test_admin_subscription_overview_requires_admin(self):
        """GET /api/admin/subscription-overview should reject non-admin users"""
        token = self.get_recruiter_token()
        assert token is not None, "Recruiter login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/subscription-overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be 403 Forbidden for non-admin
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ Admin subscription overview correctly rejects non-admin users")
    
    # ============================================
    # Test 2: /api/auth/me returns subscription_status
    # ============================================
    def test_auth_me_returns_subscription_status_for_recruiter(self):
        """GET /api/auth/me returns subscription_status in account object for recruiters"""
        token = self.get_recruiter_token()
        assert token is not None, "Recruiter login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify account object exists
        assert "account" in data, "Response missing account object"
        account = data["account"]
        
        # Verify subscription_status is present
        assert "subscription_status" in account, "Account missing subscription_status"
        
        # Verify subscription_status is a valid value
        valid_statuses = ["active", "trial", "past_due", "inactive", "pending", "cancelled", "expired"]
        assert account["subscription_status"] in valid_statuses, f"Invalid subscription_status: {account['subscription_status']}"
        
        print(f"✓ /api/auth/me returns subscription_status: {account['subscription_status']}")
        print(f"  Tier: {account.get('tier_id', 'N/A')}")
        
        # If past_due, check for grace_days_remaining
        if account["subscription_status"] == "past_due":
            assert "grace_days_remaining" in account, "past_due account should have grace_days_remaining"
            print(f"  Grace days remaining: {account['grace_days_remaining']}")
    
    # ============================================
    # Test 3: Admin reactivate endpoint
    # ============================================
    def test_admin_reactivate_endpoint_exists(self):
        """POST /api/admin/accounts/{account_id}/reactivate endpoint exists"""
        token = self.get_admin_token()
        assert token is not None, "Admin login failed"
        
        # Use a fake account_id to test endpoint existence
        fake_account_id = "test-nonexistent-account-id"
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/accounts/{fake_account_id}/reactivate",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should return 404 for non-existent account, not 405 (method not allowed)
        assert response.status_code in [404, 200], f"Expected 404 or 200, got {response.status_code}: {response.text}"
        print("✓ Admin reactivate endpoint exists and responds correctly")
    
    def test_admin_reactivate_requires_admin(self):
        """POST /api/admin/accounts/{account_id}/reactivate should reject non-admin users"""
        token = self.get_recruiter_token()
        assert token is not None, "Recruiter login failed"
        
        fake_account_id = "test-account-id"
        
        response = self.session.post(
            f"{BASE_URL}/api/admin/accounts/{fake_account_id}/reactivate",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be 403 Forbidden for non-admin
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ Admin reactivate endpoint correctly rejects non-admin users")
    
    # ============================================
    # Test 4: Payment webhook endpoint exists
    # ============================================
    def test_payment_webhook_endpoint_exists(self):
        """POST /api/payments/webhook endpoint exists and accepts form data"""
        # Send minimal form data to test endpoint existence
        response = self.session.post(
            f"{BASE_URL}/api/payments/webhook",
            data={
                "m_payment_id": "test-payment-id",
                "payment_status": "COMPLETE"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should return 200 with status (even if payment not found)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Response should have status field"
        print(f"✓ Payment webhook endpoint exists, response: {data}")
    
    def test_payment_webhook_handles_token_based_recurring(self):
        """POST /api/payments/webhook handles token-based recurring ITN"""
        # Test with a token (no m_payment_id) - simulates recurring payment
        response = self.session.post(
            f"{BASE_URL}/api/payments/webhook",
            data={
                "token": "test-nonexistent-token",
                "payment_status": "COMPLETE",
                "amount_gross": "999.00"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should return 200 (even if account not found for token)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # When token not found, should return error message
        if data.get("status") == "error":
            assert "message" in data, "Error response should have message"
            print(f"✓ Payment webhook handles token-based ITN (token not found as expected): {data}")
        else:
            print(f"✓ Payment webhook handles token-based ITN: {data}")
    
    # ============================================
    # Test 5: Verify recruiter account data structure
    # ============================================
    def test_recruiter_account_has_required_fields(self):
        """Verify recruiter account has all required billing fields"""
        token = self.get_recruiter_token()
        assert token is not None, "Recruiter login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "account" in data, "Response missing account"
        account = data["account"]
        
        # Check required fields for billing cycle enforcement
        required_fields = ["id", "name", "tier_id", "subscription_status"]
        for field in required_fields:
            assert field in account, f"Account missing required field: {field}"
        
        print(f"✓ Recruiter account has all required fields")
        print(f"  Account ID: {account['id']}")
        print(f"  Company: {account['name']}")
        print(f"  Tier: {account['tier_id']}")
        print(f"  Status: {account['subscription_status']}")
        
        # Check optional billing fields
        optional_fields = ["subscription_end_date", "grace_days_remaining", "grace_period_end"]
        for field in optional_fields:
            if field in account:
                print(f"  {field}: {account[field]}")


class TestAdminDashboardIntegration:
    """Integration tests for admin dashboard subscription features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_admin_token(self):
        """Login as admin and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def test_admin_can_view_all_subscription_statuses(self):
        """Admin can view counts for all subscription statuses"""
        token = self.get_admin_token()
        assert token is not None, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/subscription-overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        status_counts = data["status_counts"]
        total_accounts = sum(status_counts.values())
        
        print(f"✓ Admin subscription overview:")
        print(f"  Total accounts: {total_accounts}")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
    
    def test_grace_period_accounts_have_days_remaining(self):
        """Grace period accounts include grace_days_remaining field"""
        token = self.get_admin_token()
        assert token is not None, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/subscription-overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        grace_accounts = data["grace_period_accounts"]
        
        if len(grace_accounts) > 0:
            for acc in grace_accounts:
                assert "id" in acc, "Grace period account missing id"
                assert "name" in acc, "Grace period account missing name"
                assert "grace_days_remaining" in acc, "Grace period account missing grace_days_remaining"
                print(f"✓ Grace period account: {acc['name']} - {acc['grace_days_remaining']} days remaining")
        else:
            print("✓ No accounts currently in grace period (expected for clean state)")
    
    def test_suspended_accounts_have_deactivation_info(self):
        """Suspended accounts include deactivation details"""
        token = self.get_admin_token()
        assert token is not None, "Admin login failed"
        
        response = self.session.get(
            f"{BASE_URL}/api/admin/subscription-overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        suspended_accounts = data["suspended_accounts"]
        
        if len(suspended_accounts) > 0:
            for acc in suspended_accounts:
                assert "id" in acc, "Suspended account missing id"
                assert "name" in acc, "Suspended account missing name"
                print(f"✓ Suspended account: {acc['name']}")
                if "deactivation_reason" in acc:
                    print(f"  Reason: {acc['deactivation_reason']}")
                if "deactivated_at" in acc:
                    print(f"  Deactivated at: {acc['deactivated_at']}")
        else:
            print("✓ No suspended accounts (expected for clean state)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
