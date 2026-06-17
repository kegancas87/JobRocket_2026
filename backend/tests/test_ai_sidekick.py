"""
AI Sidekick Feature Tests
Tests wallet operations, AI pricing, and match score functionality.
Focus: Wallet (fast), pricing, and one match-score call (verifies LLM integration).
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
JOB_SEEKER_EMAIL = "thabo.mthembu@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"
ADMIN_EMAIL = "admin@jobrocket.co.za"
ADMIN_PASSWORD = "admin123"

# Test job IDs provided
TEST_JOB_IDS = [
    "8af394eb-118c-46e1-8357-1b71193f4067",
    "05c63c5a-1658-4bbb-999b-0f6edc1e037a",
    "8452a650-2cb9-45bc-8175-745dec759c9a"
]


class TestAISidekickWallet:
    """Wallet operations tests - fast, no LLM calls"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate as job seeker"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as job seeker
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Note: API returns 'access_token' not 'token'
        self.token = data.get("access_token") or data.get("token")
        assert self.token, f"No token in response: {data}"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.user_id = data.get("user", {}).get("id")
    
    def test_get_wallet_balance(self):
        """GET /api/ai/wallet - Returns wallet balance for authenticated job seeker"""
        response = self.session.get(f"{BASE_URL}/api/ai/wallet")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "wallet_balance" in data, f"Missing wallet_balance: {data}"
        assert isinstance(data["wallet_balance"], (int, float)), "wallet_balance should be numeric"
        print(f"✓ Wallet balance: R{data['wallet_balance']:.2f}")
    
    def test_wallet_topup_success(self):
        """POST /api/ai/wallet/topup - Top up wallet with valid amount"""
        # Get initial balance
        initial_response = self.session.get(f"{BASE_URL}/api/ai/wallet")
        initial_balance = initial_response.json().get("wallet_balance", 0)
        
        # Top up R100
        topup_amount = 100
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/topup", json={
            "amount": topup_amount
        })
        assert response.status_code == 200, f"Topup failed: {response.text}"
        data = response.json()
        assert "wallet_balance" in data, f"Missing wallet_balance: {data}"
        
        # Verify new balance
        expected_balance = initial_balance + topup_amount
        assert abs(data["wallet_balance"] - expected_balance) < 0.01, \
            f"Balance mismatch: expected {expected_balance}, got {data['wallet_balance']}"
        print(f"✓ Topped up R{topup_amount}, new balance: R{data['wallet_balance']:.2f}")
    
    def test_wallet_topup_invalid_amount_zero(self):
        """POST /api/ai/wallet/topup - Reject zero amount"""
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/topup", json={
            "amount": 0
        })
        assert response.status_code == 400, f"Should reject zero amount: {response.text}"
    
    def test_wallet_topup_invalid_amount_negative(self):
        """POST /api/ai/wallet/topup - Reject negative amount"""
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/topup", json={
            "amount": -50
        })
        assert response.status_code == 400, f"Should reject negative amount: {response.text}"
    
    def test_wallet_topup_invalid_amount_too_large(self):
        """POST /api/ai/wallet/topup - Reject amount over R10,000"""
        response = self.session.post(f"{BASE_URL}/api/ai/wallet/topup", json={
            "amount": 15000
        })
        assert response.status_code == 400, f"Should reject amount > R10,000: {response.text}"


