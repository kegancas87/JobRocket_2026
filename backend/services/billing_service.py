"""
JobRocket - Billing Service
Handles subscriptions, add-ons, extra user seats, and billing history
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.enums import (
    TierId, AddonId, FeatureId,
    PaymentStatus, PaymentProvider,
    SubscriptionStatus, BillingCycle
)
from models.tiers import get_tier_config, get_addon_config, TIER_CONFIG, ADDON_CONFIG

logger = logging.getLogger(__name__)


class BillingService:
    """Service for all billing-related operations"""
    
    EXTRA_USER_PRICE = 899  # R899/user/month
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # ==========================================
    # Billing History
    # ==========================================
    
    async def get_billing_history(
        self,
        account_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Get billing/payment history for an account"""
        cursor = self.db.payments.find(
            {"account_id": account_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        history = []
        async for payment in cursor:
            if "_id" in payment:
                del payment["_id"]
            
            # Enrich with readable info
            payment["tier_name"] = None
            payment["addon_name"] = None
            
            if payment.get("tier_id"):
                tier = get_tier_config(TierId(payment["tier_id"]))
                payment["tier_name"] = tier["name"]
            
            if payment.get("addon_id"):
                addon = get_addon_config(AddonId(payment["addon_id"]))
                if addon:
                    payment["addon_name"] = addon["name"]
            
            history.append(payment)
        
        return history
    
    async def get_billing_summary(self, account_id: str) -> Dict[str, Any]:
        """Get billing summary for an account"""
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return {}
        
        tier_config = get_tier_config(TierId(account.get("tier_id", "starter")))
        
        # Calculate current monthly charges
        base_subscription = tier_config["price_monthly"]
        extra_users = account.get("extra_users_count", 0)
        extra_users_charge = extra_users * self.EXTRA_USER_PRICE
        
        # Get active add-ons
        active_addons = []
        addons_charge = 0
        cursor = self.db.account_addons.find({
            "account_id": account_id,
            "is_active": True
        })
        async for addon_doc in cursor:
            addon_config = get_addon_config(AddonId(addon_doc["addon_id"]))
            if addon_config:
                active_addons.append({
                    "id": addon_doc["id"],
                    "addon_id": addon_doc["addon_id"],
                    "name": addon_config["name"],
                    "price": addon_config.get("price_monthly") or addon_config.get("price_once", 0),
                    "is_recurring": addon_config.get("is_recurring", True),
                    "purchased_date": addon_doc.get("purchased_date"),
                    "expires_date": addon_doc.get("expires_date")
                })
                if addon_config.get("is_recurring"):
                    addons_charge += addon_config.get("price_monthly", 0)
        
        # Get extra user seats
        extra_seats = []
        cursor = self.db.user_seats.find({
            "account_id": account_id,
            "is_active": True
        })
        async for seat in cursor:
            if "_id" in seat:
                del seat["_id"]
            extra_seats.append(seat)
        
        total_monthly = base_subscription + extra_users_charge + addons_charge
        
        return {
            "account_id": account_id,
            "tier_id": account.get("tier_id"),
            "tier_name": tier_config["name"],
            "subscription_status": account.get("subscription_status"),
            "billing_cycle": account.get("billing_cycle", "monthly"),
            "subscription_start_date": account.get("subscription_start_date"),
            "subscription_end_date": account.get("subscription_end_date"),
            "charges": {
                "base_subscription": base_subscription,
                "extra_users_count": extra_users,
                "extra_users_charge": extra_users_charge,
                "active_addons_count": len(active_addons),
                "addons_charge": addons_charge,
                "total_monthly": total_monthly
            },
            "included_users": tier_config["included_users"],
            "current_users": account.get("current_user_count", 1),
            "max_users": tier_config["included_users"] + extra_users,
            "active_addons": active_addons,
            "extra_seats": extra_seats
        }
    
    # ==========================================
    # Subscription Management
    # ==========================================
    
    async def upgrade_subscription(
        self,
        account_id: str,
        new_tier_id: TierId,
        payment_id: str
    ) -> Dict[str, Any]:
        """Upgrade account subscription after payment"""
        tier_config = get_tier_config(new_tier_id)
        
        now = datetime.utcnow()
        end_date = now + timedelta(days=30)
        
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": {
                "tier_id": new_tier_id.value,
                "subscription_status": SubscriptionStatus.ACTIVE.value,
                "subscription_start_date": now,
                "subscription_end_date": end_date,
                "updated_at": now
            }}
        )
        
        return {
            "success": True,
            "tier_id": new_tier_id.value,
            "tier_name": tier_config["name"],
            "subscription_end_date": end_date.isoformat()
        }
    
    async def cancel_subscription(
        self,
        account_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Cancel subscription (remains active until end of billing period)"""
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return {"success": False, "error": "Account not found"}
        
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": {
                "subscription_status": SubscriptionStatus.CANCELLED.value,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Log cancellation
        await self.db.billing_events.insert_one({
            "id": str(uuid.uuid4()),
            "account_id": account_id,
            "user_id": user_id,
            "event_type": "subscription_cancelled",
            "details": {
                "tier_id": account.get("tier_id"),
                "effective_until": account.get("subscription_end_date")
            },
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": "Subscription cancelled. Access continues until end of billing period.",
            "effective_until": account.get("subscription_end_date")
        }
    
    # ==========================================
    # Add-on Management
    # ==========================================
    
    async def purchase_addon(
        self,
        account_id: str,
        addon_id: AddonId,
        payment_id: str,
        price_paid: float
    ) -> Dict[str, Any]:
        """Activate add-on after payment"""
        addon_config = get_addon_config(addon_id)
        if not addon_config:
            return {"success": False, "error": "Invalid add-on"}
        
        now = datetime.utcnow()
        expires_date = None
        if addon_config.get("is_recurring"):
            expires_date = now + timedelta(days=30)
        
        addon_doc = {
            "id": str(uuid.uuid4()),
            "account_id": account_id,
            "addon_id": addon_id.value,
            "feature_id": addon_config["feature_id"].value,
            "purchased_date": now,
            "expires_date": expires_date,
            "is_active": True,
            "price_paid": price_paid,
            "payment_id": payment_id
        }
        
        await self.db.account_addons.insert_one(addon_doc)
        
        return {
            "success": True,
            "addon_id": addon_id.value,
            "addon_name": addon_config["name"],
            "feature_id": addon_config["feature_id"].value,
            "expires_date": expires_date.isoformat() if expires_date else None
        }
    
    async def cancel_addon(
        self,
        account_id: str,
        addon_purchase_id: str
    ) -> Dict[str, Any]:
        """Cancel an add-on subscription"""
        addon = await self.db.account_addons.find_one({
            "id": addon_purchase_id,
            "account_id": account_id,
            "is_active": True
        })
        
        if not addon:
            return {"success": False, "error": "Add-on not found or already cancelled"}
        
        await self.db.account_addons.update_one(
            {"id": addon_purchase_id},
            {"$set": {
                "is_active": False,
                "cancelled_at": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Add-on cancelled. Feature access continues until expiry.",
            "expires_date": addon.get("expires_date")
        }
    
    async def get_active_addons(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all active add-ons for an account"""
        addons = []
        cursor = self.db.account_addons.find({
            "account_id": account_id,
            "is_active": True
        })
        
        async for addon_doc in cursor:
            if "_id" in addon_doc:
                del addon_doc["_id"]
            
            addon_config = get_addon_config(AddonId(addon_doc["addon_id"]))
            if addon_config:
                addon_doc["name"] = addon_config["name"]
                addon_doc["description"] = addon_config["description"]
            
            addons.append(addon_doc)
        
        return addons
    
    # ==========================================
    # Extra User Seats
    # ==========================================
    
    async def purchase_extra_seats(
        self,
        account_id: str,
        quantity: int,
        payment_id: str
    ) -> Dict[str, Any]:
        """Add extra user seats after payment"""
        now = datetime.utcnow()
        
        # Create seat records
        seats_created = []
        for _ in range(quantity):
            seat_doc = {
                "id": str(uuid.uuid4()),
                "account_id": account_id,
                "purchased_date": now,
                "expires_date": now + timedelta(days=30),
                "is_active": True,
                "price_paid": self.EXTRA_USER_PRICE,
                "payment_id": payment_id
            }
            await self.db.user_seats.insert_one(seat_doc)
            seats_created.append(seat_doc["id"])
        
        # Update account's extra user count
        await self.db.accounts.update_one(
            {"id": account_id},
            {
                "$inc": {"extra_users_count": quantity},
                "$set": {"updated_at": now}
            }
        )
        
        return {
            "success": True,
            "quantity": quantity,
            "total_price": quantity * self.EXTRA_USER_PRICE,
            "seat_ids": seats_created
        }
    
    async def cancel_extra_seat(
        self,
        account_id: str,
        seat_id: str
    ) -> Dict[str, Any]:
        """Cancel an extra user seat (effective at end of billing cycle)"""
        seat = await self.db.user_seats.find_one({
            "id": seat_id,
            "account_id": account_id,
            "is_active": True
        })
        
        if not seat:
            return {"success": False, "error": "Seat not found or already cancelled"}
        
        # Mark as cancelled but keep active until expiry
        await self.db.user_seats.update_one(
            {"id": seat_id},
            {"$set": {
                "cancelled_at": datetime.utcnow(),
                "auto_renew": False
            }}
        )
        
        return {
            "success": True,
            "message": "Seat cancelled. Will be removed after billing cycle ends.",
            "expires_date": seat.get("expires_date")
        }
    
    async def get_extra_seats(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all extra user seats for an account"""
        seats = []
        cursor = self.db.user_seats.find({"account_id": account_id})
        
        async for seat in cursor:
            if "_id" in seat:
                del seat["_id"]
            seats.append(seat)
        
        return seats
    
    # ==========================================
    # Payment Creation Helpers
    # ==========================================
    
    async def create_payment_record(
        self,
        account_id: str,
        user_id: str,
        payment_type: str,
        amount: float,
        tier_id: Optional[TierId] = None,
        addon_id: Optional[AddonId] = None,
        extra_seats: int = 0
    ) -> Dict[str, Any]:
        """Create a payment record"""
        payment_doc = {
            "id": str(uuid.uuid4()),
            "account_id": account_id,
            "user_id": user_id,
            "payment_type": payment_type,
            "tier_id": tier_id.value if tier_id else None,
            "addon_id": addon_id.value if addon_id else None,
            "extra_seats": extra_seats,
            "amount": amount,
            "discount_code": None,
            "discount_amount": 0,
            "final_amount": amount,
            "currency": "ZAR",
            "provider": PaymentProvider.PAYFAST.value,
            "status": PaymentStatus.PENDING.value,
            "created_at": datetime.utcnow()
        }
        
        await self.db.payments.insert_one(payment_doc)
        
        if "_id" in payment_doc:
            del payment_doc["_id"]
        
        return payment_doc
    
    async def complete_payment(
        self,
        payment_id: str,
        provider_reference: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Mark payment as completed and activate purchased item"""
        payment = await self.db.payments.find_one({"id": payment_id})
        if not payment:
            return False, None
        
        if payment["status"] != PaymentStatus.PENDING.value:
            return False, None
        
        # Update payment status
        await self.db.payments.update_one(
            {"id": payment_id},
            {"$set": {
                "status": PaymentStatus.COMPLETED.value,
                "provider_reference": provider_reference,
                "completed_at": datetime.utcnow()
            }}
        )
        
        # Activate the purchased item
        result = {}
        
        if payment.get("tier_id"):
            # Subscription payment
            result = await self.upgrade_subscription(
                payment["account_id"],
                TierId(payment["tier_id"]),
                payment_id
            )
        
        elif payment.get("addon_id"):
            # Add-on payment
            result = await self.purchase_addon(
                payment["account_id"],
                AddonId(payment["addon_id"]),
                payment_id,
                payment["final_amount"]
            )
        
        elif payment.get("extra_seats"):
            # Extra seats payment
            result = await self.purchase_extra_seats(
                payment["account_id"],
                payment["extra_seats"],
                payment_id
            )
        
        return True, result
    
    async def fail_payment(
        self,
        payment_id: str,
        reason: str
    ):
        """Mark payment as failed"""
        await self.db.payments.update_one(
            {"id": payment_id},
            {"$set": {
                "status": PaymentStatus.FAILED.value,
                "failure_reason": reason,
                "failed_at": datetime.utcnow()
            }}
        )


def create_billing_service(db: AsyncIOMotorDatabase) -> BillingService:
    """Factory function to create billing service"""
    return BillingService(db)
