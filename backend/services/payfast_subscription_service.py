"""
JobRocket - PayFast Subscription Service
Handles subscription billing, payment tracking, retries, and account status management
"""

import os
import uuid
import hashlib
import urllib.parse
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


class PayFastSubscriptionService:
    """Service for managing PayFast subscriptions and payments"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # ==========================================
    # PayFast Signature Generation
    # ==========================================
    
    def generate_signature(self, data: dict, passphrase: str = None) -> str:
        """Generate MD5 signature for PayFast data"""
        # Sort and encode parameters
        param_string = "&".join(
            f"{k}={urllib.parse.quote_plus(str(v))}" 
            for k, v in data.items() 
            if v is not None and v != ""
        )
        
        if passphrase:
            param_string += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
        
        return hashlib.md5(param_string.encode()).hexdigest()
    
    def get_payfast_url(self) -> str:
        """Get PayFast URL based on sandbox mode"""
        if PAYFAST_SANDBOX:
            return "https://sandbox.payfast.co.za/eng/process"
        return "https://www.payfast.co.za/eng/process"
    
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
        notify_url: str
    ) -> Dict[str, Any]:
        """Initiate a new subscription or reactivation payment"""
        
        tier_config = get_tier_config(TierId(tier_id))
        if not tier_config:
            raise ValueError(f"Invalid tier: {tier_id}")
        
        payment_id = str(uuid.uuid4())
        amount = tier_config["price_monthly"] / 100  # Convert cents to rands
        
        # Create payment record
        payment_record = {
            "id": payment_id,
            "account_id": account_id,
            "tier_id": tier_id,
            "payment_type": "subscription",
            "amount": tier_config["price_monthly"],
            "currency": "ZAR",
            "status": PaymentStatus.PENDING.value,
            "provider": "payfast",
            "created_at": datetime.utcnow(),
            "description": f"Monthly subscription - {tier_config['name']} plan"
        }
        await self.db.payments.insert_one(payment_record)
        
        # Build PayFast data
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
            "amount": f"{amount:.2f}",
            "item_name": f"JobRocket {tier_config['name']} Plan",
            "item_description": f"Monthly subscription to {tier_config['name']} plan",
            "subscription_type": "1",  # Subscription
            "billing_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "recurring_amount": f"{amount:.2f}",
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
        extra_data: dict = None
    ) -> Dict[str, Any]:
        """Initiate payment for add-ons (extra seats, etc.)"""
        
        payment_id = str(uuid.uuid4())
        amount_rands = amount / 100
        
        # Create payment record
        payment_record = {
            "id": payment_id,
            "account_id": account_id,
            "payment_type": addon_type,
            "amount": amount,
            "currency": "ZAR",
            "status": PaymentStatus.PENDING.value,
            "provider": "payfast",
            "created_at": datetime.utcnow(),
            "description": description,
            "extra_data": extra_data or {}
        }
        await self.db.payments.insert_one(payment_record)
        
        # Build PayFast data
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
    
    # ==========================================
    # Payment Processing (ITN Handler)
    # ==========================================
    
    async def process_itn(self, itn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process PayFast Instant Transaction Notification"""
        
        payment_id = itn_data.get("m_payment_id")
        payment_status = itn_data.get("payment_status")
        pf_payment_id = itn_data.get("pf_payment_id")
        
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
        
        if payment_status == "COMPLETE":
            update_data["status"] = PaymentStatus.COMPLETED.value
            update_data["paid_at"] = datetime.utcnow()
            
            # Process based on payment type
            if payment.get("payment_type") == "subscription":
                await self._activate_subscription(payment)
            elif payment.get("payment_type") == "extra_seat":
                await self._activate_extra_seat(payment)
            elif payment.get("payment_type") == "addon":
                await self._activate_addon(payment)
            
            # Send success email
            await self._send_payment_success_email(payment)
            
        elif payment_status == "FAILED":
            update_data["status"] = PaymentStatus.FAILED.value
            update_data["failed_at"] = datetime.utcnow()
            
            # Send failure email
            await self._send_payment_failure_email(payment)
            
        elif payment_status == "CANCELLED":
            update_data["status"] = PaymentStatus.CANCELLED.value
        
        await self.db.payments.update_one(
            {"id": payment_id},
            {"$set": update_data}
        )
        
        return {"success": True, "payment_id": payment_id, "status": payment_status}
    
    async def _activate_subscription(self, payment: Dict[str, Any]):
        """Activate subscription after successful payment"""
        account_id = payment.get("account_id")
        tier_id = payment.get("tier_id")
        
        now = datetime.utcnow()
        next_billing_date = now + timedelta(days=30)
        
        await self.db.accounts.update_one(
            {"id": account_id},
            {"$set": {
                "tier_id": tier_id,
                "subscription_status": SubscriptionStatus.ACTIVE.value,
                "subscription_start_date": now,
                "subscription_end_date": next_billing_date,
                "next_billing_date": next_billing_date,
                "last_payment_date": now,
                "last_payment_id": payment.get("id"),
                "payment_retry_count": 0,
                "grace_period_start": None,
                "updated_at": now
            }}
        )
        
        logger.info(f"Subscription activated for account {account_id}, next billing: {next_billing_date}")
    
    async def _activate_extra_seat(self, payment: Dict[str, Any]):
        """Activate extra seat after successful payment"""
        account_id = payment.get("account_id")
        extra_data = payment.get("extra_data", {})
        seat_id = extra_data.get("seat_id")
        user_id = extra_data.get("user_id")
        
        if seat_id:
            await self.db.extra_seats.update_one(
                {"id": seat_id},
                {"$set": {
                    "is_active": True,
                    "payment_status": "paid",
                    "last_payment_date": datetime.utcnow(),
                    "next_billing_date": datetime.utcnow() + timedelta(days=30)
                }}
            )
        
        if user_id:
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "seat_active": True,
                    "seat_payment_status": "paid"
                }}
            )
        
        logger.info(f"Extra seat {seat_id} activated for account {account_id}")
    
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
        
        # Already inactive
        if current_status == SubscriptionStatus.INACTIVE.value:
            return {
                "status": "inactive",
                "needs_payment": True,
                "message": "Subscription is inactive. Please make a payment to reactivate."
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
                        "message": "Grace period expired. Account deactivated."
                    }
                else:
                    # Still in grace period
                    days_remaining = (grace_end - now).days
                    return {
                        "status": "grace_period",
                        "needs_payment": True,
                        "grace_days_remaining": days_remaining,
                        "message": f"Payment overdue. {days_remaining} days remaining in grace period."
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
                    "message": f"Payment overdue. {GRACE_PERIOD_DAYS} days grace period started."
                }
        
        return {
            "status": "active",
            "needs_payment": False,
            "next_billing_date": subscription_end
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
    # Payment Retry System
    # ==========================================
    
    async def get_accounts_for_retry(self) -> List[Dict[str, Any]]:
        """Get accounts that need payment retry (within grace period)"""
        now = datetime.utcnow()
        grace_cutoff = now - timedelta(days=GRACE_PERIOD_DAYS)
        
        accounts = await self.db.accounts.find({
            "subscription_status": {"$in": [
                SubscriptionStatus.PAST_DUE.value,
                "past_due"
            ]},
            "grace_period_start": {"$gte": grace_cutoff},
            "$or": [
                {"last_retry_date": {"$lt": now - timedelta(hours=24)}},
                {"last_retry_date": None}
            ]
        }).to_list(100)
        
        return accounts
    
    async def record_retry_attempt(self, account_id: str):
        """Record a payment retry attempt"""
        await self.db.accounts.update_one(
            {"id": account_id},
            {
                "$set": {"last_retry_date": datetime.utcnow()},
                "$inc": {"payment_retry_count": 1}
            }
        )
    
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
            return {"is_extra_seat": False, "seat_active": True}
        
        # Check seat payment status
        if seat.get("payment_status") != "paid" or not seat.get("is_active"):
            return {
                "is_extra_seat": True,
                "seat_active": False,
                "needs_payment": True,
                "message": "Seat payment required. Please contact your account owner."
            }
        
        # Check if seat billing is overdue
        next_billing = seat.get("next_billing_date")
        if next_billing and datetime.utcnow() > next_billing:
            return {
                "is_extra_seat": True,
                "seat_active": False,
                "needs_payment": True,
                "message": "Seat payment overdue."
            }
        
        return {"is_extra_seat": True, "seat_active": True}
    
    async def deactivate_seat(self, seat_id: str):
        """Deactivate an extra seat due to payment failure"""
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
            
            # Update user
            if seat.get("user_id"):
                await self.db.users.update_one(
                    {"id": seat.get("user_id")},
                    {"$set": {
                        "seat_active": False,
                        "seat_payment_status": "failed"
                    }}
                )
        
        logger.info(f"Extra seat {seat_id} deactivated due to payment failure")
    
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
                    <p>Please log in to JobRocket and update your payment details or make a manual payment.</p>
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
                    <p>Please make a payment to avoid any interruption to your services.</p>
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