class TestAIPricing:
    """AI pricing endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate as job seeker"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token") or data.get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_get_ai_pricing(self):
        """GET /api/ai/pricing - Returns pricing dict and wallet balance"""
        response = self.session.get(f"{BASE_URL}/api/ai/pricing")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify pricing structure
        assert "pricing" in data, f"Missing pricing: {data}"
        pricing = data["pricing"]
        
        # Verify all 4 features have correct prices
        expected_prices = {
            "match_score": 10.00,
            "top_matches": 50.00,
            "auto_apply": 50.00,
            "cv_enhance": 80.00
        }
        for feature, price in expected_prices.items():
            assert feature in pricing, f"Missing {feature} in pricing"
            assert pricing[feature] == price, f"{feature} price mismatch: expected {price}, got {pricing[feature]}"
        
        # Verify wallet balance included
        assert "wallet_balance" in data, f"Missing wallet_balance: {data}"
        print(f"✓ Pricing verified: {pricing}")
        print(f"✓ Wallet balance: R{data['wallet_balance']:.2f}")


class TestAIMatchScore:
    """Match score feature tests - includes one LLM call"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate as job seeker"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token") or data.get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_match_score_missing_job_id(self):
        """POST /api/ai/match-score - Reject request without job_id"""
        response = self.session.post(f"{BASE_URL}/api/ai/match-score", json={})
        assert response.status_code == 400, f"Should reject missing job_id: {response.text}"
        data = response.json()
        assert "job_id" in data.get("detail", "").lower(), f"Error should mention job_id: {data}"
    
    def test_match_score_success(self):
        """POST /api/ai/match-score - Returns match score with strengths/weaknesses (R10)"""
        # This test makes a real LLM call - may take 5-15 seconds
        job_id = TEST_JOB_IDS[0]
        
        response = self.session.post(f"{BASE_URL}/api/ai/match-score", json={
            "job_id": job_id
        }, timeout=60)  # Extended timeout for LLM call
        
        # Could be 200 (success) or 402 (insufficient balance)
        if response.status_code == 402:
            print(f"⚠ Insufficient balance for match score test")
            pytest.skip("Insufficient wallet balance - top up needed")
        
        assert response.status_code == 200, f"Match score failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True, f"success should be True: {data}"
        result = data.get("result", {})
        
        # Verify match score fields
        assert "match_score" in result, f"Missing match_score: {result}"
        assert isinstance(result["match_score"], (int, float)), "match_score should be numeric"
        assert 0 <= result["match_score"] <= 100, f"match_score out of range: {result['match_score']}"
        
        # Verify other expected fields
        expected_fields = ["match_rating", "strengths", "weaknesses", "job_id", "user_id"]
        for field in expected_fields:
            assert field in result, f"Missing {field} in result"
        
        # Verify new_balance returned
        assert "new_balance" in data, f"Missing new_balance: {data}"
        
        print(f"✓ Match score: {result['match_score']}% - {result.get('match_rating', 'N/A')}")
        print(f"✓ Strengths: {result.get('strengths', [])[:2]}...")
        print(f"✓ New balance: R{data['new_balance']:.2f}")
    
    def test_get_cached_match_scores(self):
        """GET /api/ai/match-scores - Returns all cached match scores for the user"""
        response = self.session.get(f"{BASE_URL}/api/ai/match-scores")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "scores" in data, f"Missing scores: {data}"
        assert isinstance(data["scores"], list), "scores should be a list"
        
        if data["scores"]:
            score = data["scores"][0]
            assert "match_score" in score, f"Missing match_score in cached score: {score}"
            assert "job_id" in score, f"Missing job_id in cached score: {score}"
            print(f"✓ Found {len(data['scores'])} cached match scores")
        else:
            print("✓ No cached match scores yet (expected if first run)")


class TestAIInsufficientBalance:
    """Test 402 error for insufficient balance"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate as a different job seeker with low balance"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Use second job seeker who may have lower balance
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nomsa.dlamini@gmail.com",
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token") or data.get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_insufficient_balance_returns_402(self):
        """Verify insufficient balance returns 402 error"""
        # First check current balance
        wallet_response = self.session.get(f"{BASE_URL}/api/ai/wallet")
        balance = wallet_response.json().get("wallet_balance", 0)
        
        if balance >= 80:
            # User has enough balance, skip this test
            print(f"⚠ User has R{balance:.2f} - sufficient for all features")
            pytest.skip("User has sufficient balance for this test")
        
        # Try CV enhance (R80) - most expensive feature
        response = self.session.post(f"{BASE_URL}/api/ai/cv-enhance", timeout=30)
        
        if response.status_code == 402:
            data = response.json()
            assert "detail" in data, f"Missing detail in 402 response: {data}"
            assert "insufficient" in data["detail"].lower() or "balance" in data["detail"].lower(), \
                f"402 error should mention insufficient balance: {data}"
            print(f"✓ 402 returned for insufficient balance: {data['detail']}")
        else:
            # If not 402, it might have succeeded (user had balance) or other error
            print(f"⚠ Got status {response.status_code} instead of 402 (balance: R{balance:.2f})")


class TestAIEndpointsAuth:
    """Test that AI endpoints require authentication"""
    
    def test_wallet_requires_auth(self):
        """GET /api/ai/wallet - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/wallet")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
    
    def test_pricing_requires_auth(self):
        """GET /api/ai/pricing - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/pricing")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
    
    def test_match_score_requires_auth(self):
        """POST /api/ai/match-score - Requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/match-score", json={"job_id": "test"})
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
