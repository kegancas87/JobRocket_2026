"""
JobRocket - Scheduled Tasks for Billing
Run this script daily via cron to:
1. Check PayFast for successful payments on past-due accounts
2. Deactivate accounts after grace period expires
3. Send reminder emails on specific days
4. Handle extra seat payment failures

Usage: python -m tasks.billing_scheduler
Cron: 0 6 * * * cd /app/backend && python -m tasks.billing_scheduler >> /var/log/billing.log 2>&1
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "jobrocket")

GRACE_PERIOD_DAYS = 7


async def run_billing_tasks():
    """Run all daily billing tasks"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    logger.info("=" * 60)
    logger.info("Starting daily billing tasks...")
    logger.info(f"Time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 60)
    
    payfast_service = create_payfast_subscription_service(db)
    
    now = datetime.utcnow()
    
    # ==========================================
    # 1. Check past-due accounts and ping PayFast
    # ==========================================
    logger.info("\n[TASK 1] Checking past-due accounts for payments...")
    
    past_due_accounts = await db.accounts.find({
        "subscription_status": {"$in": ["past_due", "PAST_DUE"]}
    }).to_list(1000)
    
    logger.info(f"Found {len(past_due_accounts)} accounts in past due status")
    
    reactivated_count = 0
    deactivated_count = 0
    
    for account in past_due_accounts:
        account_id = account.get("id")
        grace_period_start = account.get("grace_period_start")
        company_name = account.get("company_name", account_id)
        
        if not grace_period_start:
            # Start grace period if not set
            await db.accounts.update_one(
                {"id": account_id},
                {"$set": {"grace_period_start": now}}
            )
            grace_period_start = now
            logger.info(f"  Started grace period for: {company_name}")
        
        # Calculate days remaining in grace period
        grace_end = grace_period_start + timedelta(days=GRACE_PERIOD_DAYS)
        days_remaining = (grace_end - now).days
        
        logger.info(f"  Checking account: {company_name} (Days remaining: {days_remaining})")
        
        if days_remaining <= 0:
            # Grace period expired - deactivate account
            logger.info(f"    -> DEACTIVATING: Grace period expired")
            await db.accounts.update_one(
                {"id": account_id},
                {"$set": {
                    "subscription_status": "inactive",
                    "deactivated_at": now,
                    "deactivation_reason": "payment_failure_grace_expired"
                }}
            )
            
            # Send deactivation email
            owner = await db.users.find_one({
                "account_id": account_id,
                "account_role": "owner"
            })
            if owner:
                await payfast_service._send_deactivation_email(account, owner)
            
            deactivated_count += 1
            
        else:
            # Still in grace period - check PayFast for payment
            logger.info(f"    -> Pinging PayFast to check payment status...")
            
            result = await payfast_service.check_and_retry_payment(account_id)
            
            if result.get("success") and result.get("status") == "reactivated":
                logger.info(f"    -> REACTIVATED: Payment detected, new billing day: {result.get('new_billing_day')}")
                reactivated_count += 1
            else:
                logger.info(f"    -> No payment detected: {result.get('error', result.get('status', 'unknown'))}")
                
                # Send reminder on specific days (7, 5, 3, 2, 1)
                if days_remaining in [7, 5, 3, 2, 1]:
                    logger.info(f"    -> Sending reminder email (Day {days_remaining})")
                    await payfast_service.send_grace_period_reminder(account_id, days_remaining)
                
                # Record retry attempt
                await db.accounts.update_one(
                    {"id": account_id},
                    {
                        "$set": {"last_retry_date": now},
                        "$inc": {"payment_retry_count": 1}
                    }
                )
    
    logger.info(f"\nPast-due summary: {reactivated_count} reactivated, {deactivated_count} deactivated")
    
    # ==========================================
    # 2. Check accounts approaching billing date
    # ==========================================
    logger.info("\n[TASK 2] Checking accounts approaching billing date...")
    
    # Find accounts where next_billing_date is within 3 days
    upcoming_billing = await db.accounts.find({
        "subscription_status": "active",
        "next_billing_date": {
            "$gte": now,
            "$lte": now + timedelta(days=3)
        }
    }).to_list(100)
    
    logger.info(f"Found {len(upcoming_billing)} accounts with upcoming billing in 3 days")
    
    # ==========================================
    # 3. Check extra seats with failed payments
    # ==========================================
    logger.info("\n[TASK 3] Checking extra seats with payment issues...")
    
    failed_seats = await db.extra_seats.find({
        "payment_status": {"$in": ["failed", "pending"]},
        "is_active": True
    }).to_list(1000)
    
    logger.info(f"Found {len(failed_seats)} extra seats with payment issues")
    
    seats_deactivated = 0
    for seat in failed_seats:
        seat_id = seat.get("id")
        last_payment_date = seat.get("last_payment_date") or seat.get("purchased_date")
        
        if last_payment_date:
            days_overdue = (now - last_payment_date).days - 30
            
            if days_overdue > GRACE_PERIOD_DAYS:
                # Deactivate the seat (read-only mode)
                logger.info(f"  Deactivating seat {seat_id} - {days_overdue} days overdue")
                await payfast_service.deactivate_seat(seat_id)
                seats_deactivated += 1
    
    logger.info(f"Extra seats deactivated: {seats_deactivated}")
    
    # ==========================================
    # 4. Check addon subscriptions
    # ==========================================
    logger.info("\n[TASK 4] Checking addon subscriptions...")
    
    overdue_addons = await db.account_addons.find({
        "is_active": True,
        "is_recurring": True,
        "next_billing_date": {"$lt": now}
    }).to_list(1000)
    
    logger.info(f"Found {len(overdue_addons)} overdue addon subscriptions")
    
    for addon in overdue_addons:
        addon_id = addon.get("addon_id")
        account_id = addon.get("account_id")
        
        # Check if AI feature (don't deactivate, just log)
        is_ai = addon.get("is_ai_feature", False)
        
        if not is_ai:
            # Deactivate non-AI addon
            await db.account_addons.update_one(
                {"id": addon.get("id")},
                {"$set": {
                    "is_active": False,
                    "payment_status": "overdue",
                    "deactivated_at": now
                }}
            )
            logger.info(f"  Deactivated addon {addon_id} for account {account_id}")
    
    # ==========================================
    # 5. Generate daily summary
    # ==========================================
    logger.info("\n[TASK 5] Generating daily billing summary...")
    
    active_count = await db.accounts.count_documents({"subscription_status": "active"})
    inactive_count = await db.accounts.count_documents({"subscription_status": "inactive"})
    past_due_count = await db.accounts.count_documents({"subscription_status": {"$in": ["past_due", "PAST_DUE"]}})
    trial_count = await db.accounts.count_documents({"subscription_status": "trial"})
    
    # Today's payments
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_payments = await db.payments.count_documents({
        "status": "completed",
        "paid_at": {"$gte": today_start}
    })
    
    today_revenue_cursor = db.payments.aggregate([
        {"$match": {"status": "completed", "paid_at": {"$gte": today_start}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    today_revenue_result = await today_revenue_cursor.to_list(1)
    today_revenue = today_revenue_result[0]["total"] if today_revenue_result else 0
    
    logger.info("\n" + "=" * 60)
    logger.info("DAILY BILLING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Active Subscriptions:   {active_count}")
    logger.info(f"Trial Accounts:         {trial_count}")
    logger.info(f"Past Due:               {past_due_count}")
    logger.info(f"Inactive:               {inactive_count}")
    logger.info(f"Today's Payments:       {today_payments}")
    logger.info(f"Today's Revenue:        R{today_revenue/100:.2f}")
    logger.info(f"Accounts Reactivated:   {reactivated_count}")
    logger.info(f"Accounts Deactivated:   {deactivated_count}")
    logger.info(f"Seats Deactivated:      {seats_deactivated}")
    logger.info("=" * 60)
    
    # Store summary in database for admin dashboard
    await db.billing_summaries.insert_one({
        "date": today_start,
        "active_subscriptions": active_count,
        "trial_accounts": trial_count,
        "past_due": past_due_count,
        "inactive": inactive_count,
        "payments_count": today_payments,
        "revenue": today_revenue,
        "reactivated": reactivated_count,
        "deactivated": deactivated_count,
        "seats_deactivated": seats_deactivated,
        "created_at": now
    })
    
    logger.info("\nBilling tasks completed successfully!")
    
    client.close()


async def run_manual_check(account_id: str):
    """Manually check and retry payment for a specific account"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    payfast_service = create_payfast_subscription_service(db)
    result = await payfast_service.check_and_retry_payment(account_id)
    
    print(f"Result for account {account_id}: {result}")
    
    client.close()
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JobRocket Billing Scheduler")
    parser.add_argument("--account", help="Check specific account ID")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    
    args = parser.parse_args()
    
    if args.account:
        asyncio.run(run_manual_check(args.account))
    else:
        asyncio.run(run_billing_tasks())
