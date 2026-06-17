"""
Test Admin AI Analytics Dashboard API
Tests the /api/admin/ai/analytics endpoint for:
- Admin access (should return comprehensive data)
- Job seeker access (should return 403)
- Recruiter access (should return 403)
- Unauthenticated access (should return 401)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_CREDS = {"email": "admin@jobrocket.co.za", "password": "admin123"}
JOB_SEEKER_CREDS = {"email": "thabo.mthembu@gmail.com", "password": "demo123"}
RECRUITER_CREDS = {"email": "hr@techcorp.co.za", "password": "demo123"}


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def job_seeker_token():
    """Get job seeker authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Job seeker login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def recruiter_token():
    """Get recruiter authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=RECRUITER_CREDS)
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Recruiter login failed: {response.status_code} - {response.text}")


class TestAdminAIAnalyticsAuth:
    """Test authentication and authorization for admin AI analytics endpoint"""

    def test_admin_ai_analytics_no_auth_returns_401_or_403(self):
        """Unauthenticated request should return 401 or 403 (access denied)"""
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics")
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
        print(f"PASSED: Unauthenticated request returns {response.status_code} (access denied)")

    def test_admin_ai_analytics_job_seeker_returns_403(self, job_seeker_token):
        """Job seeker should get 403 Forbidden"""
        headers = {"Authorization": f"Bearer {job_seeker_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASSED: Job seeker gets 403 Forbidden")

    def test_admin_ai_analytics_recruiter_returns_403(self, recruiter_token):
        """Recruiter should get 403 Forbidden"""
        headers = {"Authorization": f"Bearer {recruiter_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASSED: Recruiter gets 403 Forbidden")


class TestAdminAIAnalyticsData:
    """Test admin AI analytics data structure and content"""

    def test_admin_ai_analytics_returns_200(self, admin_token):
        """Admin should get 200 OK with comprehensive data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASSED: Admin gets 200 OK")

    def test_admin_ai_analytics_has_summary(self, admin_token):
        """Response should contain summary with revenue metrics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "summary" in data, "Response missing 'summary' field"
        summary = data["summary"]
        
        # Check all required summary fields
        required_fields = [
            "total_revenue", "total_refunds", "net_revenue", 
            "total_ai_actions", "unique_ai_users",
            "total_topups", "topup_count", "refund_count",
            "total_auto_topups", "auto_topup_count"
        ]
        for field in required_fields:
            assert field in summary, f"Summary missing '{field}' field"
        
        # Verify net_revenue calculation
        assert summary["net_revenue"] == summary["total_revenue"] - summary["total_refunds"], \
            "Net revenue calculation incorrect"
        
        print(f"PASSED: Summary contains all required fields")
        print(f"  - Net Revenue: R{summary['net_revenue']}")
        print(f"  - Total AI Actions: {summary['total_ai_actions']}")
        print(f"  - Unique AI Users: {summary['unique_ai_users']}")

    def test_admin_ai_analytics_has_revenue_by_feature(self, admin_token):
        """Response should contain revenue breakdown by AI feature"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "revenue_by_feature" in data, "Response missing 'revenue_by_feature' field"
        revenue_by_feature = data["revenue_by_feature"]
        
        # Check expected AI features
        expected_features = ["match_score", "top_matches", "auto_apply", "cv_enhance"]
        for feature in expected_features:
            assert feature in revenue_by_feature, f"Missing feature: {feature}"
            assert "total_revenue" in revenue_by_feature[feature], f"Feature {feature} missing total_revenue"
            assert "usage_count" in revenue_by_feature[feature], f"Feature {feature} missing usage_count"
        
        print(f"PASSED: Revenue by feature contains all 4 AI features")
        for feature in expected_features:
            stats = revenue_by_feature[feature]
            print(f"  - {feature}: R{stats['total_revenue']} ({stats['usage_count']} uses)")

    def test_admin_ai_analytics_has_daily_trend(self, admin_token):
        """Response should contain daily revenue trend data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "daily_trend" in data, "Response missing 'daily_trend' field"
        daily_trend = data["daily_trend"]
        
        # daily_trend is a list of date/revenue/actions objects
        assert isinstance(daily_trend, list), "daily_trend should be a list"
        
        if len(daily_trend) > 0:
            # Check structure of trend data
            first_entry = daily_trend[0]
            assert "date" in first_entry, "Trend entry missing 'date'"
            assert "revenue" in first_entry, "Trend entry missing 'revenue'"
            assert "actions" in first_entry, "Trend entry missing 'actions'"
        
        print(f"PASSED: Daily trend contains {len(daily_trend)} days of data")

    def test_admin_ai_analytics_has_top_users(self, admin_token):
        """Response should contain top AI users leaderboard"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "top_users" in data, "Response missing 'top_users' field"
        top_users = data["top_users"]
        
        assert isinstance(top_users, list), "top_users should be a list"
        
        if len(top_users) > 0:
            first_user = top_users[0]
            required_fields = ["user_id", "email", "name", "total_spent", "action_count"]
            for field in required_fields:
                assert field in first_user, f"Top user missing '{field}' field"
        
        print(f"PASSED: Top users contains {len(top_users)} users")
        for i, user in enumerate(top_users[:3]):
            print(f"  #{i+1}: {user['name']} - R{user['total_spent']} ({user['action_count']} actions)")

    def test_admin_ai_analytics_has_wallet_stats(self, admin_token):
        """Response should contain wallet statistics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "wallet_stats" in data, "Response missing 'wallet_stats' field"
        wallet_stats = data["wallet_stats"]
        
        required_fields = ["total_balance_held", "users_with_balance", "avg_balance"]
        for field in required_fields:
            assert field in wallet_stats, f"Wallet stats missing '{field}' field"
        
        print(f"PASSED: Wallet stats present")
        print(f"  - Total Balance Held: R{wallet_stats['total_balance_held']}")
        print(f"  - Users with Balance: {wallet_stats['users_with_balance']}")
        print(f"  - Avg Balance: R{wallet_stats['avg_balance']}")

    def test_admin_ai_analytics_has_auto_topup_stats(self, admin_token):
        """Response should contain auto top-up statistics"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "auto_topup_stats" in data, "Response missing 'auto_topup_stats' field"
        auto_topup_stats = data["auto_topup_stats"]
        
        required_fields = ["users_with_card", "users_auto_topup_enabled"]
        for field in required_fields:
            assert field in auto_topup_stats, f"Auto topup stats missing '{field}' field"
        
        print(f"PASSED: Auto top-up stats present")
        print(f"  - Users with Card: {auto_topup_stats['users_with_card']}")
        print(f"  - Auto Top-Up Enabled: {auto_topup_stats['users_auto_topup_enabled']}")

    def test_admin_ai_analytics_has_recent_transactions(self, admin_token):
        """Response should contain recent transactions table"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "recent_transactions" in data, "Response missing 'recent_transactions' field"
        recent_transactions = data["recent_transactions"]
        
        assert isinstance(recent_transactions, list), "recent_transactions should be a list"
        
        if len(recent_transactions) > 0:
            first_tx = recent_transactions[0]
            # Check for expected fields
            assert "action" in first_tx, "Transaction missing 'action' field"
            assert "user_id" in first_tx, "Transaction missing 'user_id' field"
            assert "user_name" in first_tx, "Transaction missing 'user_name' field"
        
        print(f"PASSED: Recent transactions contains {len(recent_transactions)} entries")

    def test_admin_ai_analytics_has_pricing(self, admin_token):
        """Response should contain current AI pricing"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/ai/analytics", headers=headers)
        data = response.json()
        
        assert "pricing" in data, "Response missing 'pricing' field"
        pricing = data["pricing"]
        
        # Check expected pricing keys
        expected_features = ["match_score", "top_matches", "auto_apply", "cv_enhance"]
        for feature in expected_features:
            assert feature in pricing, f"Pricing missing '{feature}'"
            assert isinstance(pricing[feature], (int, float)), f"Pricing for {feature} should be numeric"
        
        print(f"PASSED: Pricing present for all features")
        for feature in expected_features:
            print(f"  - {feature}: R{pricing[feature]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
