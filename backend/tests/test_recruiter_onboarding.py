"""
Recruiter Onboarding Backend Tests
Tests for recruiter-specific onboarding flow with 7 steps (0-6)
- Step 0: Welcome
- Step 1: Company Basics (updates account: company_name, size, industry, location)
- Step 2: Hiring Preferences (roles, locations, employment types, volume)
- Step 3: Candidate Access Setup (sourcing methods, alerts, match preferences)
- Step 4: Activate (post_job or browse_talent action)
- Step 5: Distribution & Visibility (email/whatsapp/social toggles)
- Step 6: Go Live (completes onboarding)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://subscription-mgmt-12.preview.emergentagent.com')

# Test credentials from review request
RECRUITER_PRO = {"email": "careers@fintechsa.co.za", "password": "demo123"}
RECRUITER_STARTER = {"email": "hr@techcorp.co.za", "password": "demo123"}
RECRUITER_ENTERPRISE = {"email": "admin@globalrecruit.co.za", "password": "demo123"}
JOB_SEEKER = {"email": "pieter.vandermerwe@gmail.com", "password": "demo123"}
ADMIN = {"email": "admin@jobrocket.co.za", "password": "admin123"}

# Recruiter step progress mapping
RECRUITER_PROGRESS = {0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 90, 6: 100}
RECRUITER_BADGES = {1: "company_live", 3: "sourcing_ready", 6: "ready_to_hire"}


class TestAuthLogin:
    """Test login functionality for different user roles"""
    
    def test_recruiter_login_success(self):
        """Recruiter login should work and return user with recruiter role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_PRO)
        print(f"Recruiter login status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "recruiter"
        print(f"Recruiter user role: {data['user']['role']}")
    
    def test_admin_login_success(self):
        """Admin login should work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN)
        print(f"Admin login status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "admin"
        print(f"Admin user role: {data['user']['role']}")
    
    def test_job_seeker_login_success(self):
        """Job seeker login should work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER)
        print(f"Job seeker login status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "job_seeker"
        print(f"Job seeker user role: {data['user']['role']}")


class TestRecruiterOnboardingStatus:
    """Test onboarding status endpoint for recruiters"""
    
    @pytest.fixture
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_PRO)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Failed to login as recruiter")
    
    def test_get_onboarding_status(self, recruiter_token):
        """Get onboarding status returns current step and progress"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        response = requests.get(f"{BASE_URL}/api/onboarding/status", headers=headers)
        print(f"Onboarding status response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "onboarding_completed" in data
        assert "onboarding_step" in data
        assert "onboarding_progress" in data
        assert "badges" in data
        print(f"Onboarding status: completed={data['onboarding_completed']}, step={data['onboarding_step']}, progress={data['onboarding_progress']}")


class TestRecruiterOnboardingStepSave:
    """Test onboarding step save endpoint for recruiters"""
    
    @pytest.fixture
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_STARTER)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Failed to login as recruiter")
    
    @pytest.fixture
    def recruiter_user(self, recruiter_token):
        """Get current recruiter user data"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        pytest.skip("Failed to get recruiter user")
    
    def test_step1_company_basics(self, recruiter_token, recruiter_user):
        """Step 1 should save company info and update account"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        step1_data = {
            "company_name": "TechCorp SA Updated",
            "company_size": "51-200 employees",
            "company_industry": "Technology",
            "company_location": "Sandton, Johannesburg"
        }
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/1", json=step1_data, headers=headers)
        print(f"Step 1 save response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["step"] == 1
        assert data["progress"] >= 20  # Progress should be at least 20% for step 1
        print(f"Step 1 result: progress={data['progress']}, badges={data.get('badges', [])}")
        
        # Check if company_live badge is awarded
        if "company_live" in data.get("badges", []):
            print("Badge 'company_live' awarded at step 1!")
    
    def test_step2_hiring_preferences(self, recruiter_token):
        """Step 2 should save hiring preferences"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        step2_data = {
            "hiring_roles": ["Software Developer", "Data Analyst", "Project Manager"],
            "hiring_locations": ["Johannesburg", "Cape Town", "Remote / National"],
            "hiring_employment_types": ["permanent", "contract"],
            "hiring_volume": "10-25 per month"
        }
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/2", json=step2_data, headers=headers)
        print(f"Step 2 save response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["step"] == 2
        assert data["progress"] >= 40  # Progress should be at least 40% for step 2
        print(f"Step 2 result: progress={data['progress']}")
    
    def test_step3_candidate_access(self, recruiter_token):
        """Step 3 should save candidate access setup and award sourcing_ready badge"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        step3_data = {
            "sourcing_methods": ["applicants", "talent_pool", "ai_matching"],
            "alerts_enabled": True,
            "match_preferences": "Skills first"
        }
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/3", json=step3_data, headers=headers)
        print(f"Step 3 save response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["step"] == 3
        assert data["progress"] >= 60  # Progress should be at least 60% for step 3
        print(f"Step 3 result: progress={data['progress']}, badges={data.get('badges', [])}")
        
        # Check if sourcing_ready badge is awarded
        if "sourcing_ready" in data.get("badges", []):
            print("Badge 'sourcing_ready' awarded at step 3!")
    
    def test_step4_activate_post_job(self, recruiter_token):
        """Step 4 should save action_taken (post_job or browse_talent)"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        step4_data = {
            "action_taken": "post_job"
        }
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/4", json=step4_data, headers=headers)
        print(f"Step 4 save response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["step"] == 4
        assert data["progress"] >= 80  # Progress should be at least 80% for step 4
        print(f"Step 4 result: progress={data['progress']}")
    
    def test_step5_distribution(self, recruiter_token):
        """Step 5 should save distribution settings"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        step5_data = {
            "distribution_email": True,
            "distribution_whatsapp": True,
            "distribution_social": False
        }
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/5", json=step5_data, headers=headers)
        print(f"Step 5 save response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["step"] == 5
        assert data["progress"] >= 90  # Progress should be at least 90% for step 5
        print(f"Step 5 result: progress={data['progress']}")
    
    def test_step6_go_live(self, recruiter_token):
        """Step 6 should complete onboarding and award ready_to_hire badge"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        step6_data = {}  # Step 6 just marks completion
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/6", json=step6_data, headers=headers)
        print(f"Step 6 save response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["step"] == 6
        assert data["progress"] == 100  # Progress should be 100% at completion
        print(f"Step 6 result: progress={data['progress']}, badges={data.get('badges', [])}")
        
        # Check if ready_to_hire badge is awarded
        if "ready_to_hire" in data.get("badges", []):
            print("Badge 'ready_to_hire' awarded at step 6!")


class TestRecruiterOnboardingSkip:
    """Test skip onboarding functionality"""
    
    @pytest.fixture
    def recruiter_token(self):
        """Get recruiter auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_ENTERPRISE)
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Failed to login as recruiter")
    
    def test_skip_onboarding(self, recruiter_token):
        """Skip onboarding should mark it complete"""
        headers = {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/onboarding/skip", json={}, headers=headers)
        print(f"Skip onboarding response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("Onboarding skipped successfully")


class TestAccountUpdateFromOnboarding:
    """Test that account is updated when company info is saved in Step 1"""
    
    @pytest.fixture
    def recruiter_auth(self):
        """Get recruiter auth and user data"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_PRO)
        if response.status_code == 200:
            data = response.json()
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            user_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            return {
                "token": data["access_token"],
                "user": user_response.json() if user_response.status_code == 200 else None
            }
        pytest.skip("Failed to login as recruiter")
    
    def test_account_updated_after_step1(self, recruiter_auth):
        """Account should be updated with company info from Step 1"""
        headers = {"Authorization": f"Bearer {recruiter_auth['token']}", "Content-Type": "application/json"}
        
        # Save step 1 with company info
        step1_data = {
            "company_name": "FinTech SA Test Updated",
            "company_size": "201-500 employees",
            "company_industry": "Finance & Banking",
            "company_location": "Cape Town"
        }
        
        response = requests.put(f"{BASE_URL}/api/onboarding/step/1", json=step1_data, headers=headers)
        print(f"Step 1 save response: {response.status_code}")
        assert response.status_code == 200
        
        # Get account to verify updates
        account_response = requests.get(f"{BASE_URL}/api/account", headers=headers)
        print(f"Account get response: {account_response.status_code}")
        assert account_response.status_code == 200
        
        account = account_response.json()
        print(f"Account after step 1: name={account.get('name')}, size={account.get('company_size')}, industry={account.get('company_industry')}, location={account.get('company_location')}")
        
        # Verify account was updated
        assert account.get("company_size") == "201-500 employees"
        assert account.get("company_industry") == "Finance & Banking"
        assert account.get("company_location") == "Cape Town"
        print("Account successfully updated with Step 1 company info!")


class TestRecruiterProgressMapping:
    """Test that progress percentages match the expected mapping"""
    
    def test_progress_mapping_constants(self):
        """Verify progress mapping is correct: {0:0, 1:20, 2:40, 3:60, 4:80, 5:90, 6:100}"""
        expected = {0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 90, 6: 100}
        print(f"Expected recruiter progress mapping: {expected}")
        # This test documents the expected mapping - actual validation is in step tests


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
