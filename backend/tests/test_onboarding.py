"""
JobRocket Onboarding Feature Tests
Tests for gamified job seeker onboarding flow (Steps 0-6)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://multi-tenant-build.preview.emergentagent.com')

# Test credentials from review_request
JOB_SEEKER_NO_ONBOARDING = {"email": "nomsa.dlamini@gmail.com", "password": "demo123"}
JOB_SEEKER_PARTIAL = {"email": "thabo.mthembu@gmail.com", "password": "demo123"}
JOB_SEEKER_REGULAR = {"email": "pieter.vandermerwe@gmail.com", "password": "demo123"}
RECRUITER = {"email": "careers@fintechsa.co.za", "password": "demo123"}
ADMIN = {"email": "admin@jobrocket.co.za", "password": "admin123"}


class TestOnboardingAPIs:
    """Test onboarding backend endpoints"""
    
    @pytest.fixture
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    @pytest.fixture
    def job_seeker_token(self, api_client):
        """Get job seeker auth token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_NO_ONBOARDING)
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Job seeker login failed - skipping authenticated tests")
    
    @pytest.fixture
    def recruiter_token(self, api_client):
        """Get recruiter auth token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=RECRUITER)
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Recruiter login failed - skipping authenticated tests")
    
    @pytest.fixture
    def admin_token(self, api_client):
        """Get admin auth token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=ADMIN)
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed - skipping authenticated tests")
    
    # ==========================================
    # Login Tests - Role-based redirect check
    # ==========================================
    
    def test_job_seeker_login_success(self, api_client):
        """Job seeker login should succeed and return user data"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_NO_ONBOARDING)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "job_seeker"
        print(f"Job seeker login success. User: {data['user'].get('first_name', 'N/A')}")
        print(f"Onboarding completed: {data['user'].get('onboarding_completed', 'N/A')}")
    
    def test_recruiter_login_success(self, api_client):
        """Recruiter login should succeed (should NOT trigger onboarding)"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=RECRUITER)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "recruiter"
        # Recruiters shouldn't have onboarding fields
        print(f"Recruiter login success. User role: {data['user']['role']}")
    
    def test_admin_login_success(self, api_client):
        """Admin login should succeed (should NOT trigger onboarding)"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json=ADMIN)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        print(f"Admin login success. User role: {data['user']['role']}")
    
    # ==========================================
    # Onboarding Status API Tests
    # ==========================================
    
    def test_onboarding_status_endpoint(self, api_client, job_seeker_token):
        """GET /api/onboarding/status should return onboarding progress"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = api_client.get(f"{BASE_URL}/api/onboarding/status", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "onboarding_completed" in data
        assert "onboarding_step" in data
        assert "onboarding_progress" in data
        assert "badges" in data
        
        print(f"Onboarding status: step={data['onboarding_step']}, progress={data['onboarding_progress']}%, completed={data['onboarding_completed']}")
        print(f"Badges: {data['badges']}")
    
    def test_onboarding_status_requires_auth(self, api_client):
        """GET /api/onboarding/status without auth should fail"""
        response = api_client.get(f"{BASE_URL}/api/onboarding/status")
        assert response.status_code == 401 or response.status_code == 403
        print("Onboarding status correctly requires authentication")
    
    # ==========================================
    # Step Save API Tests (PUT /api/onboarding/step/{step})
    # ==========================================
    
    def test_save_step_1_location(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/1 should save location data"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        step_data = {
            "location": "TEST_Johannesburg, Gauteng"
        }
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/1", json=step_data, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("step") == 1
        assert data.get("progress") >= 15  # Step 1 = 15%
        
        print(f"Step 1 saved. Progress: {data.get('progress')}%")
    
    def test_save_step_2_professional(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/2 should save professional snapshot data"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        step_data = {
            "desired_job_title": "TEST_Software Developer",
            "years_of_experience": "3-5 years",
            "industry_preference": "Technology",
            "employment_type_preference": ["permanent", "remote"]
        }
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/2", json=step_data, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("step") == 2
        assert data.get("progress") >= 35  # Step 2 = 35%
        
        # Check if badge is earned at step 2
        badges = data.get("badges", [])
        print(f"Step 2 saved. Progress: {data.get('progress')}%, Badges: {badges}")
        if "profile_started" in badges:
            print("Badge earned: profile_started")
    
    def test_save_step_3_skills(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/3 should save skills data"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        step_data = {
            "skills": ["Python", "JavaScript", "React", "Node.js"],
            "seniority_level": "Mid Level",
            "key_strengths": ["Problem Solving", "Communication", "Teamwork"]
        }
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/3", json=step_data, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("step") == 3
        assert data.get("progress") >= 55  # Step 3 = 55%
        
        print(f"Step 3 saved. Progress: {data.get('progress')}%")
    
    def test_save_step_4_cv_info(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/4 should save CV related info"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        step_data = {
            "linkedin_url": "https://linkedin.com/in/test-profile",
            "desired_salary_range": "R30,000 - R50,000 per month"
        }
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/4", json=step_data, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("step") == 4
        assert data.get("progress") >= 75  # Step 4 = 75%
        
        print(f"Step 4 saved. Progress: {data.get('progress')}%")
    
    def test_save_step_5_experience(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/5 should save experience and availability"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        step_data = {
            "work_experience": [
                {
                    "company": "TEST_Tech Corp",
                    "position": "Software Developer",
                    "start_date": "2022-01-01",
                    "end_date": "",
                    "current": True,
                    "description": "Full-stack development",
                    "location": "Johannesburg"
                }
            ],
            "availability": "Immediately",
            "notice_period": ""
        }
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/5", json=step_data, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("step") == 5
        assert data.get("progress") >= 90  # Step 5 = 90%
        
        # Check if badge is earned at step 5
        badges = data.get("badges", [])
        print(f"Step 5 saved. Progress: {data.get('progress')}%, Badges: {badges}")
        if "almost_there" in badges:
            print("Badge earned: almost_there")
    
    def test_save_step_6_profile_boost(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/6 should save profile boost data and complete onboarding"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        step_data = {
            "about_me": "TEST_Passionate developer with experience in web technologies.",
            "open_to_opportunities": True,
            "additional_documents": []
        }
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/6", json=step_data, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("step") == 6
        assert data.get("progress") == 100  # Step 6 = 100%
        
        # Check if badge is earned at step 6
        badges = data.get("badges", [])
        print(f"Step 6 saved. Progress: {data.get('progress')}%, Badges: {badges}")
        if "profile_complete" in badges:
            print("Badge earned: profile_complete")
    
    def test_save_invalid_step(self, api_client, job_seeker_token):
        """PUT /api/onboarding/step/99 should return error for invalid step"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = api_client.put(f"{BASE_URL}/api/onboarding/step/99", json={}, headers=headers)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("Invalid step correctly rejected with 400")
    
    # ==========================================
    # Skip Onboarding API Tests
    # ==========================================
    
    def test_skip_onboarding_endpoint(self, api_client, job_seeker_token):
        """POST /api/onboarding/skip should mark onboarding as complete"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = api_client.post(f"{BASE_URL}/api/onboarding/skip", json={}, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        
        print("Skip onboarding endpoint works correctly")
    
    def test_skip_onboarding_requires_auth(self, api_client):
        """POST /api/onboarding/skip without auth should fail"""
        response = api_client.post(f"{BASE_URL}/api/onboarding/skip", json={})
        assert response.status_code == 401 or response.status_code == 403
        print("Skip onboarding correctly requires authentication")


