#!/usr/bin/env python3
"""
Backend Test Suite for Job Rocket Payfast Payment Initiation
Tests Payfast payment initiation functionality in sandbox mode with focus on package validation
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://career-launchpad-16.preview.emergentagent.com/api"
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

class PayfastPaymentTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.packages = []
        self.payment_ids = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, files=None, use_params=False):
        """Make HTTP request with proper error handling"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = {}
        
        if headers:
            request_headers.update(headers)
            
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        
        # Don't set Content-Type for file uploads
        if not files and method.upper() in ["POST", "PUT"]:
            request_headers["Content-Type"] = "application/json"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, params=data)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=request_headers, files=files, data=data)
                elif use_params:
                    response = requests.post(url, headers=request_headers, params=data)
                else:
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
        """Setup test environment with demo recruiter login"""
        print_test_header("Setting up Payfast Payment Test Environment")
        
        # Login as demo recruiter (as specified in review request)
        recruiter_login_data = {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", recruiter_login_data)
        if not self.assert_response(response, 200, "Demo Recruiter Login"):
            print_error("Failed to login with demo recruiter account")
            print_info("Trying alternative demo recruiter account...")
            
            # Try alternative demo account
            alt_login_data = {
                "email": "demo.recruiter@test.com",
                "password": "demo123"
            }
            
            response = self.make_request("POST", "/auth/login", alt_login_data)
            if not self.assert_response(response, 200, "Alternative Demo Recruiter Login"):
                return False
            
        login_result = response.json()
        self.recruiter_token = login_result["access_token"]
        self.recruiter_user_id = login_result["user"]["id"]
        
        print_info(f"Logged in as recruiter: {login_result['user']['email']}")
        print_info(f"Recruiter ID: {self.recruiter_user_id}")
        print_info(f"User Role: {login_result['user']['role']}")
        
        # Verify user is recruiter
        if login_result['user']['role'] != 'recruiter':
            print_error(f"User role should be 'recruiter', got '{login_result['user']['role']}'")
            return False
        
        return True

    def test_package_types_validation(self):
        """Test package types validation and CV_SEARCH_UNLIMITED availability"""
        print_test_header("Package Types Validation")
        
        # Get all available packages
        response = self.make_request("GET", "/packages", auth_token=self.recruiter_token)
        if not self.assert_response(response, 200, "Get All Packages"):
            return
        
        packages = response.json()
        if not packages:
            print_error("No packages available for testing")
            return
        
        self.packages = packages
        print_info(f"Found {len(packages)} packages")
        
        # Expected package types from review request
        expected_package_types = [
            "two_listings",
            "five_listings", 
            "unlimited_listings",
            "cv_search_unlimited"  # This was the missing one that caused 422 error
        ]
        
        found_package_types = []
        
        # Test each package and verify structure
        for package in packages:
            package_type = package.get("package_type")
            found_package_types.append(package_type)
            
            print_info(f"Package: {package.get('name')} - Type: {package_type} - Price: R{package.get('price')}")
            
            # Verify required fields
            required_fields = ["id", "name", "package_type", "price", "description"]
            for field in required_fields:
                if field in package:
                    print_success(f"Package {package_type} has {field}")
                else:
                    print_error(f"Package {package_type} missing {field}")
        
        # Check if all expected package types are available
        for expected_type in expected_package_types:
            if expected_type in found_package_types:
                print_success(f"Package type '{expected_type}' is available")
            else:
                print_error(f"Package type '{expected_type}' is MISSING - this could cause 422 errors")
        
        # Special focus on CV_SEARCH_UNLIMITED (the one mentioned in review request)
        cv_unlimited_package = None
        for package in packages:
            if package.get("package_type") == "cv_search_unlimited":
                cv_unlimited_package = package
                break
        
        if cv_unlimited_package:
            print_success("CV_SEARCH_UNLIMITED package found - this should resolve the 422 error")
            print_info(f"CV_SEARCH_UNLIMITED details: {cv_unlimited_package}")
        else:
            print_error("CV_SEARCH_UNLIMITED package NOT FOUND - this is likely causing the 422 error")

    def test_payment_initiation_endpoint(self):
        """Test payment initiation endpoint with all valid package types"""
        print_test_header("Payment Initiation Endpoint Testing")
        
        if not self.packages:
            print_error("No packages available for payment initiation testing")
            return
        
        # Test payment initiation for each package type
        valid_package_types = ["two_listings", "five_listings", "unlimited_listings", "cv_search_unlimited"]
        
        for package_type in valid_package_types:
            # Find package with this type
            test_package = None
            for package in self.packages:
                if package.get("package_type") == package_type:
                    test_package = package
                    break
            
            if not test_package:
                print_error(f"Package type '{package_type}' not found in available packages")
                continue
            
            print_info(f"Testing payment initiation for {package_type}")
            
            # Test payment initiation
            payment_params = {
                "package_type": package_type
            }
            
            response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
            if self.assert_response(response, 200, f"Payment Initiation - {package_type}"):
                result = response.json()
                
                # Verify required fields in response
                required_fields = ["payment_id", "payment_url", "amount", "currency", "package_name"]
                for field in required_fields:
                    if field in result:
                        print_success(f"{package_type} payment response has {field}: {result[field]}")
                    else:
                        print_error(f"{package_type} payment response missing {field}")
                
                # Verify payment URL points to sandbox
                payment_url = result.get("payment_url", "")
                if "sandbox.payfast.co.za" in payment_url:
                    print_success(f"{package_type} payment URL correctly points to Payfast sandbox")
                    print_info(f"Sandbox URL: {payment_url}")
                else:
                    print_error(f"{package_type} payment URL should point to sandbox, got: {payment_url}")
                
                # Verify amount matches package price
                expected_amount = test_package.get("price")
                actual_amount = result.get("amount")
                if expected_amount and actual_amount:
                    if abs(float(expected_amount) - float(actual_amount)) < 0.01:
                        print_success(f"{package_type} payment amount correct: R{actual_amount}")
                    else:
                        print_error(f"{package_type} payment amount mismatch: expected R{expected_amount}, got R{actual_amount}")
                
                # Verify currency is ZAR
                if result.get("currency") == "ZAR":
                    print_success(f"{package_type} payment currency is ZAR")
                else:
                    print_error(f"{package_type} payment currency should be ZAR, got {result.get('currency')}")
                
                # Store payment ID for potential webhook testing
                if "payment_id" in result:
                    self.payment_ids.append(result["payment_id"])
            else:
                # This is the 422 error we're trying to resolve
                if response and response.status_code == 422:
                    print_error(f"422 Unprocessable Entity for {package_type} - this is the error mentioned in review request")
                    try:
                        error_detail = response.json()
                        print_error(f"Error details: {error_detail}")
                    except:
                        print_error(f"Error response: {response.text}")

    def test_payfast_sandbox_configuration(self):
        """Test Payfast sandbox mode configuration"""
        print_test_header("Payfast Sandbox Configuration Testing")
        
        if not self.packages:
            print_error("No packages available for sandbox configuration testing")
            return
        
        # Test with first available package
        test_package = self.packages[0]
        
        payment_data = {
            "package_type": test_package["package_type"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Sandbox Configuration Test"):
            result = response.json()
            payment_url = result.get("payment_url", "")
            
            # Verify sandbox URL structure
            if "sandbox.payfast.co.za" in payment_url:
                print_success("✅ PAYFAST_SANDBOX=True is working correctly")
                print_success("✅ Payment URLs point to sandbox environment")
                print_info(f"Sandbox URL: {payment_url}")
                
                # Verify it's the correct sandbox URL format
                if "https://sandbox.payfast.co.za/eng/process" in payment_url:
                    print_success("✅ Correct sandbox URL format: https://sandbox.payfast.co.za/eng/process")
                else:
                    print_warning(f"Sandbox URL format may be different: {payment_url}")
            else:
                print_error("❌ PAYFAST_SANDBOX=True is NOT working - URLs should point to sandbox")
                print_error(f"Got URL: {payment_url}")
                
                # Check if it's pointing to production (which would be wrong for testing)
                if "www.payfast.co.za" in payment_url:
                    print_error("❌ CRITICAL: Payment URL points to PRODUCTION Payfast - this is dangerous for testing!")
        
        # Test multiple packages to ensure consistent sandbox behavior
        print_info("Testing sandbox configuration across multiple package types...")
        
        for i, package in enumerate(self.packages[:3]):  # Test first 3 packages
            payment_data = {
                "package_type": package["package_type"]
            }
            
            response = self.make_request("POST", "/payments/initiate", data=payment_data, auth_token=self.recruiter_token)
            if response and response.status_code == 200:
                result = response.json()
                payment_url = result.get("payment_url", "")
                
                if "sandbox.payfast.co.za" in payment_url:
                    print_success(f"Package {package['name']} uses sandbox URL ✅")
                else:
                    print_error(f"Package {package['name']} NOT using sandbox URL ❌")

    def test_payfast_payment_data_structure(self):
        """Test that payment data includes all required Payfast fields"""
        print_test_header("Payfast Payment Data Structure")
        
        if not self.packages:
            print_error("No packages available for data structure testing")
            return
        
        test_package = self.packages[0]
        
        payment_data = {
            "package_type": test_package["package_type"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Payment Data Structure Test"):
            result = response.json()
            
            # Check for all required Payfast fields in the response
            payfast_required_fields = {
                "payment_id": "Unique payment identifier",
                "payment_url": "Payfast payment URL",
                "amount": "Payment amount",
                "currency": "Payment currency (should be ZAR)",
                "package_name": "Package/item name"
            }
            
            for field, description in payfast_required_fields.items():
                if field in result and result[field]:
                    print_success(f"✅ {field}: {result[field]} ({description})")
                else:
                    print_error(f"❌ Missing or empty {field} ({description})")
            
            # Verify payment URL contains query parameters (typical for Payfast)
            payment_url = result.get("payment_url", "")
            if "?" in payment_url and "&" in payment_url:
                print_success("✅ Payment URL contains query parameters (typical for Payfast)")
                
                # Try to extract some common Payfast parameters
                if "merchant_id=" in payment_url:
                    print_success("✅ Payment URL contains merchant_id parameter")
                if "amount=" in payment_url:
                    print_success("✅ Payment URL contains amount parameter")
                if "item_name=" in payment_url:
                    print_success("✅ Payment URL contains item_name parameter")
            else:
                print_warning("⚠️ Payment URL may not contain expected query parameters")

    def test_recruiter_authentication_requirement(self):
        """Test that payment initiation requires recruiter authentication"""
        print_test_header("Recruiter Authentication Requirement")
        
        if not self.packages:
            print_error("No packages available for authentication testing")
            return
        
        test_package = self.packages[0]
        payment_data = {
            "package_type": test_package["package_type"]
        }
        
        # Test 1: No authentication (should fail)
        response = self.make_request("POST", "/payments/initiate", data=payment_data)
        if self.assert_response(response, 401, "Payment Without Authentication (Should Fail)"):
            print_success("✅ Payment initiation correctly requires authentication")
        
        # Test 2: Invalid token (should fail)
        response = self.make_request("POST", "/payments/initiate", data=payment_data, auth_token="invalid_token")
        if self.assert_response(response, 401, "Payment With Invalid Token (Should Fail)"):
            print_success("✅ Payment initiation correctly validates authentication token")
        
        # Test 3: Valid recruiter token (should succeed)
        response = self.make_request("POST", "/payments/initiate", data=payment_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Payment With Valid Recruiter Token"):
            print_success("✅ Payment initiation works with valid recruiter authentication")

    def test_invalid_package_types(self):
        """Test payment initiation with invalid package types"""
        print_test_header("Invalid Package Types Testing")
        
        invalid_package_types = [
            "invalid_package",
            "nonexistent_type",
            "",
            None,
            "cv_search_5",  # Non-existent CV search package
            "unlimited_cv"  # Similar but wrong name
        ]
        
        for invalid_type in invalid_package_types:
            print_info(f"Testing invalid package type: {invalid_type}")
            
            payment_data = {
                "package_type": invalid_type
            }
            
            response = self.make_request("POST", "/payments/initiate", data=payment_data, auth_token=self.recruiter_token)
            
            # Should return 400 (Bad Request) or 422 (Unprocessable Entity)
            if response and response.status_code in [400, 422]:
                print_success(f"✅ Invalid package type '{invalid_type}' correctly rejected with status {response.status_code}")
            else:
                expected_status = response.status_code if response else "No response"
                print_error(f"❌ Invalid package type '{invalid_type}' should be rejected, got status: {expected_status}")

    def run_all_tests(self):
        """Run all Payfast payment initiation tests"""
        print_test_header("Starting Payfast Payment Initiation Test Suite")
        print_info("Focus: Testing payment initiation functionality in sandbox mode")
        print_info("Specific focus on CV_SEARCH_UNLIMITED package and 422 error resolution")
        
        if not self.setup_test_environment():
            print_error("Failed to setup test environment")
            return
        
        # Run all test methods in logical order
        test_methods = [
            self.test_package_types_validation,
            self.test_payment_initiation_endpoint,
            self.test_payfast_sandbox_configuration,
            self.test_payfast_payment_data_structure,
            self.test_recruiter_authentication_requirement,
            self.test_invalid_package_types
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print_error(f"Test {test_method.__name__} failed with exception: {str(e)}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"{test_method.__name__}: {str(e)}")
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print final test results summary"""
        print_test_header("Payfast Payment Initiation Test Results")
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        print_info(f"Total Tests: {total_tests}")
        print_success(f"Passed: {passed}")
        
        if failed > 0:
            print_error(f"Failed: {failed}")
            print_error("Failed Tests:")
            for error in self.test_results["errors"]:
                print_error(f"  - {error}")
        else:
            print_success("🎉 All Payfast payment initiation tests passed!")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print_info(f"Success Rate: {success_rate:.1f}%")
        
        # Summary of key findings
        print_test_header("Key Findings Summary")
        if "cv_search_unlimited" in [pkg.get("package_type") for pkg in self.packages]:
            print_success("✅ CV_SEARCH_UNLIMITED package is available - 422 error should be resolved")
        else:
            print_error("❌ CV_SEARCH_UNLIMITED package is missing - this is likely causing 422 errors")
        
        if any("sandbox.payfast.co.za" in str(pid) for pid in self.payment_ids):
            print_success("✅ Payfast sandbox mode is working correctly")
        else:
            print_warning("⚠️ Could not verify sandbox mode functionality")


if __name__ == "__main__":
    print_test_header("Job Rocket Payfast Payment Initiation Test Suite")
    print_info("Testing Payfast payment initiation functionality specifically")
    print_info("Focus: Sandbox mode, package validation, and CV_SEARCH_UNLIMITED availability")
    
    # Run the Payfast payment test suite
    payfast_test_suite = PayfastPaymentTestSuite()
    payfast_test_suite.run_all_tests()