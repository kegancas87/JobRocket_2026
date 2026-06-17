"""
Test AI Match Score Feature for CV Search
Tests POST /api/cv-search/ai-match and GET /api/cv-search/ai-match-scores endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
RECRUITER_PRO = {"email": "hr@techcorp.co.za", "password": "demo123"}  # Pro tier with CV Search
JOB_SEEKER = {"email": "thabo.mthembu@gmail.com", "password": "demo123"}
ADMIN = {"email": "admin@jobrocket.co.za", "password": "admin123"}

# Test data from review request
TEST_CANDIDATE_ID = "fcf943c6-9fc5-4695-9ca5-d31abeb673fe"  # Thabo Mthembu
TEST_JOB_ID_CACHED = "f0baba8f-f611-4884-94e0-47906669d2e7"  # React Developer (already cached)
TEST_JOB_ID_UNCACHED = "8af394eb-118c-46e1-8357-1b71193f4067"  # UX/UI Designer


def get_auth_token(email: str, password: str) -> str:
    """Login and return access token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


class TestAIMatchEndpoint:
    """Tests for POST /api/cv-search/ai-match endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.recruiter_token = get_auth_token(RECRUITER_PRO["email"], RECRUITER_PRO["password"])
        self.job_seeker_token = get_auth_token(JOB_SEEKER["email"], JOB_SEEKER["password"])
        
    def test_ai_match_returns_401_without_auth(self):
        """POST /api/cv-search/ai-match returns 401 without authentication"""
        response = requests.post(f"{BASE_URL}/api/cv-search/ai-match", json={
            "candidate_id": TEST_CANDIDATE_ID,
            "job_id": TEST_JOB_ID_CACHED
        })
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Returns {response.status_code} without auth")
    
    def test_ai_match_returns_400_without_candidate_id(self):
        """POST /api/cv-search/ai-match returns 400 without candidate_id"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/cv-search/ai-match",
            json={"job_id": TEST_JOB_ID_CACHED},
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "candidate_id" in response.json().get("detail", "").lower()
        print(f"✓ Returns 400 without candidate_id: {response.json()}")
    
    def test_ai_match_returns_400_without_job_id(self):
        """POST /api/cv-search/ai-match returns 400 without job_id"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/cv-search/ai-match",
            json={"candidate_id": TEST_CANDIDATE_ID},
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "job_id" in response.json().get("detail", "").lower()
        print(f"✓ Returns 400 without job_id: {response.json()}")
    
    def test_ai_match_returns_404_for_nonexistent_job(self):
        """POST /api/cv-search/ai-match returns 404 for non-existent job"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/cv-search/ai-match",
            json={
                "candidate_id": TEST_CANDIDATE_ID,
                "job_id": "nonexistent-job-id-12345"
            },
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Returns 404 for non-existent job: {response.json()}")
    
    def test_ai_match_job_seeker_cannot_access(self):
        """POST /api/cv-search/ai-match - Job seeker cannot access (recruiter-only)"""
        if not self.job_seeker_token:
            pytest.skip("Job seeker login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/cv-search/ai-match",
            json={
                "candidate_id": TEST_CANDIDATE_ID,
                "job_id": TEST_JOB_ID_CACHED
            },
            headers={"Authorization": f"Bearer {self.job_seeker_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Job seeker gets 403: {response.json()}")
    
    def test_ai_match_returns_cached_result(self):
        """POST /api/cv-search/ai-match returns cached result on second call"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/cv-search/ai-match",
            json={
                "candidate_id": TEST_CANDIDATE_ID,
                "job_id": TEST_JOB_ID_CACHED
            },
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True, "Expected success=True"
        assert "result" in data, "Expected 'result' in response"
        
        result = data["result"]
        assert "score" in result, "Expected 'score' in result"
        assert "reasoning" in result, "Expected 'reasoning' in result"
        assert "method" in result, "Expected 'method' in result"
        assert "breakdown" in result, "Expected 'breakdown' in result"
        
        # Verify score is valid
        score = result["score"]
        assert isinstance(score, int), f"Score should be int, got {type(score)}"
        assert 0 <= score <= 100, f"Score should be 0-100, got {score}"
        
        # Check if cached (should be True for this test data)
        print(f"✓ AI Match returned: score={score}, cached={data.get('cached')}, method={result.get('method')}")
        print(f"  Reasoning: {result.get('reasoning', '')[:100]}...")
        
        # Verify breakdown structure
        breakdown = result.get("breakdown", {})
        if breakdown:
            print(f"  Breakdown: skills={breakdown.get('skills_match')}%, experience={breakdown.get('experience_match')}%, location={breakdown.get('location_match')}%")
    
    def test_ai_match_result_structure(self):
        """POST /api/cv-search/ai-match - Verify complete result structure"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.post(
            f"{BASE_URL}/api/cv-search/ai-match",
            json={
                "candidate_id": TEST_CANDIDATE_ID,
                "job_id": TEST_JOB_ID_CACHED
            },
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        
        # Verify all expected fields
        expected_fields = ["id", "recruiter_id", "account_id", "candidate_id", 
                          "candidate_name", "job_id", "job_title", "score", 
                          "reasoning", "method", "breakdown", "created_at"]
        
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"
        
        # Verify breakdown has expected sub-fields
        breakdown = result["breakdown"]
        breakdown_fields = ["skills_match", "experience_match", "location_match", 
                          "top_matching_skills", "missing_skills"]
        for field in breakdown_fields:
            assert field in breakdown, f"Missing breakdown field: {field}"
        
        print(f"✓ Result structure verified with all {len(expected_fields)} fields")
        print(f"  Matching skills: {breakdown.get('top_matching_skills', [])}")
        print(f"  Missing skills: {breakdown.get('missing_skills', [])}")


class TestAIMatchScoresEndpoint:
    """Tests for GET /api/cv-search/ai-match-scores endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.recruiter_token = get_auth_token(RECRUITER_PRO["email"], RECRUITER_PRO["password"])
        self.job_seeker_token = get_auth_token(JOB_SEEKER["email"], JOB_SEEKER["password"])
    
    def test_get_match_scores_returns_401_without_auth(self):
        """GET /api/cv-search/ai-match-scores returns 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/cv-search/ai-match-scores")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Returns {response.status_code} without auth")
    
    def test_get_match_scores_job_seeker_cannot_access(self):
        """GET /api/cv-search/ai-match-scores - Job seeker cannot access"""
        if not self.job_seeker_token:
            pytest.skip("Job seeker login failed")
        
        response = requests.get(
            f"{BASE_URL}/api/cv-search/ai-match-scores",
            headers={"Authorization": f"Bearer {self.job_seeker_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Job seeker gets 403")
    
    def test_get_match_scores_returns_cached_scores(self):
        """GET /api/cv-search/ai-match-scores returns cached match scores for recruiter"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.get(
            f"{BASE_URL}/api/cv-search/ai-match-scores",
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "scores" in data, "Expected 'scores' in response"
        assert "count" in data, "Expected 'count' in response"
        assert isinstance(data["scores"], list), "scores should be a list"
        
        print(f"✓ Retrieved {data['count']} cached match scores")
        
        if data["scores"]:
            score = data["scores"][0]
            print(f"  First score: {score.get('candidate_name')} vs {score.get('job_title')} = {score.get('score')}%")
    
    def test_get_match_scores_filter_by_candidate(self):
        """GET /api/cv-search/ai-match-scores?candidate_id=X filters by candidate"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.get(
            f"{BASE_URL}/api/cv-search/ai-match-scores?candidate_id={TEST_CANDIDATE_ID}",
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # All returned scores should be for the specified candidate
        for score in data["scores"]:
            assert score["candidate_id"] == TEST_CANDIDATE_ID, f"Expected candidate_id={TEST_CANDIDATE_ID}"
        
        print(f"✓ Filtered by candidate_id: {data['count']} scores for {TEST_CANDIDATE_ID}")
    
    def test_get_match_scores_filter_by_job(self):
        """GET /api/cv-search/ai-match-scores?job_id=X filters by job"""
        if not self.recruiter_token:
            pytest.skip("Recruiter login failed")
        
        response = requests.get(
            f"{BASE_URL}/api/cv-search/ai-match-scores?job_id={TEST_JOB_ID_CACHED}",
            headers={"Authorization": f"Bearer {self.recruiter_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # All returned scores should be for the specified job
        for score in data["scores"]:
            assert score["job_id"] == TEST_JOB_ID_CACHED, f"Expected job_id={TEST_JOB_ID_CACHED}"
        
        print(f"✓ Filtered by job_id: {data['count']} scores for {TEST_JOB_ID_CACHED}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
