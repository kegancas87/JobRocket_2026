"""
JobRocket - Account Service
Handles account creation, management, and subscription operations
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.enums import (
    TierId, SubscriptionStatus, BillingCycle, 
    AccountRole, UserRole, InvitationStatus
)
from models.schemas import Account, User, TeamInvitation
from models.tiers import get_tier_config


class AccountService:
    """Service for account management operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_account_for_user(
        self,
        user_id: str,
        company_name: str,
        tier_id: TierId = TierId.STARTER
    ) -> Account:
        """
        Create a new account when a recruiter signs up.
        The user becomes the account owner.
        """
        tier_config = get_tier_config(tier_id)
        
        account = Account(
            name=company_name,
            owner_user_id=user_id,
            tier_id=tier_id,
            subscription_status=SubscriptionStatus.PENDING,  # Pending until payment
            current_user_count=1,
        )
        
        # Insert account
        await self.db.accounts.insert_one(account.dict())
        
        # Update user with account reference
        await self.db.users.update_one(
            {"id": user_id},
            {"$set": {
                "account_id": account.id,
                "account_role": AccountRole.OWNER,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return account
    
    async def get_account(self, account_id: str) -> Optional[dict]:
        """Get account by ID"""
        account = await self.db.accounts.find_one({"id": account_id})
        if account and "_id" in account:
            del account["_id"]
        return account
    
    async def get_account_by_owner(self, owner_user_id: str) -> Optional[dict]:
        """Get account by owner user ID"""
        account = await self.db.accounts.find_one({"owner_user_id": owner_user_id})
        if account and "_id" in account:
            del account["_id"]
        return account
    
    async def update_account(
        self, 
        account_id: str, 
        update_data: dict
    ) -> Optional[dict]:
        """Update account details"""
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": update_data}
        )
        
        return await self.get_account(account_id)
    
    async def activate_subscription(
        self,
        account_id: str,
        tier_id: TierId,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ) -> Optional[dict]:
        """Activate or upgrade subscription after payment"""
        now = datetime.utcnow()
        
        if billing_cycle == BillingCycle.MONTHLY:
            end_date = now + timedelta(days=30)
        else:
            end_date = now + timedelta(days=365)
        
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": {
                "tier_id": tier_id,
                "subscription_status": SubscriptionStatus.ACTIVE,
                "subscription_start_date": now,
                "subscription_end_date": end_date,
                "billing_cycle": billing_cycle,
                "updated_at": now
            }}
        )
        
        return await self.get_account(account_id)
    
    async def cancel_subscription(self, account_id: str) -> Optional[dict]:
        """Cancel subscription (will expire at end of billing period)"""
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": {
                "subscription_status": SubscriptionStatus.CANCELLED,
                "updated_at": datetime.utcnow()
            }}
        )
        return await self.get_account(account_id)
    
    async def get_account_users(self, account_id: str) -> list:
        """Get all users belonging to an account"""
        users = []
        cursor = self.db.users.find({"account_id": account_id})
        async for user in cursor:
            if "_id" in user:
                del user["_id"]
            # Remove sensitive data
            if "password_hash" in user:
                del user["password_hash"]
            users.append(user)
        return users
    
    async def add_user_to_account(
        self,
        account_id: str,
        user_id: str,
        account_role: AccountRole = AccountRole.RECRUITER
    ) -> Tuple[bool, Optional[str]]:
        """Add a user to an account"""
        account = await self.get_account(account_id)
        if not account:
            return False, "Account not found"
        
        tier_config = get_tier_config(TierId(account["tier_id"]))
        included_users = tier_config.get("included_users", 1)
        extra_users = account.get("extra_users_count", 0)
        max_users = included_users + extra_users
        current_users = account.get("current_user_count", 1)
        
        if current_users >= max_users:
            return False, f"User limit reached ({max_users}). Purchase additional user seats."
        
        # Update user
        await self.db.users.update_one(
            {"id": user_id},
            {"$set": {
                "account_id": account_id,
                "account_role": account_role,
                "role": UserRole.RECRUITER,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Increment user count
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$inc": {"current_user_count": 1}}
        )
        
        return True, None
    
    async def remove_user_from_account(
        self,
        account_id: str,
        user_id: str,
        requesting_user_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Remove a user from an account"""
        account = await self.get_account(account_id)
        if not account:
            return False, "Account not found"
        
        # Can't remove the owner
        if account["owner_user_id"] == user_id:
            return False, "Cannot remove the account owner"
        
        # Check permission (only owner/admin can remove)
        requesting_user = await self.db.users.find_one({"id": requesting_user_id})
        if not requesting_user:
            return False, "Requesting user not found"
        
        req_role = requesting_user.get("account_role")
        if req_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
            return False, "Permission denied"
        
        # Remove user from account
        await self.db.users.update_one(
            {"id": user_id},
            {"$set": {
                "account_id": None,
                "account_role": None,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Decrement user count
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$inc": {"current_user_count": -1}}
        )
        
        return True, None
    
    async def add_extra_user_seats(
        self,
        account_id: str,
        seats: int = 1
    ) -> Optional[dict]:
        """Add extra user seats to account (after payment)"""
        await self.db.accounts.update_one(
            {"id": account_id},
            {
                "$inc": {"extra_users_count": seats},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return await self.get_account(account_id)
    
    async def create_invitation(
        self,
        account_id: str,
        inviter_user_id: str,
        email: str,
        first_name: str,
        last_name: str,
        account_role: AccountRole = AccountRole.RECRUITER
    ) -> Tuple[Optional[TeamInvitation], Optional[str]]:
        """Create a team invitation"""
        # Check if email already has pending invitation
        existing = await self.db.team_invitations.find_one({
            "account_id": account_id,
            "email": email,
            "status": InvitationStatus.PENDING
        })
        if existing:
            return None, "An invitation is already pending for this email"
        
        # Check if user already exists in account
        existing_user = await self.db.users.find_one({
            "email": email,
            "account_id": account_id
        })
        if existing_user:
            return None, "User is already a member of this account"
        
        invitation = TeamInvitation(
            account_id=account_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            account_role=account_role,
            invited_by=inviter_user_id
        )
        
        await self.db.team_invitations.insert_one(invitation.dict())
        
        return invitation, None
    
    async def get_pending_invitations(self, account_id: str) -> list:
        """Get all pending invitations for an account"""
        invitations = []
        cursor = self.db.team_invitations.find({
            "account_id": account_id,
            "status": InvitationStatus.PENDING
        })
        async for inv in cursor:
            if "_id" in inv:
                del inv["_id"]
            invitations.append(inv)
        return invitations
    
    async def accept_invitation(
        self,
        invitation_token: str,
        user_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Accept a team invitation"""
        invitation = await self.db.team_invitations.find_one({
            "invitation_token": invitation_token,
            "status": InvitationStatus.PENDING
        })
        
        if not invitation:
            return False, "Invitation not found or expired"
        
        if datetime.utcnow() > invitation["expires_at"]:
            await self.db.team_invitations.update_one(
                {"id": invitation["id"]},
                {"$set": {"status": InvitationStatus.EXPIRED}}
            )
            return False, "Invitation has expired"
        
        # Add user to account
        success, error = await self.add_user_to_account(
            invitation["account_id"],
            user_id,
            AccountRole(invitation["account_role"])
        )
        
        if not success:
            return False, error
        
        # Mark invitation as accepted
        await self.db.team_invitations.update_one(
            {"id": invitation["id"]},
            {"$set": {"status": InvitationStatus.ACCEPTED}}
        )
        
        return True, None


def create_account_service(db: AsyncIOMotorDatabase) -> AccountService:
    """Factory function to create account service"""
    return AccountService(db)
