"""
JobRocket - Feature Access Service
Handles feature gating based on account tier and add-ons
"""

from typing import Optional, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.enums import TierId, FeatureId, AddonId, AccountRole
from models.tiers import (
    get_tier_config, get_addon_config, tier_has_feature,
    get_available_addons_for_tier, ADDON_CONFIG
)


class FeatureAccessService:
    """Service to check feature access based on account tier and add-ons"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_account_features(self, account_id: str) -> Tuple[List[FeatureId], List[AddonId]]:
        """
        Get all features available to an account (tier features + purchased add-ons)
        Returns: (features, active_addon_ids)
        """
        # Get account
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return [], []
        
        tier_id = TierId(account.get("tier_id", TierId.STARTER))
        tier_config = get_tier_config(tier_id)
        
        # Start with tier features
        features = list(tier_config.get("features", []))
        
        # Get active add-ons
        active_addons = []
        addons_cursor = self.db.account_addons.find({
            "account_id": account_id,
            "is_active": True
        })
        
        async for addon_doc in addons_cursor:
            addon_id = AddonId(addon_doc["addon_id"])
            active_addons.append(addon_id)
            
            # Add the feature this addon unlocks
            feature_id = addon_doc.get("feature_id")
            if feature_id and feature_id not in features:
                features.append(FeatureId(feature_id))
        
        return features, active_addons
    
    async def has_feature(self, account_id: str, feature_id: FeatureId) -> bool:
        """Check if an account has access to a specific feature"""
        features, _ = await self.get_account_features(account_id)
        return feature_id in features
    
    async def check_feature_access(
        self, 
        account_id: str, 
        feature_id: FeatureId
    ) -> Tuple[bool, Optional[str]]:
        """
        Check feature access with detailed response
        Returns: (has_access, error_message)
        """
        # Get account
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return False, "Account not found"
        
        # Check subscription status
        if account.get("subscription_status") not in ["active", "trial"]:
            return False, "Subscription is not active"
        
        # Check if feature is available
        features, _ = await self.get_account_features(account_id)
        if feature_id in features:
            return True, None
        
        # Feature not available - check if it can be purchased as add-on
        tier_id = TierId(account.get("tier_id", TierId.STARTER))
        available_addons = get_available_addons_for_tier(tier_id)
        
        # Find addon that provides this feature
        for addon in available_addons:
            if addon.get("feature_id") == feature_id:
                addon_name = addon.get("name", "an add-on")
                return False, f"This feature requires {addon_name}. You can purchase it from your account settings."
        
        # Feature not available at this tier
        return False, f"This feature is not available on your current plan. Please upgrade to access this feature."
    
    async def can_add_user(self, account_id: str) -> Tuple[bool, Optional[str]]:
        """Check if account can add another user"""
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return False, "Account not found"
        
        tier_id = TierId(account.get("tier_id", TierId.STARTER))
        tier_config = get_tier_config(tier_id)
        
        # Check multi-user access
        if not tier_config.get("multi_user_access", False):
            included_users = tier_config.get("included_users", 1)
            if account.get("current_user_count", 1) >= included_users:
                return False, f"Your plan only includes {included_users} user(s). Upgrade to Pro or Enterprise for multi-user access."
        
        # Check user limit
        included_users = tier_config.get("included_users", 1)
        extra_users = account.get("extra_users_count", 0)
        max_users = included_users + extra_users
        current_users = account.get("current_user_count", 1)
        
        if current_users >= max_users:
            extra_price = tier_config.get("extra_user_price", 899)
            return False, f"You've reached your user limit ({max_users}). You can add extra users at R{extra_price}/month each."
        
        return True, None
    
    async def get_user_permissions(
        self, 
        user_id: str, 
        account_id: str
    ) -> dict:
        """Get user's permissions within an account"""
        user = await self.db.users.find_one({"id": user_id})
        if not user or user.get("account_id") != account_id:
            return {"can_view": False, "can_edit": False, "can_manage": False, "can_admin": False}
        
        account_role = user.get("account_role", AccountRole.VIEWER)
        
        # Check if account has role-based permissions
        account = await self.db.accounts.find_one({"id": account_id})
        tier_id = TierId(account.get("tier_id", TierId.STARTER)) if account else TierId.STARTER
        has_rbac = tier_has_feature(tier_id, FeatureId.ACCOUNT_ROLE_BASED_PERMISSIONS)
        
        if not has_rbac:
            # Without RBAC, all users have full access
            return {
                "can_view": True,
                "can_edit": True,
                "can_manage": True,
                "can_admin": account_role == AccountRole.OWNER
            }
        
        # With RBAC, respect role hierarchy
        permissions = {
            AccountRole.OWNER: {"can_view": True, "can_edit": True, "can_manage": True, "can_admin": True},
            AccountRole.ADMIN: {"can_view": True, "can_edit": True, "can_manage": True, "can_admin": False},
            AccountRole.RECRUITER: {"can_view": True, "can_edit": True, "can_manage": False, "can_admin": False},
            AccountRole.VIEWER: {"can_view": True, "can_edit": False, "can_manage": False, "can_admin": False},
        }
        
        return permissions.get(AccountRole(account_role), permissions[AccountRole.VIEWER])
    
    async def get_available_addons(self, account_id: str) -> List[dict]:
        """Get add-ons available for purchase by this account"""
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return []
        
        tier_id = TierId(account.get("tier_id", TierId.STARTER))
        available = get_available_addons_for_tier(tier_id)
        
        # Get already purchased add-ons
        purchased_ids = set()
        addons_cursor = self.db.account_addons.find({
            "account_id": account_id,
            "is_active": True
        })
        async for addon_doc in addons_cursor:
            purchased_ids.add(addon_doc["addon_id"])
        
        # Filter out already purchased
        result = []
        for addon in available:
            addon_dict = dict(addon)
            addon_dict["is_purchased"] = addon["id"] in purchased_ids
            if not addon_dict["is_purchased"]:
                result.append(addon_dict)
        
        return result


def create_feature_service(db: AsyncIOMotorDatabase) -> FeatureAccessService:
    """Factory function to create feature access service"""
    return FeatureAccessService(db)