class TestFileUploadAPIs:
    """Test file upload endpoints for onboarding"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        return session
    
    @pytest.fixture
    def job_seeker_token(self, api_client):
        """Get job seeker auth token"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/login", 
            json=JOB_SEEKER_NO_ONBOARDING,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Job seeker login failed - skipping upload tests")
    
    def test_cv_upload_endpoint_exists(self, api_client, job_seeker_token):
        """POST /api/uploads/cv endpoint should exist and require file"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        # Test without file - should return 422 (validation error)
        response = api_client.post(f"{BASE_URL}/api/uploads/cv", headers=headers)
        
        # Either 400 or 422 is acceptable for missing file
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"
        print(f"CV upload endpoint exists. Response without file: {response.status_code}")
    
    def test_cv_upload_with_test_file(self, api_client, job_seeker_token):
        """POST /api/uploads/cv should accept PDF files"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        # Create a minimal test PDF (just PDF header)
        test_pdf_content = b"%PDF-1.4\nTest CV file content\n%%EOF"
        files = {"file": ("test_cv.pdf", test_pdf_content, "application/pdf")}
        
        response = api_client.post(f"{BASE_URL}/api/uploads/cv", headers=headers, files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data
        assert "filename" in data
        print(f"CV uploaded successfully. URL: {data['url']}")
    
    def test_profile_picture_upload_endpoint(self, api_client, job_seeker_token):
        """POST /api/uploads/profile-picture endpoint should exist"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        # Test without file - should return 422
        response = api_client.post(f"{BASE_URL}/api/uploads/profile-picture", headers=headers)
        
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"
        print(f"Profile picture upload endpoint exists. Response without file: {response.status_code}")
    
    def test_profile_picture_upload_with_image(self, api_client, job_seeker_token):
        """POST /api/uploads/profile-picture should accept images"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        # Create a minimal valid PNG (1x1 pixel)
        png_header = b'\x89PNG\r\n\x1a\n'
        png_ihdr = b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        png_idat = b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
        png_iend = b'\x00\x00\x00\x00IEND\xaeB`\x82'
        test_png = png_header + png_ihdr + png_idat + png_iend
        
        files = {"file": ("test_avatar.png", test_png, "image/png")}
        
        response = api_client.post(f"{BASE_URL}/api/uploads/profile-picture", headers=headers, files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data
        print(f"Profile picture uploaded successfully. URL: {data['url']}")
    
    def test_document_upload_endpoint(self, api_client, job_seeker_token):
        """POST /api/uploads/document endpoint should exist"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        # Test without file
        response = api_client.post(f"{BASE_URL}/api/uploads/document", headers=headers)
        
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"
        print(f"Document upload endpoint exists. Response without file: {response.status_code}")
    
    def test_document_upload_with_file(self, api_client, job_seeker_token):
        """POST /api/uploads/document should accept PDFs"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        
        test_pdf_content = b"%PDF-1.4\nTest Certificate\n%%EOF"
        files = {"file": ("test_certificate.pdf", test_pdf_content, "application/pdf")}
        
        response = api_client.post(f"{BASE_URL}/api/uploads/document", headers=headers, files=files)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "url" in data
        print(f"Document uploaded successfully. URL: {data['url']}")


class TestOnboardingUserFlow:
    """Test complete onboarding flow integration"""
    
    @pytest.fixture
    def api_client(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    def test_onboarding_completed_flag_after_step6(self, api_client):
        """Verify onboarding_completed is True after completing step 6"""
        # Login
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_NO_ONBOARDING)
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Complete step 6
        step_data = {
            "about_me": "Test user profile",
            "open_to_opportunities": True
        }
        api_client.put(f"{BASE_URL}/api/onboarding/step/6", json=step_data, headers=headers)
        
        # Check status
        status_response = api_client.get(f"{BASE_URL}/api/onboarding/status", headers=headers)
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert data.get("onboarding_completed") == True, "onboarding_completed should be True after step 6"
        assert data.get("onboarding_progress") == 100, "Progress should be 100% after step 6"
        
        print(f"Onboarding completed successfully: {data}")
    
    def test_progress_bar_percentages(self, api_client):
        """Verify progress percentages match expected values"""
        # Login
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_REGULAR)
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Expected progress mapping: 0->0%, 1->15%, 2->35%, 3->55%, 4->75%, 5->90%, 6->100%
        expected_progress = {1: 15, 2: 35, 3: 55, 4: 75, 5: 90, 6: 100}
        
        # Test each step
        for step, expected in expected_progress.items():
            response = api_client.put(f"{BASE_URL}/api/onboarding/step/{step}", json={}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                actual_progress = data.get("progress", 0)
                # Progress should be at least the expected value
                assert actual_progress >= expected, f"Step {step}: expected progress >= {expected}%, got {actual_progress}%"
                print(f"Step {step}: progress = {actual_progress}% (expected >= {expected}%)")
    
    def test_auth_me_includes_onboarding_fields(self, api_client):
        """GET /api/auth/me should include onboarding fields for job seekers"""
        # Login
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_NO_ONBOARDING)
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user profile
        me_response = api_client.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        data = me_response.json()
        assert "onboarding_completed" in data or data.get("role") != "job_seeker"
        print(f"User profile includes onboarding data: onboarding_completed={data.get('onboarding_completed')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
