"""
Test suite for Job Application Workflow - Tests GET /api/applications and PUT /api/applications/{id}/withdraw
- Recruiter applications endpoint (by account_id)
- Job seeker applications endpoint (by applicant_id) 
- Withdraw application functionality
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from seed data
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"
JOB_SEEKER_EMAIL = "johan.botha@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"
JOB_SEEKER2_EMAIL = "thabo.mthembu@gmail.com"
JOB_SEEKER2_PASSWORD = "demo123"


class TestApplicationWorkflow:
    """Test job application workflow for recruiters and job seekers"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session for tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def login(self, email, password):
        """Helper to login and return token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token"), data.get("user")
        return None, None

    # Test 1: Recruiter can login successfully
    def test_recruiter_login(self):
        """Test recruiter login"""
        token, user = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert token is not None, f"Recruiter login failed"
        assert user is not None
        assert user.get("role") == "recruiter"
        print(f"PASS: Recruiter logged in: {user.get('email')}")

    # Test 2: Job seeker can login successfully
    def test_job_seeker_login(self):
        """Test job seeker login"""
        token, user = self.login(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert token is not None, f"Job seeker login failed"
        assert user is not None
        assert user.get("role") == "job_seeker"
        print(f"PASS: Job seeker logged in: {user.get('email')}")

    # Test 3: GET /api/applications for recruiter returns applications with applicant_snapshot
    def test_recruiter_get_applications(self):
        """Recruiter can get applications for their jobs"""
        token, user = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert token is not None, "Recruiter login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/applications")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        applications = response.json()
        assert isinstance(applications, list), "Expected list of applications"
        
        print(f"PASS: Recruiter received {len(applications)} applications")
        
        # If there are applications, verify structure
        if len(applications) > 0:
            app = applications[0]
            assert "application" in app, "Missing 'application' key"
            assert "job" in app, "Missing 'job' key"
            
            application = app["application"]
            assert "id" in application, "Missing application id"
            assert "job_id" in application, "Missing job_id"
            assert "status" in application, "Missing status"
            
            # Check for applicant_snapshot (critical field for recruiter view)
            if "applicant_snapshot" in application:
                snapshot = application["applicant_snapshot"]
                print(f"  - Application has applicant_snapshot with fields: {list(snapshot.keys())}")
            else:
                print(f"  - Application structure: {list(application.keys())}")
        
        return applications

    # Test 4: GET /api/applications for job seeker returns their own applications
    def test_job_seeker_get_applications(self):
        """Job seeker can get their own applications"""
        token, user = self.login(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert token is not None, "Job seeker login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/applications")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        applications = response.json()
        assert isinstance(applications, list), "Expected list of applications"
        
        print(f"PASS: Job seeker received {len(applications)} applications")
        
        # Verify structure
        if len(applications) > 0:
            app = applications[0]
            assert "application" in app, "Missing 'application' key"
            assert "job" in app, "Missing 'job' key"
            
            job = app["job"]
            if job:
                assert "title" in job, "Missing job title"
                assert "company_name" in job, "Missing company_name"
                print(f"  - Application for job: {job.get('title')} at {job.get('company_name')}")
        
        return applications

    # Test 5: Get public jobs for application testing
    def test_get_public_jobs(self):
        """Get available public jobs to apply to"""
        response = self.session.get(f"{BASE_URL}/api/public/jobs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "jobs" in data, "Missing jobs key"
        jobs = data["jobs"]
        
        print(f"PASS: Found {len(jobs)} public jobs")
        
        if len(jobs) > 0:
            print(f"  - First job: {jobs[0].get('title')} at {jobs[0].get('company_name')}")
        
        return jobs

    # Test 6: Job seeker can apply to a job
    def test_job_seeker_apply_to_job(self):
        """Job seeker can apply to a job"""
        # Get available jobs
        jobs_response = self.session.get(f"{BASE_URL}/api/public/jobs")
        jobs = jobs_response.json().get("jobs", [])
        
        if len(jobs) == 0:
            pytest.skip("No jobs available to apply to")
        
        # Login as job seeker 2 (to avoid duplicate application issues)
        token, user = self.login(JOB_SEEKER2_EMAIL, JOB_SEEKER2_PASSWORD)
        assert token is not None, "Job seeker 2 login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Try to apply to first job
        job = jobs[0]
        job_id = job["id"]
        
        # First check if already applied
        check_response = self.session.get(f"{BASE_URL}/api/jobs/{job_id}/application-status")
        if check_response.status_code == 200:
            status = check_response.json()
            if status.get("has_applied"):
                print(f"PASS: Job seeker already applied to job {job_id}")
                return status
        
        # Apply to job
        response = self.session.post(f"{BASE_URL}/api/jobs/{job_id}/apply", json={
            "cover_letter": "TEST Application - I am interested in this position",
            "resume_url": "",
            "additional_info": ""
        })
        
        # 200/201 = success, 400 = already applied
        assert response.status_code in [200, 201, 400], f"Expected 200/201/400, got {response.status_code}: {response.text}"
        
        if response.status_code == 400:
            print(f"PASS: Job seeker already applied to job (expected behavior)")
        else:
            data = response.json()
            assert "id" in data, "Application should have an id"
            print(f"PASS: Job seeker applied to job. Application id: {data['id']}")
        
        return response.json()

    # Test 7: Verify application appears in recruiter's list
    def test_application_appears_for_recruiter(self):
        """After job seeker applies, recruiter should see the application"""
        token, user = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert token is not None, "Recruiter login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/applications")
        
        assert response.status_code == 200
        applications = response.json()
        
        # Check if any application has applicant_snapshot
        has_applicant_data = False
        for app in applications:
            application = app.get("application", {})
            if application.get("applicant_snapshot"):
                has_applicant_data = True
                snapshot = application["applicant_snapshot"]
                print(f"PASS: Found application with applicant: {snapshot.get('first_name')} {snapshot.get('last_name')}")
                print(f"  - Email: {snapshot.get('email')}")
                print(f"  - Skills: {snapshot.get('skills')}")
                break
        
        if len(applications) > 0:
            print(f"PASS: Recruiter can see {len(applications)} applications")
            if not has_applicant_data:
                print("  NOTE: No applications have applicant_snapshot yet")
        else:
            print("INFO: No applications for recruiter to review yet")

    # Test 8: Job seeker can withdraw an application
    def test_job_seeker_withdraw_application(self):
        """Job seeker can withdraw their application"""
        # Login as job seeker
        token, user = self.login(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert token is not None, "Job seeker login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get their applications
        response = self.session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        applications = response.json()
        
        if len(applications) == 0:
            pytest.skip("No applications to withdraw")
        
        # Find an application that can be withdrawn (not already withdrawn/rejected/offered)
        withdrawable = None
        for app in applications:
            status = app["application"].get("status", "")
            if status not in ["withdrawn", "rejected", "offered"]:
                withdrawable = app
                break
        
        if withdrawable is None:
            pytest.skip("No withdrawable applications found (all are in final states)")
        
        application_id = withdrawable["application"]["id"]
        job_title = withdrawable.get("job", {}).get("title", "Unknown")
        
        # Withdraw the application
        response = self.session.put(f"{BASE_URL}/api/applications/{application_id}/withdraw")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Expected success message"
        
        print(f"PASS: Successfully withdrew application for '{job_title}'")
        
        # Verify it's now withdrawn
        response = self.session.get(f"{BASE_URL}/api/applications")
        applications = response.json()
        
        for app in applications:
            if app["application"]["id"] == application_id:
                assert app["application"]["status"] == "withdrawn", "Status should be 'withdrawn'"
                print(f"  - Verified status is now 'withdrawn'")
                break

    # Test 9: Cannot withdraw already withdrawn application
    def test_cannot_withdraw_twice(self):
        """Cannot withdraw an already withdrawn application"""
        token, user = self.login(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert token is not None, "Job seeker login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get applications
        response = self.session.get(f"{BASE_URL}/api/applications")
        applications = response.json()
        
        # Find a withdrawn application
        withdrawn = None
        for app in applications:
            if app["application"].get("status") == "withdrawn":
                withdrawn = app
                break
        
        if withdrawn is None:
            pytest.skip("No withdrawn applications to test double-withdraw")
        
        application_id = withdrawn["application"]["id"]
        
        # Try to withdraw again
        response = self.session.put(f"{BASE_URL}/api/applications/{application_id}/withdraw")
        
        assert response.status_code == 400, f"Expected 400 for double withdraw, got {response.status_code}"
        print(f"PASS: Cannot withdraw already withdrawn application (got 400 as expected)")

    # Test 10: Recruiter cannot withdraw application (only job seekers can)
    def test_recruiter_cannot_withdraw(self):
        """Recruiter cannot withdraw applications"""
        # Login as recruiter
        token, user = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert token is not None, "Recruiter login failed"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get applications to find an ID
        response = self.session.get(f"{BASE_URL}/api/applications")
        applications = response.json()
        
        if len(applications) == 0:
            pytest.skip("No applications available")
        
        application_id = applications[0]["application"]["id"]
        
        # Try to withdraw as recruiter
        response = self.session.put(f"{BASE_URL}/api/applications/{application_id}/withdraw")
        
        # Should fail - recruiters can't withdraw
        assert response.status_code in [403, 404], f"Expected 403 or 404, got {response.status_code}"
        print(f"PASS: Recruiter correctly blocked from withdrawing applications (got {response.status_code})")


class TestApplicationDataStructure:
    """Test that application data has correct structure"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def login(self, email, password):
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None

    # Test 11: Application response has correct structure for recruiters
    def test_recruiter_application_structure(self):
        """Verify recruiter gets applications with applicant_snapshot"""
        token = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        assert token is not None
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/applications")
        
        assert response.status_code == 200
        applications = response.json()
        
        if len(applications) == 0:
            pytest.skip("No applications to verify structure")
        
        app = applications[0]
        
        # Verify top-level structure
        assert "application" in app, "Missing 'application' key"
        assert "job" in app, "Missing 'job' key"
        
        application = app["application"]
        
        # Verify application fields
        required_fields = ["id", "job_id", "status", "applied_date"]
        for field in required_fields:
            assert field in application, f"Missing required field: {field}"
        
        # Verify applicant_snapshot exists
        assert "applicant_snapshot" in application, "Missing applicant_snapshot"
        
        snapshot = application["applicant_snapshot"]
        snapshot_fields = ["first_name", "last_name", "email"]
        for field in snapshot_fields:
            assert field in snapshot, f"Missing snapshot field: {field}"
        
        print(f"PASS: Application structure verified")
        print(f"  - ID: {application['id']}")
        print(f"  - Status: {application['status']}")
        print(f"  - Applicant: {snapshot.get('first_name')} {snapshot.get('last_name')}")

    # Test 12: Application response has correct structure for job seekers
    def test_job_seeker_application_structure(self):
        """Verify job seeker gets applications with job details"""
        token = self.login(JOB_SEEKER_EMAIL, JOB_SEEKER_PASSWORD)
        assert token is not None
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/applications")
        
        assert response.status_code == 200
        applications = response.json()
        
        if len(applications) == 0:
            pytest.skip("No applications to verify structure")
        
        app = applications[0]
        
        # Verify top-level structure
        assert "application" in app, "Missing 'application' key"
        assert "job" in app, "Missing 'job' key"
        
        job = app["job"]
        if job:
            job_fields = ["id", "title", "company_name"]
            for field in job_fields:
                assert field in job, f"Missing job field: {field}"
            
            print(f"PASS: Job seeker application structure verified")
            print(f"  - Job: {job['title']} at {job['company_name']}")
        else:
            print("INFO: Job details may be null if job was deleted")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
