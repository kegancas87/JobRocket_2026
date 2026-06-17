"""
Test suite for Change Password feature
Tests POST /api/auth/change-password endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials - IMPORTANT: Always revert passwords back to demo123 after testing
JOB_SEEKER_EMAIL = "thabo.mthembu@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"


class TestChangePassword:
    """Tests for POST /api/auth/change-password endpoint"""

    @pytest.fixture
    def job_seeker_token(self):
        """Get auth token for job seeker"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Could not login as job seeker: {response.text}")
        return response.json().get("access_token")

    @pytest.fixture
    def recruiter_token(self):
        """Get auth token for recruiter"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Could not login as recruiter: {response.text}")
        return response.json().get("access_token")

    def test_change_password_requires_auth(self):
        """Test that change-password endpoint returns 401/403 without auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/change-password", json={
            "current_password": "demo123",
            "new_password": "newpass123"
        })
        # FastAPI returns 403 for missing auth, 401 for invalid auth - both are acceptable
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}: {response.text}"
        print(f"PASSED: Change password returns {response.status_code} without auth token")

    def test_change_password_wrong_current_password(self, job_seeker_token):
        """Test that wrong current password returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpass123"
            },
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "incorrect" in data.get("detail", "").lower() or "wrong" in data.get("detail", "").lower(), \
            f"Expected error about incorrect password, got: {data}"
        print("PASSED: Wrong current password returns 400 with appropriate error")

    def test_change_password_too_short(self, job_seeker_token):
        """Test that new password < 6 chars returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": JOB_SEEKER_PASSWORD,
                "new_password": "abc"  # Too short
            },
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "6 characters" in data.get("detail", "").lower() or "at least" in data.get("detail", "").lower(), \
            f"Expected error about password length, got: {data}"
        print("PASSED: Too short password returns 400 with appropriate error")

    def test_change_password_same_password(self, job_seeker_token):
        """Test that same password returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": JOB_SEEKER_PASSWORD,
                "new_password": JOB_SEEKER_PASSWORD  # Same as current
            },
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "different" in data.get("detail", "").lower() or "same" in data.get("detail", "").lower(), \
            f"Expected error about same password, got: {data}"
        print("PASSED: Same password returns 400 with appropriate error")

    def test_change_password_missing_fields(self, job_seeker_token):
        """Test that missing fields returns error"""
        # Missing new_password
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={"current_password": JOB_SEEKER_PASSWORD},
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASSED: Missing new_password returns 400")

        # Missing current_password
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={"new_password": "newpass123"},
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        print("PASSED: Missing current_password returns 400")

    def test_change_password_success_and_revert(self, job_seeker_token):
        """Test successful password change and revert back to original"""
        new_password = "temppass123"
        
        # Step 1: Change password to new password
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": JOB_SEEKER_PASSWORD,
                "new_password": new_password
            },
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "success" in data.get("message", "").lower(), f"Expected success message, got: {data}"
        print("PASSED: Password changed successfully")

        # Step 2: Verify new password works by logging in
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": new_password
        })
        assert login_response.status_code == 200, f"Login with new password failed: {login_response.text}"
        new_token = login_response.json().get("access_token")
        print("PASSED: Login with new password works")

        # Step 3: Revert password back to original
        revert_response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": new_password,
                "new_password": JOB_SEEKER_PASSWORD
            },
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert revert_response.status_code == 200, f"Password revert failed: {revert_response.text}"
        print("PASSED: Password reverted back to original")

        # Step 4: Verify original password works
        final_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert final_login.status_code == 200, f"Login with original password failed: {final_login.text}"
        print("PASSED: Original password works after revert")

    def test_change_password_recruiter(self, recruiter_token):
        """Test that recruiters can also change password"""
        new_password = "temprecruiter123"
        
        # Change password
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": RECRUITER_PASSWORD,
                "new_password": new_password
            },
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASSED: Recruiter password changed successfully")

        # Login with new password
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": new_password
        })
        assert login_response.status_code == 200, f"Login with new password failed: {login_response.text}"
        new_token = login_response.json().get("access_token")
        print("PASSED: Recruiter login with new password works")

        # Revert password
        revert_response = requests.post(
            f"{BASE_URL}/api/auth/change-password",
            json={
                "current_password": new_password,
                "new_password": RECRUITER_PASSWORD
            },
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert revert_response.status_code == 200, f"Password revert failed: {revert_response.text}"
        print("PASSED: Recruiter password reverted back to original")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
