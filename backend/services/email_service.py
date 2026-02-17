"""
Reusable Email Notification Service
Supports multiple email addresses for different notification types
"""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class EmailType(str, Enum):
    """Email types with corresponding sender addresses"""
    JOB_ALERTS = "job_alerts"
    JOB_APPLICATIONS = "job_applications"
    ACCOUNT_NOTIFICATIONS = "account_notifications"
    SYSTEM = "system"


class EmailConfig:
    """Email configuration loaded from environment variables"""
    
    @classmethod
    def get_smtp_server(cls):
        return os.environ.get("EMAIL_SMTP_SERVER", "mail.jobrocket.co.za")
    
    @classmethod
    def get_smtp_port(cls):
        return int(os.environ.get("EMAIL_SMTP_PORT", "465"))
    
    @classmethod
    def get_account(cls, email_type: EmailType) -> Optional[Dict]:
        """Get email account configuration for a specific type"""
        accounts = {
            EmailType.JOB_ALERTS: {
                "address": os.environ.get("EMAIL_JOB_ALERTS_ADDRESS"),
                "password": os.environ.get("EMAIL_JOB_ALERTS_PASSWORD"),
                "from_name": os.environ.get("EMAIL_JOB_ALERTS_FROM_NAME", "Job Rocket Alerts")
            },
            EmailType.JOB_APPLICATIONS: {
                "address": os.environ.get("EMAIL_JOB_APPLICATIONS_ADDRESS"),
                "password": os.environ.get("EMAIL_JOB_APPLICATIONS_PASSWORD"),
                "from_name": os.environ.get("EMAIL_JOB_APPLICATIONS_FROM_NAME", "Job Rocket Applications")
            },
            EmailType.ACCOUNT_NOTIFICATIONS: {
                "address": os.environ.get("EMAIL_ACCOUNT_NOTIFICATIONS_ADDRESS"),
                "password": os.environ.get("EMAIL_ACCOUNT_NOTIFICATIONS_PASSWORD"),
                "from_name": os.environ.get("EMAIL_ACCOUNT_NOTIFICATIONS_FROM_NAME", "Job Rocket")
            },
            EmailType.SYSTEM: {
                "address": os.environ.get("EMAIL_SYSTEM_ADDRESS"),
                "password": os.environ.get("EMAIL_SYSTEM_PASSWORD"),
                "from_name": os.environ.get("EMAIL_SYSTEM_FROM_NAME", "Job Rocket System")
            }
        }
        
        account = accounts.get(email_type)
        if account and account.get("address") and account.get("password"):
            return account
        return None


class EmailService:
    """
    Reusable email service for sending notifications
    Supports HTML emails, attachments, and multiple sender addresses
    """
    
    def send_email(
        self,
        email_type: EmailType,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict:
        """
        Send an email using the specified email type's account
        
        Args:
            email_type: Type of email (determines sender address)
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body of the email
            plain_content: Plain text fallback (optional)
            attachments: List of attachments [{"filename": str, "content": bytes}]
            cc: List of CC recipients
            bcc: List of BCC recipients
            
        Returns:
            Dict with success status and message
        """
        account = EmailConfig.get_account(email_type)
        if not account:
            return {
                "success": False,
                "error": f"Email account not configured for type: {email_type.value}"
            }
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{account['from_name']} <{account['address']}>"
            msg["To"] = to_email
            
            if cc:
                msg["Cc"] = ", ".join(cc)
            
            # Add plain text part
            if plain_content:
                part1 = MIMEText(plain_content, "plain")
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={attachment['filename']}"
                    )
                    msg.attach(part)
            
            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Create SSL context and send
            context = ssl.create_default_context()
            
            smtp_server = EmailConfig.get_smtp_server()
            smtp_port = EmailConfig.get_smtp_port()
            
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(account["address"], account["password"])
                server.sendmail(account["address"], recipients, msg.as_string())
            
            return {"success": True, "message": "Email sent successfully"}
            
        except smtplib.SMTPAuthenticationError as e:
            return {"success": False, "error": f"SMTP Authentication failed: {str(e)}"}
        except smtplib.SMTPException as e:
            return {"success": False, "error": f"SMTP error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to send email: {str(e)}"}
    
    def send_bulk_emails(
        self,
        email_type: EmailType,
        emails: List[Dict]
    ) -> List[Dict]:
        """
        Send multiple emails efficiently using a single SMTP connection
        
        Args:
            email_type: Type of email (determines sender address)
            emails: List of email dicts with keys: to_email, subject, html_content, plain_content
            
        Returns:
            List of results for each email
        """
        account = EmailConfig.get_account(email_type)
        if not account:
            return [{"success": False, "error": f"Email account not configured"} for _ in emails]
        
        results = []
        context = ssl.create_default_context()
        
        smtp_server = EmailConfig.get_smtp_server()
        smtp_port = EmailConfig.get_smtp_port()
        
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(account["address"], account["password"])
                
                for email_data in emails:
                    try:
                        msg = MIMEMultipart("alternative")
                        msg["Subject"] = email_data["subject"]
                        msg["From"] = f"{account['from_name']} <{account['address']}>"
                        msg["To"] = email_data["to_email"]
                        
                        if email_data.get("plain_content"):
                            msg.attach(MIMEText(email_data["plain_content"], "plain"))
                        
                        msg.attach(MIMEText(email_data["html_content"], "html"))
                        
                        server.sendmail(
                            account["address"],
                            [email_data["to_email"]],
                            msg.as_string()
                        )
                        results.append({"success": True, "to_email": email_data["to_email"]})
                        
                    except Exception as e:
                        results.append({
                            "success": False,
                            "to_email": email_data["to_email"],
                            "error": str(e)
                        })
                        
        except Exception as e:
            # If connection fails, mark all as failed
            results = [{"success": False, "error": str(e)} for _ in emails]
        
        return results


