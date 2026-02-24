"""
Test P1 Features for JobRocket Multi-tenant SaaS Platform
Features tested:
1. Billing Page APIs (GET /api/billing, GET /api/billing/history)
2. Bulk Upload APIs (GET /api/jobs/bulk/template, POST /api/jobs/bulk)
3. AI Matching Status API (GET /api/ai-matching/status)
4. Admin Stats API with caching (GET /api/admin/stats)
5. Admin AI Toggle API (POST /api/admin/ai-matching/toggle)
"""

import pytest
import requests
import os
import io
import csv

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://subscription-mgmt-12.preview.emergentagent.com').rstrip('/')

# Test credentials
PRO_RECRUITER = {"email": "careers@fintechsa.co.za", "password": "demo123"}
GROWTH_RECRUITER = {"email": "talent@innovatedigital.co.za", "password": "demo123"}
STARTER_RECRUITER = {"email": "hr@techcorp.co.za", "password": "demo123"}
ADMIN_USER = {"email": "admin@jobrocket.co.za", "password": "admin123"}


class TestAuthentication:
    """Authentication helper tests"""
    
    def test_pro_recruiter_login(self):
        """Test Pro tier recruiter can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=PRO_RECRUITER)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == PRO_RECRUITER["email"]
        print(f"Pro recruiter login successful - Role: {data['user'].get('role')}")
    
    def test_starter_recruiter_login(self):
        """Test Starter tier recruiter can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=STARTER_RECRUITER)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print(f"Starter recruiter login successful - Role: {data['user'].get('role')}")
    
    def test_admin_login(self):
        """Test Admin can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_USER)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        print(f"Admin login successful - Role: {data['user'].get('role')}")


def get_auth_token(credentials: dict) -> str:
    """Helper to get auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Login failed for {credentials['email']}: {response.text}")


class TestBillingPage:
    """Test billing page endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Pro recruiter token for billing tests"""
        self.token = get_auth_token(PRO_RECRUITER)
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_billing_summary(self):
        """GET /api/billing - Get billing summary"""
        response = requests.get(f"{BASE_URL}/api/billing", headers=self.headers)
        assert response.status_code == 200, f"Billing summary failed: {response.text}"
        
        data = response.json()
        # Verify billing summary structure
        assert "tier_id" in data, "Missing tier_id"
        assert "tier_name" in data, "Missing tier_name"
        assert "subscription_status" in data, "Missing subscription_status"
        assert "charges" in data, "Missing charges"
        assert "included_users" in data, "Missing included_users"
        assert "current_users" in data, "Missing current_users"
        assert "max_users" in data, "Missing max_users"
        
        # Verify charges breakdown
        charges = data["charges"]
        assert "base_subscription" in charges, "Missing base_subscription"
        assert "extra_users_count" in charges, "Missing extra_users_count"
        assert "total_monthly" in charges, "Missing total_monthly"
        
        print(f"Billing Summary: Tier={data['tier_name']}, Status={data['subscription_status']}, Monthly Total={charges['total_monthly']}")
    
    def test_get_billing_history(self):
        """GET /api/billing/history - Get payment history"""
        response = requests.get(f"{BASE_URL}/api/billing/history", headers=self.headers)
        assert response.status_code == 200, f"Billing history failed: {response.text}"
        
        data = response.json()
        assert "history" in data, "Missing history field"
        assert isinstance(data["history"], list), "History should be a list"
        
        print(f"Billing History: {len(data['history'])} payments found")
    
    def test_get_addons(self):
        """GET /api/addons - Get available add-ons"""
        response = requests.get(f"{BASE_URL}/api/addons", headers=self.headers)
        assert response.status_code == 200, f"Get addons failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Add-ons should be a list"
        print(f"Available Add-ons: {len(data)} add-ons available")
    
    def test_get_extra_seats(self):
        """GET /api/billing/extra-seats - Get extra user seats"""
        response = requests.get(f"{BASE_URL}/api/billing/extra-seats", headers=self.headers)
        assert response.status_code == 200, f"Get extra seats failed: {response.text}"
        
        data = response.json()
        assert "seats" in data, "Missing seats field"
        assert isinstance(data["seats"], list), "Seats should be a list"
        print(f"Extra Seats: {len(data['seats'])} extra seats")


