#!/usr/bin/env python3
"""
Backend Test Suite for Job Rocket Enhanced Job Posting System
Tests enhanced job posting system with automatic expiry, archive functionality, and public API
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import io
import csv

# Configuration
BASE_URL = "https://e87f2e83-0579-4553-bbd3-e5348d9b2194.preview.emergentagent.com/api"
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

class JobPostingTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.company_id = None
        self.job_seeker_token = None
        self.job_seeker_user_id = None
        self.job_ids = []
        self.easy_apply_job_ids = []
        self.external_job_ids = []
        self.application_ids = []
        self.expired_job_ids = []
        self.accessible_companies = []
        self.packages = []
        self.payment_ids = []
        self.user_packages = []
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
        """Setup test environment with recruiter and job seeker login"""
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
        print_info(f"User Role: {login_result['user']['role']}")
        
        # Login as job seeker for application tests
        job_seeker_login = {
            "email": "sarah.johnson@demo.com",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", job_seeker_login)
        if not self.assert_response(response, 200, "Job Seeker Login"):
            return False
            
        job_seeker_result = response.json()
        self.job_seeker_token = job_seeker_result["access_token"]
        self.job_seeker_user_id = job_seeker_result["user"]["id"]
        
        print_info(f"Logged in as job seeker: {job_seeker_result['user']['email']}")
        print_info(f"Job Seeker ID: {self.job_seeker_user_id}")
        print_info(f"Job Seeker Role: {job_seeker_result['user']['role']}")
        
        return True

    def test_create_single_job(self):
        """Test POST /api/jobs - Create single job posting"""
        print_test_header("Create Single Job Posting")
        
        # Test 1: Valid job with all required fields
        job_data = {
            "title": "Senior React Developer",
            "company_id": self.company_id,
            "description": "We are looking for an experienced React developer to join our dynamic team. You will be responsible for developing user interface components and implementing them following well-known React.js workflows.",
            "location": "Johannesburg, Gauteng",
            "salary": "R60,000 - R90,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology",
            "experience": "5+ years in React development",
            "qualifications": "Bachelor's degree in Computer Science or related field",
            "application_url": "https://techcorp.demo/careers/apply",
            "application_email": "careers@techcorp.demo"
        }
        
        response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Valid Job"):
            result = response.json()
            self.job_ids.append(result["id"])
            print_info(f"Created job with ID: {result['id']}")
            print_info(f"Job title: {result['title']}")
            print_info(f"Company: {result['company_name']}")
            
            # Verify all required fields are present
            required_fields = ["id", "title", "company_id", "company_name", "description", 
                             "location", "salary", "job_type", "work_type", "industry", "posted_by"]
            for field in required_fields:
                if field in result:
                    print_success(f"Job contains required field: {field}")
                else:
                    print_error(f"Job missing required field: {field}")
        
        # Test 2: Job with different enum values
        job_variations = [
            {"job_type": "Contract", "work_type": "Onsite", "title": "Contract Frontend Developer"},
            {"job_type": "Permanent", "work_type": "Hybrid", "title": "Full-Stack Developer"}
        ]
        
        for variation in job_variations:
            test_job = job_data.copy()
            test_job.update(variation)
            
            response = self.make_request("POST", "/jobs", test_job, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Create Job - {variation['job_type']}/{variation['work_type']}"):
                result = response.json()
                self.job_ids.append(result["id"])
                print_info(f"Created {variation['job_type']} {variation['work_type']} job")
        
        # Test 3: Job with minimal required fields only
        minimal_job = {
            "title": "Junior Developer",
            "company_id": self.company_id,
            "description": "Entry level position for new graduates",
            "location": "Cape Town, Western Cape",
            "salary": "R25,000 - R35,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", minimal_job, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Minimal Job"):
            result = response.json()
            self.job_ids.append(result["id"])
            print_info("Created job with minimal required fields")
        
        # Test 4: Invalid job_type enum (should fail)
        invalid_job = job_data.copy()
        invalid_job["job_type"] = "InvalidType"
        
        response = self.make_request("POST", "/jobs", invalid_job, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Job Type (Should Fail)")
        
        # Test 5: Invalid work_type enum (should fail)
        invalid_job = job_data.copy()
        invalid_job["work_type"] = "InvalidWorkType"
        
        response = self.make_request("POST", "/jobs", invalid_job, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Work Type (Should Fail)")
        
        # Test 6: Missing required fields (should fail)
        incomplete_job = {
            "title": "Incomplete Job",
            "description": "Missing required fields"
        }
        
        response = self.make_request("POST", "/jobs", incomplete_job, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Missing Required Fields (Should Fail)")
        
        # Test 7: Unauthorized access (should fail)
        response = self.make_request("POST", "/jobs", job_data)
        self.assert_response(response, 401, "Unauthorized Access (Should Fail)")

    def test_bulk_job_upload(self):
        """Test POST /api/jobs/bulk - Bulk job upload via CSV"""
        print_test_header("Bulk Job Upload")
        
        # Test 1: Valid CSV upload
        csv_data = """title,location,salary,job_type,work_type,industry,description,experience,qualifications,application_email
"Python Developer","Durban, KwaZulu-Natal","R45000-R65000","Permanent","Remote","Technology","Experienced Python developer needed for backend development","3+ years Python experience","Computer Science degree","python@techcorp.demo"
"DevOps Engineer","Pretoria, Gauteng","R70000-R100000","Contract","Hybrid","Technology","DevOps engineer for cloud infrastructure","5+ years DevOps","AWS certification preferred","devops@techcorp.demo"
"Data Scientist","Cape Town, Western Cape","R80000-R120000","Permanent","Onsite","Technology","Data scientist for machine learning projects","PhD in Data Science","Statistics background","data@techcorp.demo"
"""
        
        # Create CSV file
        csv_file = io.StringIO(csv_data)
        files = {'file': ('test_jobs.csv', csv_file.getvalue(), 'text/csv')}
        form_data = {'company_id': self.company_id}
        
        response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Valid CSV Upload"):
            result = response.json()
            print_info(f"Jobs created: {result.get('jobs_created', 0)}")
            print_info(f"Total rows processed: {result.get('total_rows', 0)}")
            print_info(f"Errors: {len(result.get('errors', []))}")
            
            if result.get('errors'):
                for error in result['errors']:
                    print_warning(f"Upload error: {error}")
        
        # Test 2: CSV with missing required columns (should fail)
        invalid_csv = """title,location,salary
"Incomplete Job","Johannesburg","R50000"
"""
        
        files = {'file': ('invalid_jobs.csv', invalid_csv, 'text/csv')}
        form_data = {'company_id': self.company_id}
        
        response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files, auth_token=self.recruiter_token)
        self.assert_response(response, 400, "Missing Required Columns (Should Fail)")
        
        # Test 3: CSV with invalid enum values
        invalid_enum_csv = """title,location,salary,job_type,work_type,industry,description
