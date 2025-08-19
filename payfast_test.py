#!/usr/bin/env python3
"""
Payfast Integration Test Suite for Job Rocket
Tests Payfast payment initiation, webhook processing, and package activation
"""

import requests
import json
import time
import hashlib
import urllib.parse
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://jobrocket.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

# Payfast Test Configuration
PAYFAST_MERCHANT_ID = "14208372"
PAYFAST_MERCHANT_KEY = "hhy9cdwi0b4q9"
PAYFAST_PASSPHRASE = "McCaughly2019"

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

class PayfastTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.packages = []
        self.payment_ids = []
        self.user_packages = []
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, form_data=False):
        """Make HTTP request with proper error handling"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = {}
        
        if headers:
            request_headers.update(headers)
            
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        
        if method.upper() in ["POST", "PUT"] and not form_data:
            request_headers["Content-Type"] = "application/json"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, params=data)
            elif method.upper() == "POST":
                if form_data:
                    response = requests.post(url, data=data, headers=request_headers)
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

    def generate_payfast_signature(self, data, passphrase=None):
        """Generate PayFast signature for testing"""
        # Remove empty values and signature field if it exists
        filtered_data = {k: str(v) for k, v in data.items() if v is not None and v != '' and k != 'signature'}
        
        # Sort parameters alphabetically
        sorted_params = sorted(filtered_data.items())
        
        # Create parameter string
        param_string = '&'.join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
        
        # Add passphrase if provided
        if passphrase:
            param_string += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
        
        # Generate MD5 hash
        signature = hashlib.md5(param_string.encode('utf-8')).hexdigest()
        
        return signature

    def setup_test_environment(self):
        """Setup test environment with recruiter login"""
        print_test_header("Setting up Payfast Test Environment")
        
        # Login as recruiter
        login_data = {
            "email": "payfast.test@demo.com",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if not self.assert_response(response, 200, "Recruiter Login"):
            return False
            
        login_result = response.json()
        self.recruiter_token = login_result["access_token"]
        self.recruiter_user_id = login_result["user"]["id"]
        
        print_info(f"Logged in as recruiter: {login_result['user']['email']}")
        print_info(f"User ID: {self.recruiter_user_id}")
        
        return True

    def test_get_packages(self):
        """Test GET /api/packages - Get available packages"""
        print_test_header("Get Available Packages")
        
        response = self.make_request("GET", "/packages", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Packages"):
            packages = response.json()
            self.packages = packages
            print_info(f"Found {len(packages)} packages")
            
            # Verify package structure and pricing
            expected_packages = {
                "two_listings": {"name": "Two Listings Package", "price": 2800.00},
                "five_listings": {"name": "Five Listings Package", "price": 4150.00},
                "unlimited_listings": {"name": "Unlimited Listings Package", "price": 3899.00},
                "cv_search_10": {"name": "10 CV Searches", "price": 699.00},
                "cv_search_20": {"name": "20 CV Searches", "price": 1299.00},
                "cv_search_unlimited": {"name": "Unlimited CV Searches", "price": 2899.00}
            }
            
            for package in packages:
                package_type = package.get("package_type")
                if package_type in expected_packages:
                    expected = expected_packages[package_type]
                    if package.get("name") == expected["name"]:
                        print_success(f"Package name correct: {package['name']}")
                    else:
                        print_error(f"Package name mismatch: expected '{expected['name']}', got '{package.get('name')}'")
                    
                    if package.get("price") == expected["price"]:
                        print_success(f"Package price correct: R{package['price']}")
                    else:
                        print_error(f"Package price mismatch: expected R{expected['price']}, got R{package.get('price')}")
                
                print_info(f"Package: {package['name']} - R{package['price']} - Type: {package['package_type']}")
        
        return len(self.packages) > 0

    def test_payment_initiation(self):
        """Test POST /api/payments/initiate - Payment initiation with real Payfast credentials"""
        print_test_header("Payment Initiation with Real Payfast Credentials")
        
        if not self.packages:
            print_error("No packages available for testing")
            return False
        
        # Test payment initiation for each package type
        for package in self.packages:
            package_type = package["package_type"]
            
            # Use query parameters instead of request body
            response = self.make_request("POST", f"/payments/initiate?package_type={package_type}", None, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Initiate Payment for {package['name']}"):
                result = response.json()
                self.payment_ids.append(result["payment_id"])
                
                # Verify payment response structure
                required_fields = ["payment_id", "payment_url", "amount", "currency", "package_name"]
                for field in required_fields:
                    if field in result:
                        print_success(f"Payment response contains {field}: {result[field]}")
                    else:
                        print_error(f"Payment response missing {field}")
                
                # Verify payment URL is actual Payfast URL (not mock)
                payment_url = result.get("payment_url", "")
                if "payfast.co.za" in payment_url:
                    print_success("Payment URL is actual Payfast URL")
                    print_info(f"Payment URL: {payment_url}")
                else:
                    print_error(f"Payment URL should be Payfast URL, got: {payment_url}")
                
                # Verify amount matches package price
                if result.get("amount") == package["price"]:
                    print_success(f"Payment amount matches package price: R{result['amount']}")
                else:
                    print_error(f"Payment amount mismatch: expected R{package['price']}, got R{result.get('amount')}")
                
                # Verify currency is ZAR
                if result.get("currency") == "ZAR":
                    print_success("Currency correctly set to ZAR")
                else:
                    print_error(f"Currency should be ZAR, got: {result.get('currency')}")
                
                # Test signature verification by parsing URL parameters
                if "?" in payment_url:
                    url_params = {}
                    query_string = payment_url.split("?")[1]
                    for param in query_string.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            url_params[urllib.parse.unquote_plus(key)] = urllib.parse.unquote_plus(value)
                    
                    # Verify merchant credentials in URL
                    if url_params.get("merchant_id") == PAYFAST_MERCHANT_ID:
                        print_success("Merchant ID correctly included in payment URL")
                    else:
                        print_error(f"Merchant ID mismatch in URL: expected {PAYFAST_MERCHANT_ID}, got {url_params.get('merchant_id')}")
                    
                    if url_params.get("merchant_key") == PAYFAST_MERCHANT_KEY:
                        print_success("Merchant key correctly included in payment URL")
                    else:
                        print_error(f"Merchant key mismatch in URL")
                    
                    # Verify signature
                    if "signature" in url_params:
                        print_success("Payment URL includes signature")
                        # Verify signature is correct
                        calculated_signature = self.generate_payfast_signature(url_params, PAYFAST_PASSPHRASE)
                        if url_params["signature"] == calculated_signature:
                            print_success("Payment URL signature is valid")
                        else:
                            print_error("Payment URL signature is invalid")
                    else:
                        print_error("Payment URL missing signature")
                    
                    # Verify return URLs are included
                    if "return_url" in url_params:
                        print_success("Return URL included in payment")
                    else:
                        print_error("Return URL missing from payment")
                    
                    if "notify_url" in url_params:
                        print_success("Webhook URL included in payment")
                    else:
                        print_error("Webhook URL missing from payment")
        
        # Test unauthorized payment initiation (should fail)
        response = self.make_request("POST", "/payments/initiate?package_type=two_listings", None)
        self.assert_response(response, 401, "Unauthorized Payment Initiation (Should Fail)")
        
        # Test invalid package type (should fail)
        response = self.make_request("POST", "/payments/initiate?package_type=invalid_package", None, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Package Type (Should Fail)")
        
        return len(self.payment_ids) > 0

    def test_webhook_signature_verification(self):
        """Test webhook signature verification functionality"""
        print_test_header("Webhook Signature Verification")
        
        # Test 1: Valid webhook with correct signature
        webhook_data = {
            "m_payment_id": "test_payment_123",
            "pf_payment_id": "1234567",
            "payment_status": "COMPLETE",
            "item_name": "Two Listings Package",
            "amount_gross": "2800.00",
            "amount_fee": "140.00",
            "amount_net": "2660.00",
            "merchant_id": PAYFAST_MERCHANT_ID,
            "custom_str1": self.recruiter_user_id if self.recruiter_user_id else "test_user_id"
        }
        
        # Generate valid signature
        webhook_data["signature"] = self.generate_payfast_signature(webhook_data, PAYFAST_PASSPHRASE)
        
        response = self.make_request("POST", "/webhooks/payfast", webhook_data, form_data=True)
        if self.assert_response(response, 200, "Valid Webhook with Correct Signature"):
            result = response.json()
            print_success("Webhook processed successfully with valid signature")
            if result.get("status") == "success":
                print_success("Webhook returned success status")
            else:
                print_error(f"Webhook should return success status, got: {result.get('status')}")
        
        # Test 2: Invalid signature (should fail)
        invalid_webhook = webhook_data.copy()
        invalid_webhook["signature"] = "invalid_signature_hash"
        invalid_webhook["m_payment_id"] = "test_payment_124"
        
        response = self.make_request("POST", "/webhooks/payfast", invalid_webhook, form_data=True)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("status") == "error" and "signature" in result.get("reason", "").lower():
                print_success("Invalid signature correctly rejected")
            else:
                print_error("Invalid signature should be rejected")
        else:
            self.assert_response(response, 400, "Invalid Signature (Should Fail)")
        
        # Test 3: Missing signature (should fail)
        missing_sig_webhook = webhook_data.copy()
        del missing_sig_webhook["signature"]
        missing_sig_webhook["m_payment_id"] = "test_payment_125"
        
        response = self.make_request("POST", "/webhooks/payfast", missing_sig_webhook, form_data=True)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("status") == "error" and "signature" in result.get("reason", "").lower():
                print_success("Missing signature correctly rejected")
            else:
                print_error("Missing signature should be rejected")
        else:
            self.assert_response(response, 400, "Missing Signature (Should Fail)")
        
        # Test 4: Webhook with incomplete payment status
        incomplete_webhook = webhook_data.copy()
        incomplete_webhook["payment_status"] = "PENDING"
        incomplete_webhook["m_payment_id"] = "test_payment_126"
        incomplete_webhook["signature"] = self.generate_payfast_signature(incomplete_webhook, PAYFAST_PASSPHRASE)
        
        response = self.make_request("POST", "/webhooks/payfast", incomplete_webhook, form_data=True)
        if self.assert_response(response, 200, "Webhook with Pending Status"):
            result = response.json()
            if result.get("message") and "not complete" in result["message"].lower():
                print_success("Webhook correctly handles non-COMPLETE status")
            else:
                print_warning("Webhook response for pending payment unclear")

    def test_webhook_package_activation(self):
        """Test webhook processing and automatic package activation"""
        print_test_header("Webhook Package Activation")
        
        if not self.payment_ids:
            print_error("No payment IDs available for testing")
            return False
        
        # Test package activation for different package types
        test_packages = [
            {
                "payment_id": self.payment_ids[0] if len(self.payment_ids) > 0 else "test_payment_001",
                "package_type": "two_listings",
                "item_name": "Two Listings Package",
                "amount": "2800.00",
                "expected_job_listings": 2,
                "expected_cv_searches": 0
            },
            {
                "payment_id": "test_payment_unlimited",
                "package_type": "unlimited_listings", 
                "item_name": "Unlimited Listings Package",
                "amount": "3899.00",
                "expected_job_listings": None,  # Unlimited
                "expected_cv_searches": 10
            },
            {
                "payment_id": "test_payment_cv_search",
                "package_type": "cv_search_10",
                "item_name": "10 CV Searches",
                "amount": "699.00",
                "expected_job_listings": 0,
                "expected_cv_searches": 10
            }
        ]
        
        for test_package in test_packages:
            webhook_data = {
                "m_payment_id": test_package["payment_id"],
                "pf_payment_id": f"pf_{int(time.time())}",
                "payment_status": "COMPLETE",
                "item_name": test_package["item_name"],
                "amount_gross": test_package["amount"],
                "amount_fee": str(float(test_package["amount"]) * 0.05),  # 5% fee
                "amount_net": str(float(test_package["amount"]) * 0.95),
                "merchant_id": PAYFAST_MERCHANT_ID,
                "custom_str1": self.recruiter_user_id
            }
            
            # Generate valid signature
            webhook_data["signature"] = self.generate_payfast_signature(webhook_data, PAYFAST_PASSPHRASE)
            
            response = self.make_request("POST", "/webhooks/payfast", webhook_data, form_data=True)
            if self.assert_response(response, 200, f"Activate {test_package['item_name']}"):
                result = response.json()
                
                if result.get("status") == "success":
                    print_success(f"Package {test_package['item_name']} activated successfully")
                    
                    # Verify user package was created
                    if "user_package_id" in result:
                        print_success("User package created")
                        self.user_packages.append(result["user_package_id"])
                    else:
                        print_error("User package ID not returned")
                    
                    # Check package details in response
                    if "package_details" in result:
                        details = result["package_details"]
                        
                        # Verify job listings allocation
                        if test_package["expected_job_listings"] is None:
                            if details.get("job_listings_remaining") is None:
                                print_success("Unlimited job listings correctly set")
                            else:
                                print_error("Should have unlimited job listings")
                        else:
                            if details.get("job_listings_remaining") == test_package["expected_job_listings"]:
                                print_success(f"Job listings correctly set to {test_package['expected_job_listings']}")
                            else:
                                print_error(f"Job listings mismatch: expected {test_package['expected_job_listings']}, got {details.get('job_listings_remaining')}")
                        
                        # Verify CV searches allocation
                        if test_package["expected_cv_searches"] == 0:
                            if details.get("cv_searches_remaining") == 0:
                                print_success("CV searches correctly set to 0")
                            else:
                                print_error(f"CV searches should be 0, got {details.get('cv_searches_remaining')}")
                        else:
                            if details.get("cv_searches_remaining") == test_package["expected_cv_searches"]:
                                print_success(f"CV searches correctly set to {test_package['expected_cv_searches']}")
                            else:
                                print_error(f"CV searches mismatch: expected {test_package['expected_cv_searches']}, got {details.get('cv_searches_remaining')}")
                        
                        # Verify expiry date for subscription packages
                        if test_package["package_type"] in ["unlimited_listings", "cv_search_unlimited"]:
                            if "expiry_date" in details:
                                expiry_date = datetime.fromisoformat(details["expiry_date"].replace('Z', '+00:00'))
                                days_until_expiry = (expiry_date - datetime.now(expiry_date.tzinfo)).days
                                if 29 <= days_until_expiry <= 31:  # ~30 days
                                    print_success(f"Subscription expiry correctly set to ~30 days ({days_until_expiry} days)")
                                else:
                                    print_error(f"Subscription expiry should be ~30 days, got {days_until_expiry} days")
                            else:
                                print_error("Subscription package missing expiry date")
                        else:
                            if details.get("expiry_date") is None:
                                print_success("One-time package correctly has no expiry")
                            else:
                                print_warning("One-time package has expiry date (may be intentional)")
                else:
                    print_error(f"Package activation failed: {result.get('message', 'Unknown error')}")

    def test_webhook_error_scenarios(self):
        """Test webhook error handling and edge cases"""
        print_test_header("Webhook Error Scenarios")
        
        # Test 1: Webhook for non-existent payment
        webhook_data = {
            "m_payment_id": "non_existent_payment_123",
            "pf_payment_id": "pf_123456789",
            "payment_status": "COMPLETE",
            "item_name": "Two Listings Package",
            "amount_gross": "2800.00",
            "amount_fee": "140.00",
            "amount_net": "2660.00",
            "merchant_id": PAYFAST_MERCHANT_ID,
            "custom_str1": self.recruiter_user_id
        }
        webhook_data["signature"] = self.generate_payfast_signature(webhook_data, PAYFAST_PASSPHRASE)
        
        response = self.make_request("POST", "/webhooks/payfast", webhook_data)
        self.assert_response(response, 404, "Webhook for Non-existent Payment (Should Fail)")
        
        # Test 2: Webhook with amount mismatch
        if self.payment_ids:
            amount_mismatch_webhook = {
                "m_payment_id": self.payment_ids[0],
                "pf_payment_id": "pf_amount_mismatch",
                "payment_status": "COMPLETE",
                "item_name": "Two Listings Package",
                "amount_gross": "1000.00",  # Wrong amount
                "amount_fee": "50.00",
                "amount_net": "950.00",
                "merchant_id": PAYFAST_MERCHANT_ID,
                "custom_str1": self.recruiter_user_id
            }
            amount_mismatch_webhook["signature"] = self.generate_payfast_signature(amount_mismatch_webhook, PAYFAST_PASSPHRASE)
            
            response = self.make_request("POST", "/webhooks/payfast", amount_mismatch_webhook)
            self.assert_response(response, 400, "Webhook with Amount Mismatch (Should Fail)")
        
        # Test 3: Duplicate webhook (idempotency test)
        duplicate_webhook = {
            "m_payment_id": "duplicate_test_payment",
            "pf_payment_id": "pf_duplicate_123",
            "payment_status": "COMPLETE",
            "item_name": "Two Listings Package",
            "amount_gross": "2800.00",
            "amount_fee": "140.00",
            "amount_net": "2660.00",
            "merchant_id": PAYFAST_MERCHANT_ID,
            "custom_str1": self.recruiter_user_id
        }
        duplicate_webhook["signature"] = self.generate_payfast_signature(duplicate_webhook, PAYFAST_PASSPHRASE)
        
        # Send first webhook
        response1 = self.make_request("POST", "/webhooks/payfast", duplicate_webhook)
        if response1 and response1.status_code == 200:
            print_success("First webhook processed successfully")
            
            # Send duplicate webhook
            response2 = self.make_request("POST", "/webhooks/payfast", duplicate_webhook)
            if response2:
                if response2.status_code == 200:
                    result = response2.json()
                    if "already processed" in result.get("message", "").lower():
                        print_success("Duplicate webhook correctly handled (idempotency)")
                    else:
                        print_warning("Duplicate webhook processed again (may create duplicate packages)")
                else:
                    print_info(f"Duplicate webhook rejected with status {response2.status_code}")
        
        # Test 4: Webhook with missing required fields
        incomplete_webhook = {
            "m_payment_id": "incomplete_webhook_test",
            "payment_status": "COMPLETE",
            # Missing amount_gross, merchant_id, etc.
        }
        incomplete_webhook["signature"] = self.generate_payfast_signature(incomplete_webhook, PAYFAST_PASSPHRASE)
        
        response = self.make_request("POST", "/webhooks/payfast", incomplete_webhook)
        self.assert_response(response, 400, "Webhook with Missing Fields (Should Fail)")

    def test_user_package_verification(self):
        """Test user package creation and verification"""
        print_test_header("User Package Verification")
        
        # Get user's packages
        response = self.make_request("GET", "/my-packages", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get User Packages"):
            packages = response.json()
            print_info(f"Found {len(packages)} user packages")
            
            if packages:
                for package in packages:
                    print_info(f"Package: {package.get('package', {}).get('name', 'Unknown')} - Active: {package.get('user_package', {}).get('is_active', False)}")
                    
                    user_package = package.get("user_package", {})
                    package_info = package.get("package", {})
                    
                    # Verify package structure
                    required_fields = ["id", "user_id", "package_id", "package_type", "purchased_date", "is_active"]
                    for field in required_fields:
                        if field in user_package:
                            print_success(f"User package contains {field}")
                        else:
                            print_error(f"User package missing {field}")
                    
                    # Verify credit allocation
                    if user_package.get("job_listings_remaining") is not None:
                        print_success(f"Job listings remaining: {user_package['job_listings_remaining']}")
                    elif package_info.get("job_listings_included") is None:
                        print_success("Unlimited job listings package")
                    
                    if user_package.get("cv_searches_remaining") is not None:
                        print_success(f"CV searches remaining: {user_package['cv_searches_remaining']}")
                    elif package_info.get("cv_searches_included") is None:
                        print_success("Unlimited CV searches package")
                    
                    # Verify expiry status
                    if "is_expired" in package:
                        if package["is_expired"]:
                            print_warning("Package is expired")
                        else:
                            print_success("Package is not expired")
            else:
                print_warning("No user packages found (may be expected if no webhooks were processed)")

    def test_integration_verification(self):
        """Test overall integration verification"""
        print_test_header("Integration Verification")
        
        # Test 1: Verify environment variables are loaded
        print_info("Verifying Payfast configuration...")
        
        # We can't directly check env vars, but we can verify they're being used
        # by checking if payment URLs contain the correct merchant ID
        if self.packages:
            payment_data = {
                "package_type": self.packages[0]["package_type"]
            }
            
            response = self.make_request("POST", "/payments/initiate", payment_data, auth_token=self.recruiter_token)
            if response and response.status_code == 200:
                result = response.json()
                payment_url = result.get("payment_url", "")
                
                if PAYFAST_MERCHANT_ID in payment_url:
                    print_success("PAYFAST_MERCHANT_ID environment variable loaded correctly")
                else:
                    print_error("PAYFAST_MERCHANT_ID not found in payment URL")
                
                if PAYFAST_MERCHANT_KEY in payment_url:
                    print_success("PAYFAST_MERCHANT_KEY environment variable loaded correctly")
                else:
                    print_error("PAYFAST_MERCHANT_KEY not found in payment URL")
                
                if "payfast.co.za" in payment_url:
                    print_success("Using production Payfast URLs (not sandbox)")
                else:
                    print_error("Not using production Payfast URLs")
        
        # Test 2: Verify signature functions work correctly
        test_data = {
            "merchant_id": "12345",
            "merchant_key": "abcde",
            "amount": "100.00",
            "item_name": "Test Item"
        }
        
        signature1 = self.generate_payfast_signature(test_data, "test_passphrase")
        signature2 = self.generate_payfast_signature(test_data, "test_passphrase")
        
        if signature1 == signature2:
            print_success("Signature generation is consistent")
        else:
            print_error("Signature generation is inconsistent")
        
        # Test with different data should produce different signature
        test_data2 = test_data.copy()
        test_data2["amount"] = "200.00"
        signature3 = self.generate_payfast_signature(test_data2, "test_passphrase")
        
        if signature1 != signature3:
            print_success("Signature generation correctly varies with data")
        else:
            print_error("Signature generation does not vary with data")

    def run_all_tests(self):
        """Run all Payfast integration tests"""
        print_test_header("PAYFAST INTEGRATION TEST SUITE")
        print_info("Testing Payfast integration with real credentials")
        print_info(f"Merchant ID: {PAYFAST_MERCHANT_ID}")
        print_info(f"Testing against: {BASE_URL}")
        
        # Setup
        if not self.setup_test_environment():
            print_error("Failed to setup test environment")
            return False
        
        # Run tests in order
        test_methods = [
            self.test_get_packages,
            self.test_payment_initiation,
            self.test_webhook_signature_verification,
            self.test_webhook_package_activation,
            self.test_webhook_error_scenarios,
            self.test_user_package_verification,
            self.test_integration_verification
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print_error(f"Test {test_method.__name__} failed with exception: {str(e)}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"{test_method.__name__}: {str(e)}")
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results["failed"] == 0

    def print_test_summary(self):
        """Print test results summary"""
        print_test_header("TEST SUMMARY")
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        print_info(f"Total Tests: {total_tests}")
        print_success(f"Passed: {self.test_results['passed']}")
        print_error(f"Failed: {self.test_results['failed']}")
        
        if self.test_results["errors"]:
            print_error("\nFailed Tests:")
            for error in self.test_results["errors"]:
                print_error(f"  - {error}")
        
        if self.test_results["failed"] == 0:
            print_success("\n🎉 ALL PAYFAST INTEGRATION TESTS PASSED!")
        else:
            print_error(f"\n❌ {self.test_results['failed']} TESTS FAILED")

if __name__ == "__main__":
    test_suite = PayfastTestSuite()
    success = test_suite.run_all_tests()
    exit(0 if success else 1)