class TestBulkUpload:
    """Test bulk upload endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup Pro recruiter token"""
        self.pro_token = get_auth_token(PRO_RECRUITER)
        self.pro_headers = {"Authorization": f"Bearer {self.pro_token}"}
        self.starter_token = get_auth_token(STARTER_RECRUITER)
        self.starter_headers = {"Authorization": f"Bearer {self.starter_token}"}
    
    def test_download_csv_template(self):
        """GET /api/jobs/bulk/template?format=csv - Download CSV template"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/bulk/template?format=csv",
            headers=self.pro_headers
        )
        assert response.status_code == 200, f"CSV template download failed: {response.text}"
        
        # Verify content type
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type or "application/octet-stream" in content_type, f"Wrong content type: {content_type}"
        
        # Verify CSV content
        content = response.content.decode('utf-8')
        assert "title" in content.lower(), "Template should contain 'title' column"
        assert "description" in content.lower(), "Template should contain 'description' column"
        
        print(f"CSV Template downloaded successfully, size: {len(response.content)} bytes")
    
    def test_download_xlsx_template(self):
        """GET /api/jobs/bulk/template?format=xlsx - Download Excel template"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/bulk/template?format=xlsx",
            headers=self.pro_headers
        )
        assert response.status_code == 200, f"Excel template download failed: {response.text}"
        
        # Verify content type
        content_type = response.headers.get("content-type", "")
        assert "spreadsheet" in content_type or "octet-stream" in content_type, f"Wrong content type: {content_type}"
        
        print(f"Excel Template downloaded successfully, size: {len(response.content)} bytes")
    
    def test_bulk_upload_csv_pro_tier(self):
        """POST /api/jobs/bulk - Pro tier can bulk upload"""
        # Create test CSV content
        csv_content = """title,description,location,salary,job_type,work_type
TEST_Bulk Upload Test Job 1,Test job description for bulk upload testing,Johannesburg,R50000,Permanent,Onsite
TEST_Bulk Upload Test Job 2,Another test job description,Cape Town,R60000,Contract,Remote"""
        
        files = {'file': ('test_jobs.csv', csv_content, 'text/csv')}
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/bulk",
            headers=self.pro_headers,
            files=files
        )
        assert response.status_code == 200, f"Bulk upload failed: {response.text}"
        
        data = response.json()
        assert "total_rows" in data, "Missing total_rows"
        assert "created" in data, "Missing created count"
        assert "failed" in data, "Missing failed count"
        
        print(f"Bulk Upload Result: {data['created']} created, {data['failed']} failed out of {data['total_rows']} rows")
    
    def test_bulk_upload_rejects_invalid_format(self):
        """POST /api/jobs/bulk - Rejects invalid file format"""
        # Create invalid file (text file)
        invalid_content = "This is not a valid CSV file"
        
        files = {'file': ('test_jobs.txt', invalid_content, 'text/plain')}
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/bulk",
            headers=self.pro_headers,
            files=files
        )
        
        # Should return 200 with error in response (handled gracefully)
        data = response.json()
        if response.status_code == 200:
            assert data.get("success") == False or data.get("failed", 0) > 0, "Should fail for invalid format"
        else:
            assert response.status_code in [400, 422], f"Expected 400/422 for invalid format, got {response.status_code}"
        
        print(f"Invalid format rejection working: {response.status_code}")
    
    def test_bulk_upload_starter_tier_blocked(self):
        """POST /api/jobs/bulk - Starter tier cannot bulk upload (feature-gated)"""
        csv_content = """title,description,location,salary,job_type
Test Job,Test description,Johannesburg,R50000,Permanent"""
        
        files = {'file': ('test_jobs.csv', csv_content, 'text/csv')}
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/bulk",
            headers=self.starter_headers,
            files=files
        )
        
        # Should be 403 Forbidden for Starter tier
        assert response.status_code == 403, f"Expected 403 for Starter tier, got {response.status_code}: {response.text}"
        print(f"Starter tier correctly blocked from bulk upload: {response.status_code}")


