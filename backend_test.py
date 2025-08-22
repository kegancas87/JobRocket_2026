#!/usr/bin/env python3
"""
Backend Test Suite for Job Rocket - Bulk Upload Expiry Date Testing
Tests the bulk upload issue - specifically check if jobs created via bulk upload have proper expiry dates
Focus: Verify expiry_date values for both regular and bulk uploaded jobs
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "https://job-expiry-fix.preview.emergentagent.com/api"
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

class BulkUploadExpiryTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.created_job_ids = []
        self.existing_jobs = []

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
        print_test_header("Setting up Bulk Upload Expiry Test Environment")
        
        # Login as demo recruiter (as specified in review request)
        recruiter_login_data = {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", recruiter_login_data)
        if not self.assert_response(response, 200, "Demo Recruiter Login"):
            print_error("Failed to login with demo recruiter account")
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

    def test_current_jobs_in_database(self):
        """Check current jobs in the database (both regular and bulk uploaded)"""
        print_test_header("Current Jobs in Database Analysis")
        
        # Test 1: Get public jobs (no authentication required)
        print_info("Testing GET /api/public/jobs to see which jobs are visible")
        response = self.make_request("GET", "/public/jobs")
        if self.assert_response(response, 200, "Get Public Jobs"):
            public_jobs = response.json()
            print_info(f"Found {len(public_jobs)} public jobs")
            
            # Analyze expiry dates in public jobs
            expired_count = 0
            valid_expiry_count = 0
            missing_expiry_count = 0
            
            for job in public_jobs:
                job_id = job.get('id', 'Unknown')
                title = job.get('title', 'Unknown')
                expiry_date = job.get('expiry_date')
                posted_date = job.get('posted_date')
                
                print_info(f"Public Job: {title} (ID: {job_id})")
                print_info(f"  Posted: {posted_date}")
                print_info(f"  Expires: {expiry_date}")
                
                if expiry_date:
                    valid_expiry_count += 1
                    # Check if job is expired
                    try:
                        expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                        if expiry_dt < datetime.now(expiry_dt.tzinfo):
                            expired_count += 1
                            print_warning(f"  ⚠️ Job is EXPIRED")
                        else:
                            print_success(f"  ✅ Job is ACTIVE")
                    except Exception as e:
                        print_error(f"  ❌ Error parsing expiry date: {e}")
                else:
                    missing_expiry_count += 1
                    print_error(f"  ❌ Missing expiry_date")
            
            print_info(f"Public Jobs Summary:")
            print_info(f"  Total: {len(public_jobs)}")
            print_info(f"  With valid expiry dates: {valid_expiry_count}")
            print_info(f"  Missing expiry dates: {missing_expiry_count}")
            print_info(f"  Expired jobs: {expired_count}")
        
        # Test 2: Get recruiter's jobs (requires authentication)
        print_info("Testing GET /api/jobs to see recruiter's jobs")
        response = self.make_request("GET", "/jobs", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Recruiter Jobs"):
            recruiter_jobs = response.json()
            self.existing_jobs = recruiter_jobs
            print_info(f"Found {len(recruiter_jobs)} recruiter jobs")
            
            # Analyze expiry dates in recruiter jobs
            bulk_uploaded_jobs = []
            regular_jobs = []
            
            for job in recruiter_jobs:
                job_id = job.get('id', 'Unknown')
                title = job.get('title', 'Unknown')
                expiry_date = job.get('expiry_date')
                posted_date = job.get('posted_date')
                
                print_info(f"Recruiter Job: {title} (ID: {job_id})")
                print_info(f"  Posted: {posted_date}")
                print_info(f"  Expires: {expiry_date}")
                
                # Try to identify if this was bulk uploaded (heuristic based on title patterns or timing)
                if self.is_likely_bulk_uploaded(job):
                    bulk_uploaded_jobs.append(job)
                    print_info(f"  📦 Likely BULK UPLOADED")
                else:
                    regular_jobs.append(job)
                    print_info(f"  📝 Likely REGULAR job")
                
                # Verify expiry date
                if expiry_date:
                    try:
                        expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                        posted_dt = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                        
                        # Calculate days between posted and expiry
                        days_diff = (expiry_dt - posted_dt).days
                        print_info(f"  📅 Expiry is {days_diff} days after posting")
                        
                        # Check if it's around 35 days (expected default)
                        if 34 <= days_diff <= 36:
                            print_success(f"  ✅ Expiry date looks correct (~35 days)")
                        else:
                            print_warning(f"  ⚠️ Expiry date may be incorrect (expected ~35 days, got {days_diff})")
                            
                    except Exception as e:
                        print_error(f"  ❌ Error parsing dates: {e}")
                else:
                    print_error(f"  ❌ Missing expiry_date - THIS IS THE ISSUE!")
            
            print_info(f"Recruiter Jobs Analysis:")
            print_info(f"  Total jobs: {len(recruiter_jobs)}")
            print_info(f"  Likely bulk uploaded: {len(bulk_uploaded_jobs)}")
            print_info(f"  Likely regular jobs: {len(regular_jobs)}")
            
            # Focus on bulk uploaded jobs expiry dates
            if bulk_uploaded_jobs:
                print_info("Analyzing bulk uploaded jobs expiry dates:")
                for job in bulk_uploaded_jobs:
                    expiry_date = job.get('expiry_date')
                    if not expiry_date:
                        print_error(f"  ❌ Bulk job '{job.get('title')}' missing expiry_date - CONFIRMED ISSUE")
                    else:
                        print_success(f"  ✅ Bulk job '{job.get('title')}' has expiry_date")

    def is_likely_bulk_uploaded(self, job):
        """Heuristic to determine if a job was likely bulk uploaded"""
        title = job.get('title', '').lower()
        
        # Common patterns in bulk uploaded jobs
        bulk_patterns = [
            'software engineer',
            'data analyst', 
            'marketing manager',
            'sales representative',
            'customer service',
            'project manager'
        ]
        
        # Check if title matches common bulk patterns
        for pattern in bulk_patterns:
            if pattern in title:
                return True
        
        # Check if posted in batches (same minute)
        posted_date = job.get('posted_date')
        if posted_date:
            # If multiple jobs were posted at exactly the same time, likely bulk
            for other_job in self.existing_jobs:
                if other_job.get('id') != job.get('id') and other_job.get('posted_date') == posted_date:
                    return True
        
        return False

    def test_single_job_creation_expiry(self):
        """Test creating a single job to verify expiry date is set correctly"""
        print_test_header("Single Job Creation Expiry Date Test")
        
        # Create a test job
        job_data = {
            "title": "Test Single Job - Expiry Check",
            "company_id": self.recruiter_user_id,
            "description": "This is a test job to verify expiry date functionality",
            "location": "Cape Town, South Africa",
            "salary": "R25,000 - R35,000",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology",
            "experience": "2-3 years",
            "qualifications": "Bachelor's degree in Computer Science"
        }
        
        print_info("Creating single test job...")
        response = self.make_request("POST", "/jobs", data=job_data, auth_token=self.recruiter_token)
        
        if self.assert_response(response, 200, "Create Single Job"):
            job_result = response.json()
            job_id = job_result.get('id')
            self.created_job_ids.append(job_id)
            
            print_success(f"Created job with ID: {job_id}")
            
            # Verify expiry date is present and correct
            expiry_date = job_result.get('expiry_date')
            posted_date = job_result.get('posted_date')
            
            if expiry_date:
                print_success("✅ Single job has expiry_date")
                print_info(f"Posted: {posted_date}")
                print_info(f"Expires: {expiry_date}")
                
                try:
                    expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                    posted_dt = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                    
                    days_diff = (expiry_dt - posted_dt).days
                    print_info(f"Expiry is {days_diff} days after posting")
                    
                    if 34 <= days_diff <= 36:
                        print_success("✅ Single job expiry date is correct (~35 days)")
                    else:
                        print_error(f"❌ Single job expiry date incorrect (expected ~35 days, got {days_diff})")
                        
                except Exception as e:
                    print_error(f"❌ Error parsing single job dates: {e}")
            else:
                print_error("❌ Single job missing expiry_date - CRITICAL ISSUE")
        else:
            print_error("Failed to create single test job")

    def test_bulk_upload_expiry(self):
        """Test bulk upload with 1-2 jobs to verify expiry dates"""
        print_test_header("Bulk Upload Expiry Date Test")
        
        # Create a CSV content for bulk upload
        csv_content = """title,description,location,salary,job_type,work_type,industry,experience,qualifications