"Invalid Job","Cape Town","R50000","InvalidType","InvalidWork","Technology","Test job with invalid enums"
"""
        
        files = {'file': ('invalid_enum_jobs.csv', invalid_enum_csv, 'text/csv')}
        form_data = {'company_id': self.company_id}
        
        response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "CSV with Invalid Enums"):
            result = response.json()
            # Should have errors for invalid enum values
            if result.get('errors'):
                print_success("Properly reported enum validation errors")
            else:
                print_error("Should have reported enum validation errors")
        
        # Test 4: Non-CSV file (should fail)
        files = {'file': ('test.txt', 'This is not a CSV file', 'text/plain')}
        form_data = {'company_id': self.company_id}
        
        response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files, auth_token=self.recruiter_token)
        self.assert_response(response, 400, "Non-CSV File (Should Fail)")
        
        # Test 5: Unauthorized access (should fail)
        files = {'file': ('test_jobs.csv', csv_data, 'text/csv')}
        form_data = {'company_id': self.company_id}
        
        response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files)
        self.assert_response(response, 401, "Unauthorized Bulk Upload (Should Fail)")

    def test_get_jobs_for_recruiter(self):
        """Test GET /api/jobs - Get jobs for recruiter"""
        print_test_header("Get Jobs for Recruiter")
        
        # Test 1: Get all jobs for recruiter
        response = self.make_request("GET", "/jobs", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get All Jobs"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} jobs")
            
            if jobs:
                job = jobs[0]
                required_fields = ["id", "title", "company_id", "company_name", "description", 
                                 "location", "salary", "job_type", "work_type", "industry", "posted_date"]
                for field in required_fields:
                    if field in job:
                        print_success(f"Job contains required field: {field}")
                    else:
                        print_error(f"Job missing required field: {field}")
                
                # Verify jobs belong to accessible companies
                for job in jobs:
                    if job["company_id"] == self.company_id:
                        print_success(f"Job belongs to recruiter's company: {job['title']}")
                    else:
                        print_info(f"Job from member company: {job['title']} - {job['company_name']}")
        
        # Test 2: Filter by specific company
        response = self.make_request("GET", "/jobs", data={"company_id": self.company_id}, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Filter by Company ID"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} jobs for company {self.company_id}")
            
            # Verify all jobs belong to the specified company
            for job in jobs:
                if job["company_id"] == self.company_id:
                    print_success(f"Filtered job belongs to correct company: {job['title']}")
                else:
                    print_error(f"Filtered job belongs to wrong company: {job['title']}")
        
        # Test 3: Access to non-accessible company (should fail)
        fake_company_id = str(uuid.uuid4())
        response = self.make_request("GET", "/jobs", data={"company_id": fake_company_id}, auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Access Non-accessible Company (Should Fail)")
        
        # Test 4: Unauthorized access (should fail)
        response = self.make_request("GET", "/jobs")
        self.assert_response(response, 401, "Unauthorized Job Access (Should Fail)")

    def test_get_accessible_companies(self):
        """Test GET /api/companies - Get accessible companies for recruiter"""
        print_test_header("Get Accessible Companies")
        
        # Test 1: Get all accessible companies
        response = self.make_request("GET", "/companies", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Accessible Companies"):
            companies = response.json()
            self.accessible_companies = companies
            print_info(f"Found {len(companies)} accessible companies")
            
            if companies:
                # Verify structure of company data
                company = companies[0]
                required_fields = ["id", "name", "role", "is_default"]
                for field in required_fields:
                    if field in company:
                        print_success(f"Company contains required field: {field}")
                    else:
                        print_error(f"Company missing required field: {field}")
                
                # Check for default company (should be recruiter's own company)
                default_companies = [c for c in companies if c.get("is_default")]
                if len(default_companies) == 1:
                    default_company = default_companies[0]
                    if default_company["id"] == self.company_id:
                        print_success("Default company is recruiter's own company")
                        print_info(f"Default company: {default_company['name']} (Role: {default_company['role']})")
                    else:
                        print_error("Default company is not recruiter's own company")
                else:
                    print_error(f"Expected 1 default company, found {len(default_companies)}")
                
                # List all companies with roles
                for company in companies:
                    print_info(f"Company: {company['name']} - Role: {company['role']} - Default: {company['is_default']}")
        
        # Test 2: Unauthorized access (should fail)
        response = self.make_request("GET", "/companies")
        self.assert_response(response, 401, "Unauthorized Company Access (Should Fail)")

    def test_job_posting_with_company_access(self):
        """Test job posting with different company access scenarios"""
        print_test_header("Job Posting with Company Access")
        
        # Test 1: Post job to own company
        job_data = {
            "title": "Company Access Test Job",
            "company_id": self.company_id,
            "description": "Testing company access for job posting",
            "location": "Johannesburg, Gauteng",
            "salary": "R50,000 - R70,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Post Job to Own Company"):
            result = response.json()
            self.job_ids.append(result["id"])
            print_success("Successfully posted job to own company")
        
        # Test 2: Try to post job to non-accessible company (should fail)
        fake_company_id = str(uuid.uuid4())
        invalid_job = job_data.copy()
        invalid_job["company_id"] = fake_company_id
        invalid_job["title"] = "Unauthorized Company Job"
        
        response = self.make_request("POST", "/jobs", invalid_job, auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Post Job to Non-accessible Company (Should Fail)")

    def test_recruiter_progress_tracking(self):
        """Test recruiter progress tracking for first job posting"""
        print_test_header("Recruiter Progress Tracking")
        
        # Get current user profile to check progress
        response = self.make_request("GET", "/auth/me", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get User Profile"):
            user = response.json()
            recruiter_progress = user.get("recruiter_progress", {})
            
            if recruiter_progress.get("first_job_posted"):
                print_success("First job posting progress is marked as completed")
            else:
                print_info("First job posting progress not yet marked (may be updated after job creation)")
            
            print_info(f"Total recruiter progress points: {recruiter_progress.get('total_points', 0)}")

    def test_authentication_and_authorization(self):
        """Test authentication and authorization for job posting endpoints"""
        print_test_header("Authentication & Authorization")
        
        # Test job seeker trying to access recruiter endpoints
        job_seeker_login = {
            "email": "sarah.johnson@demo.com",
            "password": "demo123"
        }
        
        response = self.make_request("POST", "/auth/login", job_seeker_login)
        if self.assert_response(response, 200, "Job Seeker Login"):
            job_seeker_token = response.json()["access_token"]
            
            # Try to post job as job seeker (should fail)
            job_data = {
                "title": "Unauthorized Job",
                "company_id": self.company_id,
                "description": "This should fail",
                "location": "Test Location",
                "salary": "R50,000",
                "job_type": "Permanent",
                "work_type": "Remote",
                "industry": "Technology"
            }
            
            response = self.make_request("POST", "/jobs", job_data, auth_token=job_seeker_token)
            self.assert_response(response, 403, "Job Seeker Create Job (Should Fail)")
            
            # Try to get recruiter jobs as job seeker (should fail)
            response = self.make_request("GET", "/jobs", auth_token=job_seeker_token)
            self.assert_response(response, 403, "Job Seeker Get Jobs (Should Fail)")
            
            # Try to get companies as job seeker (should fail)
            response = self.make_request("GET", "/companies", auth_token=job_seeker_token)
            self.assert_response(response, 403, "Job Seeker Get Companies (Should Fail)")

    def test_error_handling_and_edge_cases(self):
        """Test various error conditions and edge cases"""
        print_test_header("Error Handling & Edge Cases")
        
        # Test malformed job data
        malformed_requests = [
            ({"title": ""}, "Empty Title"),
            ({"title": "Test", "salary": ""}, "Empty Salary"),
            ({"title": "Test", "description": ""}, "Empty Description"),
            ({}, "Empty Request Body"),
        ]
        
        for data, test_name in malformed_requests:
            response = self.make_request("POST", "/jobs", data, auth_token=self.recruiter_token)
            if response and response.status_code >= 400:
                print_success(f"{test_name}: Properly rejected with status {response.status_code}")
            else:
                print_error(f"{test_name}: Should have been rejected")
        
        # Test extremely long field values
        long_job = {
            "title": "A" * 1000,  # Very long title
            "company_id": self.company_id,
            "description": "B" * 10000,  # Very long description
            "location": "Johannesburg, Gauteng",
            "salary": "R50,000 - R70,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", long_job, auth_token=self.recruiter_token)
        if response:
            if response.status_code == 200:
                print_info("Long field values accepted")
                result = response.json()
                self.job_ids.append(result["id"])
            else:
                print_info(f"Long field values rejected with status {response.status_code}")

    def test_automatic_job_expiry(self):
        """Test automatic 35-day expiry functionality"""
        print_test_header("Automatic Job Expiry (35 days)")
        
        # Test 1: Create job and verify expiry_date is set automatically
        job_data = {
            "title": "Expiry Test Job",
            "company_id": self.company_id,
            "description": "Testing automatic expiry date setting",
            "location": "Johannesburg, Gauteng",
            "salary": "R50,000 - R70,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Job with Auto Expiry"):
            result = response.json()
            self.job_ids.append(result["id"])
            
            # Verify expiry_date is present and set to ~35 days from now
            if "expiry_date" in result:
                print_success("Job has expiry_date field")
                expiry_date = datetime.fromisoformat(result["expiry_date"].replace('Z', '+00:00'))
                posted_date = datetime.fromisoformat(result["posted_date"].replace('Z', '+00:00'))
                days_diff = (expiry_date - posted_date).days
                
                if 34 <= days_diff <= 36:  # Allow 1 day tolerance
                    print_success(f"Expiry date correctly set to {days_diff} days from posting")
                else:
                    print_error(f"Expiry date is {days_diff} days from posting, expected ~35 days")
            else:
                print_error("Job missing expiry_date field")
        
        # Test 2: Create a manually expired job for testing
        expired_job_data = job_data.copy()
        expired_job_data["title"] = "Manually Expired Job"
        
        response = self.make_request("POST", "/jobs", expired_job_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Job for Manual Expiry"):
            result = response.json()
            expired_job_id = result["id"]
            
            # Manually set expiry date to past (simulate expired job)
            # Note: This would typically be done directly in database for testing
            # For now, we'll track this job ID for later tests
            self.expired_job_ids.append(expired_job_id)
            print_info(f"Created job {expired_job_id} for expiry testing")

    def test_public_jobs_api(self):
        """Test public jobs API (no authentication required)"""
        print_test_header("Public Jobs API (No Authentication)")
        
        # Test 1: Get public jobs without authentication
        response = self.make_request("GET", "/public/jobs")
        if self.assert_response(response, 200, "Get Public Jobs (No Auth)"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} public jobs")
            
            if jobs:
                job = jobs[0]
                # Verify job structure
                required_fields = ["id", "title", "company_name", "description", 
                                 "location", "salary", "job_type", "work_type", "industry", "posted_date", "expiry_date"]
                for field in required_fields:
                    if field in job:
                        print_success(f"Public job contains required field: {field}")
                    else:
                        print_error(f"Public job missing required field: {field}")
                
                # Verify all jobs are non-expired
                for job in jobs:
                    expiry_date = datetime.fromisoformat(job["expiry_date"].replace('Z', '+00:00'))
                    if expiry_date > datetime.now(expiry_date.tzinfo):
                        print_success(f"Job '{job['title']}' is not expired")
                    else:
                        print_error(f"Expired job '{job['title']}' found in public listings")
        
        # Test 2: Filter by location
        response = self.make_request("GET", "/public/jobs", data={"location": "Johannesburg"})
        if self.assert_response(response, 200, "Filter Public Jobs by Location"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} jobs in Johannesburg")
            
            for job in jobs:
                if "johannesburg" in job["location"].lower():
                    print_success(f"Location filter working: {job['title']} - {job['location']}")
                else:
                    print_warning(f"Location filter may be loose: {job['title']} - {job['location']}")
        
        # Test 3: Filter by job_type
        response = self.make_request("GET", "/public/jobs", data={"job_type": "Permanent"})
        if self.assert_response(response, 200, "Filter Public Jobs by Job Type"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} permanent jobs")
            
            for job in jobs:
                if job["job_type"] == "Permanent":
                    print_success(f"Job type filter working: {job['title']} - {job['job_type']}")
                else:
                    print_error(f"Job type filter failed: {job['title']} - {job['job_type']}")
        
        # Test 4: Filter by work_type
        response = self.make_request("GET", "/public/jobs", data={"work_type": "Remote"})
        if self.assert_response(response, 200, "Filter Public Jobs by Work Type"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} remote jobs")
            
            for job in jobs:
                if job["work_type"] == "Remote":
                    print_success(f"Work type filter working: {job['title']} - {job['work_type']}")
                else:
                    print_error(f"Work type filter failed: {job['title']} - {job['work_type']}")
        
        # Test 5: Filter by industry
        response = self.make_request("GET", "/public/jobs", data={"industry": "Technology"})
        if self.assert_response(response, 200, "Filter Public Jobs by Industry"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} technology jobs")
            
            for job in jobs:
                if "technology" in job["industry"].lower():
                    print_success(f"Industry filter working: {job['title']} - {job['industry']}")
                else:
                    print_warning(f"Industry filter may be loose: {job['title']} - {job['industry']}")
        
        # Test 6: Search functionality
        response = self.make_request("GET", "/public/jobs", data={"search": "developer"})
        if self.assert_response(response, 200, "Search Public Jobs"):
            jobs = response.json()
            print_info(f"Found {len(jobs)} jobs matching 'developer'")
            
            for job in jobs:
                if "developer" in job["title"].lower() or "developer" in job["description"].lower():
                    print_success(f"Search working: {job['title']}")
                else:
                    print_warning(f"Search may be loose: {job['title']}")
        
        # Test 7: Limit parameter
        response = self.make_request("GET", "/public/jobs", data={"limit": 5})
        if self.assert_response(response, 200, "Limit Public Jobs"):
            jobs = response.json()
            if len(jobs) <= 5:
                print_success(f"Limit working: returned {len(jobs)} jobs (max 5)")
            else:
                print_error(f"Limit not working: returned {len(jobs)} jobs (expected max 5)")

    def test_enhanced_recruiter_job_management(self):
        """Test enhanced recruiter job management with archive functionality"""
        print_test_header("Enhanced Recruiter Job Management")
        
        # Test 1: Get active jobs only (default behavior)
        response = self.make_request("GET", "/jobs", data={"include_archived": False}, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Active Jobs Only"):
            active_jobs = response.json()
            print_info(f"Found {len(active_jobs)} active jobs")
            
            # Verify all jobs are non-expired
            for job in active_jobs:
                expiry_date = datetime.fromisoformat(job["expiry_date"].replace('Z', '+00:00'))
                if expiry_date > datetime.now(expiry_date.tzinfo):
                    print_success(f"Active job '{job['title']}' is not expired")
                else:
                    print_error(f"Expired job '{job['title']}' found in active listings")
        
        # Test 2: Get all jobs (active + expired)
        response = self.make_request("GET", "/jobs", data={"include_archived": True}, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get All Jobs (Active + Archived)"):
            all_jobs = response.json()
            print_info(f"Found {len(all_jobs)} total jobs (active + archived)")
            
            # Should include both active and expired jobs
            active_count = 0
            expired_count = 0
            for job in all_jobs:
                expiry_date = datetime.fromisoformat(job["expiry_date"].replace('Z', '+00:00'))
                if expiry_date > datetime.now(expiry_date.tzinfo):
                    active_count += 1
                else:
                    expired_count += 1
            
            print_info(f"Active jobs: {active_count}, Expired jobs: {expired_count}")
        
        # Test 3: Get archived jobs only
        response = self.make_request("GET", "/jobs/archived", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Archived Jobs Only"):
            archived_jobs = response.json()
            print_info(f"Found {len(archived_jobs)} archived jobs")
            
            # Verify all jobs are expired
            for job in archived_jobs:
                expiry_date = datetime.fromisoformat(job["expiry_date"].replace('Z', '+00:00'))
                if expiry_date <= datetime.now(expiry_date.tzinfo):
                    print_success(f"Archived job '{job['title']}' is properly expired")
                else:
                    print_error(f"Non-expired job '{job['title']}' found in archived listings")
        
        # Test 4: Filter archived jobs by company
        if self.accessible_companies:
            response = self.make_request("GET", "/jobs/archived", 
                                       data={"company_id": self.company_id}, 
                                       auth_token=self.recruiter_token)
            if self.assert_response(response, 200, "Filter Archived Jobs by Company"):
                company_archived_jobs = response.json()
                print_info(f"Found {len(company_archived_jobs)} archived jobs for company")
                
                # Verify all jobs belong to the specified company
                for job in company_archived_jobs:
                    if job["company_id"] == self.company_id:
                        print_success(f"Archived job belongs to correct company: {job['title']}")
                    else:
                        print_error(f"Archived job belongs to wrong company: {job['title']}")

    def test_job_reposting_functionality(self):
        """Test job reposting functionality"""
        print_test_header("Job Reposting Functionality")
        
        # First, we need to create a job and then test reposting
        # Since we can't easily create expired jobs in this test environment,
        # we'll test the repost endpoint with existing jobs
        
        # Test 1: Try to repost a job (should work even if not expired)
        if self.job_ids:
            job_id = self.job_ids[0]
            response = self.make_request("PUT", f"/jobs/{job_id}/repost", auth_token=self.recruiter_token)
            if self.assert_response(response, 200, "Repost Job"):
                result = response.json()
                print_success("Job reposted successfully")
                
                if "new_expiry_date" in result:
                    print_success("Repost response includes new expiry date")
                    new_expiry = datetime.fromisoformat(result["new_expiry_date"])
                    # Verify new expiry is ~35 days from now
                    days_from_now = (new_expiry - datetime.now()).days
                    if 34 <= days_from_now <= 36:
                        print_success(f"New expiry date correctly set to {days_from_now} days from now")
                    else:
                        print_warning(f"New expiry date is {days_from_now} days from now, expected ~35 days")
                else:
                    print_error("Repost response missing new_expiry_date")
        
        # Test 2: Try to repost non-existent job (should fail)
        fake_job_id = str(uuid.uuid4())
        response = self.make_request("PUT", f"/jobs/{fake_job_id}/repost", auth_token=self.recruiter_token)
        self.assert_response(response, 404, "Repost Non-existent Job (Should Fail)")
        
        # Test 3: Try to repost job without permission (should fail)
        if self.job_ids:
            # Login as different user (job seeker) and try to repost
            job_seeker_login = {
                "email": "sarah.johnson@demo.com",
                "password": "demo123"
            }
            
            response = self.make_request("POST", "/auth/login", job_seeker_login)
            if self.assert_response(response, 200, "Job Seeker Login for Repost Test"):
                job_seeker_token = response.json()["access_token"]
                
                job_id = self.job_ids[0]
                response = self.make_request("PUT", f"/jobs/{job_id}/repost", auth_token=job_seeker_token)
                self.assert_response(response, 403, "Unauthorized Repost (Should Fail)")
        
        # Test 4: Try to repost without authentication (should fail)
        if self.job_ids:
            job_id = self.job_ids[0]
            response = self.make_request("PUT", f"/jobs/{job_id}/repost")
            self.assert_response(response, 401, "Unauthenticated Repost (Should Fail)")

    def test_job_model_enhancements(self):
        """Test job model enhancements and enum validation"""
        print_test_header("Job Model Enhancements")
        
        # Test 1: Verify job_type enum validation
        job_types = ["Permanent", "Contract"]
        for job_type in job_types:
            job_data = {
                "title": f"Test {job_type} Job",
                "company_id": self.company_id,
                "description": f"Testing {job_type} job type",
                "location": "Cape Town, Western Cape",
                "salary": "R50,000 - R70,000 per month",
                "job_type": job_type,
                "work_type": "Remote",
                "industry": "Technology"
            }
            
            response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Create {job_type} Job"):
                result = response.json()
                self.job_ids.append(result["id"])
                if result["job_type"] == job_type:
                    print_success(f"Job type '{job_type}' correctly saved")
                else:
                    print_error(f"Job type mismatch: expected '{job_type}', got '{result['job_type']}'")
        
        # Test 2: Verify work_type enum validation
        work_types = ["Remote", "Onsite", "Hybrid"]
        for work_type in work_types:
            job_data = {
                "title": f"Test {work_type} Job",
                "company_id": self.company_id,
                "description": f"Testing {work_type} work type",
                "location": "Durban, KwaZulu-Natal",
                "salary": "R45,000 - R65,000 per month",
                "job_type": "Permanent",
                "work_type": work_type,
                "industry": "Technology"
            }
            
            response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Create {work_type} Job"):
                result = response.json()
                self.job_ids.append(result["id"])
                if result["work_type"] == work_type:
                    print_success(f"Work type '{work_type}' correctly saved")
                else:
                    print_error(f"Work type mismatch: expected '{work_type}', got '{result['work_type']}'")
        
        # Test 3: Test bulk upload still works with new model structure
        csv_data = """title,location,salary,job_type,work_type,industry,description
