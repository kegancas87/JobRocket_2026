#!/usr/bin/env python3
"""
Backend Test Suite for Job Rocket Discount Codes System and Payfast Sandbox Mode
Tests discount codes system, admin management, payment integration, and Payfast sandbox configuration
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

class DiscountCodesTestSuite:
    def __init__(self):
        self.admin_token = None
        self.admin_user_id = None
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.discount_codes = []
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
        """Setup test environment with admin and recruiter login"""
        print_test_header("Setting up Test Environment")
        
        # Login as admin
        admin_login_data = {
            "email": "admin@jobrocket.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_login_data)
        if not self.assert_response(response, 200, "Admin Login"):
            return False
            
        login_result = response.json()
        self.admin_token = login_result["access_token"]
        self.admin_user_id = login_result["user"]["id"]
        
        print_info(f"Logged in as admin: {login_result['user']['email']}")
        print_info(f"Admin ID: {self.admin_user_id}")
        print_info(f"User Role: {login_result['user']['role']}")
        
        # Login as recruiter for payment tests
        recruiter_login_data = {
            "email": "demo.recruiter@test.com",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", recruiter_login_data)
        if not self.assert_response(response, 200, "Recruiter Login"):
            return False
            
        recruiter_result = response.json()
        self.recruiter_token = recruiter_result["access_token"]
        self.recruiter_user_id = recruiter_result["user"]["id"]
        
        print_info(f"Logged in as recruiter: {recruiter_result['user']['email']}")
        print_info(f"Recruiter ID: {self.recruiter_user_id}")
        print_info(f"Recruiter Role: {recruiter_result['user']['role']}")
        
        return True

    def test_payfast_sandbox_configuration(self):
        """Test Payfast sandbox mode configuration"""
        print_test_header("Payfast Sandbox Mode Configuration")
        
        # Get packages first
        response = self.make_request("GET", "/packages", auth_token=self.recruiter_token)
        if not self.assert_response(response, 200, "Get Packages"):
            return
        
        packages = response.json()
        if not packages:
            print_error("No packages available for testing")
            return
        
        self.packages = packages
        test_package = packages[0]  # Use first package for testing
        
        # Test 1: Initiate payment and verify sandbox URL
        payment_params = {
            "package_type": test_package["package_type"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
        if self.assert_response(response, 200, "Initiate Payment in Sandbox Mode"):
            result = response.json()
            payment_url = result.get("payment_url", "")
            
            # Verify payment URL points to sandbox
            if "sandbox.payfast.co.za" in payment_url:
                print_success("Payment URL correctly points to Payfast sandbox")
                print_info(f"Sandbox URL: {payment_url}")
            else:
                print_error(f"Payment URL should point to sandbox, got: {payment_url}")
            
            # Verify other payment fields
            required_fields = ["payment_id", "amount", "currency", "package_name"]
            for field in required_fields:
                if field in result:
                    print_success(f"Payment response contains {field}: {result[field]}")
                else:
                    print_error(f"Payment response missing {field}")
            
            # Store payment ID for webhook testing
            if "payment_id" in result:
                self.payment_ids.append(result["payment_id"])
        
        # Test 2: Verify sandbox environment variables are working
        # This is implicit in the URL test above, but we can test multiple packages
        for i, package in enumerate(packages[:3]):  # Test first 3 packages
            payment_params = {
                "package_type": package["package_type"]
            }
            
            response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
            if self.assert_response(response, 200, f"Sandbox Payment for {package['name']}"):
                result = response.json()
                payment_url = result.get("payment_url", "")
                
                if "sandbox.payfast.co.za" in payment_url:
                    print_success(f"Package {package['name']} uses sandbox URL")
                else:
                    print_error(f"Package {package['name']} not using sandbox URL")

    def test_admin_discount_codes_management(self):
        """Test admin discount codes management endpoints"""
        print_test_header("Admin Discount Codes Management")
        
        # Test 1: Create percentage discount code
        percentage_discount = {
            "code": "WELCOME20",
            "name": "Welcome 20% Off",
            "description": "20% discount for new customers",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "minimum_amount": 1000.0,
            "maximum_discount": 500.0,
            "usage_limit": 100,
            "user_limit": 1,
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        }
        
        response = self.make_request("POST", "/admin/discount-codes", percentage_discount, auth_token=self.admin_token)
        if self.assert_response(response, 200, "Create Percentage Discount Code"):
            result = response.json()
            self.discount_codes.append(result)
            print_success(f"Created discount code: {result['code']}")
            
            # Verify all fields are saved correctly
            for key, value in percentage_discount.items():
                if key in result and str(result[key]) == str(value):
                    print_success(f"Field {key} correctly saved")
                elif key in result:
                    print_info(f"Field {key}: expected {value}, got {result[key]}")
        
        # Test 2: Create fixed amount discount code
        fixed_discount = {
            "code": "SAVE500",
            "name": "Save R500",
            "description": "Fixed R500 discount",
            "discount_type": "fixed_amount",
            "discount_value": 500.0,
            "minimum_amount": 2000.0,
            "usage_limit": 50,
            "applicable_packages": ["unlimited_listings", "five_listings"]
        }
        
        response = self.make_request("POST", "/admin/discount-codes", fixed_discount, auth_token=self.admin_token)
        if self.assert_response(response, 200, "Create Fixed Amount Discount Code"):
            result = response.json()
            self.discount_codes.append(result)
            print_success(f"Created fixed discount code: {result['code']}")
        
        # Test 3: Create discount with expiry date
        expiry_discount = {
            "code": "EXPIRY10",
            "name": "Expiry Test 10%",
            "description": "Discount with expiry date",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "valid_until": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
        }
        
        response = self.make_request("POST", "/admin/discount-codes", expiry_discount, auth_token=self.admin_token)
        if self.assert_response(response, 200, "Create Discount with Expiry"):
            result = response.json()
            self.discount_codes.append(result)
            print_success(f"Created expiry discount code: {result['code']}")
        
        # Test 4: Test validation - duplicate code (should fail)
        duplicate_discount = {
            "code": "WELCOME20",  # Same as first discount
            "name": "Duplicate Code",
            "discount_type": "percentage",
            "discount_value": 15.0
        }
        
        response = self.make_request("POST", "/admin/discount-codes", duplicate_discount, auth_token=self.admin_token)
        self.assert_response(response, 400, "Create Duplicate Code (Should Fail)")
        
        # Test 5: Test validation - percentage > 100 (should fail)
        invalid_percentage = {
            "code": "INVALID150",
            "name": "Invalid Percentage",
            "discount_type": "percentage",
            "discount_value": 150.0
        }
        
        response = self.make_request("POST", "/admin/discount-codes", invalid_percentage, auth_token=self.admin_token)
        self.assert_response(response, 422, "Invalid Percentage > 100 (Should Fail)")
        
        # Test 6: Test validation - negative discount value (should fail)
        negative_discount = {
            "code": "NEGATIVE",
            "name": "Negative Discount",
            "discount_type": "fixed_amount",
            "discount_value": -100.0
        }
        
        response = self.make_request("POST", "/admin/discount-codes", negative_discount, auth_token=self.admin_token)
        self.assert_response(response, 422, "Negative Discount Value (Should Fail)")
        
        # Test 7: Non-admin access (should fail)
        response = self.make_request("POST", "/admin/discount-codes", percentage_discount, auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Non-admin Create Discount (Should Fail)")

    def test_admin_discount_codes_crud(self):
        """Test CRUD operations for discount codes"""
        print_test_header("Admin Discount Codes CRUD Operations")
        
        if not self.discount_codes:
            print_error("No discount codes available for CRUD testing")
            return
        
        # Test 1: List all discount codes
        response = self.make_request("GET", "/admin/discount-codes", auth_token=self.admin_token)
        if self.assert_response(response, 200, "List All Discount Codes"):
            codes = response.json()
            print_info(f"Found {len(codes)} discount codes")
            
            if codes:
                code = codes[0]
                required_fields = ["id", "code", "name", "discount_type", "discount_value", "status", "created_date"]
                for field in required_fields:
                    if field in code:
                        print_success(f"Discount code contains field: {field}")
                    else:
                        print_error(f"Discount code missing field: {field}")
        
        # Test 2: Get specific discount code
        test_code = self.discount_codes[0]
        response = self.make_request("GET", f"/admin/discount-codes/{test_code['id']}", auth_token=self.admin_token)
        if self.assert_response(response, 200, "Get Specific Discount Code"):
            result = response.json()
            if result["id"] == test_code["id"]:
                print_success("Retrieved correct discount code")
            else:
                print_error("Retrieved wrong discount code")
        
        # Test 3: Update discount code
        update_data = {
            "name": "Updated Welcome Discount",
            "description": "Updated description for welcome discount",
            "discount_value": 25.0
        }
        
        response = self.make_request("PUT", f"/admin/discount-codes/{test_code['id']}", update_data, auth_token=self.admin_token)
        if self.assert_response(response, 200, "Update Discount Code"):
            result = response.json()
            if result["name"] == update_data["name"]:
                print_success("Discount code name updated successfully")
            if result["discount_value"] == update_data["discount_value"]:
                print_success("Discount code value updated successfully")
        
        # Test 4: Deactivate discount code
        response = self.make_request("POST", f"/admin/discount-codes/{test_code['id']}/deactivate", auth_token=self.admin_token)
        if self.assert_response(response, 200, "Deactivate Discount Code"):
            # Verify code is deactivated
            response = self.make_request("GET", f"/admin/discount-codes/{test_code['id']}", auth_token=self.admin_token)
            if response and response.status_code == 200:
                result = response.json()
                if result["status"] == "inactive":
                    print_success("Discount code successfully deactivated")
                else:
                    print_error(f"Discount code status should be 'inactive', got '{result['status']}'")
        
        # Test 5: Get usage statistics
        response = self.make_request("GET", "/admin/discount-codes/stats/usage", auth_token=self.admin_token)
        if self.assert_response(response, 200, "Get Usage Statistics"):
            stats = response.json()
            print_info(f"Usage statistics: {stats}")
            
            # Verify stats structure
            if isinstance(stats, dict):
                print_success("Usage statistics returned as dictionary")
            else:
                print_error("Usage statistics should be a dictionary")
        
        # Test 6: Try to get non-existent discount code (should fail)
        fake_id = str(uuid.uuid4())
        response = self.make_request("GET", f"/admin/discount-codes/{fake_id}", auth_token=self.admin_token)
        self.assert_response(response, 404, "Get Non-existent Discount Code (Should Fail)")
        
        # Test 7: Delete discount code
        if len(self.discount_codes) > 1:
            delete_code = self.discount_codes[1]
            response = self.make_request("DELETE", f"/admin/discount-codes/{delete_code['id']}", auth_token=self.admin_token)
            if self.assert_response(response, 200, "Delete Discount Code"):
                # Verify code is deleted
                response = self.make_request("GET", f"/admin/discount-codes/{delete_code['id']}", auth_token=self.admin_token)
                self.assert_response(response, 404, "Verify Discount Code Deleted")
        
        # Test 8: Non-admin access to CRUD operations (should fail)
        response = self.make_request("GET", "/admin/discount-codes", auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Non-admin List Codes (Should Fail)")
        
        response = self.make_request("PUT", f"/admin/discount-codes/{test_code['id']}", update_data, auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Non-admin Update Code (Should Fail)")

    def test_discount_codes_payment_integration(self):
        """Test discount codes integration with payment system"""
        print_test_header("Discount Codes Payment Integration")
        
        if not self.packages or not self.discount_codes:
            print_error("No packages or discount codes available for payment integration testing")
            return
        
        # Find an active discount code (create a new one if needed since we deactivated one earlier)
        active_discount = None
        for code in self.discount_codes:
            if code.get("status") == "active":
                active_discount = code
                break
        
        if not active_discount:
            # Create a new active discount code for testing
            test_discount = {
                "code": "TESTPAY20",
                "name": "Test Payment 20% Off",
                "description": "Test discount for payment integration",
                "discount_type": "percentage",
                "discount_value": 20.0,
                "minimum_amount": 1000.0
            }
            
            response = self.make_request("POST", "/admin/discount-codes", test_discount, auth_token=self.admin_token)
            if self.assert_response(response, 200, "Create Test Discount for Payment"):
                active_discount = response.json()
                self.discount_codes.append(active_discount)
            else:
                print_error("Could not create test discount code for payment integration")
                return
        
        test_package = self.packages[0]  # Use first package
        
        # Test 1: Initiate payment with valid discount code
        payment_params = {
            "package_type": test_package["package_type"],
            "discount_code": active_discount["code"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
        if self.assert_response(response, 200, "Payment with Valid Discount Code"):
            result = response.json()
            
            # Verify discount is applied
            required_fields = ["payment_id", "discount_amount", "final_amount", "discount_code"]
            for field in required_fields:
                if field in result:
                    print_success(f"Payment response contains {field}: {result[field]}")
                else:
                    print_error(f"Payment response missing {field}")
            
            # Verify discount calculation
            discount_amount = result.get("discount_amount", 0)
            final_amount = result.get("final_amount", 0)
            
            if discount_amount > 0:
                print_success(f"Discount applied: R{discount_amount}")
                print_success(f"Final amount after discount: R{final_amount}")
            else:
                print_error("No discount amount found in payment response")
            
            # Verify payment URL still points to sandbox
            payment_url = result.get("payment_url", "")
            if "sandbox.payfast.co.za" in payment_url:
                print_success("Discounted payment still uses sandbox URL")
            else:
                print_error("Discounted payment should use sandbox URL")
            
            # Store payment ID for webhook testing
            if "payment_id" in result:
                self.payment_ids.append(result["payment_id"])
        
        # Test 2: Initiate payment with invalid discount code
        invalid_payment_params = {
            "package_type": test_package["package_type"],
            "discount_code": "INVALID_CODE"
        }
        
        response = self.make_request("POST", "/payments/initiate", data=invalid_payment_params, auth_token=self.recruiter_token, use_params=True)
        self.assert_response(response, 400, "Payment with Invalid Discount Code (Should Fail)")

    def test_discount_codes_public_validation(self):
        """Test public discount codes validation endpoint"""
        print_test_header("Discount Codes Public Validation")
        
        if not self.packages or not self.discount_codes:
            print_error("No packages or discount codes available for validation testing")
            return
        
        # Find an active discount code
        active_discount = None
        for code in self.discount_codes:
            if code.get("status") == "active":
                active_discount = code
                break
        
        if not active_discount:
            print_error("No active discount codes available for testing")
            return
        
        test_package = self.packages[0]
        
        # Test 1: Validate valid discount code
        validation_data = {
            "code": active_discount["code"],
            "package_type": test_package["package_type"],
            "package_price": test_package["price"]
        }
        
        response = self.make_request("POST", "/discount-codes/validate", validation_data)
        if self.assert_response(response, 200, "Validate Valid Discount Code"):
            result = response.json()
            
            # Verify validation response structure
            required_fields = ["valid", "discount_details", "original_price", "discount_amount", "final_price"]
            for field in required_fields:
                if field in result:
                    print_success(f"Validation response contains {field}")
                else:
                    print_error(f"Validation response missing {field}")
            
            if result.get("valid") == True:
                print_success("Discount code validation returned valid=True")
            else:
                print_error("Discount code validation should return valid=True")
            
            # Verify price calculations
            original_price = result.get("original_price", 0)
            discount_amount = result.get("discount_amount", 0)
            final_price = result.get("final_price", 0)
            
            if original_price > 0 and discount_amount >= 0:
                expected_final = original_price - discount_amount
                if abs(final_price - expected_final) < 0.01:
                    print_success(f"Validation calculation correct: R{original_price} - R{discount_amount} = R{final_price}")
                else:
                    print_error(f"Validation calculation incorrect")
        
        # Test 2: Validate invalid discount code
        invalid_validation = {
            "code": "INVALID_CODE_123",
            "package_type": test_package["package_type"],
            "package_price": test_package["price"]
        }
        
        response = self.make_request("POST", "/discount-codes/validate", invalid_validation)
        if self.assert_response(response, 200, "Validate Invalid Discount Code"):
            result = response.json()
            if result.get("valid") == False:
                print_success("Invalid discount code validation returned valid=False")
                if "error" in result:
                    print_success(f"Error message provided: {result['error']}")
            else:
                print_error("Invalid discount code validation should return valid=False")
        
        # Test 3: Test validation without authentication (should work - public endpoint)
        public_validation = {
            "code": active_discount["code"],
            "package_type": test_package["package_type"],
            "package_price": test_package["price"]
        }
        
        response = self.make_request("POST", "/discount-codes/validate", public_validation)
        if self.assert_response(response, 200, "Public Validation (No Auth)"):
            print_success("Discount validation works without authentication")

    def test_webhook_processing_with_discounts(self):
        """Test webhook processing with discount codes"""
        print_test_header("Webhook Processing with Discount Codes")
        
        if not self.payment_ids:
            print_warning("No payment IDs available for webhook testing - skipping webhook tests")
            return
        
        # Note: In a real test environment, we would simulate Payfast webhook calls
        # For now, we'll test the webhook endpoint structure and basic validation
        
        payment_id = self.payment_ids[0]
        
        # Test 1: Simulate webhook data (this would normally come from Payfast)
        webhook_data = {
            "m_payment_id": payment_id,
            "pf_payment_id": "1234567",
            "payment_status": "COMPLETE",
            "item_name": "Test Package",
            "amount_gross": "2800.00",
            "amount_fee": "50.00",
            "amount_net": "2750.00",
            "signature": "test_signature"
        }
        
        # Note: We can't actually test the webhook without proper Payfast signatures
        # But we can verify the endpoint exists and handles requests
        response = self.make_request("POST", "/webhooks/payfast", webhook_data)
        
        # The webhook should return 200 even if signature validation fails
        # (it logs the error but doesn't return error status to Payfast)
        if response:
            if response.status_code in [200, 400]:
                print_info(f"Webhook endpoint responded with status {response.status_code}")
                print_info("Webhook endpoint is accessible and processing requests")
            else:
                print_error(f"Unexpected webhook response status: {response.status_code}")
        else:
            print_error("Webhook endpoint not accessible")

    def run_all_tests(self):
        """Run all discount codes and Payfast sandbox tests"""
        print_test_header("Starting Discount Codes and Payfast Sandbox Test Suite")
        
        if not self.setup_test_environment():
            print_error("Failed to setup test environment")
            return
        
        # Run all test methods
        test_methods = [
            self.test_payfast_sandbox_configuration,
            self.test_admin_discount_codes_management,
            self.test_admin_discount_codes_crud,
            self.test_discount_codes_payment_integration,
            self.test_discount_codes_public_validation,
            self.test_webhook_processing_with_discounts
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
        print_test_header("Test Results Summary")
        
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
            print_success("All tests passed!")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print_info(f"Success Rate: {success_rate:.1f}%")


class CVUploadTestSuite:
    def __init__(self):
        self.job_seeker_token = None
        self.job_seeker_user_id = None
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.uploaded_files = []
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
        """Setup test environment with job seeker and recruiter login"""
        print_test_header("Setting up CV Upload Test Environment")
        
        # Login as job seeker (demo account)
        job_seeker_login_data = {
            "email": "demo_jobseeker@example.com",
            "password": "password"
        }
        
        response = self.make_request("POST", "/auth/login", job_seeker_login_data)
        if not self.assert_response(response, 200, "Job Seeker Login"):
            return False
            
        login_result = response.json()
        self.job_seeker_token = login_result["access_token"]
        self.job_seeker_user_id = login_result["user"]["id"]
        
        print_info(f"Logged in as job seeker: {login_result['user']['email']}")
        print_info(f"Job Seeker ID: {self.job_seeker_user_id}")
        print_info(f"User Role: {login_result['user']['role']}")
        
        # Login as recruiter for comparison tests
        recruiter_login_data = {
            "email": "demo.recruiter@test.com",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", recruiter_login_data)
        if not self.assert_response(response, 200, "Recruiter Login"):
            return False
            
        recruiter_result = response.json()
        self.recruiter_token = recruiter_result["access_token"]
        self.recruiter_user_id = recruiter_result["user"]["id"]
        
        print_info(f"Logged in as recruiter: {recruiter_result['user']['email']}")
        print_info(f"Recruiter ID: {self.recruiter_user_id}")
        print_info(f"Recruiter Role: {recruiter_result['user']['role']}")
        
        return True

    def create_test_file(self, filename, content, content_type):
        """Create a test file for upload"""
        import tempfile
        import os
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name, content_type

    def test_cv_upload_valid_files(self):
        """Test CV upload with valid file types and sizes"""
        print_test_header("CV Upload - Valid Files")
        
        # Test 1: Upload valid PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        temp_pdf, _ = self.create_test_file(".pdf", pdf_content, "application/pdf")
        
        with open(temp_pdf, 'rb') as f:
            files = {'file': ('test_resume.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 200, "Upload Valid PDF File"):
                result = response.json()
                
                # Verify response structure
                required_fields = ["message", "file_url", "filename"]
                for field in required_fields:
                    if field in result:
                        print_success(f"Response contains {field}: {result[field]}")
                    else:
                        print_error(f"Response missing {field}")
                
                # Verify file URL format
                file_url = result.get("file_url", "")
                if file_url.startswith("/uploads/cvs/") and file_url.endswith(".pdf"):
                    print_success(f"File URL format correct: {file_url}")
                    self.uploaded_files.append(file_url)
                else:
                    print_error(f"File URL format incorrect: {file_url}")
                
                # Verify filename preservation
                if result.get("filename") == "test_resume.pdf":
                    print_success("Original filename preserved")
                else:
                    print_error(f"Original filename not preserved: {result.get('filename')}")
        
        # Clean up temp file
        import os
        os.unlink(temp_pdf)
        
        # Test 2: Upload valid DOC file (simulated)
        doc_content = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"A" * 1000  # DOC file header + content
        temp_doc, _ = self.create_test_file(".doc", doc_content, "application/msword")
        
        with open(temp_doc, 'rb') as f:
            files = {'file': ('test_resume.doc', f, 'application/msword')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 200, "Upload Valid DOC File"):
                result = response.json()
                file_url = result.get("file_url", "")
                if file_url.endswith(".doc"):
                    print_success("DOC file uploaded successfully")
                    self.uploaded_files.append(file_url)
        
        os.unlink(temp_doc)
        
        # Test 3: Upload valid DOCX file (simulated)
        docx_content = b"PK\x03\x04" + b"A" * 1000  # DOCX file header + content
        temp_docx, _ = self.create_test_file(".docx", docx_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        with open(temp_docx, 'rb') as f:
            files = {'file': ('test_resume.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 200, "Upload Valid DOCX File"):
                result = response.json()
                file_url = result.get("file_url", "")
                if file_url.endswith(".docx"):
                    print_success("DOCX file uploaded successfully")
                    self.uploaded_files.append(file_url)
        
        os.unlink(temp_docx)

    def test_cv_upload_file_validation(self):
        """Test CV upload file type and size validation"""
        print_test_header("CV Upload - File Validation")
        
        # Test 1: Invalid file type (TXT)
        txt_content = b"This is a text file, not a CV"
        temp_txt, _ = self.create_test_file(".txt", txt_content, "text/plain")
        
        with open(temp_txt, 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 400, "Upload Invalid File Type (Should Fail)"):
                result = response.json()
                if "Only PDF, DOC, and DOCX files are allowed" in result.get("detail", ""):
                    print_success("Correct error message for invalid file type")
                else:
                    print_error(f"Unexpected error message: {result.get('detail')}")
        
        import os
        os.unlink(temp_txt)
        
        # Test 2: File too large (over 5MB)
        large_content = b"A" * (6 * 1024 * 1024)  # 6MB file
        temp_large, _ = self.create_test_file(".pdf", large_content, "application/pdf")
        
        with open(temp_large, 'rb') as f:
            files = {'file': ('large_resume.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 400, "Upload Large File (Should Fail)"):
                result = response.json()
                if "File size must be less than 5MB" in result.get("detail", ""):
                    print_success("Correct error message for large file")
                else:
                    print_error(f"Unexpected error message: {result.get('detail')}")
        
        os.unlink(temp_large)
        
        # Test 3: Invalid file type (JPG image)
        jpg_content = b"\xff\xd8\xff\xe0" + b"A" * 1000  # JPG header + content
        temp_jpg, _ = self.create_test_file(".jpg", jpg_content, "image/jpeg")
        
        with open(temp_jpg, 'rb') as f:
            files = {'file': ('profile_pic.jpg', f, 'image/jpeg')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            self.assert_response(response, 400, "Upload Image File (Should Fail)")
        
        os.unlink(temp_jpg)

    def test_cv_upload_authentication(self):
        """Test CV upload authentication requirements"""
        print_test_header("CV Upload - Authentication")
        
        # Test 1: Upload without authentication (should fail)
        pdf_content = b"%PDF-1.4\nTest PDF content"
        temp_pdf, _ = self.create_test_file(".pdf", pdf_content, "application/pdf")
        
        with open(temp_pdf, 'rb') as f:
            files = {'file': ('test_resume.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files)
            
            self.assert_response(response, 401, "Upload Without Auth (Should Fail)")
        
        import os
        os.unlink(temp_pdf)
        
        # Test 2: Upload with invalid token (should fail)
        pdf_content = b"%PDF-1.4\nTest PDF content"
        temp_pdf, _ = self.create_test_file(".pdf", pdf_content, "application/pdf")
        
        with open(temp_pdf, 'rb') as f:
            files = {'file': ('test_resume.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token="invalid_token")
            
            self.assert_response(response, 401, "Upload With Invalid Token (Should Fail)")
        
        os.unlink(temp_pdf)
        
        # Test 3: Upload as recruiter (should work - any authenticated user can upload)
        pdf_content = b"%PDF-1.4\nRecruiter PDF content"
        temp_pdf, _ = self.create_test_file(".pdf", pdf_content, "application/pdf")
        
        with open(temp_pdf, 'rb') as f:
            files = {'file': ('recruiter_resume.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.recruiter_token)
            
            if self.assert_response(response, 200, "Upload As Recruiter"):
                result = response.json()
                file_url = result.get("file_url", "")
                if file_url:
                    print_success("Recruiter can upload CV files")
                    self.uploaded_files.append(file_url)
        
        os.unlink(temp_pdf)

    def test_static_file_serving(self):
        """Test static file serving for uploaded CV files"""
        print_test_header("Static File Serving")
        
        if not self.uploaded_files:
            print_warning("No uploaded files available for static file serving test")
            return
        
        # Test 1: Access uploaded file via static URL
        for file_url in self.uploaded_files[:3]:  # Test first 3 uploaded files
            # Convert API file URL to full URL
            static_url = f"https://career-launchpad-16.preview.emergentagent.com{file_url}"
            
            response = requests.get(static_url)
            if response.status_code == 200:
                print_success(f"File accessible via static URL: {file_url}")
                
                # Verify content type
                content_type = response.headers.get('content-type', '')
                if any(ct in content_type.lower() for ct in ['pdf', 'msword', 'officedocument']):
                    print_success(f"Correct content type: {content_type}")
                else:
                    print_info(f"Content type: {content_type}")
                
                # Verify file size
                content_length = len(response.content)
                if content_length > 0:
                    print_success(f"File has content: {content_length} bytes")
                else:
                    print_error("File appears to be empty")
            else:
                print_error(f"File not accessible: {file_url} (Status: {response.status_code})")
        
        # Test 2: Try to access non-existent file (should fail)
        fake_url = "https://career-launchpad-16.preview.emergentagent.com/uploads/cvs/nonexistent_file.pdf"
        response = requests.get(fake_url)
        if response.status_code == 404:
            print_success("Non-existent file returns 404 as expected")
        else:
            print_error(f"Non-existent file should return 404, got {response.status_code}")

    def test_cv_upload_integration_with_job_application(self):
        """Test integration of CV upload with job application system"""
        print_test_header("CV Upload Integration with Job Applications")
        
        if not self.uploaded_files:
            print_warning("No uploaded files available for integration test")
            return
        
        # First, get available jobs for application
        response = self.make_request("GET", "/public/jobs")
        if not self.assert_response(response, 200, "Get Public Jobs"):
            return
        
        jobs = response.json()
        if not jobs:
            print_warning("No public jobs available for application test")
            return
        
        # Find a job that supports Easy Apply (no application_url)
        easy_apply_job = None
        for job in jobs:
            if not job.get("application_url"):
                easy_apply_job = job
                break
        
        if not easy_apply_job:
            print_warning("No Easy Apply jobs available for testing")
            return
        
        print_info(f"Testing with job: {easy_apply_job['title']}")
        
        # Test 1: Apply to job using uploaded CV
        file_url = self.uploaded_files[0]  # Use first uploaded file
        
        application_data = {
            "job_id": easy_apply_job["id"],
            "cover_letter": "This is a test cover letter for CV upload integration testing.",
            "resume_url": f"https://career-launchpad-16.preview.emergentagent.com{file_url}",
            "additional_info": "Testing CV upload integration with job applications."
        }
        
        response = self.make_request("POST", f"/jobs/{easy_apply_job['id']}/apply", application_data, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Apply to Job with Uploaded CV"):
            result = response.json()
            
            # Verify application contains CV URL
            if result.get("resume_url") == application_data["resume_url"]:
                print_success("Job application contains uploaded CV URL")
            else:
                print_error(f"CV URL mismatch in application: {result.get('resume_url')}")
            
            # Verify other application fields
            required_fields = ["id", "job_id", "applicant_id", "status", "applied_date"]
            for field in required_fields:
                if field in result:
                    print_success(f"Application contains {field}")
                else:
                    print_error(f"Application missing {field}")
        
        # Test 2: Verify recruiter can see application with CV URL
        # First login as recruiter and get applications
        response = self.make_request("GET", f"/jobs/{easy_apply_job['id']}/applications", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Recruiter View Applications"):
            applications = response.json()
            
            # Find our test application
            test_application = None
            for app in applications:
                if app.get("resume_url") == application_data["resume_url"]:
                    test_application = app
                    break
            
            if test_application:
                print_success("Recruiter can see application with uploaded CV URL")
                print_info(f"CV URL in recruiter view: {test_application['resume_url']}")
            else:
                print_error("Recruiter cannot see application with uploaded CV")

    def test_cv_upload_edge_cases(self):
        """Test edge cases and error scenarios"""
        print_test_header("CV Upload - Edge Cases")
        
        # Test 1: Upload file with no extension
        content = b"%PDF-1.4\nTest content"
        temp_file, _ = self.create_test_file("", content, "application/pdf")
        
        with open(temp_file, 'rb') as f:
            files = {'file': ('resume_no_extension', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 200, "Upload File Without Extension"):
                result = response.json()
                file_url = result.get("file_url", "")
                if ".pdf" in file_url:  # Should default to .pdf
                    print_success("File without extension defaults to .pdf")
                    self.uploaded_files.append(file_url)
        
        import os
        os.unlink(temp_file)
        
        # Test 2: Upload file with special characters in name
        content = b"%PDF-1.4\nSpecial chars test"
        temp_file, _ = self.create_test_file(".pdf", content, "application/pdf")
        
        with open(temp_file, 'rb') as f:
            files = {'file': ('résumé with spaces & symbols!.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            if self.assert_response(response, 200, "Upload File With Special Characters"):
                result = response.json()
                if result.get("filename") == "résumé with spaces & symbols!.pdf":
                    print_success("Original filename with special characters preserved")
                file_url = result.get("file_url", "")
                if file_url:
                    self.uploaded_files.append(file_url)
        
        os.unlink(temp_file)
        
        # Test 3: Upload empty file (should fail)
        empty_content = b""
        temp_empty, _ = self.create_test_file(".pdf", empty_content, "application/pdf")
        
        with open(temp_empty, 'rb') as f:
            files = {'file': ('empty.pdf', f, 'application/pdf')}
            response = self.make_request("POST", "/upload-cv", files=files, auth_token=self.job_seeker_token)
            
            # This might succeed or fail depending on implementation
            if response.status_code in [200, 400]:
                print_info(f"Empty file upload returned status {response.status_code}")
            else:
                print_error(f"Unexpected status for empty file: {response.status_code}")
        
        os.unlink(temp_empty)

    def run_all_tests(self):
        """Run all CV upload tests"""
        print_test_header("Starting CV Upload Test Suite")
        
        if not self.setup_test_environment():
            print_error("Failed to setup test environment")
            return
        
        # Run all test methods
        test_methods = [
            self.test_cv_upload_valid_files,
            self.test_cv_upload_file_validation,
            self.test_cv_upload_authentication,
            self.test_static_file_serving,
            self.test_cv_upload_integration_with_job_application,
            self.test_cv_upload_edge_cases
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
        print_test_header("CV Upload Test Results Summary")
        
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
            print_success("All CV upload tests passed!")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print_info(f"Success Rate: {success_rate:.1f}%")


if __name__ == "__main__":
    print_test_header("Job Rocket Backend Test Suite")
    print_info("Testing CV File Upload functionality and Easy Apply enhancements")
    
    # Run the CV upload test suite
    cv_test_suite = CVUploadTestSuite()
    cv_test_suite.run_all_tests()