"Bulk Test Job 1 - Expiry Check","Test job 1 from bulk upload to verify expiry dates","Johannesburg, South Africa","R30,000 - R40,000","Permanent","Hybrid","Technology","3-5 years","Bachelor's degree"
"Bulk Test Job 2 - Expiry Check","Test job 2 from bulk upload to verify expiry dates","Durban, South Africa","R28,000 - R38,000","Contract","Remote","Marketing","2-4 years","Diploma or degree"""
        
        print_info("Creating CSV file for bulk upload test...")
        
        # Create file-like object for upload
        files = {
            'file': ('test_bulk_jobs.csv', csv_content, 'text/csv')
        }
        
        # Add company_id as form data
        form_data = {
            'company_id': self.recruiter_user_id
        }
        
        print_info("Uploading bulk jobs CSV...")
        response = self.make_request("POST", "/jobs/bulk", files=files, data=form_data, auth_token=self.recruiter_token)
        
        if self.assert_response(response, 200, "Bulk Upload Jobs"):
            bulk_result = response.json()
            print_success("✅ Bulk upload completed")
            print_info(f"Bulk upload result: {bulk_result}")
            
            # Check if jobs were created
            jobs_created = bulk_result.get('jobs_created', 0)
            if jobs_created > 0:
                print_success(f"✅ {jobs_created} jobs created via bulk upload")
                
                # Wait a moment for jobs to be fully processed
                time.sleep(2)
                
                # Get updated job list to find the newly created bulk jobs
                response = self.make_request("GET", "/jobs", auth_token=self.recruiter_token)
                if response and response.status_code == 200:
                    updated_jobs = response.json()
                    
                    # Find the bulk uploaded jobs (look for our test titles)
                    bulk_test_jobs = []
                    for job in updated_jobs:
                        if "Bulk Test Job" in job.get('title', '') and "Expiry Check" in job.get('title', ''):
                            bulk_test_jobs.append(job)
                            self.created_job_ids.append(job.get('id'))
                    
                    print_info(f"Found {len(bulk_test_jobs)} bulk uploaded test jobs")
                    
                    # Analyze expiry dates for bulk uploaded jobs
                    for i, job in enumerate(bulk_test_jobs, 1):
                        job_id = job.get('id')
                        title = job.get('title')
                        expiry_date = job.get('expiry_date')
                        posted_date = job.get('posted_date')
                        
                        print_info(f"Bulk Job {i}: {title}")
                        print_info(f"  ID: {job_id}")
                        print_info(f"  Posted: {posted_date}")
                        print_info(f"  Expires: {expiry_date}")
                        
                        if expiry_date:
                            print_success(f"  ✅ Bulk job {i} has expiry_date")
                            
                            try:
                                expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                                posted_dt = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                                
                                days_diff = (expiry_dt - posted_dt).days
                                print_info(f"  📅 Expiry is {days_diff} days after posting")
                                
                                if 34 <= days_diff <= 36:
                                    print_success(f"  ✅ Bulk job {i} expiry date is correct (~35 days)")
                                else:
                                    print_error(f"  ❌ Bulk job {i} expiry date incorrect (expected ~35 days, got {days_diff})")
                                    
                            except Exception as e:
                                print_error(f"  ❌ Error parsing bulk job {i} dates: {e}")
                        else:
                            print_error(f"  ❌ Bulk job {i} missing expiry_date - THIS IS THE BULK UPLOAD ISSUE!")
                    
                    # Summary of bulk upload expiry date test
                    jobs_with_expiry = sum(1 for job in bulk_test_jobs if job.get('expiry_date'))
                    jobs_without_expiry = len(bulk_test_jobs) - jobs_with_expiry
                    
                    print_info(f"Bulk Upload Expiry Summary:")
                    print_info(f"  Jobs created: {len(bulk_test_jobs)}")
                    print_info(f"  Jobs with expiry_date: {jobs_with_expiry}")
                    print_info(f"  Jobs missing expiry_date: {jobs_without_expiry}")
                    
                    if jobs_without_expiry > 0:
                        print_error(f"❌ CONFIRMED: {jobs_without_expiry} bulk uploaded jobs are missing expiry_date")
                        print_error("❌ This confirms the bulk upload expiry date issue reported")
                    else:
                        print_success("✅ All bulk uploaded jobs have proper expiry dates")
                        print_success("✅ Bulk upload expiry date issue appears to be FIXED")
                        
                else:
                    print_error("Failed to retrieve updated job list after bulk upload")
            else:
                print_error("No jobs were created during bulk upload")
                if 'errors' in bulk_result:
                    print_error(f"Bulk upload errors: {bulk_result['errors']}")
        else:
            print_error("Bulk upload failed")
            if response:
                print_error(f"Response: {response.text}")

    def test_expiry_date_calculation_logic(self):
        """Test the expiry date calculation logic specifically"""
        print_test_header("Expiry Date Calculation Logic Test")
        
        print_info("Testing if the issue is with expiry_date calculation or assignment...")
        
        # Create multiple jobs with different methods to compare
        test_jobs = []
        
        # Test 1: Single job creation
        single_job_data = {
            "title": "Expiry Logic Test - Single Job",
            "company_id": self.recruiter_user_id,
            "description": "Testing expiry date calculation for single job creation",
            "location": "Cape Town, South Africa",
            "salary": "R30,000",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        print_info("Creating single job to test expiry calculation...")
        response = self.make_request("POST", "/jobs", data=single_job_data, auth_token=self.recruiter_token)
        if response and response.status_code == 200:
            job = response.json()
            test_jobs.append(("Single", job))
            self.created_job_ids.append(job.get('id'))
            print_success("✅ Single job created for expiry testing")
        
        # Test 2: Bulk upload
        csv_content = """title,description,location,salary,job_type,work_type,industry
"Expiry Logic Test - Bulk Job","Testing expiry date calculation for bulk upload","Pretoria, South Africa","R32,000","Contract","Onsite","Finance"
"""
        
        files = {'file': ('expiry_test.csv', csv_content, 'text/csv')}
        form_data = {'company_id': self.recruiter_user_id}
        
        print_info("Creating bulk job to test expiry calculation...")
        response = self.make_request("POST", "/jobs/bulk", files=files, data=form_data, auth_token=self.recruiter_token)
        if response and response.status_code == 200:
            time.sleep(2)  # Wait for processing
            
            # Get the bulk job
            response = self.make_request("GET", "/jobs", auth_token=self.recruiter_token)
            if response and response.status_code == 200:
                jobs = response.json()
                for job in jobs:
                    if "Expiry Logic Test - Bulk Job" in job.get('title', ''):
                        test_jobs.append(("Bulk", job))
                        self.created_job_ids.append(job.get('id'))
                        print_success("✅ Bulk job created for expiry testing")
                        break
        
        # Analyze the expiry date calculation for both methods
        print_info("Analyzing expiry date calculation logic...")
        
        current_time = datetime.utcnow()
        expected_expiry = current_time + timedelta(days=35)
        
        for job_type, job in test_jobs:
            title = job.get('title')
            expiry_date = job.get('expiry_date')
            posted_date = job.get('posted_date')
            
            print_info(f"{job_type} Job Analysis: {title}")
            
            if expiry_date and posted_date:
                try:
                    expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                    posted_dt = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                    
                    # Calculate actual days difference
                    actual_days = (expiry_dt - posted_dt).days
                    
                    # Calculate expected expiry based on posted date
                    expected_expiry_for_job = posted_dt + timedelta(days=35)
                    
                    print_info(f"  Posted: {posted_dt}")
                    print_info(f"  Expires: {expiry_dt}")
                    print_info(f"  Expected Expiry: {expected_expiry_for_job}")
                    print_info(f"  Actual Days: {actual_days}")
                    
                    if 34 <= actual_days <= 36:
                        print_success(f"  ✅ {job_type} job expiry calculation is CORRECT")
                    else:
                        print_error(f"  ❌ {job_type} job expiry calculation is WRONG (expected ~35 days, got {actual_days})")
                        
                    # Check if expiry is in the future
                    if expiry_dt > datetime.now(expiry_dt.tzinfo):
                        print_success(f"  ✅ {job_type} job expiry is in the future (not expired)")
                    else:
                        print_warning(f"  ⚠️ {job_type} job expiry is in the past (expired)")
                        
                except Exception as e:
                    print_error(f"  ❌ Error analyzing {job_type} job dates: {e}")
            else:
                if not expiry_date:
                    print_error(f"  ❌ {job_type} job missing expiry_date - CALCULATION NOT APPLIED")
                if not posted_date:
                    print_error(f"  ❌ {job_type} job missing posted_date - CANNOT CALCULATE")

    def cleanup_test_jobs(self):
        """Clean up test jobs created during testing"""
        print_test_header("Cleaning Up Test Jobs")
        
        if not self.created_job_ids:
            print_info("No test jobs to clean up")
            return
        
        print_info(f"Cleaning up {len(self.created_job_ids)} test jobs...")
        
        for job_id in self.created_job_ids:
            # Note: There might not be a delete endpoint, so we'll just log the IDs
            print_info(f"Test job created: {job_id}")
        
        print_info("Test jobs left in database for manual review if needed")

    def run_all_tests(self):
        """Run all bulk upload expiry date tests"""
        print_test_header("Starting Bulk Upload Expiry Date Test Suite")
        print_info("Focus: Testing bulk upload expiry date issue")
        print_info("Checking if jobs created via bulk upload have proper expiry dates")
        
        if not self.setup_test_environment():
            print_error("Failed to setup test environment")
            return
        
        # Run all test methods in logical order
        test_methods = [
            self.test_current_jobs_in_database,
            self.test_single_job_creation_expiry,
            self.test_bulk_upload_expiry,
            self.test_expiry_date_calculation_logic
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print_error(f"Test {test_method.__name__} failed with exception: {str(e)}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"{test_method.__name__}: {str(e)}")
        
        # Cleanup
        self.cleanup_test_jobs()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print final test results summary"""
        print_test_header("Bulk Upload Expiry Date Test Results")
        
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
            print_success("🎉 All bulk upload expiry date tests passed!")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print_info(f"Success Rate: {success_rate:.1f}%")
        
        # Summary of key findings
        print_test_header("Key Findings Summary")
        print_info("Based on the test results:")
        print_info("1. Check if bulk uploaded jobs have expiry_date field")
        print_info("2. Compare expiry dates between single and bulk uploaded jobs")
        print_info("3. Verify expiry date calculation logic (should be ~35 days from posting)")
        print_info("4. Identify if the issue is in bulk upload processing or expiry calculation")


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
        
        payment_params = {
            "package_type": test_package["package_type"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
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
            payment_params = {
                "package_type": package["package_type"]
            }
            
            response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
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
        
        payment_params = {
            "package_type": test_package["package_type"]
        }
        
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
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
        payment_params = {
            "package_type": test_package["package_type"]
        }
        
        # Test 1: No authentication (should fail)
        response = self.make_request("POST", "/payments/initiate", data=payment_params, use_params=True)
        if self.assert_response(response, 401, "Payment Without Authentication (Should Fail)"):
            print_success("✅ Payment initiation correctly requires authentication")
        
        # Test 2: Invalid token (should fail)
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token="invalid_token", use_params=True)
        if self.assert_response(response, 401, "Payment With Invalid Token (Should Fail)"):
            print_success("✅ Payment initiation correctly validates authentication token")
        
        # Test 3: Valid recruiter token (should succeed)
        response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
        if self.assert_response(response, 200, "Payment With Valid Recruiter Token"):
            print_success("✅ Payment initiation works with valid recruiter authentication")

    def test_invalid_package_types(self):
        """Test payment initiation with invalid package types"""
        print_test_header("Invalid Package Types Testing")
        
        invalid_package_types = [
            "invalid_package",
            "nonexistent_type",
            "",
            "cv_search_5",  # Non-existent CV search package
            "unlimited_cv"  # Similar but wrong name
        ]
        
        for invalid_type in invalid_package_types:
            print_info(f"Testing invalid package type: {invalid_type}")
            
            payment_params = {
                "package_type": invalid_type
            }
            
            response = self.make_request("POST", "/payments/initiate", data=payment_params, auth_token=self.recruiter_token, use_params=True)
            
            # Should return 400 (Bad Request) or 422 (Unprocessable Entity)
            if response and response.status_code in [400, 422]:
                print_success(f"✅ Invalid package type '{invalid_type}' correctly rejected with status {response.status_code}")
            else:
                expected_status = response.status_code if response else "No response"
                print_error(f"❌ Invalid package type '{invalid_type}' should be rejected, got status: {expected_status}")
        
        # Test None separately as it causes JSON serialization issues
        print_info("Testing None package type")
        try:
            response = self.make_request("POST", "/payments/initiate", data={}, auth_token=self.recruiter_token, use_params=True)
            if response and response.status_code in [400, 422]:
                print_success(f"✅ Missing package type correctly rejected with status {response.status_code}")
            else:
                expected_status = response.status_code if response else "No response"
                print_error(f"❌ Missing package type should be rejected, got status: {expected_status}")
        except Exception as e:
            print_info(f"Exception handling None package type (expected): {str(e)}")

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
    print_test_header("Job Rocket Bulk Upload Expiry Date Test Suite")
    print_info("Testing bulk upload expiry date issue specifically")
    print_info("Focus: Verify if jobs created via bulk upload have proper expiry dates")
    print_info("Using demo recruiter credentials: lisa.martinez@techcorp.demo/demo123")
    
    # Run the bulk upload expiry test suite
    bulk_test_suite = BulkUploadExpiryTestSuite()
    bulk_test_suite.run_all_tests()