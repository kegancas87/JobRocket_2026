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
BASE_URL = "https://2f81706c-76db-49e4-a24b-38ca4e94e2e2.preview.emergentagent.com/api"
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

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, files=None):
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
                else:
                    # For POST requests, if data contains simple key-value pairs, use as params
                    # Otherwise use as JSON body
                    if data and all(isinstance(v, (str, int, float, bool)) for v in data.values()):
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
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token)
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
            
            response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token)
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
        
        # Find an active discount code
        active_discount = None
        for code in self.discount_codes:
            if code.get("status") == "active":
                active_discount = code
                break
        
        if not active_discount:
            print_error("No active discount codes available for testing")
            return
        
        test_package = self.packages[0]  # Use first package
        
        # Test 1: Initiate payment with valid discount code
        payment_params = {
            "package_type": test_package["package_type"],
            "discount_code": active_discount["code"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Payment with Valid Discount Code"):
            result = response.json()
            
            # Verify discount is applied
            required_fields = ["payment_id", "amount", "discount_amount", "final_amount", "discount_code"]
            for field in required_fields:
                if field in result:
                    print_success(f"Payment response contains {field}: {result[field]}")
                else:
                    print_error(f"Payment response missing {field}")
            
            # Verify discount calculation
            original_amount = result.get("amount", 0)
            discount_amount = result.get("discount_amount", 0)
            final_amount = result.get("final_amount", 0)
            
            if original_amount > 0 and discount_amount > 0:
                expected_final = original_amount - discount_amount
                if abs(final_amount - expected_final) < 0.01:  # Allow for floating point precision
                    print_success(f"Discount calculation correct: R{original_amount} - R{discount_amount} = R{final_amount}")
                else:
                    print_error(f"Discount calculation incorrect: expected R{expected_final}, got R{final_amount}")
            
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
        
        response = self.make_request("POST", "/payments/initiate", data=invalid_payment_params, auth_token=self.recruiter_token)
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


if __name__ == "__main__":
    # Run the discount codes test suite
    test_suite = DiscountCodesTestSuite()
    test_suite.run_all_tests()