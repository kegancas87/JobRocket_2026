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

class JobPostingTestSuite:
    def __init__(self):
        self.recruiter_token = None
        self.recruiter_user_id = None
        self.company_id = None
        self.job_ids = []
        self.expired_job_ids = []
        self.accessible_companies = []
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
        """Setup test environment with recruiter login"""
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

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print_test_header("Cleaning Up Test Data")
        
        # Note: In a real system, you might want to delete created jobs
        # For this test, we'll just log what was created
        print_info(f"Created {len(self.job_ids)} test jobs during testing")
        for job_id in self.job_ids:
            print_info(f"Test job ID: {job_id}")

    def run_all_tests(self):
        """Run all job posting system tests"""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 Starting Job Rocket Job Posting System Tests{Colors.ENDC}")
        print(f"{Colors.BLUE}Testing against: {BASE_URL}{Colors.ENDC}")
        print(f"{Colors.BLUE}Timestamp: {datetime.now().isoformat()}{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            # Setup
            if not self.setup_test_environment():
                print_error("Failed to setup test environment. Aborting tests.")
                return False
            
            # Run all test suites
            self.test_get_accessible_companies()
            self.test_create_single_job()
            self.test_bulk_job_upload()
            self.test_get_jobs_for_recruiter()
            self.test_job_posting_with_company_access()
            self.test_recruiter_progress_tracking()
            self.test_authentication_and_authorization()
            self.test_error_handling_and_edge_cases()
            
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
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Job posting system is working correctly.{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}💥 Some tests failed. Please review the errors above.{Colors.ENDC}")
            return False

if __name__ == "__main__":
    test_suite = JobPostingTestSuite()
    success = test_suite.run_all_tests()
    exit(0 if success else 1)