# Email Templates
class EmailTemplates:
    """HTML email templates for different notification types"""
    
    @staticmethod
    def get_base_template(content: str, preview_text: str = "") -> str:
        """Base HTML email template with Job Rocket branding"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Rocket</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, Helvetica, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
    <!-- Preview text -->
    <div style="display: none; max-height: 0; overflow: hidden;">
        {preview_text}
    </div>
    
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center; background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">
                                🚀 Job Rocket
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            {content}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8fafc; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="margin: 0 0 10px 0; color: #64748b; font-size: 14px;">
                                © {datetime.now().year} Job Rocket. All rights reserved.
                            </p>
                            <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                You're receiving this email because you have an account with Job Rocket.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    @staticmethod
    def job_alert_notification(
        user_name: str,
        job_title: str,
        company_name: str,
        location: str,
        work_type: str,
        salary_range: str,
        job_url: str,
        alert_name: str
    ) -> Dict[str, str]:
        """Job alert notification email template"""
        
        content = f"""
            <h2 style="margin: 0 0 20px 0; color: #1e293b; font-size: 24px;">
                New Job Match! 🎯
            </h2>
            
            <p style="margin: 0 0 20px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                Hi {user_name},
            </p>
            
            <p style="margin: 0 0 25px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                Great news! A new job matching your alert "<strong>{alert_name}</strong>" has just been posted.
            </p>
            
            <!-- Job Card -->
            <div style="background-color: #f8fafc; border-radius: 8px; padding: 25px; margin-bottom: 25px; border-left: 4px solid #2563eb;">
                <h3 style="margin: 0 0 15px 0; color: #1e293b; font-size: 20px;">
                    {job_title}
                </h3>
                <p style="margin: 0 0 10px 0; color: #2563eb; font-size: 16px; font-weight: 600;">
                    {company_name}
                </p>
                <table role="presentation" style="width: 100%; margin-top: 15px;">
                    <tr>
                        <td style="padding: 5px 0; color: #64748b; font-size: 14px;">
                            📍 <strong>Location:</strong> {location}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0; color: #64748b; font-size: 14px;">
                            💼 <strong>Work Type:</strong> {work_type}
                        </td>
                    </tr>
                    {f'<tr><td style="padding: 5px 0; color: #64748b; font-size: 14px;">💰 <strong>Salary:</strong> {salary_range}</td></tr>' if salary_range else ''}
                </table>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="{job_url}" style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: #ffffff; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px;">
                    View Job & Apply
                </a>
            </div>
            
            <p style="margin: 25px 0 0 0; color: #94a3b8; font-size: 13px; text-align: center;">
                You're receiving this because you set up a job alert on Job Rocket.
                <br>
                <a href="#" style="color: #2563eb;">Manage your alerts</a>
            </p>
"""
        
        plain_content = f"""
New Job Match!

Hi {user_name},

Great news! A new job matching your alert "{alert_name}" has just been posted.

{job_title}
{company_name}
Location: {location}
Work Type: {work_type}
{f'Salary: {salary_range}' if salary_range else ''}

View and apply: {job_url}

---
You're receiving this because you set up a job alert on Job Rocket.
"""
        
        return {
            "html": EmailTemplates.get_base_template(content, f"New job match: {job_title} at {company_name}"),
            "plain": plain_content
        }
    
    @staticmethod
    def job_application_received(
        recruiter_name: str,
        applicant_name: str,
        job_title: str,
        application_url: str
    ) -> Dict[str, str]:
        """Job application notification for recruiters"""
        
        content = f"""
            <h2 style="margin: 0 0 20px 0; color: #1e293b; font-size: 24px;">
                New Application Received! 📬
            </h2>
            
            <p style="margin: 0 0 20px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                Hi {recruiter_name},
            </p>
            
            <p style="margin: 0 0 25px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                <strong>{applicant_name}</strong> has applied for the position of <strong>{job_title}</strong>.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{application_url}" style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: #ffffff; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px;">
                    Review Application
                </a>
            </div>
"""
        
        plain_content = f"""
New Application Received!

Hi {recruiter_name},

{applicant_name} has applied for the position of {job_title}.

Review the application: {application_url}
"""
        
        return {
            "html": EmailTemplates.get_base_template(content, f"New application from {applicant_name}"),
            "plain": plain_content
        }


# Singleton instance
email_service = EmailService()
