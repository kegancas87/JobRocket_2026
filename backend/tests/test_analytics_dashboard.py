"""
Test Analytics Dashboard API - Iteration 5
Tests the admin-only /api/admin/analytics endpoint

Test Coverage:
- Admin access to analytics endpoint
- Non-admin (recruiter, job seeker) denied access (403)
- Response contains expected data structures: monthly_trends, jobs_by_industry, jobs_by_location, etc.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from PRD
ADMIN_EMAIL = "admin@jobrocket.co.za"
ADMIN_PASSWORD = "admin123"
RECRUITER_EMAIL = "careers@fintechsa.co.za"
RECRUITER_PASSWORD = "demo123"
JOB_SEEKER_EMAIL = "pieter.vandermerwe@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"


class TestAdminAnalyticsEndpoint:
    """Tests for GET /api/admin/analytics endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Recruiter login failed: {response.status_code}")
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def job_seeker_token(self):
        """Get job seeker authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Job seeker login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_admin_login_succeeds(self):
        """Verify admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        print(f"Admin login successful - user ID: {data['user']['id']}")
    
    def test_analytics_endpoint_returns_200_for_admin(self, admin_token):
        """Admin should get 200 response from analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Analytics endpoint failed for admin: {response.status_code} - {response.text}"
        print("Analytics endpoint accessible for admin")
    
    def test_analytics_response_contains_monthly_trends(self, admin_token):
        """Response should contain monthly_trends array with 6 months of data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "monthly_trends" in data, "Response missing monthly_trends"
        assert isinstance(data["monthly_trends"], list), "monthly_trends should be a list"
        assert len(data["monthly_trends"]) == 6, f"Expected 6 months of data, got {len(data['monthly_trends'])}"
        
        # Verify structure of each month entry
        for month_data in data["monthly_trends"]:
            assert "month" in month_data, "Missing 'month' field"
            assert "accounts" in month_data, "Missing 'accounts' field"
            assert "users" in month_data, "Missing 'users' field"
            assert "jobs" in month_data, "Missing 'jobs' field"
            assert "applications" in month_data, "Missing 'applications' field"
        
        print(f"Monthly trends: {data['monthly_trends']}")
    
    def test_analytics_response_contains_jobs_by_industry(self, admin_token):
        """Response should contain jobs_by_industry breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "jobs_by_industry" in data, "Response missing jobs_by_industry"
        assert isinstance(data["jobs_by_industry"], list), "jobs_by_industry should be a list"
        
        # Each entry should have name and count
        for item in data["jobs_by_industry"]:
            assert "name" in item, "Missing 'name' field in jobs_by_industry"
            assert "count" in item, "Missing 'count' field in jobs_by_industry"
        
        print(f"Jobs by industry: {data['jobs_by_industry']}")
    
    def test_analytics_response_contains_jobs_by_location(self, admin_token):
        """Response should contain jobs_by_location breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "jobs_by_location" in data, "Response missing jobs_by_location"
        assert isinstance(data["jobs_by_location"], list), "jobs_by_location should be a list"
        
        for item in data["jobs_by_location"]:
            assert "name" in item, "Missing 'name' field in jobs_by_location"
            assert "count" in item, "Missing 'count' field in jobs_by_location"
        
        print(f"Jobs by location: {data['jobs_by_location']}")
    
    def test_analytics_response_contains_work_type_and_job_type(self, admin_token):
        """Response should contain jobs_by_work_type and jobs_by_job_type"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "jobs_by_work_type" in data, "Response missing jobs_by_work_type"
        assert "jobs_by_job_type" in data, "Response missing jobs_by_job_type"
        
        print(f"Jobs by work type: {data['jobs_by_work_type']}")
        print(f"Jobs by job type: {data['jobs_by_job_type']}")
    
    def test_analytics_response_contains_onboarding_stats(self, admin_token):
        """Response should contain onboarding completion stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "onboarding" in data, "Response missing onboarding"
        onboarding = data["onboarding"]
        
        assert "job_seekers" in onboarding, "Missing job_seekers onboarding stats"
        assert "recruiters" in onboarding, "Missing recruiters onboarding stats"
        
        # Each should have completed and total
        for role in ["job_seekers", "recruiters"]:
            assert "completed" in onboarding[role], f"Missing completed count for {role}"
            assert "total" in onboarding[role], f"Missing total count for {role}"
        
        print(f"Onboarding stats: {data['onboarding']}")
    
    def test_analytics_response_contains_accounts_detail(self, admin_token):
        """Response should contain accounts_detail table data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "accounts_detail" in data, "Response missing accounts_detail"
        assert isinstance(data["accounts_detail"], list), "accounts_detail should be a list"
        
        # Verify structure of account detail entries
        if len(data["accounts_detail"]) > 0:
            account = data["accounts_detail"][0]
            required_fields = ["id", "name", "tier_id", "subscription_status", "owner_email", 
                             "user_count", "job_count", "application_count", "mrr", "created_at"]
            for field in required_fields:
                assert field in account, f"Missing '{field}' in accounts_detail"
        
        print(f"Accounts detail count: {len(data['accounts_detail'])}")
        if data["accounts_detail"]:
            print(f"Sample account: {data['accounts_detail'][0]['name']} - Tier: {data['accounts_detail'][0]['tier_id']}")
    
    def test_analytics_endpoint_denied_for_recruiter(self, recruiter_token):
        """Recruiter should get 403 Forbidden from analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for recruiter, got {response.status_code}"
        print("Analytics endpoint correctly denied for recruiter (403)")
    
    def test_analytics_endpoint_denied_for_job_seeker(self, job_seeker_token):
        """Job seeker should get 403 Forbidden from analytics endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/analytics",
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for job seeker, got {response.status_code}"
        print("Analytics endpoint correctly denied for job seeker (403)")
    
    def test_analytics_endpoint_denied_without_auth(self):
        """Unauthenticated request should get 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"Analytics endpoint correctly denied without auth ({response.status_code})")


