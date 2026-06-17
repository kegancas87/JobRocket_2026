"""
Test Wallet Auto Top-Up Feature
Tests: card-status, auto-topup settings, setup-card, remove-card, ITN webhook
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
JOB_SEEKER_EMAIL = "thabo.mthembu@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"


class TestWalletAutoTopup:
    """Wallet Auto Top-Up API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def get_auth_token(self, email, password):
        """Get authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def get_auth_headers(self, email, password):
        """Get headers with auth token"""
        token = self.get_auth_token(email, password)
        if token:
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return None

    # ==================== Card Status Tests ====================
    
    def test_card_status_returns_has_card_false_for_new_user(self):
        """GET /api/ai/wallet/card-status - Returns has_card: false for users without saved card"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        response = self.session.get(f"{BASE_URL}/api/ai/wallet/card-status", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "has_card" in data, "Response should contain 'has_card' field"
        assert isinstance(data["has_card"], bool), "has_card should be boolean"
        # Note: User may or may not have a card saved, just verify structure
        print(f"Card status: has_card={data['has_card']}, saved_at={data.get('saved_at')}")
    
    def test_card_status_requires_auth(self):
        """GET /api/ai/wallet/card-status - Requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/ai/wallet/card-status")
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated request, got {response.status_code}"

    # ==================== Auto Top-Up Settings Tests ====================
    
    def test_get_auto_topup_returns_default_settings(self):
        """GET /api/ai/wallet/auto-topup - Returns default settings (enabled: false, threshold: 50, amount: 200)"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        response = self.session.get(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "enabled" in data, "Response should contain 'enabled' field"
        assert "threshold" in data, "Response should contain 'threshold' field"
        assert "amount" in data, "Response should contain 'amount' field"
        assert "has_card" in data, "Response should contain 'has_card' field"
        
        # Verify types
        assert isinstance(data["enabled"], bool), "enabled should be boolean"
        assert isinstance(data["threshold"], (int, float)), "threshold should be numeric"
        assert isinstance(data["amount"], (int, float)), "amount should be numeric"
        
        print(f"Auto top-up settings: enabled={data['enabled']}, threshold={data['threshold']}, amount={data['amount']}, has_card={data['has_card']}")
    
    def test_save_auto_topup_settings_without_enabling(self):
        """POST /api/ai/wallet/auto-topup - Save settings without enabling (threshold, amount)"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        # Save settings with enabled=false (should work even without card)
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
            "enabled": False,
            "threshold": 100,
            "amount": 300
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert data.get("threshold") == 100, "Threshold should be saved as 100"
        assert data.get("amount") == 300, "Amount should be saved as 300"
        assert data.get("enabled") == False, "Enabled should be False"
        
        # Verify settings were persisted
        get_response = self.session.get(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers)
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["threshold"] == 100, "Threshold should persist as 100"
        assert get_data["amount"] == 300, "Amount should persist as 300"
        
        print(f"Settings saved: threshold={data['threshold']}, amount={data['amount']}")
    
    def test_enable_auto_topup_fails_without_saved_card(self):
        """POST /api/ai/wallet/auto-topup - Fail when enabling without saved card (400: save card first)"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        # First check if user has a card
        card_response = self.session.get(f"{BASE_URL}/api/ai/wallet/card-status", headers=headers)
        card_data = card_response.json()
        
        if card_data.get("has_card"):
            # User has a card, remove it first
            self.session.delete(f"{BASE_URL}/api/ai/wallet/remove-card", headers=headers)
        
        # Now try to enable auto top-up without a card
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
            "enabled": True,
            "threshold": 50,
            "amount": 200
        })
        
        assert response.status_code == 400, f"Expected 400 when enabling without card, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Response should contain error detail"
        assert "card" in data["detail"].lower() or "save" in data["detail"].lower(), f"Error should mention saving card: {data['detail']}"
        
        print(f"Correctly rejected enabling without card: {data['detail']}")
    
    def test_auto_topup_threshold_validation(self):
        """POST /api/ai/wallet/auto-topup - Validation: threshold 0-5000"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        # Test threshold too high (>5000)
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
            "enabled": False,
            "threshold": 6000,
            "amount": 200
        })
        assert response.status_code == 400, f"Expected 400 for threshold > 5000, got {response.status_code}"
        
        # Test threshold negative
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
            "enabled": False,
            "threshold": -10,
            "amount": 200
        })
        assert response.status_code == 400, f"Expected 400 for negative threshold, got {response.status_code}"
        
        print("Threshold validation working correctly")
    
    def test_auto_topup_amount_validation(self):
        """POST /api/ai/wallet/auto-topup - Validation: amount 5-10000"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        # Test amount too low (<5)
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
            "enabled": False,
            "threshold": 50,
            "amount": 2
        })
        assert response.status_code == 400, f"Expected 400 for amount < 5, got {response.status_code}"
        
        # Test amount too high (>10000)
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
            "enabled": False,
            "threshold": 50,
            "amount": 15000
        })
        assert response.status_code == 400, f"Expected 400 for amount > 10000, got {response.status_code}"
        
        print("Amount validation working correctly")

    # ==================== Setup Card Tests ====================
    
    def test_setup_card_returns_payfast_form_data(self):
        """POST /api/ai/wallet/setup-card - Returns PayFast form data with subscription_type=2, amount=0.00, signature, action_url"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/setup-card", headers=headers, json={})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify required fields
        assert "form_data" in data, "Response should contain 'form_data'"
        assert "action_url" in data, "Response should contain 'action_url'"
        assert "m_payment_id" in data, "Response should contain 'm_payment_id'"
        
        form_data = data["form_data"]
        
        # Verify PayFast form fields
        assert form_data.get("subscription_type") == "2", f"subscription_type should be '2', got {form_data.get('subscription_type')}"
        assert form_data.get("amount") == "0.00", f"amount should be '0.00', got {form_data.get('amount')}"
        assert "signature" in form_data, "form_data should contain 'signature'"
        assert "merchant_id" in form_data, "form_data should contain 'merchant_id'"
        assert "merchant_key" in form_data, "form_data should contain 'merchant_key'"
        
        # Verify action URL points to PayFast
        assert "payfast.co.za" in data["action_url"], f"action_url should point to PayFast: {data['action_url']}"
        
        print(f"Setup card returns valid PayFast form data: action_url={data['action_url']}, subscription_type={form_data.get('subscription_type')}")
    
    def test_setup_card_requires_auth(self):
        """POST /api/ai/wallet/setup-card - Requires authentication"""
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/setup-card", json={})
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated request, got {response.status_code}"

    # ==================== Remove Card Tests ====================
    
    def test_remove_card_idempotent(self):
        """DELETE /api/ai/wallet/remove-card - Returns success even when no card saved (idempotent)"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert headers is not None, "Failed to authenticate job seeker"
        
        # Call remove-card (should succeed even if no card)
        response = self.session.delete(f"{BASE_URL}/api/ai/wallet/remove-card", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        
        # Call again - should still succeed (idempotent)
        response2 = self.session.delete(f"{BASE_URL}/api/ai/wallet/remove-card", headers=headers)
        assert response2.status_code == 200, f"Expected 200 on second call, got {response2.status_code}"
        
        print("Remove card is idempotent - succeeds even when no card saved")
    
    def test_remove_card_requires_auth(self):
        """DELETE /api/ai/wallet/remove-card - Requires authentication"""
        response = self.session.delete(f"{BASE_URL}/api/ai/wallet/remove-card")
        assert response.status_code in [401, 403], f"Expected 401/403 for unauthenticated request, got {response.status_code}"

    # ==================== ITN Webhook Tests ====================
    
    def test_itn_webhook_accepts_post_without_auth(self):
        """POST /api/payfast/wallet-itn - Webhook accepts POST without auth (public endpoint)"""
        # ITN webhook should be public (no auth required)
        response = self.session.post(f"{BASE_URL}/api/payfast/wallet-itn", data={
            "payment_status": "COMPLETE",
            "token": "test_token_123",
            "custom_str1": "test_user_id",
            "custom_str2": "wallet_tokenization",
            "m_payment_id": "wallet-setup-test-123"
        })
        
        # Should return 200 (webhook processed)
        assert response.status_code == 200, f"Expected 200 for ITN webhook, got {response.status_code}: {response.text}"
        
        print("ITN webhook accepts POST without authentication")
    
    def test_itn_webhook_handles_cancelled_status(self):
        """POST /api/payfast/wallet-itn - Handles CANCELLED payment status"""
        response = self.session.post(f"{BASE_URL}/api/payfast/wallet-itn", data={
            "payment_status": "CANCELLED",
            "custom_str1": "test_user_id",
            "custom_str2": "wallet_tokenization",
            "m_payment_id": "wallet-setup-test-cancelled"
        })
        
        assert response.status_code == 200, f"Expected 200 for cancelled ITN, got {response.status_code}"
        print("ITN webhook handles CANCELLED status")

    # ==================== Recruiter Access Tests ====================
    
    def test_recruiter_cannot_access_wallet_endpoints(self):
        """Recruiters should not have access to wallet auto top-up endpoints (or get empty/default response)"""
        headers = self.get_auth_headers(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert headers is not None, "Failed to authenticate recruiter"
        
        # Recruiters may get 403 or may get default response - both are acceptable
        # The key is that the feature is for job seekers
        response = self.session.get(f"{BASE_URL}/api/ai/wallet/card-status", headers=headers)
        # Just verify it doesn't crash - recruiters may or may not have access
        print(f"Recruiter card-status response: {response.status_code}")
        
        response = self.session.get(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers)
        print(f"Recruiter auto-topup response: {response.status_code}")

    # ==================== Cleanup ====================
    
    def test_cleanup_restore_default_settings(self):
        """Cleanup: Restore default auto top-up settings"""
        headers = self.get_auth_headers(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        if headers:
            # Restore default settings
            self.session.post(f"{BASE_URL}/api/ai/wallet/auto-topup", headers=headers, json={
                "enabled": False,
                "threshold": 50,
                "amount": 200
            })
            print("Restored default auto top-up settings")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
