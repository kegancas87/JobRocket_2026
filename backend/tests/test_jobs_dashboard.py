"""
Test suite for Jobs Dashboard feature
Tests: GET /api/jobs/dashboard, PUT /api/jobs/{job_id}/notes, PUT /api/jobs/{job_id}/reactivate, GET /api/jobs/{job_id}/applicants
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://job-rocket-billing.preview.emergentagent.com').rstrip('/')

# Test credentials
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"


class TestJobsDashboardEndpoints:
    """Test Jobs Dashboard API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication before each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as recruiter
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
    # ================================
    # GET /api/jobs/dashboard tests
    # ================================
    
    def test_dashboard_returns_200(self):
        """Dashboard endpoint returns 200 OK"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
    def test_dashboard_contains_stats(self):
        """Dashboard returns dashboard_stats with required fields"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        data = response.json()
        
        assert "dashboard_stats" in data, "Response missing dashboard_stats"
        stats = data["dashboard_stats"]
        
        # Verify all required stat fields
        assert "total_active_jobs" in stats, "Missing total_active_jobs"
        assert "total_expired_jobs" in stats, "Missing total_expired_jobs"
        assert "total_applications_this_month" in stats, "Missing total_applications_this_month"
        assert "total_interviews" in stats, "Missing total_interviews"
        
        # Verify types
        assert isinstance(stats["total_active_jobs"], int)
        assert isinstance(stats["total_expired_jobs"], int)
        assert isinstance(stats["total_applications_this_month"], int)
        assert isinstance(stats["total_interviews"], int)
        
    def test_dashboard_contains_jobs_list(self):
        """Dashboard returns jobs list with required fields"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        data = response.json()
        
        assert "jobs" in data, "Response missing jobs list"
        jobs = data["jobs"]
        assert isinstance(jobs, list), "Jobs should be a list"
        
        # If there are jobs, verify structure
        if len(jobs) > 0:
            job = jobs[0]
            # Core job fields
            assert "id" in job, "Job missing id"
            assert "title" in job, "Job missing title"
            assert "location" in job, "Job missing location"
            assert "posted_date" in job, "Job missing posted_date"
            
            # Dashboard-specific fields
            assert "stats" in job, "Job missing stats"
            assert "days_until_expiry" in job, "Job missing days_until_expiry"
            assert "is_expired" in job, "Job missing is_expired"
            assert "is_expiring_soon" in job, "Job missing is_expiring_soon"
            
    def test_job_stats_structure(self):
        """Job stats contain application counts"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        data = response.json()
        jobs = data.get("jobs", [])
        
        if len(jobs) > 0:
            job = jobs[0]
            stats = job.get("stats", {})
            
            # Verify application stats
            assert "total_applications" in stats, "Stats missing total_applications"
            assert "pending" in stats, "Stats missing pending"
            assert "shortlisted" in stats, "Stats missing shortlisted"
            assert "interviewed" in stats, "Stats missing interviewed"
            assert "offered" in stats, "Stats missing offered"
            
    def test_dashboard_search_filter(self):
        """Dashboard search filter works"""
        # First get all jobs to find a search term
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        data = response.json()
        
        if len(data.get("jobs", [])) > 0:
            # Use first job title as search term
            search_term = data["jobs"][0]["title"][:10]  # First 10 chars
            
            # Search with that term
            response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"search": search_term})
            assert response.status_code == 200
            search_data = response.json()
            
            # Should return at least 1 result
            assert len(search_data.get("jobs", [])) >= 1, "Search should return at least 1 job"
            
    def test_dashboard_sort_by_newest(self):
        """Dashboard sort by newest works"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"sort_by": "newest"})
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        if len(jobs) >= 2:
            # Verify sorted descending by posted_date
            for i in range(len(jobs) - 1):
                date1 = jobs[i].get("posted_date", "")
                date2 = jobs[i+1].get("posted_date", "")
                assert date1 >= date2, "Jobs should be sorted by newest first"
                
    def test_dashboard_sort_by_expiring_soon(self):
        """Dashboard sort by expiring soon works"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"sort_by": "expiring_soon"})
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        
    def test_dashboard_sort_by_most_applications(self):
        """Dashboard sort by most applications works"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"sort_by": "most_applications"})
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        if len(jobs) >= 2:
            # Verify sorted descending by application count
            for i in range(len(jobs) - 1):
                count1 = jobs[i].get("stats", {}).get("total_applications", 0)
                count2 = jobs[i+1].get("stats", {}).get("total_applications", 0)
                assert count1 >= count2, "Jobs should be sorted by most applications first"
                
    def test_dashboard_include_expired_false(self):
        """Dashboard excludes expired jobs by default"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"include_expired": "false"})
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        # None of the jobs should be expired
        for job in jobs:
            assert not job.get("is_expired", False), f"Job {job['id']} is expired but include_expired=false"
            
    def test_dashboard_include_expired_true(self):
        """Dashboard includes expired jobs when requested"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"include_expired": "true"})
        assert response.status_code == 200
        
        data = response.json()
        # Should get more jobs (or same if no expired jobs exist)
        assert "jobs" in data
        
    # ================================
    # PUT /api/jobs/{job_id}/notes tests
    # ================================
    
    def test_update_notes_returns_200(self):
        """Update notes endpoint returns 200"""
        # Get a job to update
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        jobs = response.json().get("jobs", [])
        
        if len(jobs) > 0:
            job_id = jobs[0]["id"]
            
            # Update notes
            response = self.session.put(
                f"{BASE_URL}/api/jobs/{job_id}/notes",
                json={"notes": "Test note from API test"}
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
    def test_update_notes_persists(self):
        """Updated notes are persisted and returned in dashboard"""
        # Get a job to update
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        jobs = response.json().get("jobs", [])
        
        if len(jobs) > 0:
            job_id = jobs[0]["id"]
            test_note = f"Test note at {datetime.now().isoformat()}"
            
            # Update notes
            self.session.put(f"{BASE_URL}/api/jobs/{job_id}/notes", json={"notes": test_note})
            
            # Fetch dashboard again and verify
            response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
            jobs = response.json().get("jobs", [])
            
            target_job = next((j for j in jobs if j["id"] == job_id), None)
            assert target_job is not None, "Job not found after update"
            assert target_job.get("recruiter_notes") == test_note, "Notes not persisted correctly"
            
    def test_update_notes_nonexistent_job_returns_404(self):
        """Update notes for non-existent job returns 404"""
        response = self.session.put(
            f"{BASE_URL}/api/jobs/nonexistent-job-id/notes",
            json={"notes": "Test note"}
        )
        assert response.status_code == 404
        
    # ================================
    # PUT /api/jobs/{job_id}/reactivate tests
    # ================================
    
    def test_reactivate_job_endpoint_exists(self):
        """Reactivate job endpoint is accessible"""
        # Get a job (even if not expired, endpoint should be accessible)
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"include_expired": "true"})
        jobs = response.json().get("jobs", [])
        
        if len(jobs) > 0:
            job_id = jobs[0]["id"]
            
            # Try to reactivate (even if already active, endpoint should return 200)
            response = self.session.put(
                f"{BASE_URL}/api/jobs/{job_id}/reactivate",
                json={"extension_days": 35}
            )
            # Should get 200 regardless of job status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
    def test_reactivate_with_different_extension_days(self):
        """Reactivate job with various extension periods"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard", params={"include_expired": "true"})
        jobs = response.json().get("jobs", [])
        
        if len(jobs) > 0:
            job_id = jobs[0]["id"]
            
            # Test with 7 days
            response = self.session.put(
                f"{BASE_URL}/api/jobs/{job_id}/reactivate",
                json={"extension_days": 7}
            )
            assert response.status_code == 200
            data = response.json()
            assert "new_expiry_date" in data, "Response should include new_expiry_date"
            
    def test_reactivate_nonexistent_job_returns_404(self):
        """Reactivate non-existent job returns 404"""
        response = self.session.put(
            f"{BASE_URL}/api/jobs/nonexistent-job-id/reactivate",
            json={"extension_days": 35}
        )
        assert response.status_code == 404
        
    # ================================
    # GET /api/jobs/{job_id}/applicants tests
    # ================================
    
    def test_get_applicants_returns_200(self):
        """Get applicants endpoint returns 200"""
        # Get a job with applications
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        jobs = response.json().get("jobs", [])
        
        # Find a job with applications
        job_with_apps = next((j for j in jobs if j.get("stats", {}).get("total_applications", 0) > 0), None)
        
        if job_with_apps:
            job_id = job_with_apps["id"]
            response = self.session.get(f"{BASE_URL}/api/jobs/{job_id}/applicants")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
    def test_get_applicants_structure(self):
        """Get applicants returns correct structure"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        jobs = response.json().get("jobs", [])
        
        job_with_apps = next((j for j in jobs if j.get("stats", {}).get("total_applications", 0) > 0), None)
        
        if job_with_apps:
            job_id = job_with_apps["id"]
            response = self.session.get(f"{BASE_URL}/api/jobs/{job_id}/applicants")
            data = response.json()
            
            # Verify structure
            assert "job" in data, "Response missing job"
            assert "applications" in data, "Response missing applications"
            assert "total_count" in data, "Response missing total_count"
            
            # Verify applications have applicant_profile
            applications = data.get("applications", [])
            if len(applications) > 0:
                app = applications[0]
                assert "id" in app, "Application missing id"
                assert "status" in app, "Application missing status"
                assert "applied_date" in app, "Application missing applied_date"
                
    def test_get_applicants_with_status_filter(self):
        """Get applicants with status filter works"""
        response = self.session.get(f"{BASE_URL}/api/jobs/dashboard")
        jobs = response.json().get("jobs", [])
        
        job_with_apps = next((j for j in jobs if j.get("stats", {}).get("total_applications", 0) > 0), None)
        
        if job_with_apps:
            job_id = job_with_apps["id"]
            
            # Test various status filters
            for status in ["all", "pending", "reviewed", "shortlisted", "interviewed", "offered", "rejected"]:
                response = self.session.get(f"{BASE_URL}/api/jobs/{job_id}/applicants", params={"status_filter": status})
                assert response.status_code == 200, f"Status filter '{status}' failed"
                
    def test_get_applicants_nonexistent_job_returns_404(self):
        """Get applicants for non-existent job returns 404"""
        response = self.session.get(f"{BASE_URL}/api/jobs/nonexistent-job-id/applicants")
        assert response.status_code == 404


class TestDashboardAuthorization:
    """Test authorization for dashboard endpoints"""
    
    def test_dashboard_requires_auth(self):
        """Dashboard endpoint requires authentication"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/jobs/dashboard")
        # Should get 403 (Forbidden) or 401 (Unauthorized)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
    def test_notes_requires_auth(self):
        """Notes endpoint requires authentication"""
        session = requests.Session()
        response = session.put(f"{BASE_URL}/api/jobs/some-job-id/notes", json={"notes": "test"})
        assert response.status_code in [401, 403]
        
    def test_reactivate_requires_auth(self):
        """Reactivate endpoint requires authentication"""
        session = requests.Session()
        response = session.put(f"{BASE_URL}/api/jobs/some-job-id/reactivate", json={"extension_days": 35})
        assert response.status_code in [401, 403]
        
    def test_applicants_requires_auth(self):
        """Applicants endpoint requires authentication"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/jobs/some-job-id/applicants")
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
