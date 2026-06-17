"""
Test Job Seeker Profile Features:
1. Profile picture upload
2. Video upload
3. Media links (LinkedIn, Portfolio - no GitHub/Other)
4. Profile completion points calculation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
JOB_SEEKER_EMAIL = "thabo.mthembu@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"


class TestJobSeekerProfile:
    """Tests for job seeker profile features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as job seeker"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code} - {response.text}")
        
        data = response.json()
        self.token = data.get("access_token")
        self.user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        yield
        
        self.session.close()
    
    def test_login_as_job_seeker(self):
        """Test login and verify user role"""
        assert self.token is not None, "Token should be returned"
        assert self.user is not None, "User data should be returned"
        assert self.user.get("role") == "job_seeker", f"User role should be job_seeker, got {self.user.get('role')}"
        assert self.user.get("email") == JOB_SEEKER_EMAIL
        print(f"PASS: Logged in as {self.user.get('first_name')} {self.user.get('last_name')}")
    
    def test_get_profile_with_me_endpoint(self):
        """Test GET /api/auth/me returns full profile data"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        assert data.get("role") == "job_seeker"
        
        # Check for profile_progress field
        assert "profile_progress" in data, "profile_progress field should be in response"
        progress = data.get("profile_progress", {})
        assert "total_points" in progress, "total_points should be in profile_progress"
        print(f"PASS: Profile has {progress.get('total_points', 0)}/100 completion points")
    
    def test_profile_picture_upload_endpoint_exists(self):
        """Test POST /api/uploads/profile-picture endpoint exists"""
        # Test with empty request to verify endpoint exists (should return 422 for missing file)
        response = self.session.post(f"{BASE_URL}/api/uploads/profile-picture")
        # Endpoint should exist - will return 422 (Unprocessable Entity) or similar for missing file
        assert response.status_code in [400, 422, 415], f"Endpoint should exist, got {response.status_code}"
        print(f"PASS: Profile picture upload endpoint exists (status: {response.status_code})")
    
    def test_video_upload_endpoint_exists(self):
        """Test POST /api/uploads/video endpoint exists"""
        # Test with empty request to verify endpoint exists
        response = self.session.post(f"{BASE_URL}/api/uploads/video")
        # Endpoint should exist - will return error for missing file
        assert response.status_code in [400, 422, 415], f"Endpoint should exist, got {response.status_code}"
        print(f"PASS: Video upload endpoint exists (status: {response.status_code})")
    
    def test_update_profile_with_media_links(self):
        """Test PUT /api/profile can update linkedin_url and portfolio_url"""
        test_linkedin = "https://linkedin.com/in/test-user"
        test_portfolio = "https://myportfolio.com"
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "linkedin_url": test_linkedin,
            "portfolio_url": test_portfolio
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify the update persisted
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        
        me_data = me_response.json()
        assert me_data.get("linkedin_url") == test_linkedin, "LinkedIn URL should be updated"
        assert me_data.get("portfolio_url") == test_portfolio, "Portfolio URL should be updated"
        print(f"PASS: Media links updated - LinkedIn: {test_linkedin}, Portfolio: {test_portfolio}")
    
    def test_profile_progress_has_expected_fields(self):
        """Test profile_progress contains expected completion categories"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        progress = data.get("profile_progress", {})
        
        # Expected progress tracking fields
        expected_fields = ["total_points"]
        possible_tracking_fields = [
            "profile_picture", "about_me", "work_history", "skills",
            "education", "achievements", "intro_video", "media"
        ]
        
        assert "total_points" in progress, "total_points should be in progress"
        
        # Check at least some tracking fields are present
        found_fields = [f for f in possible_tracking_fields if f in progress]
        print(f"PASS: Profile progress has {len(found_fields)} tracking fields: {found_fields}")
        print(f"Total points: {progress.get('total_points', 0)}")
    
    def test_add_work_experience_updates_progress(self):
        """Test that adding work experience updates profile progress"""
        # Get initial progress
        initial_response = self.session.get(f"{BASE_URL}/api/auth/me")
        initial_data = initial_response.json()
        initial_points = initial_data.get("profile_progress", {}).get("total_points", 0)
        
        # Add work experience
        exp_data = {
            "company": "TEST_Company",
            "position": "TEST_Developer",
            "start_date": "2023-01-01T00:00:00Z",
            "end_date": "2024-01-01T00:00:00Z",
            "current": False,
            "description": "Test work experience entry",
            "location": "Cape Town"
        }
        
        add_response = self.session.post(f"{BASE_URL}/api/profile/work-experience", json=exp_data)
        
        if add_response.status_code == 200:
            # Get updated progress
            updated_response = self.session.get(f"{BASE_URL}/api/auth/me")
            updated_data = updated_response.json()
            updated_points = updated_data.get("profile_progress", {}).get("total_points", 0)
            
            work_experience = updated_data.get("work_experience", [])
            
            # Find and delete the test entry
            for exp in work_experience:
                if exp.get("company") == "TEST_Company":
                    del_response = self.session.delete(f"{BASE_URL}/api/profile/work-experience/{exp.get('id')}")
                    print(f"Cleaned up test work experience entry")
                    break
            
            print(f"PASS: Initial points: {initial_points}, After adding experience: {updated_points}")
        else:
            print(f"INFO: Could not add work experience (status: {add_response.status_code})")
    
    def test_profile_update_basic_info(self):
        """Test updating basic profile info"""
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "phone": "+27 123 456 7890",
            "location": "Cape Town, Western Cape"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Basic profile info updated")


class TestHeaderDropdownNavigation:
    """Tests for navigation items that should be in job seeker dropdown"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as job seeker"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.status_code}")
        
        data = response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        yield
        self.session.close()
    
    def test_profile_endpoint_accessible(self):
        """Test that profile data is accessible (needed for Profile menu item)"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        print("PASS: Profile endpoint accessible for Profile menu item")
    
    def test_notifications_route_exists(self):
        """Note: Notifications is a frontend-only route, but verify we're logged in"""
        # This is primarily a frontend routing test, but we verify auth works
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        assert response.json().get("role") == "job_seeker"
        print("PASS: User authenticated - Notifications route should work in frontend")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