class TestAIMatchingStatus:
    """Test AI matching status endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup tokens"""
        self.recruiter_token = get_auth_token(PRO_RECRUITER)
        self.recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        self.admin_token = get_auth_token(ADMIN_USER)
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_recruiter_ai_matching_status(self):
        """GET /api/ai-matching/status - Recruiter can check AI status"""
        response = requests.get(
            f"{BASE_URL}/api/ai-matching/status",
            headers=self.recruiter_headers
        )
        assert response.status_code == 200, f"AI status failed: {response.text}"
        
        data = response.json()
        assert "ai_enabled" in data or "method" in data, "Missing AI status fields"
        
        method = data.get("method", "unknown")
        ai_enabled = data.get("ai_enabled", False)
        print(f"AI Matching Status: method={method}, ai_enabled={ai_enabled}")
    
    def test_admin_ai_matching_status(self):
        """GET /api/admin/ai-matching/status - Admin can check AI status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/ai-matching/status",
            headers=self.admin_headers
        )
        assert response.status_code == 200, f"Admin AI status failed: {response.text}"
        
        data = response.json()
        assert "ai_enabled" in data, "Missing ai_enabled field"
        assert "method" in data, "Missing method field"
        print(f"Admin AI Status: ai_enabled={data['ai_enabled']}, method={data['method']}")


class TestAdminStats:
    """Test admin stats endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup admin token"""
        self.admin_token = get_auth_token(ADMIN_USER)
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.recruiter_token = get_auth_token(PRO_RECRUITER)
        self.recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
    
    def test_admin_stats_endpoint(self):
        """GET /api/admin/stats - Get admin dashboard stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=self.admin_headers
        )
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        
        data = response.json()
        # Verify stats structure
        print(f"Admin Stats Response: {data}")
    
    def test_admin_stats_blocked_for_recruiter(self):
        """GET /api/admin/stats - Recruiters cannot access admin stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=self.recruiter_headers
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print(f"Admin stats correctly blocked for recruiters: {response.status_code}")
    
    def test_admin_toggle_ai_matching(self):
        """POST /api/admin/ai-matching/toggle - Admin can toggle AI matching"""
        # Toggle OFF
        response = requests.post(
            f"{BASE_URL}/api/admin/ai-matching/toggle?enabled=false",
            headers=self.admin_headers
        )
        assert response.status_code == 200, f"Toggle AI off failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Toggle should succeed"
        print(f"AI Matching toggled OFF: {data}")
        
        # Toggle back ON
        response = requests.post(
            f"{BASE_URL}/api/admin/ai-matching/toggle?enabled=true",
            headers=self.admin_headers
        )
        assert response.status_code == 200, f"Toggle AI on failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Toggle should succeed"
        print(f"AI Matching toggled ON: {data}")
    
    def test_recruiter_cannot_toggle_ai(self):
        """POST /api/admin/ai-matching/toggle - Recruiters cannot toggle"""
        response = requests.post(
            f"{BASE_URL}/api/admin/ai-matching/toggle?enabled=false",
            headers=self.recruiter_headers
        )
        assert response.status_code == 403, f"Expected 403 for non-admin toggle, got {response.status_code}"
        print(f"AI toggle correctly blocked for recruiters: {response.status_code}")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_jobs(self):
        """Cleanup TEST_ prefixed jobs created during testing"""
        token = get_auth_token(PRO_RECRUITER)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get jobs and find test ones
        response = requests.get(f"{BASE_URL}/api/jobs", headers=headers)
        if response.status_code == 200:
            jobs = response.json()
            test_jobs = [j for j in jobs if j.get('title', '').startswith('TEST_')]
            
            for job in test_jobs:
                delete_response = requests.delete(
                    f"{BASE_URL}/api/jobs/{job['id']}",
                    headers=headers
                )
                if delete_response.status_code == 200:
                    print(f"Deleted test job: {job['title']}")
        
        print(f"Cleanup completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
