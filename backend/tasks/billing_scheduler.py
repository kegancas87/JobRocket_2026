"""
JobRocket - Scheduled Tasks for Billing
Run this script daily via cron to:
1. Retry failed payments during grace period
2. Deactivate accounts after grace period expires
3. Send reminder emails
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.payfast_subscription_service import create_payfast_subscription_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "jobrocket")

GRACE_PERIOD_DAYS = 7


async def run_billing_tasks():
    """Run all daily billing tasks"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    logger.info("Starting daily billing tasks...")
    
    payfast_service = create_payfast_subscription_service(db)
    
    now = datetime.utcnow()
    
    # 1. Check all accounts with past_due status
    past_due_accounts = await db.accounts.find({
        "subscription_status": {"$in": ["past_due", "PAST_DUE"]}
    }).to_list(1000)
    
    logger.info(f"Found {len(past_due_accounts)} accounts in past due status")
    
    for account in past_due_accounts:
        account_id = account.get("id")
        grace_period_start = account.get("grace_period_start")
        
        if not grace_period_start:
            # Start grace period if not set
            await db.accounts.update_one(
                {"id": account_id},
                {"$set": {"grace_period_start": now}}
            )
            grace_period_start = now
        
        # Calculate days remaining in grace period
        grace_end = grace_period_start + timedelta(days=GRACE_PERIOD_DAYS)
        days_remaining = (grace_end - now).days
        
        if days_remaining <= 0:
            # Grace period expired - deactivate account
            logger.info(f"Deactivating account {account_id} - grace period expired")
            await db.accounts.update_one(
                {"id": account_id},
                {"$set": {
                    "subscription_status": "inactive",
                    "deactivated_at": now,
                    "deactivation_reason": "payment_failure"
                }}
            )
            
            # Send deactivation email
            owner = await db.users.find_one({
                "account_id": account_id,
                "account_role": "owner"
            })
            if owner:
                await payfast_service._send_deactivation_email(account, owner)
        else:
            # Still in grace period - send reminder
            logger.info(f"Account {account_id} has {days_remaining} days remaining in grace period")
            
            # Send reminder on days 5, 3, and 1
            if days_remaining in [5, 3, 1]:
                await payfast_service.send_grace_period_reminder(account_id, days_remaining)
            
            # Record retry attempt (PayFast will handle the actual retry via subscription)
            await payfast_service.record_retry_attempt(account_id)
    
    # 2. Check extra seats with failed payments
    failed_seats = await db.extra_seats.find({
        "payment_status": {"$in": ["failed", "pending"]},
        "is_active": True
    }).to_list(1000)
    
    logger.info(f"Found {len(failed_seats)} extra seats with payment issues")
    
    for seat in failed_seats:
        seat_id = seat.get("id")
        last_payment_date = seat.get("last_payment_date")
        
        if last_payment_date:
            days_overdue = (now - last_payment_date).days - 30
            
            if days_overdue > GRACE_PERIOD_DAYS:
                # Deactivate the seat
                logger.info(f"Deactivating seat {seat_id} - payment overdue")
                await payfast_service.deactivate_seat(seat_id)
    
    # 3. Log summary
    active_count = await db.accounts.count_documents({"subscription_status": "active"})
    inactive_count = await db.accounts.count_documents({"subscription_status": "inactive"})
    past_due_count = await db.accounts.count_documents({"subscription_status": "past_due"})
    
    logger.info(f"Billing task complete. Active: {active_count}, Past Due: {past_due_count}, Inactive: {inactive_count}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(run_billing_tasks())
