"""
Test Admin Account Management Feature - Iteration 6
Tests: Admin Account Management at /manage-accounts
Endpoints:
- GET /api/admin/accounts/{id} - Get account details
- PUT /api/admin/accounts/{id}/tier - Change subscription tier
- POST /api/admin/accounts/{id}/addon - Grant add-on
- DELETE /api/admin/accounts/{id}/addon/{purchase_id} - Revoke add-on
- POST /api/admin/accounts/{id}/seats - Add seats
- POST /api/admin/accounts/{id}/credits - Add credits
- GET /api/admin/accounts/{id}/audit-log - Get audit log
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@jobrocket.co.za"
ADMIN_PASSWORD = "admin123"
RECRUITER_EMAIL = "careers@fintechsa.co.za"
RECRUITER_PASSWORD = "demo123"

# Test account IDs
STARTER_ACCOUNT_ID = "a91d2838-5931-44cc-b9cf-d72e6894fa1c"  # TechCorp SA Updated
ENTERPRISE_ACCOUNT_ID = "9a4b2095-49df-425b-a476-6b0098339113"  # Global Recruitment Agency

class TestSetup:
    """Test fixtures and setup"""
    
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
        """Get recruiter authentication token (non-admin)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        assert response.status_code == 200, f"Recruiter login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture
    def admin_headers(self, admin_token):
        """Admin auth headers"""
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def recruiter_headers(self, recruiter_token):
        """Recruiter (non-admin) auth headers"""
        return {"Authorization": f"Bearer {recruiter_token}", "Content-Type": "application/json"}


