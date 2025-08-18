#!/usr/bin/env python3
"""
Backend Test Suite for Job Rocket Job Posting System
Tests all job posting API endpoints including single job creation, bulk upload, and company access
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import io
import csv

# Configuration
BASE_URL = "https://rocket-ats.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}Testing: {test_name}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

class InvitationTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.company_id = None
        self.branch_ids = []
        self.invitation_tokens = []
        self.invitation_ids = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = HEADERS.copy()
        
        if headers:
            request_headers.update(headers)
            
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=request_headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=request_headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {str(e)}")
            return None

    def assert_response(self, response, expected_status, test_name):
        """Assert response status and handle results"""
        if response is None:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: Request failed")
            print_error(f"{test_name}: Request failed")
            return False
            
        if response.status_code == expected_status:
            self.test_results["passed"] += 1
            print_success(f"{test_name}: Status {response.status_code}")
            return True
        else:
            self.test_results["failed"] += 1
            error_msg = f"{test_name}: Expected {expected_status}, got {response.status_code}"
            if response.text:
                error_msg += f" - {response.text}"
            self.test_results["errors"].append(error_msg)
            print_error(error_msg)
            return False

    def setup_test_environment(self):
        """Setup test environment with recruiter login and company structure"""
        print_test_header("Setting up Test Environment")
        
        # Login as recruiter
        login_data = {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if not self.assert_response(response, 200, "Recruiter Login"):
            return False
            
        login_result = response.json()
        self.recruiter_token = login_result["access_token"]
        self.recruiter_user_id = login_result["user"]["id"]
        self.company_id = self.recruiter_user_id  # In this system, user_id = company_id for recruiters
        
        print_info(f"Logged in as recruiter: {login_result['user']['email']}")
        print_info(f"Company ID: {self.company_id}")
        
        # Create test branches for invitation testing
        branch_data = {
            "name": "Test Branch - Johannesburg",
            "location": "Johannesburg, Gauteng",
            "email": "jhb@techcorp.demo",
            "phone": "+27 11 123 4567",
            "is_headquarters": False
        }
        
        response = self.make_request("POST", "/company/branches", branch_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Test Branch"):
            branch_result = response.json()
            self.branch_ids.append(branch_result["id"])
            print_info(f"Created test branch: {branch_result['id']}")
        
        return True

    def test_create_team_invitation(self):
        """Test POST /api/company/invite - Create team invitation"""
        print_test_header("Create Team Invitation")
        
        # Test 1: Valid invitation with branch assignment
        invitation_data = {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "recruiter",
            "branch_ids": self.branch_ids
        }
        
        response = self.make_request("POST", "/company/invite", invitation_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Valid Invitation"):
            result = response.json()
            self.invitation_tokens.append(result["invitation_token"])
            self.invitation_ids.append(result["id"])
            print_info(f"Created invitation with token: {result['invitation_token'][:20]}...")
            print_info(f"Invitation expires at: {result['expires_at']}")
        
        # Test 2: Invitation with different roles
        for role in ["manager", "admin", "viewer"]:
            invitation_data = {
                "email": f"test.{role}@example.com",
                "first_name": "Test",
                "last_name": role.capitalize(),
                "role": role,
                "branch_ids": []
            }
            
            response = self.make_request("POST", "/company/invite", invitation_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Create {role.capitalize()} Invitation"):
                result = response.json()
                self.invitation_tokens.append(result["invitation_token"])
                self.invitation_ids.append(result["id"])
        
        # Test 3: Duplicate invitation (should fail)
        response = self.make_request("POST", "/company/invite", invitation_data, auth_token=self.recruiter_token)
        self.assert_response(response, 400, "Duplicate Invitation (Should Fail)")
        
        # Test 4: Invalid branch ID (should fail)
        invalid_invitation = {
            "email": "invalid.branch@example.com",
            "first_name": "Invalid",
            "last_name": "Branch",
            "role": "recruiter",
            "branch_ids": ["invalid-branch-id"]
        }
        
        response = self.make_request("POST", "/company/invite", invalid_invitation, auth_token=self.recruiter_token)
        self.assert_response(response, 400, "Invalid Branch ID (Should Fail)")
        
        # Test 5: Unauthorized access (no token)
        response = self.make_request("POST", "/company/invite", invitation_data)
        self.assert_response(response, 401, "Unauthorized Access (Should Fail)")

    def test_view_company_invitations(self):
        """Test GET /api/company/invitations - View all company invitations"""
        print_test_header("View Company Invitations")
        
        # Test 1: Get all invitations
        response = self.make_request("GET", "/company/invitations", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Company Invitations"):
            invitations = response.json()
            print_info(f"Found {len(invitations)} invitations")
            
            # Verify invitation structure
            if invitations:
                invitation = invitations[0]
                required_fields = ["id", "email", "first_name", "last_name", "role", "status", "invitation_token", "expires_at"]
                for field in required_fields:
                    if field in invitation:
                        print_success(f"Invitation contains required field: {field}")
                    else:
                        print_error(f"Invitation missing required field: {field}")
        
        # Test 2: Unauthorized access
        response = self.make_request("GET", "/company/invitations")
        self.assert_response(response, 401, "Unauthorized Access (Should Fail)")

    def test_get_invitation_details_public(self):
        """Test GET /api/public/invitations/{invitation_token} - Public invitation details"""
        print_test_header("Get Public Invitation Details")
        
        if not self.invitation_tokens:
            print_error("No invitation tokens available for testing")
            return
        
        # Test 1: Valid invitation token
        token = self.invitation_tokens[0]
        response = self.make_request("GET", f"/public/invitations/{token}")
        if self.assert_response(response, 200, "Get Valid Invitation Details"):
            details = response.json()
            required_fields = ["invitation_id", "company_name", "first_name", "last_name", "role", "expires_at"]
            for field in required_fields:
                if field in details:
                    print_success(f"Invitation details contain: {field}")
                else:
                    print_error(f"Invitation details missing: {field}")
            
            print_info(f"Company: {details.get('company_name', 'N/A')}")
            print_info(f"Role: {details.get('role', 'N/A')}")
            print_info(f"Branches: {len(details.get('branches', []))}")
        
        # Test 2: Invalid invitation token
        response = self.make_request("GET", "/public/invitations/invalid-token-123")
        self.assert_response(response, 404, "Invalid Token (Should Fail)")
        
        # Test 3: Empty token
        response = self.make_request("GET", "/public/invitations/")
        self.assert_response(response, 404, "Empty Token (Should Fail)")

    def test_register_via_invitation(self):
        """Test POST /api/public/invitations/{invitation_token}/register - Register new user via invitation"""
        print_test_header("Register via Invitation")
        
        if not self.invitation_tokens:
            print_error("No invitation tokens available for testing")
            return
        
        # Test 1: Valid registration
        token = self.invitation_tokens[0]
        registration_data = {
            "email": "john.doe@example.com",  # Must match invitation email
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = self.make_request("POST", f"/public/invitations/{token}/register", registration_data)
        if self.assert_response(response, 200, "Valid Registration"):
            result = response.json()
            if "access_token" in result and "user" in result:
                print_success("Registration returned access token and user data")
                print_info(f"New user ID: {result['user']['id']}")
                print_info(f"User role: {result['user']['role']}")
            else:
                print_error("Registration response missing required fields")
        
        # Test 2: Email mismatch (should fail)
        if len(self.invitation_tokens) > 1:
            token = self.invitation_tokens[1]
            wrong_email_data = {
                "email": "wrong.email@example.com",
                "password": "securepassword123",
                "first_name": "Wrong",
                "last_name": "Email"
            }
            
            response = self.make_request("POST", f"/public/invitations/{token}/register", wrong_email_data)
            self.assert_response(response, 400, "Email Mismatch (Should Fail)")
        
        # Test 3: Already used invitation (should fail)
        response = self.make_request("POST", f"/public/invitations/{self.invitation_tokens[0]}/register", registration_data)
        self.assert_response(response, 400, "Already Used Invitation (Should Fail)")
        
        # Test 4: Invalid token
        invalid_registration = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = self.make_request("POST", "/public/invitations/invalid-token/register", invalid_registration)
        self.assert_response(response, 404, "Invalid Token (Should Fail)")

    def test_cancel_invitation(self):
        """Test POST /api/company/invitations/{invitation_id}/cancel - Cancel pending invitation"""
        print_test_header("Cancel Invitation")
        
        if not self.invitation_ids:
            print_error("No invitation IDs available for testing")
            return
        
        # Test 1: Cancel valid pending invitation
        if len(self.invitation_ids) > 1:  # Keep first one for other tests
            invitation_id = self.invitation_ids[1]
            response = self.make_request("POST", f"/company/invitations/{invitation_id}/cancel", auth_token=self.recruiter_token)
            self.assert_response(response, 200, "Cancel Valid Invitation")
        
        # Test 2: Cancel non-existent invitation
        response = self.make_request("POST", "/company/invitations/invalid-id/cancel", auth_token=self.recruiter_token)
        self.assert_response(response, 404, "Cancel Non-existent Invitation (Should Fail)")
        
        # Test 3: Unauthorized cancellation
        if len(self.invitation_ids) > 2:
            invitation_id = self.invitation_ids[2]
            response = self.make_request("POST", f"/company/invitations/{invitation_id}/cancel")
            self.assert_response(response, 401, "Unauthorized Cancellation (Should Fail)")

    def test_invitation_expiration(self):
        """Test invitation expiration logic"""
        print_test_header("Invitation Expiration Logic")
        
        # Note: We can't easily test actual expiration without manipulating time
        # But we can test the validation logic by checking invitation details
        
        if self.invitation_tokens:
            token = self.invitation_tokens[0]
            response = self.make_request("GET", f"/public/invitations/{token}")
            if response and response.status_code == 200:
                details = response.json()
                expires_at = details.get("expires_at")
                if expires_at:
                    print_info(f"Invitation expires at: {expires_at}")
                    # Check if expiration is in the future (should be ~7 days from creation)
                    try:
                        exp_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        now = datetime.now(exp_time.tzinfo)
                        if exp_time > now:
                            print_success("Invitation expiration is in the future")
                        else:
                            print_error("Invitation appears to be expired")
                    except Exception as e:
                        print_warning(f"Could not parse expiration time: {e}")

    def test_authentication_and_authorization(self):
        """Test authentication and authorization for invitation endpoints"""
        print_test_header("Authentication & Authorization")
        
        # Test endpoints that require authentication
        protected_endpoints = [
            ("POST", "/company/invite", {"email": "test@example.com", "first_name": "Test", "last_name": "User"}),
            ("GET", "/company/invitations", None),
            ("POST", "/company/invitations/test-id/cancel", None)
        ]
        
        for method, endpoint, data in protected_endpoints:
            response = self.make_request(method, endpoint, data)
            self.assert_response(response, 401, f"Unauthorized {method} {endpoint} (Should Fail)")
        
        # Test endpoints that should be public (no auth required)
        if self.invitation_tokens:
            token = self.invitation_tokens[0]
            public_endpoints = [
                ("GET", f"/public/invitations/{token}", None),
                # Note: We can't test registration again as it would fail due to duplicate user
            ]
            
            for method, endpoint, data in public_endpoints:
                response = self.make_request(method, endpoint, data)
                # These should not return 401 (they might return other errors, but not auth errors)
                if response and response.status_code != 401:
                    print_success(f"Public endpoint {endpoint} accessible without auth")
                else:
                    print_error(f"Public endpoint {endpoint} requires auth (unexpected)")

    def test_branch_assignment_functionality(self):
        """Test branch assignment in invitations"""
        print_test_header("Branch Assignment Functionality")
        
        # Test invitation with multiple branches
        if len(self.branch_ids) > 0:
            invitation_data = {
                "email": "multi.branch@example.com",
                "first_name": "Multi",
                "last_name": "Branch",
                "role": "recruiter",
                "branch_ids": self.branch_ids
            }
            
            response = self.make_request("POST", "/company/invite", invitation_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, "Invitation with Branch Assignment"):
                result = response.json()
                if result.get("branch_ids") == self.branch_ids:
                    print_success("Branch IDs correctly assigned to invitation")
                else:
                    print_error("Branch IDs not correctly assigned")
                
                # Store for cleanup
                self.invitation_tokens.append(result["invitation_token"])
                self.invitation_ids.append(result["id"])

    def test_error_handling(self):
        """Test various error conditions and edge cases"""
        print_test_header("Error Handling & Edge Cases")
        
        # Test malformed requests
        malformed_requests = [
            ("POST", "/company/invite", {"email": "invalid-email"}, "Invalid Email Format"),
            ("POST", "/company/invite", {"first_name": "Test"}, "Missing Required Fields"),
            ("POST", "/company/invite", {}, "Empty Request Body"),
        ]
        
        for method, endpoint, data, test_name in malformed_requests:
            response = self.make_request(method, endpoint, data, auth_token=self.recruiter_token)
            if response and response.status_code >= 400:
                print_success(f"{test_name}: Properly rejected with status {response.status_code}")
            else:
                print_error(f"{test_name}: Should have been rejected")

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print_test_header("Cleaning Up Test Data")
        
        # Cancel remaining invitations
        for invitation_id in self.invitation_ids:
            response = self.make_request("POST", f"/company/invitations/{invitation_id}/cancel", auth_token=self.recruiter_token)
            if response and response.status_code == 200:
                print_info(f"Cancelled invitation: {invitation_id}")
        
        # Note: We don't delete the test branch as it might be used by other tests
        # In a real test environment, you might want to clean up branches too

    def run_all_tests(self):
        """Run all invitation system tests"""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 Starting Job Rocket Invitation System Tests{Colors.ENDC}")
        print(f"{Colors.BLUE}Testing against: {BASE_URL}{Colors.ENDC}")
        print(f"{Colors.BLUE}Timestamp: {datetime.now().isoformat()}{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            # Setup
            if not self.setup_test_environment():
                print_error("Failed to setup test environment. Aborting tests.")
                return
            
            # Run all test suites
            self.test_create_team_invitation()
            self.test_view_company_invitations()
            self.test_get_invitation_details_public()
            self.test_register_via_invitation()
            self.test_cancel_invitation()
            self.test_invitation_expiration()
            self.test_authentication_and_authorization()
            self.test_branch_assignment_functionality()
            self.test_error_handling()
            
            # Cleanup
            self.cleanup_test_data()
            
        except Exception as e:
            print_error(f"Test suite failed with exception: {str(e)}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Test suite exception: {str(e)}")
        
        # Print final results
        end_time = time.time()
        duration = end_time - start_time
        
        print_test_header("Test Results Summary")
        print(f"{Colors.GREEN}✅ Passed: {self.test_results['passed']}{Colors.ENDC}")
        print(f"{Colors.RED}❌ Failed: {self.test_results['failed']}{Colors.ENDC}")
        print(f"{Colors.BLUE}⏱️  Duration: {duration:.2f} seconds{Colors.ENDC}")
        
        if self.test_results["errors"]:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors encountered:{Colors.ENDC}")
            for error in self.test_results["errors"]:
                print(f"{Colors.RED}  • {error}{Colors.ENDC}")
        
        # Determine overall result
        if self.test_results["failed"] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Invitation system is working correctly.{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}💥 Some tests failed. Please review the errors above.{Colors.ENDC}")
            return False

if __name__ == "__main__":
    test_suite = InvitationTestSuite()
    success = test_suite.run_all_tests()
    exit(0 if success else 1)