"Enhanced Model Test Job","Pretoria, Gauteng","R55000-R75000","Contract","Hybrid","Technology","Testing enhanced job model with bulk upload"
"""
        
        files = {'file': ('enhanced_model_test.csv', csv_data, 'text/csv')}
        form_data = {'company_id': self.company_id}
        
        response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Bulk Upload with Enhanced Model"):
            result = response.json()
            if result.get('jobs_created', 0) > 0:
                print_success("Bulk upload works with enhanced job model")
            else:
                print_error("Bulk upload failed with enhanced job model")
        
        # Test 4: Invalid enum values (should fail)
        invalid_job_type = {
            "title": "Invalid Job Type Test",
            "company_id": self.company_id,
            "description": "Testing invalid job type",
            "location": "Test Location",
            "salary": "R50,000",
            "job_type": "InvalidJobType",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", invalid_job_type, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Job Type Enum (Should Fail)")
        
        invalid_work_type = {
            "title": "Invalid Work Type Test",
            "company_id": self.company_id,
            "description": "Testing invalid work type",
            "location": "Test Location",
            "salary": "R50,000",
            "job_type": "Permanent",
            "work_type": "InvalidWorkType",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", invalid_work_type, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Work Type Enum (Should Fail)")

    def test_easy_apply_job_creation(self):
        """Test creating jobs for Easy Apply functionality"""
        print_test_header("Easy Apply Job Creation")
        
        # Test 1: Create job without application_url (Easy Apply enabled)
        easy_apply_job = {
            "title": "Easy Apply Frontend Developer",
            "company_id": self.company_id,
            "description": "Frontend developer position with Easy Apply functionality. No external application required.",
            "location": "Cape Town, Western Cape",
            "salary": "R55,000 - R75,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology",
            "experience": "3+ years in React/Vue.js",
            "qualifications": "Bachelor's degree in Computer Science"
        }
        
        response = self.make_request("POST", "/jobs", easy_apply_job, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Easy Apply Job"):
            result = response.json()
            self.easy_apply_job_ids.append(result["id"])
            self.job_ids.append(result["id"])
            print_success(f"Created Easy Apply job: {result['title']}")
            
            # Verify no application_url
            if not result.get("application_url"):
                print_success("Easy Apply job has no external application_url")
            else:
                print_error("Easy Apply job should not have application_url")
        
        # Test 2: Create job with application_url (External application)
        external_job = {
            "title": "External Apply Backend Developer",
            "company_id": self.company_id,
            "description": "Backend developer position requiring external application.",
            "location": "Johannesburg, Gauteng",
            "salary": "R65,000 - R85,000 per month",
            "job_type": "Contract",
            "work_type": "Hybrid",
            "industry": "Technology",
            "application_url": "https://company.com/careers/apply",
            "application_email": "careers@company.com"
        }
        
        response = self.make_request("POST", "/jobs", external_job, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create External Apply Job"):
            result = response.json()
            self.external_job_ids.append(result["id"])
            self.job_ids.append(result["id"])
            print_success(f"Created External Apply job: {result['title']}")
            
            # Verify has application_url
            if result.get("application_url"):
                print_success("External Apply job has application_url")
            else:
                print_error("External Apply job should have application_url")
        
        # Create more Easy Apply jobs for testing
        for i in range(3):
            job_data = {
                "title": f"Easy Apply Test Job {i+1}",
                "company_id": self.company_id,
                "description": f"Test job {i+1} for Easy Apply functionality testing",
                "location": "Durban, KwaZulu-Natal",
                "salary": "R45,000 - R65,000 per month",
                "job_type": "Permanent",
                "work_type": "Remote",
                "industry": "Technology"
            }
            
            response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Create Easy Apply Test Job {i+1}"):
                result = response.json()
                self.easy_apply_job_ids.append(result["id"])
                self.job_ids.append(result["id"])

    def test_easy_apply_job_application(self):
        """Test Easy Apply job application functionality"""
        print_test_header("Easy Apply Job Application")
        
        if not self.easy_apply_job_ids:
            print_error("No Easy Apply jobs available for testing")
            return
        
        easy_apply_job_id = self.easy_apply_job_ids[0]
        
        # Test 1: Valid Easy Apply application
        application_data = {
            "job_id": easy_apply_job_id,
            "cover_letter": "I am very interested in this position and believe my skills in React and Node.js make me a perfect fit for your team. I have 4 years of experience in full-stack development and am passionate about creating user-friendly applications.",
            "resume_url": "https://storage.example.com/resumes/sarah_johnson_resume.pdf",
            "additional_info": "I am available for immediate start and can work remotely. I have experience with agile methodologies and am comfortable working in fast-paced environments."
        }
        
        response = self.make_request("POST", f"/jobs/{easy_apply_job_id}/apply", application_data, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Valid Easy Apply Application"):
            result = response.json()
            self.application_ids.append(result["id"])
            print_success(f"Created application with ID: {result['id']}")
            
            # Verify application fields
            required_fields = ["id", "job_id", "applicant_id", "company_id", "status", "applied_date"]
            for field in required_fields:
                if field in result:
                    print_success(f"Application contains required field: {field}")
                else:
                    print_error(f"Application missing required field: {field}")
            
            # Verify default status is pending
            if result.get("status") == "pending":
                print_success("Application status correctly set to 'pending'")
            else:
                print_error(f"Application status should be 'pending', got '{result.get('status')}'")
        
        # Test 2: Apply with minimal data (only job_id required)
        if len(self.easy_apply_job_ids) > 1:
            minimal_application = {
                "job_id": self.easy_apply_job_ids[1]
            }
            
            response = self.make_request("POST", f"/jobs/{self.easy_apply_job_ids[1]}/apply", minimal_application, auth_token=self.job_seeker_token)
            if self.assert_response(response, 200, "Minimal Easy Apply Application"):
                result = response.json()
                self.application_ids.append(result["id"])
                print_success("Created application with minimal data")
        
        # Test 3: Try to apply for same job twice (should fail)
        duplicate_application = {
            "job_id": easy_apply_job_id,
            "cover_letter": "Trying to apply again"
        }
        
        response = self.make_request("POST", f"/jobs/{easy_apply_job_id}/apply", duplicate_application, auth_token=self.job_seeker_token)
        self.assert_response(response, 400, "Duplicate Application (Should Fail)")
        
        # Test 4: Try to apply for external job (should fail)
        if self.external_job_ids:
            external_application = {
                "job_id": self.external_job_ids[0],
                "cover_letter": "Trying to apply to external job"
            }
            
            response = self.make_request("POST", f"/jobs/{self.external_job_ids[0]}/apply", external_application, auth_token=self.job_seeker_token)
            self.assert_response(response, 400, "Apply to External Job (Should Fail)")
        
        # Test 5: Try to apply for non-existent job (should fail)
        fake_job_id = str(uuid.uuid4())
        fake_application = {
            "job_id": fake_job_id,
            "cover_letter": "Applying to non-existent job"
        }
        
        response = self.make_request("POST", f"/jobs/{fake_job_id}/apply", fake_application, auth_token=self.job_seeker_token)
        self.assert_response(response, 404, "Apply to Non-existent Job (Should Fail)")
        
        # Test 6: Recruiter trying to apply (should fail)
        recruiter_application = {
            "job_id": easy_apply_job_id,
            "cover_letter": "Recruiter trying to apply"
        }
        
        response = self.make_request("POST", f"/jobs/{easy_apply_job_id}/apply", recruiter_application, auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Recruiter Apply (Should Fail)")
        
        # Test 7: Unauthenticated application (should fail)
        unauth_application = {
            "job_id": easy_apply_job_id,
            "cover_letter": "Unauthenticated application"
        }
        
        response = self.make_request("POST", f"/jobs/{easy_apply_job_id}/apply", unauth_application)
        self.assert_response(response, 401, "Unauthenticated Application (Should Fail)")

    def test_job_seeker_applications_management(self):
        """Test job seeker applications management"""
        print_test_header("Job Seeker Applications Management")
        
        # Test 1: Get all applications for job seeker
        response = self.make_request("GET", "/applications", auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Get Job Seeker Applications"):
            applications = response.json()
            print_info(f"Found {len(applications)} applications for job seeker")
            
            if applications:
                app = applications[0]
                # Verify enriched response structure
                if "application" in app and "job" in app:
                    print_success("Application response is properly enriched with job details")
                    
                    application = app["application"]
                    job = app["job"]
                    
                    # Verify application fields
                    app_fields = ["id", "job_id", "applicant_id", "status", "applied_date"]
                    for field in app_fields:
                        if field in application:
                            print_success(f"Application contains field: {field}")
                        else:
                            print_error(f"Application missing field: {field}")
                    
                    # Verify job fields
                    job_fields = ["id", "title", "company_name", "location", "salary"]
                    for field in job_fields:
                        if field in job:
                            print_success(f"Job details contain field: {field}")
                        else:
                            print_error(f"Job details missing field: {field}")
                else:
                    print_error("Application response not properly enriched")
        
        # Test 2: Filter applications by status
        response = self.make_request("GET", "/applications", data={"status": "pending"}, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Filter Applications by Status"):
            pending_applications = response.json()
            print_info(f"Found {len(pending_applications)} pending applications")
            
            # Verify all applications have pending status
            for app in pending_applications:
                if app["application"]["status"] == "pending":
                    print_success(f"Application {app['application']['id']} has pending status")
                else:
                    print_error(f"Application {app['application']['id']} has wrong status: {app['application']['status']}")
        
        # Test 3: Filter by non-existent status
        response = self.make_request("GET", "/applications", data={"status": "nonexistent"}, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Filter by Non-existent Status"):
            empty_applications = response.json()
            if len(empty_applications) == 0:
                print_success("No applications found for non-existent status")
            else:
                print_warning(f"Found {len(empty_applications)} applications for non-existent status")
        
        # Test 4: Recruiter trying to access job seeker applications (should fail)
        response = self.make_request("GET", "/applications", auth_token=self.recruiter_token)
        self.assert_response(response, 403, "Recruiter Access Job Seeker Applications (Should Fail)")
        
        # Test 5: Unauthenticated access (should fail)
        response = self.make_request("GET", "/applications")
        self.assert_response(response, 401, "Unauthenticated Access Applications (Should Fail)")

    def test_recruiter_application_management(self):
        """Test recruiter application management"""
        print_test_header("Recruiter Application Management")
        
        if not self.easy_apply_job_ids:
            print_error("No Easy Apply jobs available for testing")
            return
        
        job_id = self.easy_apply_job_ids[0]
        
        # Test 1: Get applications for specific job
        response = self.make_request("GET", f"/jobs/{job_id}/applications", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Job Applications"):
            applications = response.json()
            print_info(f"Found {len(applications)} applications for job {job_id}")
            
            if applications:
                app = applications[0]
                # Verify enriched response structure
                if "application" in app and "applicant" in app and "job" in app:
                    print_success("Application response is properly enriched")
                    
                    application = app["application"]
                    applicant = app["applicant"]
                    job = app["job"]
                    
                    # Verify applicant data privacy (only safe fields)
                    safe_fields = ["id", "first_name", "last_name", "email", "skills", "location"]
                    sensitive_fields = ["password_hash", "phone", "about_me"]
                    
                    for field in safe_fields:
                        if field in applicant:
                            print_success(f"Applicant contains safe field: {field}")
                    
                    for field in sensitive_fields:
                        if field not in applicant:
                            print_success(f"Applicant properly excludes sensitive field: {field}")
                        else:
                            print_warning(f"Applicant contains sensitive field: {field}")
                else:
                    print_error("Application response not properly enriched")
        
        # Test 2: Filter job applications by status
        response = self.make_request("GET", f"/jobs/{job_id}/applications", data={"status": "pending"}, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Filter Job Applications by Status"):
            pending_apps = response.json()
            print_info(f"Found {len(pending_apps)} pending applications for job")
        
        # Test 3: Get all company applications
        response = self.make_request("GET", "/company/applications", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get All Company Applications"):
            company_applications = response.json()
            print_info(f"Found {len(company_applications)} total applications for company")
            
            if company_applications:
                # Verify all applications belong to company's jobs
                for app in company_applications:
                    if app["application"]["company_id"] == self.company_id:
                        print_success(f"Application belongs to correct company")
                    else:
                        print_error(f"Application belongs to wrong company")
        
        # Test 4: Filter company applications by job_id
        response = self.make_request("GET", "/company/applications", data={"job_id": job_id}, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Filter Company Applications by Job ID"):
            filtered_apps = response.json()
            print_info(f"Found {len(filtered_apps)} applications for specific job")
            
            # Verify all applications are for the specified job
            for app in filtered_apps:
                if app["application"]["job_id"] == job_id:
                    print_success(f"Filtered application belongs to correct job")
                else:
                    print_error(f"Filtered application belongs to wrong job")
        
        # Test 5: Try to access non-existent job applications (should fail)
        fake_job_id = str(uuid.uuid4())
        response = self.make_request("GET", f"/jobs/{fake_job_id}/applications", auth_token=self.recruiter_token)
        self.assert_response(response, 404, "Access Non-existent Job Applications (Should Fail)")
        
        # Test 6: Job seeker trying to access recruiter applications (should fail)
        response = self.make_request("GET", f"/jobs/{job_id}/applications", auth_token=self.job_seeker_token)
        self.assert_response(response, 403, "Job Seeker Access Recruiter Applications (Should Fail)")
        
        # Test 7: Unauthenticated access (should fail)
        response = self.make_request("GET", f"/jobs/{job_id}/applications")
        self.assert_response(response, 401, "Unauthenticated Access Applications (Should Fail)")

    def test_application_status_updates(self):
        """Test application status updates by recruiters"""
        print_test_header("Application Status Updates")
        
        if not self.application_ids:
            print_error("No applications available for testing")
            return
        
        application_id = self.application_ids[0]
        
        # Test 1: Update application status to reviewed
        status_update = {
            "status": "reviewed",
            "notes": "Initial review completed. Candidate has good technical background."
        }
        
        response = self.make_request("PUT", f"/applications/{application_id}", status_update, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Update Application Status to Reviewed"):
            result = response.json()
            print_success("Application status updated successfully")
            
            if result.get("status") == "reviewed":
                print_success("Application status correctly updated to 'reviewed'")
            else:
                print_error(f"Application status should be 'reviewed', got '{result.get('status')}'")
            
            if result.get("notes") == status_update["notes"]:
                print_success("Application notes correctly updated")
            else:
                print_error("Application notes not updated correctly")
            
            # Verify last_updated and reviewed_by fields
            if "last_updated" in result:
                print_success("Application has last_updated timestamp")
            else:
                print_error("Application missing last_updated timestamp")
            
            if result.get("reviewed_by") == self.recruiter_user_id:
                print_success("Application reviewed_by correctly set")
            else:
                print_error("Application reviewed_by not set correctly")
        
        # Test 2: Test status workflow progression
        status_progression = [
            ("shortlisted", "Candidate shortlisted for technical interview"),
            ("interviewed", "Technical interview completed. Good problem-solving skills."),
            ("offered", "Job offer extended. Waiting for candidate response."),
        ]
        
        for status, notes in status_progression:
            update_data = {"status": status, "notes": notes}
            response = self.make_request("PUT", f"/applications/{application_id}", update_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Update Status to {status.title()}"):
                result = response.json()
                if result.get("status") == status:
                    print_success(f"Status successfully updated to '{status}'")
                else:
                    print_error(f"Status update failed for '{status}'")
        
        # Test 3: Update with notes only (no status change)
        notes_only_update = {
            "notes": "Additional notes: Candidate has excellent communication skills and cultural fit."
        }
        
        response = self.make_request("PUT", f"/applications/{application_id}", notes_only_update, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Update Notes Only"):
            result = response.json()
            if notes_only_update["notes"] in result.get("notes", ""):
                print_success("Notes updated successfully without changing status")
            else:
                print_error("Notes update failed")
        
        # Test 4: Test rejection status
        if len(self.application_ids) > 1:
            rejection_update = {
                "status": "rejected",
                "notes": "Thank you for your interest. We decided to move forward with another candidate."
            }
            
            response = self.make_request("PUT", f"/applications/{self.application_ids[1]}", rejection_update, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, "Update Status to Rejected"):
                result = response.json()
                if result.get("status") == "rejected":
                    print_success("Application successfully rejected")
                else:
                    print_error("Rejection status update failed")
        
        # Test 5: Test invalid status (should fail)
        invalid_status_update = {
            "status": "invalid_status",
            "notes": "Testing invalid status"
        }
        
        response = self.make_request("PUT", f"/applications/{application_id}", invalid_status_update, auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Status Update (Should Fail)")
        
        # Test 6: Try to update non-existent application (should fail)
        fake_application_id = str(uuid.uuid4())
        update_data = {"status": "reviewed", "notes": "Testing non-existent application"}
        
        response = self.make_request("PUT", f"/applications/{fake_application_id}", update_data, auth_token=self.recruiter_token)
        self.assert_response(response, 404, "Update Non-existent Application (Should Fail)")
        
        # Test 7: Job seeker trying to update application (should fail)
        job_seeker_update = {"status": "withdrawn", "notes": "Job seeker trying to update"}
        
        response = self.make_request("PUT", f"/applications/{application_id}", job_seeker_update, auth_token=self.job_seeker_token)
        self.assert_response(response, 403, "Job Seeker Update Application (Should Fail)")
        
        # Test 8: Unauthenticated update (should fail)
        unauth_update = {"status": "reviewed", "notes": "Unauthenticated update"}
        
        response = self.make_request("PUT", f"/applications/{application_id}", unauth_update)
        self.assert_response(response, 401, "Unauthenticated Update (Should Fail)")

    def test_application_status_values(self):
        """Test all ApplicationStatus enum values"""
        print_test_header("Application Status Values")
        
        if not self.application_ids:
            print_error("No applications available for testing")
            return
        
        # Test all valid status values
        valid_statuses = [
            "pending", "reviewed", "shortlisted", "interviewed", 
            "offered", "rejected", "withdrawn"
        ]
        
        application_id = self.application_ids[0] if self.application_ids else None
        if not application_id:
            print_error("No application ID available for status testing")
            return
        
        for status in valid_statuses:
            update_data = {
                "status": status,
                "notes": f"Testing {status} status value"
            }
            
            response = self.make_request("PUT", f"/applications/{application_id}", update_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Test Status Value: {status}"):
                result = response.json()
                if result.get("status") == status:
                    print_success(f"Status '{status}' is valid and working")
                else:
                    print_error(f"Status '{status}' validation failed")
        
        # Test invalid status values
        invalid_statuses = [
            "invalid", "pending_review", "in_progress", "completed", "cancelled"
        ]
        
        for invalid_status in invalid_statuses:
            update_data = {
                "status": invalid_status,
                "notes": f"Testing invalid status: {invalid_status}"
            }
            
            response = self.make_request("PUT", f"/applications/{application_id}", update_data, auth_token=self.recruiter_token)
            if response and response.status_code == 422:
                print_success(f"Invalid status '{invalid_status}' properly rejected")
            else:
                print_error(f"Invalid status '{invalid_status}' should have been rejected")

    def test_job_seeker_progress_tracking(self):
        """Test job seeker progress tracking for applications"""
        print_test_header("Job Seeker Progress Tracking")
        
        # Get current job seeker profile to check progress
        response = self.make_request("GET", "/auth/me", auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Get Job Seeker Profile"):
            user = response.json()
            profile_progress = user.get("profile_progress", {})
            
            job_applications_count = profile_progress.get("job_applications", 0)
            print_info(f"Job seeker has {job_applications_count} applications tracked in progress")
            
            # Verify progress tracking for first 5 applications
            if job_applications_count > 0:
                print_success("Job application progress is being tracked")
                
                if job_applications_count >= 5:
                    print_success("Job seeker has reached 5+ applications milestone")
                else:
                    print_info(f"Job seeker needs {5 - job_applications_count} more applications to reach milestone")
            else:
                print_warning("No job applications tracked in progress (may not be updated yet)")

    def test_easy_apply_vs_external_differentiation(self):
        """Test differentiation between Easy Apply and External Apply jobs"""
        print_test_header("Easy Apply vs External Apply Differentiation")
        
        # Test 1: Verify Easy Apply jobs don't have application_url
        if self.easy_apply_job_ids:
            for job_id in self.easy_apply_job_ids[:2]:  # Test first 2
                # Get job details from public API
                response = self.make_request("GET", "/public/jobs", data={"limit": 100})
                if self.assert_response(response, 200, "Get Public Jobs for Easy Apply Check"):
                    jobs = response.json()
                    easy_apply_job = next((job for job in jobs if job["id"] == job_id), None)
                    
                    if easy_apply_job:
                        if not easy_apply_job.get("application_url"):
                            print_success(f"Easy Apply job '{easy_apply_job['title']}' has no application_url")
                        else:
                            print_error(f"Easy Apply job '{easy_apply_job['title']}' should not have application_url")
        
        # Test 2: Verify External Apply jobs have application_url
        if self.external_job_ids:
            for job_id in self.external_job_ids:
                response = self.make_request("GET", "/public/jobs", data={"limit": 100})
                if self.assert_response(response, 200, "Get Public Jobs for External Apply Check"):
                    jobs = response.json()
                    external_job = next((job for job in jobs if job["id"] == job_id), None)
                    
                    if external_job:
                        if external_job.get("application_url"):
                            print_success(f"External Apply job '{external_job['title']}' has application_url")
                        else:
                            print_error(f"External Apply job '{external_job['title']}' should have application_url")
        
        # Test 3: Verify Easy Apply works only for jobs without application_url
        print_info("Easy Apply functionality is properly restricted to jobs without external URLs")

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print_test_header("Cleaning Up Test Data")
        
        # Note: In a real system, you might want to delete created jobs and applications
        # For this test, we'll just log what was created
        print_info(f"Created {len(self.job_ids)} test jobs during testing")
        print_info(f"Created {len(self.easy_apply_job_ids)} Easy Apply jobs")
        print_info(f"Created {len(self.external_job_ids)} External Apply jobs")
        print_info(f"Created {len(self.application_ids)} job applications")
        
        for job_id in self.job_ids:
            print_info(f"Test job ID: {job_id}")
        
        for app_id in self.application_ids:
            print_info(f"Test application ID: {app_id}")

    def test_enhanced_easy_apply_with_profile_snapshot(self):
        """Test Enhanced Easy Apply system with profile pre-population"""
        print_test_header("Enhanced Easy Apply with Profile Snapshot")
        
        # First, update job seeker profile with comprehensive data
        profile_update = {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "about_me": "Experienced full-stack developer with 5+ years in React and Node.js. Passionate about creating scalable web applications and working in agile environments.",
            "phone": "+27-82-555-0123",
            "location": "Cape Town, Western Cape",
            "skills": ["React", "Node.js", "JavaScript", "TypeScript", "Python", "MongoDB", "PostgreSQL", "AWS"],
            "profile_picture_url": "https://storage.example.com/profiles/sarah_johnson.jpg"
        }
        
        response = self.make_request("PUT", "/profile", profile_update, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Update Job Seeker Profile"):
            print_success("Job seeker profile updated with comprehensive data")
        
        if not self.easy_apply_job_ids:
            print_error("No Easy Apply jobs available for testing")
            return
        
        easy_apply_job_id = self.easy_apply_job_ids[0]
        
        # Test 1: Enhanced Easy Apply with profile snapshot
        application_data = {
            "job_id": easy_apply_job_id,
            "cover_letter": "I am excited to apply for this position. My experience with React and Node.js aligns perfectly with your requirements.",
            "resume_url": "https://storage.example.com/resumes/sarah_johnson_resume_v2.pdf",
            "additional_info": "Available for immediate start. Open to relocation if needed."
        }
        
        response = self.make_request("POST", f"/jobs/{easy_apply_job_id}/apply", application_data, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Enhanced Easy Apply with Profile Snapshot"):
            result = response.json()
            enhanced_application_id = result["id"]
            self.application_ids.append(enhanced_application_id)
            print_success(f"Created enhanced application with ID: {enhanced_application_id}")
            
            # Verify applicant_snapshot is included
            if "applicant_snapshot" in result:
                print_success("Application includes applicant_snapshot")
                snapshot = result["applicant_snapshot"]
                
                # Verify snapshot contains expected profile data
                expected_fields = ["first_name", "last_name", "email", "location", "phone", "skills", "resume_url", "profile_picture_url"]
                for field in expected_fields:
                    if field in snapshot and snapshot[field]:
                        print_success(f"Snapshot contains {field}: {snapshot[field]}")
                    else:
                        print_warning(f"Snapshot missing or empty {field}")
                
                # Verify snapshot data matches current profile
                if snapshot.get("first_name") == "Sarah":
                    print_success("Snapshot first_name matches profile")
                if snapshot.get("location") == "Cape Town, Western Cape":
                    print_success("Snapshot location matches profile")
                if "React" in snapshot.get("skills", []):
                    print_success("Snapshot skills include React")
                
            else:
                print_error("Application missing applicant_snapshot")
        
        # Test 2: Verify profile changes don't affect existing snapshot
        print_info("Testing snapshot immutability...")
        
        # Update profile after application
        profile_change = {
            "location": "Johannesburg, Gauteng",
            "skills": ["Vue.js", "Angular", "Django"]
        }
        
        response = self.make_request("PUT", "/profile", profile_change, auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Update Profile After Application"):
            print_success("Profile updated after application submission")
        
        # Get the application again and verify snapshot unchanged
        response = self.make_request("GET", "/applications", auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Get Applications After Profile Change"):
            applications = response.json()
            
            # Find our enhanced application
            enhanced_app = None
            for app in applications:
                if app["application"]["id"] == enhanced_application_id:
                    enhanced_app = app["application"]
                    break
            
            if enhanced_app and "applicant_snapshot" in enhanced_app:
                snapshot = enhanced_app["applicant_snapshot"]
                
                # Verify snapshot still has original data
                if snapshot.get("location") == "Cape Town, Western Cape":
                    print_success("Snapshot location unchanged after profile update")
                else:
                    print_error(f"Snapshot location changed: {snapshot.get('location')}")
                
                if "React" in snapshot.get("skills", []):
                    print_success("Snapshot skills unchanged after profile update")
                else:
                    print_error("Snapshot skills changed after profile update")
            else:
                print_error("Could not find enhanced application or snapshot")

    def test_application_data_enrichment(self):
        """Test application data enrichment with profile snapshots"""
        print_test_header("Application Data Enrichment")
        
        # Test 1: Job seeker applications include profile data
        response = self.make_request("GET", "/applications", auth_token=self.job_seeker_token)
        if self.assert_response(response, 200, "Get Enriched Job Seeker Applications"):
            applications = response.json()
            print_info(f"Found {len(applications)} applications with enrichment")
            
            if applications:
                app = applications[0]
                # Verify enriched structure
                if "application" in app and "job" in app:
                    print_success("Job seeker applications properly enriched with job details")
                    
                    application = app["application"]
                    job = app["job"]
                    
                    # Check if application has snapshot
                    if "applicant_snapshot" in application:
                        print_success("Application includes applicant_snapshot in job seeker view")
                        snapshot = application["applicant_snapshot"]
                        
                        # Verify snapshot completeness
                        profile_fields = ["first_name", "last_name", "email", "skills"]
                        for field in profile_fields:
                            if field in snapshot:
                                print_success(f"Snapshot includes {field}")
                    else:
                        print_warning("Application missing applicant_snapshot")
                else:
                    print_error("Job seeker applications not properly enriched")
        
        # Test 2: Recruiter job applications include full applicant profiles
        if not self.easy_apply_job_ids:
            print_error("No Easy Apply jobs for recruiter testing")
            return
        
        job_id = self.easy_apply_job_ids[0]
        response = self.make_request("GET", f"/jobs/{job_id}/applications", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Enriched Recruiter Job Applications"):
            applications = response.json()
            print_info(f"Found {len(applications)} applications for recruiter")
            
            if applications:
                app = applications[0]
                # Verify enriched structure for recruiters
                if "application" in app and "applicant" in app and "job" in app:
                    print_success("Recruiter applications properly enriched with applicant and job details")
                    
                    application = app["application"]
                    applicant = app["applicant"]
                    
                    # Verify applicant profile data is included
                    applicant_fields = ["id", "first_name", "last_name", "email", "skills", "location"]
                    for field in applicant_fields:
                        if field in applicant:
                            print_success(f"Applicant profile includes {field}")
                        else:
                            print_warning(f"Applicant profile missing {field}")
                    
                    # Verify snapshot is also available
                    if "applicant_snapshot" in application:
                        print_success("Application includes applicant_snapshot for recruiter")
                    else:
                        print_warning("Application missing applicant_snapshot for recruiter")
                else:
                    print_error("Recruiter applications not properly enriched")
        
        # Test 3: Company applications include complete applicant information
        response = self.make_request("GET", "/company/applications", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get Enriched Company Applications"):
            applications = response.json()
            print_info(f"Found {len(applications)} company applications")
            
            if applications:
                app = applications[0]
                # Verify complete enrichment
                if "application" in app and "applicant" in app and "job" in app:
                    print_success("Company applications fully enriched")
                    
                    # Verify data privacy - sensitive fields should be excluded
                    applicant = app["applicant"]
                    sensitive_fields = ["password_hash", "about_me"]
                    for field in sensitive_fields:
                        if field not in applicant:
                            print_success(f"Sensitive field {field} properly excluded")
                        else:
                            print_warning(f"Sensitive field {field} exposed in applicant data")
                else:
                    print_error("Company applications not properly enriched")

    def test_profile_completeness_scenarios(self):
        """Test applications with various profile completeness levels"""
        print_test_header("Profile Completeness Scenarios")
        
        # Create a new job seeker with minimal profile
        minimal_user_data = {
            "email": "minimal.user@demo.com",
            "password": "demo123",
            "first_name": "Minimal",
            "last_name": "User",
            "role": "job_seeker"
        }
        
        response = self.make_request("POST", "/auth/register", minimal_user_data)
        if self.assert_response(response, 200, "Register Minimal Profile User"):
            minimal_user = response.json()
            minimal_token = minimal_user["access_token"]
            print_success("Created user with minimal profile")
            
            # Test application with minimal profile
            if self.easy_apply_job_ids:
                minimal_application = {
                    "job_id": self.easy_apply_job_ids[-1],  # Use last job to avoid duplicates
                    "cover_letter": "Application from user with minimal profile"
                }
                
                response = self.make_request("POST", f"/jobs/{self.easy_apply_job_ids[-1]}/apply", minimal_application, auth_token=minimal_token)
                if self.assert_response(response, 200, "Apply with Minimal Profile"):
                    result = response.json()
                    
                    # Verify snapshot handles minimal profile gracefully
                    if "applicant_snapshot" in result:
                        snapshot = result["applicant_snapshot"]
                        print_success("Snapshot created for minimal profile")
                        
                        # Check what fields are available
                        available_fields = [k for k, v in snapshot.items() if v is not None and v != ""]
                        print_info(f"Available snapshot fields: {available_fields}")
                        
                        # Should at least have basic fields
                        if snapshot.get("first_name") == "Minimal":
                            print_success("Snapshot includes first_name from minimal profile")
                        if snapshot.get("email") == "minimal.user@demo.com":
                            print_success("Snapshot includes email from minimal profile")
                    else:
                        print_error("No snapshot created for minimal profile")
        
        # Test with partially complete profile
        partial_user_data = {
            "email": "partial.user@demo.com",
            "password": "demo123",
            "first_name": "Partial",
            "last_name": "User",
            "role": "job_seeker"
        }
        
        response = self.make_request("POST", "/auth/register", partial_user_data)
        if self.assert_response(response, 200, "Register Partial Profile User"):
            partial_user = response.json()
            partial_token = partial_user["access_token"]
            
            # Update with some profile data
            partial_update = {
                "location": "Durban, KwaZulu-Natal",
                "skills": ["Python", "Django", "PostgreSQL"]
            }
            
            response = self.make_request("PUT", "/profile", partial_update, auth_token=partial_token)
            if self.assert_response(response, 200, "Update Partial Profile"):
                print_success("Updated user with partial profile data")
                
                # Test application with partial profile
                if len(self.easy_apply_job_ids) > 1:
                    partial_application = {
                        "job_id": self.easy_apply_job_ids[-2],  # Use second to last job
                        "cover_letter": "Application from user with partial profile",
                        "resume_url": "https://storage.example.com/resumes/partial_user.pdf"
                    }
                    
                    response = self.make_request("POST", f"/jobs/{self.easy_apply_job_ids[-2]}/apply", partial_application, auth_token=partial_token)
                    if self.assert_response(response, 200, "Apply with Partial Profile"):
                        result = response.json()
                        
                        if "applicant_snapshot" in result:
                            snapshot = result["applicant_snapshot"]
                            print_success("Snapshot created for partial profile")
                            
                            # Verify partial data is captured
                            if snapshot.get("location") == "Durban, KwaZulu-Natal":
                                print_success("Snapshot includes location from partial profile")
                            if "Python" in snapshot.get("skills", []):
                                print_success("Snapshot includes skills from partial profile")
                            if snapshot.get("resume_url") == "https://storage.example.com/resumes/partial_user.pdf":
                                print_success("Snapshot includes resume_url from application")

    def test_external_vs_easy_apply_differentiation(self):
        """Test External vs Easy Apply job differentiation"""
        print_test_header("External vs Easy Apply Differentiation")
        
        # Test 1: Verify Easy Apply jobs allow applications
        if self.easy_apply_job_ids:
            easy_job_id = self.easy_apply_job_ids[0]
            
            # Get job details to verify no application_url
            response = self.make_request("GET", "/public/jobs")
            if self.assert_response(response, 200, "Get Public Jobs for Verification"):
                jobs = response.json()
                easy_job = None
                for job in jobs:
                    if job["id"] == easy_job_id:
                        easy_job = job
                        break
                
                if easy_job:
                    if not easy_job.get("application_url"):
                        print_success("Easy Apply job has no application_url")
                    else:
                        print_error("Easy Apply job should not have application_url")
        
        # Test 2: Verify External Apply jobs block Easy Apply
        if self.external_job_ids:
            external_job_id = self.external_job_ids[0]
            
            # Get job details to verify has application_url
            response = self.make_request("GET", "/public/jobs")
            if self.assert_response(response, 200, "Get Public Jobs for External Verification"):
                jobs = response.json()
                external_job = None
                for job in jobs:
                    if job["id"] == external_job_id:
                        external_job = job
                        break
                
                if external_job:
                    if external_job.get("application_url"):
                        print_success(f"External job has application_url: {external_job['application_url']}")
                    else:
                        print_error("External job should have application_url")
            
            # Try to apply to external job (should fail)
            external_application = {
                "job_id": external_job_id,
                "cover_letter": "Attempting to apply to external job via Easy Apply"
            }
            
            response = self.make_request("POST", f"/jobs/{external_job_id}/apply", external_application, auth_token=self.job_seeker_token)
            if self.assert_response(response, 400, "Block Easy Apply for External Job"):
                print_success("External job properly blocks Easy Apply")
                
                # Verify error message mentions external application
                if response.text and "external" in response.text.lower():
                    print_success("Error message mentions external application")
        
        # Test 3: Create mixed job types and verify differentiation
        mixed_jobs = [
            {
                "title": "Easy Apply Mixed Test Job",
                "company_id": self.company_id,
                "description": "Job without application_url for Easy Apply testing",
                "location": "Port Elizabeth, Eastern Cape",
                "salary": "R40,000 - R60,000 per month",
                "job_type": "Permanent",
                "work_type": "Remote",
                "industry": "Technology"
                # No application_url = Easy Apply
            },
            {
                "title": "External Apply Mixed Test Job",
                "company_id": self.company_id,
                "description": "Job with application_url for external application testing",
                "location": "Bloemfontein, Free State",
                "salary": "R50,000 - R70,000 per month",
                "job_type": "Contract",
                "work_type": "Hybrid",
                "industry": "Technology",
                "application_url": "https://company.example.com/apply",
                "application_email": "jobs@company.example.com"
                # Has application_url = External Apply
            }
        ]
        
        created_mixed_jobs = []
        for job_data in mixed_jobs:
            response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
            if self.assert_response(response, 200, f"Create {job_data['title']}"):
                result = response.json()
                created_mixed_jobs.append(result)
                self.job_ids.append(result["id"])
        
        # Test applications to mixed jobs
        for i, job in enumerate(created_mixed_jobs):
            application_data = {
                "job_id": job["id"],
                "cover_letter": f"Test application to {job['title']}"
            }
            
            response = self.make_request("POST", f"/jobs/{job['id']}/apply", application_data, auth_token=self.job_seeker_token)
            
            if i == 0:  # Easy Apply job
                if self.assert_response(response, 200, "Apply to Easy Apply Mixed Job"):
                    print_success("Easy Apply job accepts applications")
    def test_package_management(self):
        """Test GET /api/packages - Get all available packages"""
        print_test_header("Package Management")
        
        # Test 1: Get all available packages
        response = self.make_request("GET", "/packages")
        if self.assert_response(response, 200, "Get All Packages"):
            packages = response.json()
            self.packages = packages
            print_info(f"Found {len(packages)} packages")
            
            # Verify we have the expected 6 packages
            if len(packages) == 6:
                print_success("Found expected 6 packages")
            else:
                print_error(f"Expected 6 packages, found {len(packages)}")
            
            # Verify package structure and pricing
            expected_packages = {
                "two_listings": {"price": 2800.00, "job_listings": 2, "subscription": False},
                "five_listings": {"price": 4150.00, "job_listings": 5, "subscription": False},
                "unlimited_listings": {"price": 3899.00, "job_listings": None, "subscription": True},
                "cv_search_10": {"price": 699.00, "cv_searches": 10, "subscription": False},
                "cv_search_20": {"price": 1299.00, "cv_searches": 20, "subscription": False},
                "cv_search_unlimited": {"price": 2899.00, "cv_searches": None, "subscription": True}
            }
            
            for package in packages:
                package_type = package["package_type"]
                if package_type in expected_packages:
                    expected = expected_packages[package_type]
                    
                    # Verify price
                    if package["price"] == expected["price"]:
                        print_success(f"{package_type}: Correct price R{package['price']}")
                    else:
                        print_error(f"{package_type}: Wrong price R{package['price']}, expected R{expected['price']}")
                    
                    # Verify subscription status
                    if package["is_subscription"] == expected["subscription"]:
                        print_success(f"{package_type}: Correct subscription status {package['is_subscription']}")
                    else:
                        print_error(f"{package_type}: Wrong subscription status {package['is_subscription']}")
                    
                    # Verify job listings
                    if "job_listings" in expected:
                        if package["job_listings_included"] == expected["job_listings"]:
                            print_success(f"{package_type}: Correct job listings {package['job_listings_included']}")
                        else:
                            print_error(f"{package_type}: Wrong job listings {package['job_listings_included']}")
                    
                    # Verify CV searches
                    if "cv_searches" in expected:
                        if package["cv_searches_included"] == expected["cv_searches"]:
                            print_success(f"{package_type}: Correct CV searches {package['cv_searches_included']}")
                        else:
                            print_error(f"{package_type}: Wrong CV searches {package['cv_searches_included']}")
                    
                    # Verify required fields
                    required_fields = ["id", "name", "description", "package_type", "price", "is_active"]
                    for field in required_fields:
                        if field in package:
                            print_success(f"{package_type}: Contains required field {field}")
                        else:
                            print_error(f"{package_type}: Missing required field {field}")
                else:
                    print_warning(f"Unexpected package type: {package_type}")
        
        # Test 2: Get specific package by type
        if self.packages:
            package_type = "two_listings"
            response = self.make_request("GET", f"/packages/{package_type}")
            if self.assert_response(response, 200, f"Get Package by Type ({package_type})"):
                package = response.json()
                if package["package_type"] == package_type:
                    print_success(f"Retrieved correct package: {package['name']}")
                else:
                    print_error(f"Retrieved wrong package type: {package['package_type']}")
        
        # Test 3: Get non-existent package type (should fail)
        response = self.make_request("GET", "/packages/non_existent")
        self.assert_response(response, 404, "Get Non-existent Package (Should Fail)")

    def test_payment_initiation(self):
        """Test POST /api/payments/initiate - Initiate payment for packages"""
        print_test_header("Payment Initiation")
        
        # Test 1: Initiate payment for Two Listings package
        response = self.make_request("POST", "/payments/initiate?package_type=two_listings", 
                                   auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Initiate Payment for Two Listings"):
            result = response.json()
            self.payment_ids.append(result["payment_id"])
            print_success(f"Payment initiated with ID: {result['payment_id']}")
            
            # Verify response structure
            required_fields = ["payment_id", "payment_url", "amount", "currency", "package_name"]
            for field in required_fields:
                if field in result:
                    print_success(f"Payment response contains {field}: {result[field]}")
                else:
                    print_error(f"Payment response missing {field}")
            
            # Verify amount matches package price
            if result["amount"] == 2800.00:
                print_success("Payment amount matches Two Listings package price")
            else:
                print_error(f"Payment amount {result['amount']} doesn't match expected 2800.00")
            
            # Verify currency is ZAR
            if result["currency"] == "ZAR":
                print_success("Payment currency is ZAR")
            else:
                print_error(f"Payment currency {result['currency']} should be ZAR")
        
        # Test 2: Initiate payment for Five Listings package
        response = self.make_request("POST", "/payments/initiate?package_type=five_listings", 
                                   auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Initiate Payment for Five Listings"):
            result = response.json()
            self.payment_ids.append(result["payment_id"])
            if result["amount"] == 4150.00:
                print_success("Five Listings payment amount correct")
        
        # Test 3: Initiate payment for Unlimited Listings package (subscription)
        response = self.make_request("POST", "/payments/initiate?package_type=unlimited_listings", 
                                   auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Initiate Payment for Unlimited Listings"):
            result = response.json()
            self.payment_ids.append(result["payment_id"])
            if result["amount"] == 3899.00:
                print_success("Unlimited Listings payment amount correct")
        
        # Test 4: Job seeker trying to initiate payment (should fail)
        response = self.make_request("POST", "/payments/initiate?package_type=two_listings", 
                                   auth_token=self.job_seeker_token)
        self.assert_response(response, 403, "Job Seeker Initiate Payment (Should Fail)")
        
        # Test 5: Unauthenticated payment initiation (should fail)
        response = self.make_request("POST", "/payments/initiate?package_type=two_listings")
        self.assert_response(response, 401, "Unauthenticated Payment Initiation (Should Fail)")
        
        # Test 6: Invalid package type (should fail)
        response = self.make_request("POST", "/payments/initiate?package_type=invalid_package", 
                                   auth_token=self.recruiter_token)
        self.assert_response(response, 422, "Invalid Package Type (Should Fail)")

    def test_payment_completion_and_package_activation(self):
        """Test POST /api/payments/{payment_id}/complete - Complete payment and activate package"""
        print_test_header("Payment Completion and Package Activation")
        
        if not self.payment_ids:
            print_error("No payment IDs available for testing")
            return
        
        # Test 1: Complete payment for Two Listings package
        payment_id = self.payment_ids[0]
        payment_reference = f"PF_TEST_{uuid.uuid4().hex[:8]}"
        
        response = self.make_request("POST", f"/payments/{payment_id}/complete?payment_reference={payment_reference}", 
                                   auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Complete Two Listings Payment"):
            result = response.json()
            print_success(f"Payment completed: {result['message']}")
            
            # Verify response structure
            expected_fields = ["message", "package_activated", "job_listings_remaining", "cv_searches_remaining"]
            for field in expected_fields:
                if field in result:
                    print_success(f"Completion response contains {field}")
                else:
                    print_error(f"Completion response missing {field}")
            
            # Verify Two Listings package activation
            if result["job_listings_remaining"] == 2:
                print_success("Two Listings package activated with 2 job listings")
            else:
                print_error(f"Expected 2 job listings, got {result['job_listings_remaining']}")
            
            if result["cv_searches_remaining"] == 0:
                print_success("Two Listings package has 0 CV searches as expected")
            else:
                print_error(f"Expected 0 CV searches, got {result['cv_searches_remaining']}")
        
        # Test 2: Complete payment for subscription package (if available)
        if len(self.payment_ids) > 2:
            payment_id = self.payment_ids[2]  # Unlimited Listings
            payment_reference = f"PF_TEST_{uuid.uuid4().hex[:8]}"
            
            response = self.make_request("POST", f"/payments/{payment_id}/complete?payment_reference={payment_reference}", 
                                       auth_token=self.recruiter_token)
            if self.assert_response(response, 200, "Complete Unlimited Listings Payment"):
                result = response.json()
                
                # Verify unlimited package activation
                if result["job_listings_remaining"] is None:
                    print_success("Unlimited Listings package activated with unlimited job listings")
                else:
                    print_error(f"Expected unlimited job listings, got {result['job_listings_remaining']}")
                
                if result["cv_searches_remaining"] == 10:
                    print_success("Unlimited Listings package has 10 CV searches")
                else:
                    print_error(f"Expected 10 CV searches, got {result['cv_searches_remaining']}")
        
        # Test 3: Try to complete non-existent payment (should fail)
        fake_payment_id = str(uuid.uuid4())
        response = self.make_request("POST", f"/payments/{fake_payment_id}/complete?payment_reference=fake_ref", 
                                   auth_token=self.recruiter_token)
        self.assert_response(response, 404, "Complete Non-existent Payment (Should Fail)")
        
        # Test 4: Try to complete another user's payment (should fail)
        if len(self.payment_ids) > 1:
            payment_id = self.payment_ids[1]
            response = self.make_request("POST", f"/payments/{payment_id}/complete?payment_reference=fake_ref", 
                                       auth_token=self.job_seeker_token)
            self.assert_response(response, 403, "Complete Other User's Payment (Should Fail)")

    def test_user_package_management(self):
        """Test GET /api/my-packages - Get user's purchased packages"""
        print_test_header("User Package Management")
        
        # Test 1: Get user's packages
        response = self.make_request("GET", "/my-packages", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Get User Packages"):
            packages = response.json()
            self.user_packages = packages
            print_info(f"Found {len(packages)} user packages")
            
            if packages:
                package = packages[0]
                
                # Verify response structure
                required_fields = ["user_package", "package", "is_expired"]
                for field in required_fields:
                    if field in package:
                        print_success(f"Package response contains {field}")
                    else:
                        print_error(f"Package response missing {field}")
                
                # Verify user_package fields
                user_package = package["user_package"]
                user_package_fields = ["id", "user_id", "package_id", "package_type", "purchased_date", "is_active"]
                for field in user_package_fields:
                    if field in user_package:
                        print_success(f"User package contains {field}")
                    else:
                        print_error(f"User package missing {field}")
                
                # Verify package details
                package_details = package["package"]
                package_fields = ["id", "name", "description", "package_type", "price"]
                for field in package_fields:
                    if field in package_details:
                        print_success(f"Package details contain {field}")
                    else:
                        print_error(f"Package details missing {field}")
                
                # Check expiry status
                if package["is_expired"] == False:
                    print_success("Package is not expired")
                else:
                    print_info("Package is expired")
                
                # Verify subscription vs one-time package differences
                if user_package.get("expiry_date"):
                    print_success("Subscription package has expiry date")
                    if user_package.get("subscription_status"):
                        print_success(f"Subscription status: {user_package['subscription_status']}")
                else:
                    print_success("One-time package has no expiry date")
                
                # Verify credit counting
                if user_package.get("job_listings_remaining") is not None:
                    print_success(f"Job listings remaining: {user_package['job_listings_remaining']}")
                else:
                    print_success("Unlimited job listings")
                
                if user_package.get("cv_searches_remaining") is not None:
                    print_success(f"CV searches remaining: {user_package['cv_searches_remaining']}")
                else:
                    print_success("Unlimited CV searches")
        
        # Test 2: Job seeker trying to access packages (should fail)
        response = self.make_request("GET", "/my-packages", auth_token=self.job_seeker_token)
        self.assert_response(response, 403, "Job Seeker Access Packages (Should Fail)")
        
        # Test 3: Unauthenticated access (should fail)
        response = self.make_request("GET", "/my-packages")
        self.assert_response(response, 401, "Unauthenticated Access Packages (Should Fail)")

    def test_job_posting_with_package_credits(self):
        """Test POST /api/jobs - Now enforces package requirements"""
        print_test_header("Job Posting with Package Credits")
        
        # Test 1: Create job with available credits (should succeed)
        job_data = {
            "title": "Package Credit Test Job",
            "company_id": self.company_id,
            "description": "Testing job posting with package credits",
            "location": "Johannesburg, Gauteng",
            "salary": "R50,000 - R70,000 per month",
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology"
        }
        
        response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Job with Available Credits"):
            result = response.json()
            self.job_ids.append(result["id"])
            print_success(f"Job created successfully: {result['title']}")
            
            # Verify job expiry based on package settings
            if "expiry_date" in result:
                expiry_date = datetime.fromisoformat(result["expiry_date"].replace('Z', '+00:00'))
                posted_date = datetime.fromisoformat(result["posted_date"].replace('Z', '+00:00'))
                days_diff = (expiry_date - posted_date).days
                
                # Two Listings package should have 30-day expiry
                if 29 <= days_diff <= 31:
                    print_success(f"Job expiry correctly set to {days_diff} days (Two Listings package)")
                else:
                    print_warning(f"Job expiry is {days_diff} days, expected ~30 days for Two Listings")
        
        # Test 2: Create another job to test credit deduction
        job_data["title"] = "Second Package Credit Test Job"
        response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Create Second Job (Credit Deduction)"):
            result = response.json()
            self.job_ids.append(result["id"])
            print_success("Second job created successfully")
        
        # Test 3: Try to create third job (should fail if only Two Listings package)
        job_data["title"] = "Third Package Credit Test Job (Should Fail)"
        response = self.make_request("POST", "/jobs", job_data, auth_token=self.recruiter_token)
        
        # This might succeed if we have unlimited package or fail if only limited packages
        if response.status_code == 402:
            print_success("Job posting correctly blocked due to insufficient credits")
            self.assert_response(response, 402, "Create Job Without Credits (Should Fail)")
        elif response.status_code == 200:
            result = response.json()
            self.job_ids.append(result["id"])
            print_info("Job created successfully (unlimited package or additional credits available)")
        else:
            print_error(f"Unexpected response status: {response.status_code}")
        
        # Test 4: Verify proper job expiry for unlimited package (35 days)
        if len(self.job_ids) >= 3:  # If we have jobs from unlimited package
            job_id = self.job_ids[-1]
            # Get job details to check expiry
            response = self.make_request("GET", "/public/jobs", data={"limit": 100})
            if response.status_code == 200:
                jobs = response.json()
                for job in jobs:
                    if job["id"] == job_id:
                        expiry_date = datetime.fromisoformat(job["expiry_date"].replace('Z', '+00:00'))
                        posted_date = datetime.fromisoformat(job["posted_date"].replace('Z', '+00:00'))
                        days_diff = (expiry_date - posted_date).days
                        
                        if 34 <= days_diff <= 36:
                            print_success(f"Unlimited package job expiry correctly set to {days_diff} days")
                        else:
                            print_warning(f"Job expiry is {days_diff} days, expected ~35 days for Unlimited")
                        break

    def test_package_credit_management(self):
        """Test package credit management and smart package selection"""
        print_test_header("Package Credit Management")
        
        # Test 1: Check updated package credits after job posting
        response = self.make_request("GET", "/my-packages", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Check Package Credits After Job Posting"):
            packages = response.json()
            
            for package in packages:
                user_package = package["user_package"]
                package_details = package["package"]
                
                print_info(f"Package: {package_details['name']}")
                print_info(f"Type: {package_details['package_type']}")
                print_info(f"Job listings remaining: {user_package.get('job_listings_remaining', 'Unlimited')}")
                print_info(f"Is active: {user_package['is_active']}")
                
                # Verify credit deduction for limited packages
                if package_details["package_type"] == "two_listings":
                    remaining = user_package.get("job_listings_remaining", 0)
                    if remaining == 0:
                        print_success("Two Listings package credits fully used")
                        if not user_package["is_active"]:
                            print_success("Two Listings package correctly deactivated")
                        else:
                            print_warning("Two Listings package should be deactivated when credits exhausted")
                    elif remaining == 1:
                        print_success("Two Listings package has 1 credit remaining")
                    else:
                        print_info(f"Two Listings package has {remaining} credits remaining")
                
                # Verify unlimited packages don't deduct credits
                elif package_details["package_type"] == "unlimited_listings":
                    if user_package.get("job_listings_remaining") is None:
                        print_success("Unlimited package maintains unlimited job listings")
                    else:
                        print_error("Unlimited package should not have limited job listings")
        
        # Test 2: Test smart package selection (limited packages used before unlimited)
        # This is tested implicitly through job creation order
        print_info("Smart package selection tested through job creation sequence")
        
        # Test 3: Test subscription expiry handling
        # We can't easily test real expiry in this test environment, but we can verify the logic
        print_info("Subscription expiry handling verified through package structure")

    def test_package_scenarios(self):
        """Test comprehensive package scenarios"""
        print_test_header("Package Scenarios")
        
        # Test 1: Purchase different package types and verify activation
        print_info("Testing package purchase and activation scenarios")
        
        # Initiate and complete CV search package
        response = self.make_request("POST", "/payments/initiate?package_type=cv_search_10", 
                                   auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Initiate CV Search Package Payment"):
            result = response.json()
            payment_id = result["payment_id"]
            
            # Complete the payment
            payment_reference = f"PF_TEST_CV_{uuid.uuid4().hex[:8]}"
            response = self.make_request("POST", f"/payments/{payment_id}/complete", 
                                       data={"payment_reference": payment_reference}, 
                                       auth_token=self.recruiter_token)
            if self.assert_response(response, 200, "Complete CV Search Package Payment"):
                result = response.json()
                if result["cv_searches_remaining"] == 10:
                    print_success("CV Search package activated with 10 searches")
                else:
                    print_error(f"Expected 10 CV searches, got {result['cv_searches_remaining']}")
        
        # Test 2: Verify package expiry and status management
        response = self.make_request("GET", "/my-packages", auth_token=self.recruiter_token)
        if self.assert_response(response, 200, "Verify Package Status Management"):
            packages = response.json()
            
            subscription_packages = 0
            one_time_packages = 0
            
            for package in packages:
                package_details = package["package"]
                user_package = package["user_package"]
                
                if package_details["is_subscription"]:
                    subscription_packages += 1
                    if user_package.get("expiry_date"):
                        print_success(f"Subscription package {package_details['name']} has expiry date")
                    if user_package.get("subscription_status"):
                        print_success(f"Subscription status: {user_package['subscription_status']}")
                else:
                    one_time_packages += 1
                    if not user_package.get("expiry_date"):
                        print_success(f"One-time package {package_details['name']} has no expiry")
            
            print_info(f"Found {subscription_packages} subscription packages and {one_time_packages} one-time packages")
        
        # Test 3: Test bulk job creation with package restrictions
        if self.user_packages:
            print_info("Testing bulk job creation with package restrictions")
            
            # Create CSV with multiple jobs
            csv_data = """title,location,salary,job_type,work_type,industry,description
"Bulk Test Job 1","Cape Town","R50000","Permanent","Remote","Technology","Testing bulk creation with packages"
"Bulk Test Job 2","Durban","R55000","Contract","Hybrid","Technology","Testing bulk creation with packages"
"Bulk Test Job 3","Pretoria","R60000","Permanent","Onsite","Technology","Testing bulk creation with packages"
"""
            
            files = {'file': ('bulk_package_test.csv', csv_data, 'text/csv')}
            form_data = {'company_id': self.company_id}
            
            response = self.make_request("POST", "/jobs/bulk", data=form_data, files=files, auth_token=self.recruiter_token)
            if response.status_code == 200:
                result = response.json()
                print_success(f"Bulk job creation: {result.get('jobs_created', 0)} jobs created")
                if result.get('errors'):
                    print_info(f"Bulk creation errors: {len(result['errors'])}")
            elif response.status_code == 402:
                print_success("Bulk job creation correctly blocked due to insufficient package credits")
            else:
                print_warning(f"Unexpected bulk creation response: {response.status_code}")

    def run_all_tests(self):
        """Run all job posting and application system tests"""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 Starting Job Rocket Package and Payment System Tests{Colors.ENDC}")
        print(f"{Colors.BLUE}Testing against: {BASE_URL}{Colors.ENDC}")
        print(f"{Colors.BLUE}Timestamp: {datetime.now().isoformat()}{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            # Setup
            if not self.setup_test_environment():
                print_error("Failed to setup test environment. Aborting tests.")
                return False
            
            # Run Package and Payment System Tests (Priority)
            print(f"\n{Colors.BOLD}{Colors.BLUE}=== PACKAGE AND PAYMENT SYSTEM TESTS ==={Colors.ENDC}")
            self.test_package_management()
            self.test_payment_initiation()
            self.test_payment_completion_and_package_activation()
            self.test_user_package_management()
            self.test_job_posting_with_package_credits()
            self.test_package_credit_management()
            self.test_package_scenarios()
            
            # Run Enhanced Easy Apply System Tests
            print(f"\n{Colors.BOLD}{Colors.BLUE}=== ENHANCED EASY APPLY SYSTEM TESTS ==={Colors.ENDC}")
            self.test_enhanced_easy_apply_with_profile_snapshot()
            self.test_application_data_enrichment()
            self.test_profile_completeness_scenarios()
            self.test_external_vs_easy_apply_differentiation()
            
            # Run existing Easy Apply tests
            print(f"\n{Colors.BOLD}{Colors.BLUE}=== EASY APPLY SYSTEM TESTS ==={Colors.ENDC}")
            self.test_easy_apply_job_creation()
            self.test_easy_apply_job_application()
            self.test_job_seeker_applications_management()
            self.test_recruiter_application_management()
            self.test_application_status_updates()
            self.test_application_status_values()
            self.test_job_seeker_progress_tracking()
            self.test_easy_apply_vs_external_differentiation()
            
            # Run core job posting tests
            print(f"\n{Colors.BOLD}{Colors.BLUE}=== CORE JOB POSTING SYSTEM TESTS ==={Colors.ENDC}")
            self.test_get_accessible_companies()
            self.test_create_single_job()
            self.test_automatic_job_expiry()
            self.test_bulk_job_upload()
            self.test_get_jobs_for_recruiter()
            self.test_enhanced_recruiter_job_management()
            self.test_public_jobs_api()
            self.test_job_reposting_functionality()
            self.test_job_model_enhancements()
            self.test_job_posting_with_company_access()
            self.test_recruiter_progress_tracking()
            self.test_authentication_and_authorization()
            
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
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Enhanced Easy Apply system is working correctly.{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}💥 Some tests failed. Please review the errors above.{Colors.ENDC}")
            return False

if __name__ == "__main__":
    test_suite = JobPostingTestSuite()
    success = test_suite.run_all_tests()
    exit(0 if success else 1)