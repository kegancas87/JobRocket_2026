"""
JobRocket - PayFast Subscription Service
Handles subscription billing, payment tracking, retries, and account status management
With support for:
- Recurring subscription billing via PayFast
- 7-day grace period with daily payment checks
- Pro-rata calculations for mid-cycle additions
- Account-level billing date tracking
"""

import os
import uuid
import hashlib
import urllib.parse
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.enums import TierId, SubscriptionStatus, PaymentStatus
from models.tiers import get_tier_config, TIER_CONFIG

logger = logging.getLogger(__name__)

# PayFast Configuration
PAYFAST_MERCHANT_ID = os.environ.get("PAYFAST_MERCHANT_ID", "10000100")
PAYFAST_MERCHANT_KEY = os.environ.get("PAYFAST_MERCHANT_KEY", "46f0cd694581a")
PAYFAST_PASSPHRASE = os.environ.get("PAYFAST_PASSPHRASE", "")
PAYFAST_SANDBOX = os.environ.get("PAYFAST_SANDBOX", "True").lower() == "true"

# Grace period in days before account deactivation
GRACE_PERIOD_DAYS = 7

# Extra seat price in cents
EXTRA_SEAT_PRICE = 89900  # R899


class PayFastSubscriptionService:
    """Service for managing PayFast subscriptions and payments"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # ==========================================
    # PayFast Signature & URL Generation
    # ==========================================
    
    def generate_signature(self, data: dict, passphrase: str = None) -> str:
        """Generate MD5 signature for PayFast data"""
        filtered_data = {k: str(v) for k, v in data.items() if v is not None and v != '' and k != 'signature'}
        sorted_params = sorted(filtered_data.items())
        param_string = '&'.join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
        
        if passphrase:
            param_string += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
        
        return hashlib.md5(param_string.encode('utf-8')).hexdigest()
    
    def get_payfast_url(self) -> str:
        """Get PayFast URL based on sandbox mode"""
        if PAYFAST_SANDBOX:
            return "https://sandbox.payfast.co.za/eng/process"
        return "https://www.payfast.co.za/eng/process"
    
    def get_payfast_api_url(self) -> str:
        """Get PayFast API URL based on sandbox mode"""
        if PAYFAST_SANDBOX:
            return "https://api.payfast.co.za/subscriptions"
        return "https://api.payfast.co.za/subscriptions"
    
    # ==========================================
    # Pro-Rata Calculation
    # ==========================================
    
    def calculate_prorata_days(self, account_billing_day: int, current_date: datetime = None) -> int:
        """
        Calculate the number of days until the next billing date.
        Returns 0 if it's the billing day itself.
        """
        if current_date is None:
            current_date = datetime.utcnow()
        
        current_day = current_date.day
        
        if current_day == account_billing_day:
            return 0
        
        # Calculate days until next billing
        if current_day < account_billing_day:
            return account_billing_day - current_day
        else:
            # Next month
            next_month = current_date.replace(day=1) + timedelta(days=32)
            next_billing = next_month.replace(day=min(account_billing_day, 28))
            return (next_billing - current_date).days
    
    def calculate_prorata_amount(self, full_price: int, prorata_days: int, discount_percent: float = 100.0) -> int:
        """
        Calculate pro-rata amount with discount.
        discount_percent: 100 means 100% discount (free), 0 means no discount
        Returns amount in cents
        """
        if prorata_days == 0:
            return full_price
        
        # Assume 30-day month
        daily_rate = full_price / 30
        prorata_amount = daily_rate * prorata_days
        
        # Apply discount
        discount_amount = prorata_amount * (discount_percent / 100)
        final_amount = prorata_amount - discount_amount
        
        return max(0, int(final_amount))
    
    # ==========================================
    # Subscription Payment Initiation
    # ==========================================
    
    async def initiate_subscription(
        self,
        account_id: str,
        tier_id: str,
        user_email: str,
        user_name: str,
        return_url: str,
        cancel_url: str,
        notify_url: str,
        is_reactivation: bool = False
    ) -> Dict[str, Any]:
        """Initiate a new subscription or reactivation payment"""
        
        tier_config = get_tier_config(TierId(tier_id))
        if not tier_config:
            raise ValueError(f"Invalid tier: {tier_id}")
        
        payment_id = str(uuid.uuid4())
        amount_cents = tier_config["price_monthly"]
        amount_rands = amount_cents / 100
        
        # Get or set billing day
        account = await self.db.accounts.find_one({"id": account_id})
        billing_day = datetime.utcnow().day
        if account and account.get("billing_day"):
            billing_day = account["billing_day"]
        
        # Create payment record
        payment_record = {
            "id": payment_id,
            "account_id": account_id,
            "tier_id": tier_id,
            "payment_type": "subscription",
            "amount": amount_cents,
            "currency": "ZAR",
            "status": PaymentStatus.PENDING.value,
            "provider": "payfast",
            "created_at": datetime.utcnow(),
            "description": f"Monthly subscription - {tier_config['name']} plan",
            "is_reactivation": is_reactivation
        }
        await self.db.payments.insert_one(payment_record)
        
        # Build PayFast data with subscription parameters
        payfast_data = {
            "merchant_id": PAYFAST_MERCHANT_ID,
            "merchant_key": PAYFAST_MERCHANT_KEY,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url,
            "name_first": user_name.split()[0] if user_name else "User",
            "name_last": user_name.split()[-1] if user_name and len(user_name.split()) > 1 else "",
            "email_address": user_email,
            "m_payment_id": payment_id,
            "amount": f"{amount_rands:.2f}",
            "item_name": f"JobRocket {tier_config['name']} Plan",
            "item_description": f"Monthly subscription to {tier_config['name']} plan",
            # Subscription parameters
            "subscription_type": "1",  # Subscription
            "billing_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "recurring_amount": f"{amount_rands:.2f}",
            "frequency": "3",  # Monthly
            "cycles": "0",  # Indefinite
        }
        
        # Add signature
        payfast_data["signature"] = self.generate_signature(payfast_data, PAYFAST_PASSPHRASE)
        
        return {
            "payment_id": payment_id,
            "payfast_url": self.get_payfast_url(),
            "payfast_data": payfast_data
        }
    
    async def initiate_extra_seat_payment(
        self,
        account_id: str,
        quantity: int,
        user_email: str,
        user_name: str,
        return_url: str,
        cancel_url: str,
        notify_url: str
    ) -> Dict[str, Any]:
        """Initiate payment for extra user seats with pro-rata calculation"""
        
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            raise ValueError("Account not found")
        
        billing_day = account.get("billing_day", datetime.utcnow().day)
        
        # Calculate pro-rata days
        prorata_days = self.calculate_prorata_days(billing_day)
        
        # First payment is free for pro-rata period (100% discount)
        # Full amount will be charged on the next billing date
        initial_amount = 0  # Free pro-rata period
        recurring_amount = EXTRA_SEAT_PRICE * quantity
        
        payment_id = str(uuid.uuid4())
        
        # Create payment record
        payment_record = {
            "id": payment_id,
            "account_id": account_id,
            "payment_type": "extra_seat",
            "quantity": quantity,
            "amount": initial_amount,
            "recurring_amount": recurring_amount,
            "currency": "ZAR",
            "status": PaymentStatus.PENDING.value,
            "provider": "payfast",
            "created_at": datetime.utcnow(),
            "description": f"{quantity} Extra User Seat(s) - Pro-rata period free",
            "prorata_days": prorata_days,
            "prorata_discount": 100
        }
        await self.db.payments.insert_one(payment_record)
        
        # If pro-rata period is free, activate immediately
        if initial_amount == 0:
            # Create seat records immediately
            seats_created = await self._create_seat_records(account_id, quantity, billing_day, payment_id)
            
            return {
                "payment_id": payment_id,
                "status": "activated",
                "message": f"{quantity} seat(s) activated. Free until billing date ({billing_day}th).",
                "seats_created": seats_created,
                "next_billing_day": billing_day
            }
        
        # Otherwise, redirect to PayFast
        amount_rands = initial_amount / 100
        recurring_rands = recurring_amount / 100
        
        payfast_data = {
            "merchant_id": PAYFAST_MERCHANT_ID,
            "merchant_key": PAYFAST_MERCHANT_KEY,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url,
            "name_first": user_name.split()[0] if user_name else "User",
            "name_last": user_name.split()[-1] if user_name and len(user_name.split()) > 1 else "",
            "email_address": user_email,
            "m_payment_id": payment_id,
            "amount": f"{amount_rands:.2f}",
            "item_name": f"JobRocket Extra User Seat(s) x{quantity}",
            "item_description": f"{quantity} extra user seat(s) - Monthly billing",
            "subscription_type": "1",
            "recurring_amount": f"{recurring_rands:.2f}",
            "frequency": "3",
            "cycles": "0",
        }
        
        payfast_data["signature"] = self.generate_signature(payfast_data, PAYFAST_PASSPHRASE)
        
        return {
            "payment_id": payment_id,
            "payfast_url": self.get_payfast_url(),
            "payfast_data": payfast_data
        }
    
    async def _create_seat_records(
        self,
        account_id: str,
        quantity: int,
        billing_day: int,
        payment_id: str
    ) -> List[str]:
        """Create extra seat records"""
        now = datetime.utcnow()
        seats_created = []
        
        # Calculate next billing date
        if now.day >= billing_day:
            next_month = now.replace(day=1) + timedelta(days=32)
            next_billing = next_month.replace(day=min(billing_day, 28))
        else:
            next_billing = now.replace(day=min(billing_day, 28))
        
        for _ in range(quantity):
            seat_id = str(uuid.uuid4())
            seat_doc = {
                "id": seat_id,
                "account_id": account_id,
                "purchased_date": now,
                "next_billing_date": next_billing,
                "is_active": True,
                "payment_status": "paid",
                "payment_id": payment_id,
                "user_id": None  # To be assigned when user is invited
            }
            await self.db.extra_seats.insert_one(seat_doc)
            seats_created.append(seat_id)
        
        # Update account's extra user count
        await self.db.accounts.update_one(
            {"id": account_id},
            {
                "$inc": {"extra_users_count": quantity},
                "$set": {"updated_at": now}
            }
        )
        
        return seats_created
    
    async def initiate_addon_payment(
        self,
        account_id: str,
        addon_type: str,
        amount: int,
        description: str,
        user_email: str,
        user_name: str,
        return_url: str,
        cancel_url: str,
        notify_url: str,
        extra_data: dict = None,
        is_ai_feature: bool = False
    ) -> Dict[str, Any]:
        """Initiate payment for add-ons with optional pro-rata calculation"""
        
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            raise ValueError("Account not found")
        
        billing_day = account.get("billing_day", datetime.utcnow().day)
        
        # AI features are NOT pro-rata'd (charged full price)
        if is_ai_feature:
            initial_amount = amount
            prorata_days = 0
            prorata_discount = 0
        else:
            # Calculate pro-rata for non-AI features
            prorata_days = self.calculate_prorata_days(billing_day)
            # 100% discount for pro-rata period
            initial_amount = 0
            prorata_discount = 100
        
        payment_id = str(uuid.uuid4())
        
        # Create payment record
        payment_record = {
            "id": payment_id,
            "account_id": account_id,
            "payment_type": addon_type,
            "amount": initial_amount,
            "recurring_amount": amount,
            "currency": "ZAR",
            "status": PaymentStatus.PENDING.value,
            "provider": "payfast",
            "created_at": datetime.utcnow(),
            "description": description,
            "extra_data": extra_data or {},
            "prorata_days": prorata_days,
            "prorata_discount": prorata_discount,
            "is_ai_feature": is_ai_feature
        }
        await self.db.payments.insert_one(payment_record)
        
        # If pro-rata period is free for non-AI features, activate immediately
        if initial_amount == 0 and not is_ai_feature:
            await self._activate_addon_immediately(payment_record)
            return {
                "payment_id": payment_id,
                "status": "activated",
                "message": f"Feature activated. Free until billing date ({billing_day}th).",
                "next_billing_day": billing_day
            }
        
        # Otherwise, redirect to PayFast
        amount_rands = initial_amount / 100
        
        payfast_data = {
            "merchant_id": PAYFAST_MERCHANT_ID,
            "merchant_key": PAYFAST_MERCHANT_KEY,
            "return_url": return_url,
            "cancel_url": cancel_url,
            "notify_url": notify_url,
            "name_first": user_name.split()[0] if user_name else "User",
            "name_last": user_name.split()[-1] if user_name and len(user_name.split()) > 1 else "",
            "email_address": user_email,
            "m_payment_id": payment_id,
            "amount": f"{amount_rands:.2f}",
            "item_name": description[:100],
            "item_description": description,
        }
        
        payfast_data["signature"] = self.generate_signature(payfast_data, PAYFAST_PASSPHRASE)
        
        return {
            "payment_id": payment_id,
            "payfast_url": self.get_payfast_url(),
            "payfast_data": payfast_data
        }
    
    async def _activate_addon_immediately(self, payment: Dict[str, Any]):
        """Activate addon immediately (for free pro-rata period)"""
        account_id = payment.get("account_id")
        addon_type = payment.get("payment_type")
        extra_data = payment.get("extra_data", {})
        
        # Mark payment as completed
        await self.db.payments.update_one(
            {"id": payment["id"]},
            {"$set": {
                "status": PaymentStatus.COMPLETED.value,
                "paid_at": datetime.utcnow(),
                "note": "Activated immediately - free pro-rata period"
            }}
        )
        
        if addon_type == "addon":
            addon_id = extra_data.get("addon_id")
            if addon_id:
                await self.db.account_addons.update_one(
                    {"account_id": account_id, "addon_id": addon_id},
                    {"$set": {
                        "is_active": True,
                        "payment_status": "paid",
                        "activated_at": datetime.utcnow()
                    }},
                    upsert=True
                )
    
    # ==========================================
    # Payment Processing (ITN Handler)
    # ==========================================
    
    async def process_itn(self, itn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process PayFast Instant Transaction Notification"""
        
        payment_id = itn_data.get("m_payment_id")
        payment_status = itn_data.get("payment_status")
        pf_payment_id = itn_data.get("pf_payment_id")
        token = itn_data.get("token")  # Subscription token
        
        if not payment_id:
            logger.error("ITN missing payment ID")
            return {"success": False, "error": "Missing payment ID"}
        
        # Find the payment record
        payment = await self.db.payments.find_one({"id": payment_id})
        if not payment:
            logger.error(f"Payment not found: {payment_id}")
            return {"success": False, "error": "Payment not found"}
        
        # Update payment record
        update_data = {
            "pf_payment_id": pf_payment_id,
            "payment_status_raw": payment_status,
            "itn_received_at": datetime.utcnow(),
            "itn_data": itn_data
        }
        
        # Store subscription token if present
        if token:
            update_data["subscription_token"] = token
            # Also store on account for future billing
            await self.db.accounts.update_one(
                {"id": payment.get("account_id")},
                {"$set": {"payfast_token": token}}
            )
        
        if payment_status == "COMPLETE":
            update_data["status"] = PaymentStatus.COMPLETED.value
            update_data["paid_at"] = datetime.utcnow()
            
            # Process based on payment type
            if payment.get("payment_type") == "subscription":
                await self._activate_subscription(payment, is_reactivation=payment.get("is_reactivation", False))
            elif payment.get("payment_type") == "extra_seat":
                await self._activate_extra_seat(payment)
            elif payment.get("payment_type") == "addon":
                await self._activate_addon(payment)
            
            # Send success email
            await self._send_payment_success_email(payment)
            
        elif payment_status == "FAILED":
            update_data["status"] = PaymentStatus.FAILED.value
            update_data["failed_at"] = datetime.utcnow()
            
            # Handle payment failure
            await self._handle_payment_failure(payment)
            
            # Send failure email
            await self._send_payment_failure_email(payment)
            
        elif payment_status == "CANCELLED":
            update_data["status"] = PaymentStatus.CANCELLED.value
        
        await self.db.payments.update_one(
            {"id": payment_id},
            {"$set": update_data}
        )
        
        return {"success": True, "payment_id": payment_id, "status": payment_status}
    
    async def _activate_subscription(self, payment: Dict[str, Any], is_reactivation: bool = False):
        """Activate subscription after successful payment"""
        account_id = payment.get("account_id")
        tier_id = payment.get("tier_id")
        
        now = datetime.utcnow()
        billing_day = now.day  # New billing cycle starts from payment date
        next_billing_date = now + timedelta(days=30)
        
        update_data = {
            "tier_id": tier_id,
            "subscription_status": SubscriptionStatus.ACTIVE.value,
            "subscription_start_date": now,
            "subscription_end_date": next_billing_date,
            "next_billing_date": next_billing_date,
            "billing_day": billing_day,
            "last_payment_date": now,
            "last_payment_id": payment.get("id"),
            "payment_retry_count": 0,
            "grace_period_start": None,
            "updated_at": now
        }
        
        # If reactivation, note the date change
        if is_reactivation:
            update_data["billing_cycle_reset_date"] = now
            update_data["billing_cycle_reset_reason"] = "late_payment_reactivation"
        
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": update_data}
        )
        
        logger.info(f"Subscription activated for account {account_id}, billing day: {billing_day}, next billing: {next_billing_date}")
    
    async def _activate_extra_seat(self, payment: Dict[str, Any]):
        """Activate extra seat after successful payment"""
        account_id = payment.get("account_id")
        quantity = payment.get("quantity", 1)
        
        account = await self.db.accounts.find_one({"id": account_id})
        billing_day = account.get("billing_day", datetime.utcnow().day)
        
        # Create seat records
        await self._create_seat_records(account_id, quantity, billing_day, payment.get("id"))
        
        logger.info(f"{quantity} extra seat(s) activated for account {account_id}")
    
    async def _activate_addon(self, payment: Dict[str, Any]):
        """Activate addon after successful payment"""
        account_id = payment.get("account_id")
        extra_data = payment.get("extra_data", {})
        addon_id = extra_data.get("addon_id")
        
        if addon_id:
            await self.db.account_addons.update_one(
                {"account_id": account_id, "addon_id": addon_id},
                {"$set": {
                    "is_active": True,
                    "payment_status": "paid",
                    "last_payment_date": datetime.utcnow()
                }},
                upsert=True
            )
        
        logger.info(f"Addon {addon_id} activated for account {account_id}")
    
    async def _handle_payment_failure(self, payment: Dict[str, Any]):
        """Handle a failed payment - start grace period if subscription"""
        account_id = payment.get("account_id")
        payment_type = payment.get("payment_type")
        
        if payment_type == "subscription":
            # Start or continue grace period
            account = await self.db.accounts.find_one({"id": account_id})
            if account and account.get("subscription_status") == SubscriptionStatus.ACTIVE.value:
                await self.db.accounts.update_one(
                    {"id": account_id},
                    {"$set": {
                        "subscription_status": SubscriptionStatus.PAST_DUE.value,
                        "grace_period_start": datetime.utcnow(),
                        "last_failed_payment_date": datetime.utcnow()
                    }}
                )
        
        elif payment_type == "extra_seat":
            # Deactivate the specific seat
            extra_data = payment.get("extra_data", {})
            seat_id = extra_data.get("seat_id")
            if seat_id:
                await self.deactivate_seat(seat_id)
    
    # ==========================================
    # Subscription Status Management
    # ==========================================
    
    async def check_subscription_status(self, account_id: str) -> Dict[str, Any]:
        """Check and update subscription status for an account"""
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return {"error": "Account not found"}
        
        now = datetime.utcnow()
        subscription_end = account.get("subscription_end_date")
        grace_period_start = account.get("grace_period_start")
        current_status = account.get("subscription_status")
        billing_day = account.get("billing_day")
        
        # Already inactive
        if current_status == SubscriptionStatus.INACTIVE.value:
            return {
                "status": "inactive",
                "needs_payment": True,
                "message": "Subscription is inactive. Please make a payment to reactivate.",
                "billing_day": billing_day
            }
        
        # Check if subscription has expired
        if subscription_end and now > subscription_end:
            # Check grace period
            if grace_period_start:
                grace_end = grace_period_start + timedelta(days=GRACE_PERIOD_DAYS)
                if now > grace_end:
                    # Grace period expired - deactivate
                    await self._deactivate_account(account_id)
                    return {
                        "status": "inactive",
                        "needs_payment": True,
                        "message": "Grace period expired. Account deactivated.",
                        "billing_day": billing_day
                    }
                else:
                    # Still in grace period
                    days_remaining = (grace_end - now).days
                    return {
                        "status": "grace_period",
                        "needs_payment": True,
                        "grace_days_remaining": days_remaining,
                        "message": f"Payment overdue. {days_remaining} days remaining in grace period.",
                        "billing_day": billing_day
                    }
            else:
                # Start grace period
                await self.db.accounts.update_one(
                    {"id": account_id},
                    {"$set": {
                        "grace_period_start": now,
                        "subscription_status": SubscriptionStatus.PAST_DUE.value
                    }}
                )
                return {
                    "status": "grace_period",
                    "needs_payment": True,
                    "grace_days_remaining": GRACE_PERIOD_DAYS,
                    "message": f"Payment overdue. {GRACE_PERIOD_DAYS} days grace period started.",
                    "billing_day": billing_day
                }
        
        return {
            "status": "active",
            "needs_payment": False,
            "next_billing_date": subscription_end,
            "billing_day": billing_day
        }
    
    async def _deactivate_account(self, account_id: str):
        """Deactivate an account due to payment failure"""
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": {
                "subscription_status": SubscriptionStatus.INACTIVE.value,
                "deactivated_at": datetime.utcnow(),
                "deactivation_reason": "payment_failure"
            }}
        )
        
        # Send deactivation email
        account = await self.db.accounts.find_one({"id": account_id})
        if account:
            owner = await self.db.users.find_one({
                "account_id": account_id,
                "account_role": "owner"
            })
            if owner:
                await self._send_deactivation_email(account, owner)
        
        logger.info(f"Account {account_id} deactivated due to payment failure")
    
    # ==========================================
    # Daily Payment Check (Called by Scheduler)
    # ==========================================
    
    async def check_and_retry_payment(self, account_id: str) -> Dict[str, Any]:
        """
        Check if a past-due account has made a payment via PayFast.
        This pings PayFast to check subscription status.
        """
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            return {"success": False, "error": "Account not found"}
        
        token = account.get("payfast_token")
        if not token:
            # No subscription token - can't check automatically
            logger.info(f"Account {account_id} has no PayFast token, skipping auto-check")
            return {"success": False, "error": "No PayFast subscription token"}
        
        # Query PayFast API for subscription status
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "merchant-id": PAYFAST_MERCHANT_ID,
                    "version": "v1",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Generate signature for API call
                signature_data = {
                    "merchant-id": PAYFAST_MERCHANT_ID,
                    "timestamp": headers["timestamp"],
                    "version": "v1"
                }
                headers["signature"] = self.generate_signature(signature_data, PAYFAST_PASSPHRASE)
                
                api_url = f"{self.get_payfast_api_url()}/{token}/fetch"
                
                response = await client.get(api_url, headers=headers, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    subscription_status = data.get("data", {}).get("status")
                    
                    if subscription_status == 1:  # Active
                        # Payment was made - reactivate
                        now = datetime.utcnow()
                        billing_day = now.day
                        
                        await self.db.accounts.update_one(
                            {"id": account_id},
                            {"$set": {
                                "subscription_status": SubscriptionStatus.ACTIVE.value,
                                "subscription_start_date": now,
                                "subscription_end_date": now + timedelta(days=30),
                                "billing_day": billing_day,
                                "next_billing_date": now + timedelta(days=30),
                                "grace_period_start": None,
                                "payment_retry_count": 0,
                                "last_payment_date": now,
                                "billing_cycle_reset_date": now,
                                "billing_cycle_reset_reason": "late_payment_auto_detected"
                            }}
                        )
                        
                        logger.info(f"Account {account_id} reactivated via PayFast check, new billing day: {billing_day}")
                        return {"success": True, "status": "reactivated", "new_billing_day": billing_day}
                    
                    elif subscription_status == 0:  # Cancelled/Inactive
                        return {"success": False, "status": "still_inactive"}
                
                else:
                    logger.warning(f"PayFast API returned {response.status_code} for account {account_id}")
                    return {"success": False, "error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error checking PayFast status for account {account_id}: {e}")
            return {"success": False, "error": str(e)}
        
        return {"success": False, "status": "no_change"}
    
    # ==========================================
    # Extra Seat Management
    # ==========================================
    
    async def check_seat_status(self, user_id: str) -> Dict[str, Any]:
        """Check if a user's seat is active (for extra seat users)"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return {"error": "User not found"}
        
        # Check if this user is an extra seat user
        seat = await self.db.extra_seats.find_one({"user_id": user_id})
        if not seat:
            # Not an extra seat user - check main subscription
            return {"is_extra_seat": False, "seat_active": True, "read_only": False}
        
        # Check seat payment status
        if seat.get("payment_status") != "paid" or not seat.get("is_active"):
            return {
                "is_extra_seat": True,
                "seat_active": False,
                "read_only": True,  # Limited read-only access
                "needs_payment": True,
                "message": "Seat payment required. You have read-only access. Please contact your account owner."
            }
        
        # Check if seat billing is overdue
        next_billing = seat.get("next_billing_date")
        if next_billing and datetime.utcnow() > next_billing:
            return {
                "is_extra_seat": True,
                "seat_active": False,
                "read_only": True,
                "needs_payment": True,
                "message": "Seat payment overdue. You have read-only access."
            }
        
        return {"is_extra_seat": True, "seat_active": True, "read_only": False}
    
    async def deactivate_seat(self, seat_id: str):
        """Deactivate an extra seat due to payment failure - gives read-only access"""
        seat = await self.db.extra_seats.find_one({"id": seat_id})
        if seat:
            await self.db.extra_seats.update_one(
                {"id": seat_id},
                {"$set": {
                    "is_active": False,
                    "payment_status": "failed",
                    "deactivated_at": datetime.utcnow()
                }}
            )
            
            # Update user to read-only mode
            if seat.get("user_id"):
                await self.db.users.update_one(
                    {"id": seat.get("user_id")},
                    {"$set": {
                        "seat_active": False,
                        "seat_payment_status": "failed",
                        "read_only_mode": True
                    }}
                )
        
        logger.info(f"Extra seat {seat_id} deactivated - user now has read-only access")
    
    # ==========================================
    # Email Notifications
    # ==========================================
    
    async def _send_payment_success_email(self, payment: Dict[str, Any]):
        """Send payment success confirmation email"""
        try:
            from services.email_service import EmailService
            
            account = await self.db.accounts.find_one({"id": payment.get("account_id")})
            owner = await self.db.users.find_one({
                "account_id": payment.get("account_id"),
                "account_role": "owner"
            })
            
            if owner and owner.get("email"):
                email_service = EmailService()
                amount = payment.get("amount", 0) / 100
                
                await email_service.send_email(
                    to_email=owner["email"],
                    subject="Payment Successful - JobRocket",
                    html_content=f"""
                    <h2>Payment Confirmation</h2>
                    <p>Dear {owner.get('first_name', 'Customer')},</p>
                    <p>Your payment of <strong>R{amount:.2f}</strong> has been successfully processed.</p>
                    <p><strong>Payment Details:</strong></p>
                    <ul>
                        <li>Description: {payment.get('description', 'Subscription payment')}</li>
                        <li>Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</li>
                        <li>Reference: {payment.get('id')}</li>
                    </ul>
                    <p>Your next billing date is the <strong>{account.get('billing_day', 1)}th</strong> of each month.</p>
                    <p>Thank you for using JobRocket!</p>
                    """,
                    email_type="billing"
                )
                logger.info(f"Payment success email sent to {owner['email']}")
        except Exception as e:
            logger.error(f"Failed to send payment success email: {e}")
    
    async def _send_payment_failure_email(self, payment: Dict[str, Any]):
        """Send payment failure alert email"""
        try:
            from services.email_service import EmailService
            
            owner = await self.db.users.find_one({
                "account_id": payment.get("account_id"),
                "account_role": "owner"
            })
            
            if owner and owner.get("email"):
                email_service = EmailService()
                amount = payment.get("amount", 0) / 100
                
                await email_service.send_email(
                    to_email=owner["email"],
                    subject="Payment Failed - Action Required - JobRocket",
                    html_content=f"""
                    <h2>Payment Failed</h2>
                    <p>Dear {owner.get('first_name', 'Customer')},</p>
                    <p>We were unable to process your payment of <strong>R{amount:.2f}</strong>.</p>
                    <p>Your account has a <strong>7-day grace period</strong> before services are suspended.</p>
                    <p>We will automatically retry the payment daily. Please ensure your payment method has sufficient funds.</p>
                    <p>You can also make a manual payment by logging in to JobRocket.</p>
                    <p><a href="https://jobrocket.co.za/billing">Update Payment</a></p>
                    <p>If you need assistance, please contact our support team.</p>
                    """,
                    email_type="billing"
                )
                logger.info(f"Payment failure email sent to {owner['email']}")
        except Exception as e:
            logger.error(f"Failed to send payment failure email: {e}")
    
    async def _send_deactivation_email(self, account: Dict[str, Any], owner: Dict[str, Any]):
        """Send account deactivation warning email"""
        try:
            from services.email_service import EmailService
            
            if owner and owner.get("email"):
                email_service = EmailService()
                
                await email_service.send_email(
                    to_email=owner["email"],
                    subject="Account Suspended - JobRocket",
                    html_content=f"""
                    <h2>Account Suspended</h2>
                    <p>Dear {owner.get('first_name', 'Customer')},</p>
                    <p>Your JobRocket account has been suspended due to a failed payment after the 7-day grace period.</p>
                    <p>To reactivate your account and resume full access to all features, please make a payment.</p>
                    <p><a href="https://jobrocket.co.za/billing">Reactivate Account</a></p>
                    <p>Your data remains safe and will be available once you reactivate.</p>
                    <p><strong>Note:</strong> Your new billing cycle will start from the date of your next payment.</p>
                    <p>If you have any questions, please contact our support team.</p>
                    """,
                    email_type="billing"
                )
                logger.info(f"Deactivation email sent to {owner['email']}")
        except Exception as e:
            logger.error(f"Failed to send deactivation email: {e}")
    
    async def send_grace_period_reminder(self, account_id: str, days_remaining: int):
        """Send grace period reminder email"""
        try:
            from services.email_service import EmailService
            
            owner = await self.db.users.find_one({
                "account_id": account_id,
                "account_role": "owner"
            })
            
            if owner and owner.get("email"):
                email_service = EmailService()
                
                await email_service.send_email(
                    to_email=owner["email"],
                    subject=f"Payment Reminder - {days_remaining} Days Left - JobRocket",
                    html_content=f"""
                    <h2>Payment Reminder</h2>
                    <p>Dear {owner.get('first_name', 'Customer')},</p>
                    <p>This is a reminder that your JobRocket payment is overdue.</p>
                    <p>You have <strong>{days_remaining} days</strong> remaining before your account is suspended.</p>
                    <p>We are attempting to process your payment automatically. Please ensure your payment method has sufficient funds.</p>
                    <p><a href="https://jobrocket.co.za/billing">Make Payment</a></p>
                    """,
                    email_type="billing"
                )
                logger.info(f"Grace period reminder sent to {owner['email']}")
        except Exception as e:
            logger.error(f"Failed to send grace period reminder: {e}")


def create_payfast_subscription_service(db: AsyncIOMotorDatabase) -> PayFastSubscriptionService:
    """Factory function to create PayFastSubscriptionService"""
    return PayFastSubscriptionService(db)
