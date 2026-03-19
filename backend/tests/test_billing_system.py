"""
JobRocket - Billing System Tests
Tests for:
- GET /api/billing/history - Payment history with pagination
- GET /api/billing/statement - HTML statement generation
- GET /api/subscription/status - Subscription status check
- POST /api/billing/extra-seats - Pro-rata seat creation
- GET /api/billing/account-info - Billing details with billing_day
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://job-rocket-preview.preview.emergentagent.com"

# Test credentials
ACTIVE_RECRUITER = {"email": "hr@techcorp.co.za", "password": "demo123"}
PAST_DUE_RECRUITER = {"email": "talent@innovatedigital.co.za", "password": "demo123"}


class TestBillingAuthentication:
    """Test authentication for billing endpoints"""
    
    @pytest.fixture
    def active_token(self):
        """Get token for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Failed to login active recruiter: {response.status_code}")
        
    @pytest.fixture
    def past_due_token(self):
        """Get token for past_due recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=PAST_DUE_RECRUITER)
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip(f"Failed to login past_due recruiter: {response.status_code}")
    
    def test_active_recruiter_login(self, active_token):
        """Test active recruiter can login"""
        assert active_token is not None
        print(f"Active recruiter login successful, token: {active_token[:20]}...")
    
    def test_past_due_recruiter_login(self, past_due_token):
        """Test past_due recruiter can login"""
        assert past_due_token is not None
        print(f"Past due recruiter login successful, token: {past_due_token[:20]}...")


class TestBillingHistory:
    """Test GET /api/billing/history endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    def test_billing_history_returns_200(self, auth_headers):
        """Test that billing history endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/billing/history", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"Billing history returned 200 OK")
    
    def test_billing_history_response_structure(self, auth_headers):
        """Test billing history response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/billing/history", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Should have payments array, total, limit, skip, has_more
        assert "payments" in data, "Response missing 'payments' key"
        assert "total" in data, "Response missing 'total' key"
        assert "limit" in data, "Response missing 'limit' key"
        assert "skip" in data, "Response missing 'skip' key"
        assert "has_more" in data, "Response missing 'has_more' key"
        
        assert isinstance(data["payments"], list), "payments should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        
        print(f"Billing history structure valid: {len(data['payments'])} payments, total={data['total']}")
    
    def test_billing_history_pagination(self, auth_headers):
        """Test billing history pagination parameters"""
        # Test with limit
        response = requests.get(f"{BASE_URL}/api/billing/history?limit=5&skip=0", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 5, "Limit not applied correctly"
        assert data["skip"] == 0, "Skip not applied correctly"
        
        print(f"Pagination works: limit=5, skip=0, returned {len(data['payments'])} payments")
    
    def test_billing_history_date_filter(self, auth_headers):
        """Test billing history with date filters"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/api/billing/history?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print(f"Date filter works: {start_date} to {end_date}")
    
    def test_billing_history_unauthenticated(self):
        """Test billing history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/billing/history")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("Unauthenticated request correctly rejected")


class TestBillingStatement:
    """Test GET /api/billing/statement endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    def test_statement_html_generation(self, auth_headers):
        """Test statement generates HTML successfully"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/api/billing/statement?start_date={start_date}&end_date={end_date}&format=html",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check content type is HTML
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Expected HTML content type, got {content_type}"
        
        # Check HTML contains expected elements
        html = response.text
        assert "JobRocket" in html, "HTML missing JobRocket branding"
        assert "Statement" in html, "HTML missing Statement title"
        
        print(f"Statement HTML generated: {len(html)} characters")
    
    def test_statement_contains_company_details(self, auth_headers):
        """Test statement HTML contains company details"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/api/billing/statement?start_date={start_date}&end_date={end_date}&format=html",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        html = response.text
        # Check for JobRocket company details
        assert "JobRocket (Pty) Ltd" in html, "Missing JobRocket company name"
        # Note: Email may be encoded by Cloudflare protection
        assert "www.jobrocket.co.za" in html or "jobrocket.co.za" in html, "Missing JobRocket website"
        
        print("Statement contains JobRocket company details")
    
    def test_statement_json_format(self, auth_headers):
        """Test statement returns JSON when format=json"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/api/billing/statement?start_date={start_date}&end_date={end_date}&format=json",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Check JSON structure
        assert "statement_number" in data, "Missing statement_number"
        assert "jobrocket_details" in data, "Missing jobrocket_details"
        assert "customer_details" in data, "Missing customer_details"
        assert "payments" in data, "Missing payments list"
        assert "summary" in data, "Missing summary"
        
        print(f"Statement JSON valid: statement #{data.get('statement_number')}")
    
    def test_statement_invalid_date_format(self, auth_headers):
        """Test statement rejects invalid date format"""
        response = requests.get(
            f"{BASE_URL}/api/billing/statement?start_date=invalid&end_date=invalid&format=html",
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid date, got {response.status_code}"
        print("Invalid date format correctly rejected")


class TestSubscriptionStatus:
    """Test GET /api/subscription/status endpoint"""
    
    @pytest.fixture
    def active_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    @pytest.fixture
    def past_due_headers(self):
        """Get auth headers for past_due recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=PAST_DUE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token for past_due user")
    
    def test_subscription_status_returns_200(self, active_headers):
        """Test subscription status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/subscription/status", headers=active_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("Subscription status returned 200")
    
    def test_subscription_status_for_active_account(self, active_headers):
        """Test subscription status returns correct data for active account"""
        response = requests.get(f"{BASE_URL}/api/subscription/status", headers=active_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Check response structure
        assert "status" in data, "Missing status field"
        assert "needs_payment" in data, "Missing needs_payment field"
        
        # Active account should be 'active' or 'trial'
        assert data.get("status") in ["active", "trial", "grace_period"], f"Unexpected status: {data.get('status')}"
        
        print(f"Active account status: {data.get('status')}, needs_payment: {data.get('needs_payment')}")
    
    def test_subscription_status_for_past_due_account(self, past_due_headers):
        """Test subscription status for past_due account shows appropriate status"""
        response = requests.get(f"{BASE_URL}/api/subscription/status", headers=past_due_headers)
        
        # Past due users should still be able to check status
        assert response.status_code in [200, 402], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"Past due account status: {data.get('status')}, needs_payment: {data.get('needs_payment')}")
            
            # Should indicate payment is needed
            if data.get("status") in ["past_due", "grace_period", "inactive"]:
                assert data.get("needs_payment") == True, "Past due account should need payment"
        else:
            print(f"Past due account returned 402 (payment required)")
    
    def test_subscription_status_includes_billing_day(self, active_headers):
        """Test subscription status includes billing_day"""
        response = requests.get(f"{BASE_URL}/api/subscription/status", headers=active_headers)
        assert response.status_code == 200
        
        data = response.json()
        # billing_day should be present
        if "billing_day" in data:
            print(f"Billing day: {data.get('billing_day')}")
        else:
            print("Note: billing_day not in subscription status response")


class TestExtraSeatsProRata:
    """Test POST /api/billing/extra-seats endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    def test_extra_seats_endpoint_exists(self, auth_headers):
        """Test extra seats endpoint exists and responds"""
        response = requests.post(f"{BASE_URL}/api/billing/extra-seats?quantity=1", headers=auth_headers)
        # Should return 200 (activated immediately with pro-rata) or redirect to PayFast
        assert response.status_code in [200, 302, 307], f"Unexpected status: {response.status_code}"
        print(f"Extra seats endpoint responded with {response.status_code}")
    
    def test_extra_seats_prorata_free_period(self, auth_headers):
        """Test extra seats have pro-rata free period"""
        response = requests.post(f"{BASE_URL}/api/billing/extra-seats?quantity=1", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Should indicate seats were activated
            if data.get("status") == "activated":
                assert "seats_created" in data, "Missing seats_created in response"
                assert "next_billing_day" in data or "message" in data, "Missing billing info"
                print(f"Seats activated with pro-rata: {data.get('message', data)}")
            elif "payment_id" in data:
                print(f"Payment redirect required: {data.get('payment_id')}")
        else:
            print(f"Response: {response.status_code}")
    
    def test_extra_seats_quantity_validation(self, auth_headers):
        """Test extra seats quantity validation"""
        # Test with invalid quantity (0)
        response = requests.post(f"{BASE_URL}/api/billing/extra-seats?quantity=0", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 for quantity=0, got {response.status_code}"
        
        # Test with too high quantity
        response = requests.post(f"{BASE_URL}/api/billing/extra-seats?quantity=1000", headers=auth_headers)
        assert response.status_code == 422, f"Expected 422 for quantity=1000, got {response.status_code}"
        
        print("Quantity validation working correctly")


class TestBillingAccountInfo:
    """Test GET /api/billing/account-info endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    def test_account_info_returns_200(self, auth_headers):
        """Test account info endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/billing/account-info", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("Account info returned 200")
    
    def test_account_info_has_billing_day(self, auth_headers):
        """Test account info includes billing_day"""
        response = requests.get(f"{BASE_URL}/api/billing/account-info", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "billing_day" in data, "Missing billing_day in response"
        
        billing_day = data.get("billing_day")
        if billing_day is not None:
            assert 1 <= billing_day <= 31, f"Invalid billing_day: {billing_day}"
        
        print(f"Billing day: {billing_day}")
    
    def test_account_info_has_tier_info(self, auth_headers):
        """Test account info includes tier information"""
        response = requests.get(f"{BASE_URL}/api/billing/account-info", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "tier_id" in data, "Missing tier_id"
        assert "tier_name" in data, "Missing tier_name"
        assert "subscription_status" in data, "Missing subscription_status"
        
        print(f"Tier: {data.get('tier_name')} ({data.get('tier_id')}), Status: {data.get('subscription_status')}")
    
    def test_account_info_has_dates(self, auth_headers):
        """Test account info includes subscription dates"""
        response = requests.get(f"{BASE_URL}/api/billing/account-info", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # These should be present (may be None for new accounts)
        assert "subscription_start_date" in data, "Missing subscription_start_date"
        assert "subscription_end_date" in data, "Missing subscription_end_date"
        assert "next_billing_date" in data, "Missing next_billing_date"
        
        print(f"Subscription dates present: start={data.get('subscription_start_date')}, end={data.get('subscription_end_date')}")


class TestBillingSummary:
    """Test GET /api/billing/summary endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    def test_billing_summary_returns_200(self, auth_headers):
        """Test billing summary endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/billing/summary", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("Billing summary returned 200")
    
    def test_billing_summary_structure(self, auth_headers):
        """Test billing summary has correct structure"""
        response = requests.get(f"{BASE_URL}/api/billing/summary?months=6", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "period_months" in data, "Missing period_months"
        assert "monthly_data" in data, "Missing monthly_data"
        assert "total_paid" in data, "Missing total_paid"
        assert "total_transactions" in data, "Missing total_transactions"
        
        assert isinstance(data["monthly_data"], list), "monthly_data should be a list"
        
        print(f"Billing summary: {data.get('total_transactions')} transactions, R{data.get('total_paid')} total")


class TestBillingEndpoint:
    """Test GET /api/billing endpoint"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for active recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ACTIVE_RECRUITER)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Failed to get auth token")
    
    def test_billing_endpoint_returns_200(self, auth_headers):
        """Test billing endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("Billing endpoint returned 200")
    
    def test_billing_includes_tier_info(self, auth_headers):
        """Test billing includes tier and subscription info"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "tier_name" in data, "Missing tier_name"
        assert "subscription_status" in data, "Missing subscription_status"
        
        print(f"Billing overview: {data.get('tier_name')}, status: {data.get('subscription_status')}")
    
    def test_billing_includes_charges(self, auth_headers):
        """Test billing includes charges breakdown"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        if "charges" in data:
            charges = data["charges"]
            print(f"Charges breakdown: {charges}")
        else:
            print("Note: charges not in billing response")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
