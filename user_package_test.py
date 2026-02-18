#!/usr/bin/env python3
"""
Backend Test Suite for Job Rocket - User Package Management Testing
Tests the /api/my-packages endpoint specifically for lisa.martinez@techcorp.demo
Focus: Verify user packages are returned correctly and investigate any query issues
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://seeker-profile-v2.preview.emergentagent.com/api"
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

class UserPackageTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.recruiter_email = None
        self.packages = []
        self.user_packages = []
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
        """Setup test environment with lisa.martinez@techcorp.demo login"""
        print_test_header("Setting up User Package Test Environment")
        
        # Login as lisa.martinez@techcorp.demo (as specified in review request)
        recruiter_login_data = {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", recruiter_login_data)
        if not self.assert_response(response, 200, "Lisa Martinez Login"):
            print_error("Failed to login with lisa.martinez@techcorp.demo account")
            print_info("This user may not exist or credentials may be incorrect")
            return False
            
        login_result = response.json()
        self.recruiter_token = login_result["access_token"]
        self.recruiter_user_id = login_result["user"]["id"]
        self.recruiter_email = login_result["user"]["email"]
        
        print_info(f"Logged in as recruiter: {self.recruiter_email}")
        print_info(f"Recruiter ID: {self.recruiter_user_id}")
        print_info(f"User Role: {login_result['user']['role']}")
        
        # Verify user is recruiter
        if login_result['user']['role'] != 'recruiter':
            print_error(f"User role should be 'recruiter', got '{login_result['user']['role']}'")
            return False
        
        return True

    def test_my_packages_endpoint(self):
        """Test the /api/my-packages endpoint specifically"""
        print_test_header("Testing /api/my-packages Endpoint")
        
        # Call GET /api/my-packages
        response = self.make_request("GET", "/my-packages", auth_token=self.recruiter_token)
        
        if not self.assert_response(response, 200, "GET /api/my-packages"):
            print_error("Failed to get user packages")
            return
        
        user_packages = response.json()
        self.user_packages = user_packages
        
        print_info(f"Found {len(user_packages)} user packages for {self.recruiter_email}")
        
        if len(user_packages) == 0:
            print_warning("No packages found for this user")
            print_info("This could indicate:")
            print_info("1. User has not purchased any packages")
            print_info("2. Database query is not finding user_packages records")
            print_info("3. User packages have expired or been deactivated")
            return
        
        # Analyze each package
        unlimited_package_found = False
        for i, user_package in enumerate(user_packages):
            print_info(f"\nPackage {i+1}:")
            print_info(f"  Package Type: {user_package.get('package_type', 'Unknown')}")
            print_info(f"  Package Name: {user_package.get('package', {}).get('name', 'Unknown')}")
            print_info(f"  Is Active: {user_package.get('is_active', 'Unknown')}")
            print_info(f"  Job Listings Remaining: {user_package.get('job_listings_remaining', 'Unknown')}")
            print_info(f"  CV Searches Remaining: {user_package.get('cv_searches_remaining', 'Unknown')}")
            print_info(f"  Purchased Date: {user_package.get('purchased_date', 'Unknown')}")
            print_info(f"  Expiry Date: {user_package.get('expiry_date', 'No expiry')}")
            
            # Check if this is the unlimited package
            if user_package.get('package_type') == 'unlimited_listings':
                unlimited_package_found = True
                print_success("✅ Found unlimited listings package!")
                
                # Verify unlimited package structure
                if user_package.get('job_listings_remaining') is None:
                    print_success("✅ Unlimited package has unlimited job listings (None value)")
                else:
                    print_warning(f"⚠️ Unlimited package shows {user_package.get('job_listings_remaining')} listings remaining")
                
                # Check if package is active
                if user_package.get('is_active'):
                    print_success("✅ Unlimited package is active")
                else:
                    print_error("❌ Unlimited package is not active")
                
                # Check expiry status
                expiry_date = user_package.get('expiry_date')
                if expiry_date:
                    try:
                        expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                        if expiry_dt > datetime.now():
                            print_success("✅ Unlimited package has not expired")
                        else:
                            print_error("❌ Unlimited package has expired")
                    except:
                        print_warning("⚠️ Could not parse expiry date")
                else:
                    print_info("ℹ️ Unlimited package has no expiry date")
        
        if not unlimited_package_found:
            print_error("❌ Unlimited package NOT found for this user")
            print_info("Available package types:")
            for user_package in user_packages:
                print_info(f"  - {user_package.get('package_type', 'Unknown')}")

    def test_package_data_structure(self):
        """Verify the package data structure is correct"""
        print_test_header("Testing Package Data Structure")
        
        if not self.user_packages:
            print_error("No user packages to test structure")
            return
        
        # Expected fields in user package response
        expected_fields = [
            "id",
            "user_id", 
            "package_id",
            "package_type",
            "purchased_date",
            "is_active",
            "package"  # Nested package details
        ]
        
        for i, user_package in enumerate(self.user_packages):
            print_info(f"Checking structure of package {i+1}")
            
            for field in expected_fields:
                if field in user_package:
                    print_success(f"✅ Has {field}: {user_package[field]}")
                else:
                    print_error(f"❌ Missing {field}")
            
            # Check nested package structure
            if "package" in user_package and user_package["package"]:
                package_details = user_package["package"]
                package_expected_fields = ["id", "name", "description", "price", "package_type"]
                
                print_info("  Checking nested package details:")
                for field in package_expected_fields:
                    if field in package_details:
                        print_success(f"  ✅ Package has {field}: {package_details[field]}")
                    else:
                        print_error(f"  ❌ Package missing {field}")
            else:
                print_error("❌ Missing nested package details")

    def investigate_database_query_issues(self):
        """Investigate potential database query issues"""
        print_test_header("Investigating Database Query Issues")
        
        print_info(f"User ID being queried: {self.recruiter_user_id}")
        print_info(f"User Email: {self.recruiter_email}")
        
        # Test if user exists in system
        response = self.make_request("GET", "/auth/me", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "User Profile Check"):
            user_profile = response.json()
            print_success(f"✅ User exists in system: {user_profile.get('email')}")
            print_info(f"User ID from profile: {user_profile.get('id')}")
            
            # Check if user ID matches
            if user_profile.get('id') == self.recruiter_user_id:
                print_success("✅ User ID consistency check passed")
            else:
                print_error(f"❌ User ID mismatch: token={self.recruiter_user_id}, profile={user_profile.get('id')}")
        
        # Check if packages exist in system
        response = self.make_request("GET", "/packages", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "System Packages Check"):
            packages = response.json()
            print_info(f"Found {len(packages)} packages in system")
            
            unlimited_package = None
            for package in packages:
                if package.get('package_type') == 'unlimited_listings':
                    unlimited_package = package
                    break
            
            if unlimited_package:
                print_success("✅ Unlimited listings package exists in system")
                print_info(f"Package ID: {unlimited_package.get('id')}")
                print_info(f"Package Name: {unlimited_package.get('name')}")
                print_info(f"Package Price: R{unlimited_package.get('price')}")
            else:
                print_error("❌ Unlimited listings package NOT found in system")

    def test_create_test_package_for_user(self):
        """Attempt to create a test package for the user via payment simulation"""
        print_test_header("Testing Package Creation for User")
        
        # First, get available packages
        response = self.make_request("GET", "/packages", auth_token=self.recruiter_token)
        if not self.assert_response(response, 200, "Get Available Packages"):
            return
        
        packages = response.json()
        unlimited_package = None
        
        for package in packages:
            if package.get('package_type') == 'unlimited_listings':
                unlimited_package = package
                break
        
        if not unlimited_package:
            print_error("Cannot test package creation - unlimited package not found")
            return
        
        print_info(f"Found unlimited package: {unlimited_package.get('name')}")
        
        # Try to initiate payment for unlimited package
        payment_params = {
            "package_type": "unlimited_listings"
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
        if self.assert_response(response, 200, "Payment Initiation for Unlimited Package"):
            payment_result = response.json()
            payment_id = payment_result.get("payment_id")
            print_success(f"✅ Payment initiated successfully: {payment_id}")
            print_info(f"Payment URL: {payment_result.get('payment_url')}")
            
            # Note: In a real scenario, we would complete the payment via webhook
            # For testing purposes, we'll just verify the payment was created
            print_info("Payment created but not completed (webhook simulation would be needed)")
            print_info("This confirms the payment system is working for this user")
        else:
            print_error("Failed to initiate payment - this could indicate package system issues")

    def run_all_tests(self):
        """Run all user package management tests"""
        print_test_header("Starting User Package Management Test Suite")
        print_info("Focus: Testing /api/my-packages endpoint for lisa.martinez@techcorp.demo")
        print_info("Investigating why unlimited package may not be returned")
        
        if not self.setup_test_environment():
            print_error("Failed to setup test environment")
            return
        
        # Run all test methods in logical order
        test_methods = [
            self.test_my_packages_endpoint,
            self.test_package_data_structure,
            self.investigate_database_query_issues,
            self.test_create_test_package_for_user
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
        print_test_header("User Package Management Test Results")
        
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
            print_success("🎉 All user package management tests passed!")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print_info(f"Success Rate: {success_rate:.1f}%")
        
        # Summary of key findings
        print_test_header("Key Findings Summary")
        
        if len(self.user_packages) > 0:
            print_success(f"✅ Found {len(self.user_packages)} user packages")
            
            unlimited_found = any(pkg.get('package_type') == 'unlimited_listings' for pkg in self.user_packages)
            if unlimited_found:
                print_success("✅ Unlimited package found for user")
            else:
                print_error("❌ Unlimited package NOT found for user")
        else:
            print_error("❌ No user packages found - this is the main issue")
            print_info("Possible causes:")
            print_info("1. User has not purchased any packages")
            print_info("2. Database query is filtering out packages incorrectly")
            print_info("3. User packages have been deactivated or expired")
            print_info("4. There's a mismatch in user_id between authentication and package records")


if __name__ == "__main__":
    print_test_header("Job Rocket User Package Management Test Suite")
    print_info("Testing /api/my-packages endpoint for lisa.martinez@techcorp.demo")
    print_info("Focus: Verify unlimited package is returned and investigate query issues")
    
    # Run the user package test suite
    test_suite = UserPackageTestSuite()
    test_suite.run_all_tests()