class TestAdminAccountDetail(TestSetup):
    """Test GET /api/admin/accounts/{id} - Admin get account details"""
    
    def test_admin_get_account_detail_success(self, admin_headers):
        """Admin can get detailed account info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        # Verify essential fields returned
        assert "id" in data
        assert data["id"] == STARTER_ACCOUNT_ID
        assert "name" in data
        assert "tier_id" in data
        assert "tier_name" in data
        assert "tier_price" in data
        assert "owner" in data
        assert "job_count" in data
        assert "active_addons" in data
        assert "credit_balance" in data
        assert "audit_log" in data
        print(f"✓ Admin got account detail: {data['name']} ({data['tier_id']})")
    
    def test_non_admin_cannot_get_account_detail(self, recruiter_headers):
        """Non-admin user cannot access admin account detail endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=recruiter_headers
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ Non-admin correctly denied access to account detail")
    
    def test_admin_get_nonexistent_account(self, admin_headers):
        """Admin gets 404 for nonexistent account"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{fake_id}",
            headers=admin_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Nonexistent account returns 404")


class TestAdminChangeTier(TestSetup):
    """Test PUT /api/admin/accounts/{id}/tier - Admin change subscription tier"""
    
    def test_admin_change_tier_to_growth(self, admin_headers):
        """Admin can change account tier from starter to growth"""
        response = requests.put(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/tier",
            headers=admin_headers,
            json={"tier_id": "growth", "reason": "Test upgrade"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert data.get("tier_id") == "growth"
        print(f"✓ Tier changed to growth: {data.get('message')}")
    
    def test_tier_change_logged_in_audit(self, admin_headers):
        """Verify tier change is logged in audit trail"""
        # Get account detail which includes audit log
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        audit_log = data.get("audit_log", [])
        assert len(audit_log) > 0, "Audit log should have entries"
        
        # Check latest entry is tier_change
        latest = audit_log[0]
        assert latest.get("action") == "tier_change", f"Expected tier_change, got {latest.get('action')}"
        assert "tier" in str(latest.get("details", {})).lower()
        print(f"✓ Tier change logged in audit: {latest}")
    
    def test_admin_revert_tier_to_starter(self, admin_headers):
        """Admin reverts account tier back to starter (cleanup)"""
        response = requests.put(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/tier",
            headers=admin_headers,
            json={"tier_id": "starter", "reason": "Test revert"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("tier_id") == "starter"
        print(f"✓ Tier reverted to starter: {data.get('message')}")
    
    def test_admin_change_tier_invalid_tier(self, admin_headers):
        """Admin cannot change to invalid tier"""
        response = requests.put(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/tier",
            headers=admin_headers,
            json={"tier_id": "invalid_tier"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid tier ID rejected with 400")
    
    def test_non_admin_cannot_change_tier(self, recruiter_headers):
        """Non-admin user cannot change tier"""
        response = requests.put(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/tier",
            headers=recruiter_headers,
            json={"tier_id": "growth"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied tier change access")


class TestAdminGrantAddon(TestSetup):
    """Test POST /api/admin/accounts/{id}/addon - Admin grant add-on"""
    
    granted_addon_id = None  # Store for revoke test
    
    def test_admin_grant_addon(self, admin_headers):
        """Admin can grant an add-on feature for free"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon",
            headers=admin_headers,
            json={"addon_id": "addon_candidate_notes", "reason": "Test grant"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "addon_id" in data
        print(f"✓ Add-on granted: {data}")
    
    def test_addon_grant_logged_in_audit(self, admin_headers):
        """Verify addon grant is logged in audit trail"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        audit_log = data.get("audit_log", [])
        
        # Find addon_grant entry
        addon_logs = [log for log in audit_log if log.get("action") == "addon_grant"]
        assert len(addon_logs) > 0, "Should have addon_grant in audit log"
        print(f"✓ Add-on grant logged in audit: {addon_logs[0]}")
        
        # Store addon id from active_addons for revoke test
        active_addons = data.get("active_addons", [])
        candidate_notes = [a for a in active_addons if a.get("addon_id") == "addon_candidate_notes"]
        if candidate_notes:
            TestAdminGrantAddon.granted_addon_id = candidate_notes[0].get("id")
    
    def test_admin_grant_duplicate_addon_fails(self, admin_headers):
        """Admin cannot grant same add-on twice"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon",
            headers=admin_headers,
            json={"addon_id": "addon_candidate_notes", "reason": "Duplicate test"}
        )
        assert response.status_code == 400, f"Expected 400 for duplicate, got {response.status_code}"
        print("✓ Duplicate add-on grant correctly rejected")
    
    def test_admin_grant_invalid_addon(self, admin_headers):
        """Admin cannot grant invalid add-on"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon",
            headers=admin_headers,
            json={"addon_id": "invalid_addon_id"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid add-on ID rejected")
    
    def test_non_admin_cannot_grant_addon(self, recruiter_headers):
        """Non-admin user cannot grant add-on"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon",
            headers=recruiter_headers,
            json={"addon_id": "addon_talent_alerts"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied add-on grant access")


class TestAdminRevokeAddon(TestSetup):
    """Test DELETE /api/admin/accounts/{id}/addon/{purchase_id} - Admin revoke add-on"""
    
    def test_admin_revoke_addon(self, admin_headers):
        """Admin can revoke an add-on from account"""
        # First get the addon id from the previously granted addon
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        active_addons = response.json().get("active_addons", [])
        candidate_notes = [a for a in active_addons if a.get("addon_id") == "addon_candidate_notes"]
        
        if not candidate_notes:
            pytest.skip("No addon to revoke - previous grant test may have failed")
        
        addon_purchase_id = candidate_notes[0].get("id")
        
        # Revoke the addon
        response = requests.delete(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon/{addon_purchase_id}",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Add-on revoked: {data}")
    
    def test_addon_revoke_logged_in_audit(self, admin_headers):
        """Verify addon revoke is logged in audit trail"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        audit_log = data.get("audit_log", [])
        
        # Find addon_revoke entry
        revoke_logs = [log for log in audit_log if log.get("action") == "addon_revoke"]
        assert len(revoke_logs) > 0, "Should have addon_revoke in audit log"
        print(f"✓ Add-on revoke logged in audit: {revoke_logs[0]}")
    
    def test_admin_revoke_nonexistent_addon(self, admin_headers):
        """Admin gets 404 for revoking nonexistent addon"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon/{fake_id}",
            headers=admin_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Nonexistent add-on revoke returns 404")
    
    def test_non_admin_cannot_revoke_addon(self, recruiter_headers):
        """Non-admin user cannot revoke add-on"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/addon/{fake_id}",
            headers=recruiter_headers
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied add-on revoke access")


class TestAdminAddSeats(TestSetup):
    """Test POST /api/admin/accounts/{id}/seats - Admin add extra seats"""
    
    def test_admin_add_seats(self, admin_headers):
        """Admin can add extra user seats for free"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/seats",
            headers=admin_headers,
            json={"quantity": 2, "reason": "Test seats"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "total_extra_seats" in data
        print(f"✓ Seats added: {data}")
    
    def test_seats_logged_in_audit(self, admin_headers):
        """Verify seats added is logged in audit trail"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        audit_log = data.get("audit_log", [])
        
        # Find seats_added entry
        seats_logs = [log for log in audit_log if log.get("action") == "seats_added"]
        assert len(seats_logs) > 0, "Should have seats_added in audit log"
        print(f"✓ Seats added logged in audit: {seats_logs[0]}")
    
    def test_admin_add_seats_invalid_quantity(self, admin_headers):
        """Admin cannot add invalid seat quantity"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/seats",
            headers=admin_headers,
            json={"quantity": -1}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid seat quantity rejected")
    
    def test_non_admin_cannot_add_seats(self, recruiter_headers):
        """Non-admin user cannot add seats"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/seats",
            headers=recruiter_headers,
            json={"quantity": 1}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied seats add access")


class TestAdminAddCredits(TestSetup):
    """Test POST /api/admin/accounts/{id}/credits - Admin add credit balance"""
    
    def test_admin_add_credits(self, admin_headers):
        """Admin can add credit balance to account"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/credits",
            headers=admin_headers,
            json={"amount": 1000, "reason": "Test credits"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "credit_balance" in data
        assert data.get("credit_balance") >= 1000  # At least the amount we added
        print(f"✓ Credits added: {data}")
    
    def test_credit_balance_reflected_in_account(self, admin_headers):
        """Verify credit balance shows in account detail"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        credit_balance = data.get("credit_balance", 0)
        assert credit_balance >= 1000, f"Credit balance should be at least 1000, got {credit_balance}"
        print(f"✓ Credit balance reflected in account: R{credit_balance}")
    
    def test_credits_logged_in_audit(self, admin_headers):
        """Verify credits added is logged in audit trail"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}",
            headers=admin_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        audit_log = data.get("audit_log", [])
        
        # Find credit_added entry
        credit_logs = [log for log in audit_log if log.get("action") == "credit_added"]
        assert len(credit_logs) > 0, "Should have credit_added in audit log"
        print(f"✓ Credit added logged in audit: {credit_logs[0]}")
    
    def test_admin_add_credits_invalid_amount(self, admin_headers):
        """Admin cannot add invalid credit amount"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/credits",
            headers=admin_headers,
            json={"amount": -100}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid credit amount rejected")
    
    def test_non_admin_cannot_add_credits(self, recruiter_headers):
        """Non-admin user cannot add credits"""
        response = requests.post(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/credits",
            headers=recruiter_headers,
            json={"amount": 500}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied credits add access")


class TestAdminAuditLog(TestSetup):
    """Test GET /api/admin/accounts/{id}/audit-log - Admin audit log"""
    
    def test_admin_get_audit_log(self, admin_headers):
        """Admin can get audit log for account"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/audit-log",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "logs" in data
        logs = data.get("logs", [])
        
        # Should have logs from previous tests
        assert len(logs) > 0, "Audit log should have entries from previous tests"
        
        # Verify log structure
        if logs:
            log = logs[0]
            assert "id" in log
            assert "account_id" in log
            assert "action" in log
            assert "created_at" in log
        
        print(f"✓ Audit log retrieved: {len(logs)} entries")
    
    def test_non_admin_cannot_get_audit_log(self, recruiter_headers):
        """Non-admin user cannot access audit log"""
        response = requests.get(
            f"{BASE_URL}/api/admin/accounts/{STARTER_ACCOUNT_ID}/audit-log",
            headers=recruiter_headers
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied audit log access")


class TestAdminStatsAccountsList(TestSetup):
    """Test /api/admin/stats endpoint returns accounts list for /manage-accounts"""
    
    def test_admin_stats_returns_accounts(self, admin_headers):
        """Admin stats endpoint returns accounts list with required fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats?force_refresh=true",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "accounts" in data, "Response should contain 'accounts' list"
        
        accounts = data.get("accounts", [])
        assert len(accounts) >= 4, f"Should have at least 4 accounts, got {len(accounts)}"
        
        # Verify account structure
        if accounts:
            acc = accounts[0]
            assert "id" in acc
            assert "name" in acc
            assert "tier_id" in acc
            # owner_email is also needed for search
            if "owner_email" in acc:
                print(f"✓ Account has owner_email for search")
        
        print(f"✓ Admin stats returned {len(accounts)} accounts with tier badges")
    
    def test_non_admin_cannot_get_admin_stats(self, recruiter_headers):
        """Non-admin user cannot access admin stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=recruiter_headers
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly denied admin stats access")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
