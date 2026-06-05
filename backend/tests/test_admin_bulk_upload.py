"""
Admin Bulk Upload Feature Tests
Tests for CSV/Excel bulk job upload functionality for admin users
"""

import pytest
import requests
import os
import io
import csv

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@jobrocket.co.za"
ADMIN_PASSWORD = "admin123"
RECRUITER_EMAIL = "hr@techcorp.co.za"
RECRUITER_PASSWORD = "demo123"
JOB_SEEKER_EMAIL = "thabo.mthembu@gmail.com"
JOB_SEEKER_PASSWORD = "demo123"


class TestAdminBulkUpload:
    """Admin Bulk Upload endpoint tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def recruiter_token(self):
        """Get recruiter authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        assert response.status_code == 200, f"Recruiter login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def job_seeker_token(self):
        """Get job seeker authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        assert response.status_code == 200, f"Job seeker login failed: {response.text}"
        return response.json().get("access_token")
    
    # ============================================
    # Template Download Tests
    # ============================================
    
    def test_template_download_csv_admin(self, admin_token):
        """Admin can download CSV template"""
        response = requests.get(
            f"{BASE_URL}/api/admin/jobs/bulk/template?format=csv",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"CSV template download failed: {response.text}"
        assert "text/csv" in response.headers.get("Content-Type", "")
        
        # Verify CSV content has correct headers
        content = response.text
        assert "Job Link" in content or "job_link" in content.lower()
        assert "Job Title" in content or "job_title" in content.lower()
        assert "Company" in content or "company" in content.lower()
        assert "Location" in content or "location" in content.lower()
        assert "Salary" in content or "salary" in content.lower()
        assert "Description" in content or "description" in content.lower()
        print(f"CSV template headers: {content.split(chr(10))[0]}")
    
    def test_template_download_xlsx_admin(self, admin_token):
        """Admin can download Excel template"""
        response = requests.get(
            f"{BASE_URL}/api/admin/jobs/bulk/template?format=xlsx",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Excel template download failed: {response.text}"
        content_type = response.headers.get("Content-Type", "")
        assert "spreadsheet" in content_type or "application/vnd" in content_type
        # Verify it's a valid xlsx file (starts with PK for zip format)
        assert response.content[:2] == b'PK', "Excel file should be a valid zip/xlsx format"
        print(f"Excel template size: {len(response.content)} bytes")
    
    def test_template_download_no_auth(self):
        """Template download requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/jobs/bulk/template?format=csv")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_template_download_recruiter_forbidden(self, recruiter_token):
        """Recruiter cannot download admin template"""
        response = requests.get(
            f"{BASE_URL}/api/admin/jobs/bulk/template?format=csv",
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for recruiter, got {response.status_code}"
        print(f"Recruiter correctly denied: {response.json()}")
    
    def test_template_download_job_seeker_forbidden(self, job_seeker_token):
        """Job seeker cannot download admin template"""
        response = requests.get(
            f"{BASE_URL}/api/admin/jobs/bulk/template?format=csv",
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for job seeker, got {response.status_code}"
    
    # ============================================
    # Bulk Upload Tests
    # ============================================
    
    def test_bulk_upload_no_auth(self):
        """Bulk upload requires authentication"""
        csv_content = "Job Title,Company,Location\nTest Job,Test Co,Test City"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = requests.post(f"{BASE_URL}/api/admin/jobs/bulk", files=files)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_bulk_upload_recruiter_forbidden(self, recruiter_token):
        """Recruiter cannot use admin bulk upload"""
        csv_content = "Job Title,Company,Location\nTest Job,Test Co,Test City"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {recruiter_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for recruiter, got {response.status_code}"
        print(f"Recruiter correctly denied bulk upload: {response.json()}")
    
    def test_bulk_upload_job_seeker_forbidden(self, job_seeker_token):
        """Job seeker cannot use admin bulk upload"""
        csv_content = "Job Title,Company,Location\nTest Job,Test Co,Test City"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {job_seeker_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for job seeker, got {response.status_code}"
    
    def test_bulk_upload_valid_csv(self, admin_token):
        """Admin can upload valid CSV with jobs"""
        # Create CSV with valid jobs
        csv_content = """Job Link,Job Title,Company,Location,Salary,Description
https://example.com/job1,TEST_BulkUpload_Developer,TEST_BulkCo,Johannesburg,R50000,A test developer position
https://example.com/job2,TEST_BulkUpload_Designer,TEST_BulkCo,Cape Town,R45000,A test designer position
,TEST_BulkUpload_Manager,TEST_BulkCo,Durban,,Management role with TBC fields
https://example.com/job4,TEST_BulkUpload_Analyst,,,R40000,"""
        
        files = {"file": ("test_jobs.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Bulk upload failed: {response.text}"
        result = response.json()
        
        # Verify response structure
        assert "total_rows" in result
        assert "created" in result
        assert "failed" in result
        assert "errors" in result
        
        # All 4 rows should be created (Job Title is mandatory, all have it)
        assert result["created"] == 4, f"Expected 4 created, got {result['created']}"
        assert result["failed"] == 0, f"Expected 0 failed, got {result['failed']}"
        
        print(f"Bulk upload result: {result}")
    
    def test_bulk_upload_missing_title_rejected(self, admin_token):
        """Rows without Job Title are rejected"""
        csv_content = """Job Link,Job Title,Company,Location,Salary,Description
https://example.com/job1,TEST_BulkUpload_Valid,TEST_Co,Johannesburg,R50000,Valid job
https://example.com/job2,,TEST_Co,Cape Town,R45000,Missing title - should fail
,TEST_BulkUpload_Valid2,TEST_Co,Durban,R40000,Another valid job"""
        
        files = {"file": ("test_jobs.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Bulk upload failed: {response.text}"
        result = response.json()
        
        # 2 valid, 1 missing title
        assert result["created"] == 2, f"Expected 2 created, got {result['created']}"
        assert result["failed"] == 1, f"Expected 1 failed, got {result['failed']}"
        
        # Check error message mentions missing title
        assert len(result["errors"]) > 0
        error_msg = result["errors"][0].get("error", "").lower()
        assert "title" in error_msg or "mandatory" in error_msg, f"Error should mention title: {result['errors']}"
        
        print(f"Missing title rejection: {result}")
    
    def test_bulk_upload_empty_fields_default_to_tbc(self, admin_token):
        """Empty fields should default to 'TBC'"""
        csv_content = """Job Link,Job Title,Company,Location,Salary,Description
,TEST_BulkUpload_TBCTest,,,, """
        
        files = {"file": ("test_tbc.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Bulk upload failed: {response.text}"
        result = response.json()
        assert result["created"] == 1, f"Expected 1 created, got {result['created']}"
        
        # Verify the job was created with TBC values by searching for it
        jobs_response = requests.get(
            f"{BASE_URL}/api/public/jobs",
            params={"limit": 100}
        )
        assert jobs_response.status_code == 200
        
        jobs = jobs_response.json().get("jobs", [])
        tbc_job = next((j for j in jobs if j.get("title") == "TEST_BulkUpload_TBCTest"), None)
        
        if tbc_job:
            # Verify TBC defaults
            assert tbc_job.get("company_name") == "TBC", f"Company should be TBC: {tbc_job.get('company_name')}"
            assert tbc_job.get("location") == "TBC", f"Location should be TBC: {tbc_job.get('location')}"
            assert tbc_job.get("salary") == "TBC", f"Salary should be TBC: {tbc_job.get('salary')}"
            assert tbc_job.get("description") == "TBC", f"Description should be TBC: {tbc_job.get('description')}"
            print(f"TBC defaults verified: company={tbc_job.get('company_name')}, location={tbc_job.get('location')}")
        else:
            print("Warning: Could not find TBC test job to verify defaults")
    
    def test_bulk_upload_job_link_maps_to_application_url(self, admin_token):
        """Job Link should map to application_url field"""
        test_url = "https://test-application-url.example.com/apply"
        csv_content = f"""Job Link,Job Title,Company,Location,Salary,Description
{test_url},TEST_BulkUpload_LinkTest,LinkTestCo,Johannesburg,R50000,Testing job link mapping"""
        
        files = {"file": ("test_link.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Bulk upload failed: {response.text}"
        result = response.json()
        assert result["created"] == 1
        
        # Find the job and verify application_url
        jobs_response = requests.get(
            f"{BASE_URL}/api/public/jobs",
            params={"limit": 100}
        )
        jobs = jobs_response.json().get("jobs", [])
        link_job = next((j for j in jobs if j.get("title") == "TEST_BulkUpload_LinkTest"), None)
        
        if link_job:
            assert link_job.get("application_url") == test_url, f"application_url should be {test_url}: {link_job.get('application_url')}"
            print(f"Job Link correctly mapped to application_url: {link_job.get('application_url')}")
        else:
            print("Warning: Could not find link test job to verify application_url")
    
    def test_bulk_upload_unsupported_format(self, admin_token):
        """Unsupported file formats are rejected"""
        txt_content = "This is not a CSV or Excel file"
        files = {"file": ("test.txt", txt_content, "text/plain")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Request failed: {response.text}"
        result = response.json()
        
        # Should fail with unsupported format error
        assert result["created"] == 0
        assert len(result["errors"]) > 0
        error_msg = result["errors"][0].get("error", "").lower()
        assert "unsupported" in error_msg or "format" in error_msg, f"Error should mention format: {result['errors']}"
        print(f"Unsupported format rejection: {result}")
    
    def test_bulk_upload_empty_rows_skipped(self, admin_token):
        """Empty rows in CSV should be skipped"""
        csv_content = """Job Link,Job Title,Company,Location,Salary,Description
https://example.com/job1,TEST_BulkUpload_EmptyRowTest,TEST_Co,Johannesburg,R50000,Valid job
,,,,,
,,,,,
https://example.com/job2,TEST_BulkUpload_EmptyRowTest2,TEST_Co,Cape Town,R45000,Another valid job"""
        
        files = {"file": ("test_empty_rows.csv", csv_content, "text/csv")}
        response = requests.post(
            f"{BASE_URL}/api/admin/jobs/bulk",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Bulk upload failed: {response.text}"
        result = response.json()
        
        # Empty rows should be skipped, not counted as failures
        # The 2 valid jobs should be created
        assert result["created"] >= 2, f"Expected at least 2 created, got {result['created']}"
        print(f"Empty rows handling: {result}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