class TestAdminStatsEndpoint:
    """Tests for GET /api/admin/stats endpoint (snapshot stats)"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_admin_stats_endpoint_returns_200(self, admin_token):
        """Admin should get 200 from stats endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Stats endpoint failed: {response.status_code} - {response.text}"
        print("Admin stats endpoint accessible")
    
    def test_admin_stats_contains_summary(self, admin_token):
        """Stats should contain summary with key metrics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data, "Response missing summary"
        summary = data["summary"]
        
        # Check expected summary fields
        expected_fields = ["monthly_revenue", "total_accounts", "active_subscriptions", 
                          "total_users", "total_recruiters", "total_job_seekers",
                          "total_jobs", "active_jobs", "total_applications"]
        for field in expected_fields:
            assert field in summary, f"Missing '{field}' in summary"
        
        print(f"Summary stats: Revenue={summary.get('monthly_revenue')}, Accounts={summary.get('total_accounts')}, Users={summary.get('total_users')}")
    
    def test_admin_stats_contains_tier_distribution(self, admin_token):
        """Stats should contain tier_distribution"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "tier_distribution" in data, "Response missing tier_distribution"
        tier_dist = data["tier_distribution"]
        
        # Should have all 4 tiers
        expected_tiers = ["starter", "growth", "pro", "enterprise"]
        for tier in expected_tiers:
            assert tier in tier_dist, f"Missing tier '{tier}' in tier_distribution"
        
        print(f"Tier distribution: {tier_dist}")
    
    def test_admin_stats_force_refresh(self, admin_token):
        """Force refresh should work"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats?force_refresh=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Force refresh failed: {response.status_code}"
        data = response.json()
        assert "last_refresh" in data, "Missing last_refresh timestamp"
        print(f"Force refresh successful - last_refresh: {data.get('last_refresh')}")


class TestNavigationAnalyticsLink:
    """Tests for navigation showing Analytics link based on user role"""
    
    def test_admin_user_has_analytics_role(self):
        """Verify admin user has admin role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "admin"
        print(f"Admin user role confirmed: {data['user']['role']}")
    
    def test_recruiter_user_has_recruiter_role(self):
        """Verify recruiter user has recruiter role (no analytics access)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "recruiter"
        print(f"Recruiter user role confirmed: {data['user']['role']}")
    
    def test_job_seeker_has_job_seeker_role(self):
        """Verify job seeker user has job_seeker role (no analytics access)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "job_seeker"
        print(f"Job seeker user role confirmed: {data['user']['role']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
