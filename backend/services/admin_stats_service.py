"""
JobRocket - Admin Stats Service
Handles caching and scheduled refresh of admin dashboard statistics
Stats are refreshed at 6am and 6pm SAST
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

# SAST is UTC+2
SAST_OFFSET = timedelta(hours=2)
REFRESH_HOURS = [6, 18]  # 6am and 6pm SAST


class AdminStatsService:
    """Service for admin dashboard statistics with caching"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._cache: Dict[str, Any] = {}
        self._last_refresh: Optional[datetime] = None
    
    async def get_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get admin stats from cache or refresh if needed.
        Stats are refreshed at 6am and 6pm SAST or on force_refresh.
        """
        if force_refresh or self._should_refresh():
            await self._refresh_stats()
        
        return self._cache
    
    def _should_refresh(self) -> bool:
        """Check if stats should be refreshed based on schedule"""
        if not self._last_refresh:
            return True
        
        now_utc = datetime.now(timezone.utc)
        now_sast = now_utc + SAST_OFFSET
        
        # Check if we've passed a refresh hour since last refresh
        last_refresh_sast = self._last_refresh + SAST_OFFSET
        
        for hour in REFRESH_HOURS:
            # Create datetime for this refresh hour today
            refresh_time_today = now_sast.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            
            # If refresh time is in the past today and after last refresh
            if refresh_time_today <= now_sast and refresh_time_today > last_refresh_sast:
                return True
        
        # Also refresh if cache is older than 12 hours (failsafe)
        if (now_utc - self._last_refresh).total_seconds() > 12 * 3600:
            return True
        
        return False
    
    async def _refresh_stats(self):
        """Refresh all statistics from database"""
        logger.info("Refreshing admin stats...")
        
        try:
            # Account stats
            total_accounts = await self.db.accounts.count_documents({})
            active_subscriptions = await self.db.accounts.count_documents({
                "subscription_status": {"$in": ["active", "trial"]}
            })
            
            # Tier distribution
            tier_distribution = {}
            for tier_id in ["starter", "growth", "pro", "enterprise"]:
                count = await self.db.accounts.count_documents({"tier_id": tier_id})
                tier_distribution[tier_id] = count
            
            # User stats
            total_users = await self.db.users.count_documents({})
            total_recruiters = await self.db.users.count_documents({"role": "recruiter"})
            total_job_seekers = await self.db.users.count_documents({"role": "job_seeker"})
            total_admins = await self.db.users.count_documents({"role": "admin"})
            
            # Job stats
            total_jobs = await self.db.jobs.count_documents({})
            active_jobs = await self.db.jobs.count_documents({
                "is_active": True,
                "expiry_date": {"$gt": datetime.utcnow()}
            })
            
            # Application stats
            total_applications = await self.db.job_applications.count_documents({})
            pending_applications = await self.db.job_applications.count_documents({
                "status": "pending"
            })
            
            # Payment stats
            total_payments = await self.db.payments.count_documents({
                "status": "completed"
            })
            
            # Calculate monthly revenue from active subscriptions
            monthly_revenue = 0
            tier_prices = {
                "starter": 6899,
                "growth": 10499,
                "pro": 19999,
                "enterprise": 39999
            }
            for tier_id, price in tier_prices.items():
                count = tier_distribution.get(tier_id, 0)
                monthly_revenue += count * price
            
            # Add-on revenue (from account_addons)
            active_addons = await self.db.account_addons.count_documents({"is_active": True})
            
            # Extra user seats revenue
            extra_users_pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$extra_users_count"}}}
            ]
            extra_users_result = await self.db.accounts.aggregate(extra_users_pipeline).to_list(1)
            total_extra_users = extra_users_result[0]["total"] if extra_users_result else 0
            monthly_revenue += total_extra_users * 899
            
            # Get recent accounts (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_accounts_30d = await self.db.accounts.count_documents({
                "created_at": {"$gte": thirty_days_ago}
            })
            
            # Get accounts list with details
            accounts_cursor = self.db.accounts.find({}).sort("created_at", -1).limit(100)
            accounts_list = []
            async for account in accounts_cursor:
                # Get owner info
                owner = await self.db.users.find_one({"id": account["owner_user_id"]})
                owner_email = owner["email"] if owner else "Unknown"
                
                # Get job count for this account
                job_count = await self.db.jobs.count_documents({"account_id": account["id"]})
                
                accounts_list.append({
                    "id": account["id"],
                    "name": account["name"],
                    "tier_id": account.get("tier_id", "starter"),
                    "tier_name": account.get("tier_id", "starter").capitalize(),
                    "subscription_status": account.get("subscription_status", "pending"),
                    "owner_email": owner_email,
                    "user_count": account.get("current_user_count", 1),
                    "job_count": job_count,
                    "created_at": account.get("created_at", datetime.utcnow()).isoformat()
                })
            
            # Update cache
            self._cache = {
                "summary": {
                    "total_accounts": total_accounts,
                    "active_subscriptions": active_subscriptions,
                    "total_users": total_users,
                    "total_recruiters": total_recruiters,
                    "total_job_seekers": total_job_seekers,
                    "total_admins": total_admins,
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "total_applications": total_applications,
                    "pending_applications": pending_applications,
                    "total_payments": total_payments,
                    "monthly_revenue": monthly_revenue,
                    "active_addons": active_addons,
                    "total_extra_users": total_extra_users,
                    "new_accounts_30d": new_accounts_30d
                },
                "tier_distribution": tier_distribution,
                "accounts": accounts_list,
                "last_refresh": datetime.utcnow().isoformat(),
                "next_refresh": self._get_next_refresh_time().isoformat()
            }
            
            self._last_refresh = datetime.now(timezone.utc)
            logger.info(f"Admin stats refreshed. Next refresh at {self._cache['next_refresh']}")
            
        except Exception as e:
            logger.error(f"Error refreshing admin stats: {e}")
            # Keep old cache if refresh fails
            if not self._cache:
                self._cache = {
                    "summary": {},
                    "tier_distribution": {},
                    "accounts": [],
                    "last_refresh": None,
                    "next_refresh": None,
                    "error": str(e)
                }
    
    def _get_next_refresh_time(self) -> datetime:
        """Calculate next scheduled refresh time"""
        now_utc = datetime.now(timezone.utc)
        now_sast = now_utc + SAST_OFFSET
        
        # Find next refresh hour
        for hour in sorted(REFRESH_HOURS):
            next_time = now_sast.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time > now_sast:
                return next_time - SAST_OFFSET  # Return in UTC
        
        # If all today's times passed, use first time tomorrow
        tomorrow = now_sast + timedelta(days=1)
        next_time = tomorrow.replace(hour=REFRESH_HOURS[0], minute=0, second=0, microsecond=0)
        return next_time - SAST_OFFSET


def create_admin_stats_service(db: AsyncIOMotorDatabase) -> AdminStatsService:
    """Factory function to create admin stats service"""
    return AdminStatsService(db)
