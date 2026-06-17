"""
JobRocket - Statement Generation Service
Generates downloadable billing statements with company and customer details
"""

import os
import io
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# JobRocket Company Details (Placeholder values)
JOBROCKET_DETAILS = {
    "company_name": "JobRocket (Pty) Ltd",
    "registration_number": "2024/123456/07",
    "vat_number": "4123456789",
    "address_line1": "123 Business Park",
    "address_line2": "Sandton",
    "city": "Johannesburg",
    "province": "Gauteng",
    "postal_code": "2196",
    "country": "South Africa",
    "email": "billing@jobrocket.co.za",
    "phone": "+27 11 123 4567",
    "website": "www.jobrocket.co.za",
    "bank_name": "First National Bank",
    "bank_account": "12345678901",
    "bank_branch": "250655"
}


class StatementService:
    """Service for generating billing statements"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_payment_history(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """Get payment history for an account with pagination"""
        
        query = {"account_id": account_id}
        
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        # Get total count
        total = await self.db.payments.count_documents(query)
        
        # Get payments
        cursor = self.db.payments.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        payments = []
        async for payment in cursor:
            if "_id" in payment:
                del payment["_id"]
            
            # Convert datetime objects to ISO strings
            for key in ["created_at", "paid_at", "failed_at", "itn_received_at"]:
                if payment.get(key):
                    payment[key] = payment[key].isoformat() if isinstance(payment[key], datetime) else payment[key]
            
            payments.append(payment)
        
        return {
            "payments": payments,
            "total": total,
            "limit": limit,
            "skip": skip,
            "has_more": (skip + limit) < total
        }
    
    async def generate_statement_data(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate statement data for a date range"""
        
        # Get account details
        account = await self.db.accounts.find_one({"id": account_id})
        if not account:
            raise ValueError("Account not found")
        
        # Get account owner details
        owner = await self.db.users.find_one({
            "account_id": account_id,
            "account_role": "owner"
        })
        
        # Get payments in date range
        payments = await self.db.payments.find({
            "account_id": account_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }).sort("created_at", -1).to_list(1000)
        
        # Calculate totals
        total_paid = sum(p.get("amount", 0) for p in payments if p.get("status") == "completed")
        total_pending = sum(p.get("amount", 0) for p in payments if p.get("status") == "pending")
        total_failed = sum(p.get("amount", 0) for p in payments if p.get("status") == "failed")
        
        # Format payments for statement
        formatted_payments = []
        for payment in payments:
            formatted_payments.append({
                "date": payment.get("created_at").strftime("%Y-%m-%d") if payment.get("created_at") else "",
                "description": payment.get("description", "Payment"),
                "type": payment.get("payment_type", "subscription"),
                "reference": payment.get("id", "")[:8].upper(),
                "amount": payment.get("amount", 0) / 100,
                "status": payment.get("status", "pending"),
                "paid_date": payment.get("paid_at").strftime("%Y-%m-%d") if payment.get("paid_at") else None
            })
        
        # Customer details
        customer_details = {
            "company_name": account.get("company_name", ""),
            "account_id": account_id,
            "contact_name": f"{owner.get('first_name', '')} {owner.get('last_name', '')}".strip() if owner else "",
            "email": owner.get("email", "") if owner else "",
            "phone": owner.get("phone", "") if owner else "",
            "address": account.get("address", ""),
            "city": account.get("city", ""),
            "province": account.get("province", ""),
            "postal_code": account.get("postal_code", ""),
            "vat_number": account.get("vat_number", "")
        }
        
        # Statement metadata
        statement_number = f"STM-{account_id[:8].upper()}-{datetime.utcnow().strftime('%Y%m%d')}"
        
        return {
            "statement_number": statement_number,
            "generated_date": datetime.utcnow().isoformat(),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "jobrocket_details": JOBROCKET_DETAILS,
            "customer_details": customer_details,
            "payments": formatted_payments,
            "summary": {
                "total_paid": total_paid / 100,
                "total_pending": total_pending / 100,
                "total_failed": total_failed / 100,
                "payment_count": len(payments),
                "currency": "ZAR"
            },
            "subscription_info": {
                "tier": account.get("tier_id", "starter"),
                "status": account.get("subscription_status", "inactive"),
                "billing_day": account.get("billing_day"),
                "next_billing_date": account.get("next_billing_date").isoformat() if account.get("next_billing_date") else None
            }
        }
    
    def generate_html_statement(self, statement_data: Dict[str, Any]) -> str:
        """Generate HTML statement for download/print"""
        
        jr = statement_data["jobrocket_details"]
        cust = statement_data["customer_details"]
        summary = statement_data["summary"]
        payments = statement_data["payments"]
        
        # Status badge colors
        status_colors = {
            "completed": "#22c55e",
            "pending": "#eab308",
            "failed": "#ef4444",
            "cancelled": "#6b7280"
        }
        
        payments_html = ""
        for p in payments:
            status_color = status_colors.get(p["status"], "#6b7280")
            payments_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{p["date"]}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{p["description"]}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{p["reference"]}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                    <span style="background-color: {status_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                        {p["status"].upper()}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">
                    R {p["amount"]:,.2f}
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Statement - {statement_data["statement_number"]}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #1f2937;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #2563eb;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: 700;
                    color: #2563eb;
                }}
                .statement-info {{
                    text-align: right;
                }}
                .statement-number {{
                    font-size: 14px;
                    color: #6b7280;
                }}
                .details-section {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 40px;
                }}
                .detail-box {{
                    width: 48%;
                }}
                .detail-box h3 {{
                    font-size: 14px;
                    color: #6b7280;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                }}
                .detail-box p {{
                    margin: 4px 0;
                    font-size: 14px;
                }}
                .payments-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }}
                .payments-table th {{
                    background-color: #f3f4f6;
                    padding: 12px;
                    text-align: left;
                    font-size: 12px;
                    text-transform: uppercase;
                    color: #6b7280;
                }}
                .summary-box {{
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 30px;
                }}
                .summary-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                }}
                .summary-total {{
                    border-top: 2px solid #2563eb;
                    padding-top: 12px;
                    margin-top: 12px;
                    font-weight: 700;
                    font-size: 18px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 12px;
                    color: #6b7280;
                    text-align: center;
                }}
                @media print {{
                    body {{ padding: 20px; }}
                    .header {{ page-break-after: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <div class="logo">JobRocket</div>
                    <p style="color: #6b7280; font-size: 14px;">Billing Statement</p>
                </div>
                <div class="statement-info">
                    <div class="statement-number">Statement #: {statement_data["statement_number"]}</div>
                    <div style="margin-top: 8px;">
                        <strong>Period:</strong> {statement_data["period_start"][:10]} to {statement_data["period_end"][:10]}
                    </div>
                    <div>
                        <strong>Generated:</strong> {statement_data["generated_date"][:10]}
                    </div>
                </div>
            </div>
            
            <div class="details-section">
                <div class="detail-box">
                    <h3>From</h3>
                    <p><strong>{jr["company_name"]}</strong></p>
                    <p>{jr["address_line1"]}</p>
                    <p>{jr["address_line2"]}, {jr["city"]}</p>
                    <p>{jr["province"]} {jr["postal_code"]}</p>
                    <p>VAT: {jr["vat_number"]}</p>
                    <p>Reg: {jr["registration_number"]}</p>
                    <p style="margin-top: 10px;">{jr["email"]}</p>
                    <p>{jr["phone"]}</p>
                </div>
                <div class="detail-box">
                    <h3>Bill To</h3>
                    <p><strong>{cust["company_name"] or cust["contact_name"]}</strong></p>
                    <p>{cust["contact_name"]}</p>
                    <p>{cust["email"]}</p>
                    {f'<p>{cust["phone"]}</p>' if cust["phone"] else ''}
                    {f'<p>{cust["address"]}</p>' if cust["address"] else ''}
                    {f'<p>{cust["city"]}, {cust["province"]} {cust["postal_code"]}</p>' if cust["city"] else ''}
                    {f'<p>VAT: {cust["vat_number"]}</p>' if cust["vat_number"] else ''}
                    <p style="margin-top: 10px; font-size: 12px; color: #6b7280;">
                        Account ID: {cust["account_id"][:8].upper()}
                    </p>
                </div>
            </div>
            
            <table class="payments-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Reference</th>
                        <th>Status</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {payments_html if payments_html else '<tr><td colspan="5" style="text-align: center; padding: 40px; color: #6b7280;">No payments in this period</td></tr>'}
                </tbody>
            </table>
            
            <div class="summary-box">
                <div class="summary-row">
                    <span>Total Paid</span>
                    <span style="color: #22c55e; font-weight: 600;">R {summary["total_paid"]:,.2f}</span>
                </div>
                <div class="summary-row">
                    <span>Pending Payments</span>
                    <span style="color: #eab308;">R {summary["total_pending"]:,.2f}</span>
                </div>
                <div class="summary-row">
                    <span>Failed Payments</span>
                    <span style="color: #ef4444;">R {summary["total_failed"]:,.2f}</span>
                </div>
                <div class="summary-row summary-total">
                    <span>Net Amount Paid</span>
                    <span style="color: #2563eb;">R {summary["total_paid"]:,.2f}</span>
                </div>
            </div>
            
            <div class="footer">
                <p>{jr["company_name"]} | {jr["website"]}</p>
                <p>For billing inquiries, contact {jr["email"]} or {jr["phone"]}</p>
                <p style="margin-top: 10px;">
                    <strong>Banking Details:</strong> {jr["bank_name"]} | Account: {jr["bank_account"]} | Branch: {jr["bank_branch"]}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def get_billing_summary_for_period(
        self,
        account_id: str,
        months: int = 12
    ) -> Dict[str, Any]:
        """Get billing summary for the last N months"""
        
        now = datetime.utcnow()
        start_date = now - timedelta(days=months * 30)
        
        # Aggregate payments by month
        pipeline = [
            {
                "$match": {
                    "account_id": account_id,
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "paid": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "completed"]}, "$amount", 0]
                        }
                    }
                }
            },
            {"$sort": {"_id.year": -1, "_id.month": -1}}
        ]
        
        result = await self.db.payments.aggregate(pipeline).to_list(months)
        
        monthly_data = []
        for item in result:
            month_str = f"{item['_id']['year']}-{str(item['_id']['month']).zfill(2)}"
            monthly_data.append({
                "month": month_str,
                "total": item["total"] / 100,
                "paid": item["paid"] / 100,
                "count": item["count"]
            })
        
        return {
            "period_months": months,
            "monthly_data": monthly_data,
            "total_paid": sum(m["paid"] for m in monthly_data),
            "total_transactions": sum(m["count"] for m in monthly_data)
        }


def create_statement_service(db: AsyncIOMotorDatabase) -> StatementService:
    """Factory function to create StatementService"""
    return StatementService(db)
