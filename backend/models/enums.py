"""
JobRocket - Enums and Constants
All enum definitions and constant values used across the application
"""

from enum import Enum


# ============================================
# User & Account Enums
# ============================================

class UserRole(str, Enum):
    """User role within the platform"""
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class AccountRole(str, Enum):
    """User's role within an account (for multi-user accounts)"""
    OWNER = "owner"
    ADMIN = "admin"
    RECRUITER = "recruiter"
    VIEWER = "viewer"


class SubscriptionStatus(str, Enum):
    """Account subscription status"""
    ACTIVE = "active"
    TRIAL = "trial"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class BillingCycle(str, Enum):
    """Billing cycle for subscriptions"""
    MONTHLY = "monthly"
    ANNUALLY = "annually"


# ============================================
# Tier & Feature Enums
# ============================================

class TierId(str, Enum):
    """Subscription tier identifiers"""
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class CompanyProfileLevel(str, Enum):
    """Company profile feature levels by tier"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    FEATURED = "featured"
    WHITE_LABEL = "white_label"


class FeatureId(str, Enum):
    """All feature identifiers for tier-gating"""
    # Account & Access
    ACCOUNT_RECRUITER_ACCOUNT = "ACCOUNT_RECRUITER_ACCOUNT"
    ACCOUNT_COMPANY_PROFILE = "ACCOUNT_COMPANY_PROFILE"
    ACCOUNT_MULTI_USER_ACCESS = "ACCOUNT_MULTI_USER_ACCESS"
    ACCOUNT_ROLE_BASED_PERMISSIONS = "ACCOUNT_ROLE_BASED_PERMISSIONS"
    
    # Job Posting
    JOB_UNLIMITED_POSTS = "JOB_UNLIMITED_POSTS"
    JOB_DURATION_35_DAYS = "JOB_DURATION_35_DAYS"
    JOB_TEMPLATES = "JOB_TEMPLATES"
    JOB_BULK_UPLOAD = "JOB_BULK_UPLOAD"
    
    # Candidate Applications
    CANDIDATE_APPLICANT_INBOX = "CANDIDATE_APPLICANT_INBOX"
    CANDIDATE_APPLICANT_FILTERING = "CANDIDATE_APPLICANT_FILTERING"
    CANDIDATE_STATUS_TRACKING = "CANDIDATE_STATUS_TRACKING"
    CANDIDATE_NOTES_TAGS = "CANDIDATE_NOTES_TAGS"
    
    # CV Database / Talent Pool
    TALENT_CV_DATABASE = "TALENT_CV_DATABASE"
    TALENT_PASSIVE_SEARCH = "TALENT_PASSIVE_SEARCH"
    TALENT_POOL_ALERTS = "TALENT_POOL_ALERTS"
    TALENT_CONTACT_ACCESS = "TALENT_CONTACT_ACCESS"
    
    # AI & Matching
    AI_MATCH_SCORE = "AI_MATCH_SCORE"
    AI_AUTO_RANKED = "AI_AUTO_RANKED"
    AI_SKILLS_MATCHING = "AI_SKILLS_MATCHING"
    
    # Distribution
    DIST_PLATFORM = "DIST_PLATFORM"
    DIST_EMAIL = "DIST_EMAIL"
    DIST_WHATSAPP = "DIST_WHATSAPP"
    DIST_SOCIAL_MEDIA = "DIST_SOCIAL_MEDIA"
    DIST_MONTHLY_CAMPAIGNS = "DIST_MONTHLY_CAMPAIGNS"
    
    # Employer Branding
    BRAND_PROFILE_PAGE = "BRAND_PROFILE_PAGE"
    BRAND_FEATURED_LISTINGS = "BRAND_FEATURED_LISTINGS"
    BRAND_EMPLOYER_VIDEO = "BRAND_EMPLOYER_VIDEO"
    BRAND_BRANDING_PACK = "BRAND_BRANDING_PACK"
    BRAND_CUSTOM_STYLING = "BRAND_CUSTOM_STYLING"
    
    # Recruiter Tools
    TOOLS_CANDIDATE_PIPELINE = "TOOLS_CANDIDATE_PIPELINE"
    TOOLS_INTERVIEW_SCHEDULING = "TOOLS_INTERVIEW_SCHEDULING"
    TOOLS_INTERNAL_COLLABORATION = "TOOLS_INTERNAL_COLLABORATION"
    TOOLS_EXPORT_CSV = "TOOLS_EXPORT_CSV"
    
    # Analytics & Reporting
    ANALYTICS_JOB_PERFORMANCE = "ANALYTICS_JOB_PERFORMANCE"
    ANALYTICS_CONVERSION_RATES = "ANALYTICS_CONVERSION_RATES"
    ANALYTICS_MONTHLY_REPORTS = "ANALYTICS_MONTHLY_REPORTS"
    
    # Integrations
    INTEGRATION_ATS_EXPORT = "INTEGRATION_ATS_EXPORT"
    INTEGRATION_API_ACCESS = "INTEGRATION_API_ACCESS"
    
    # Support & SLA
    SUPPORT_EMAIL = "SUPPORT_EMAIL"
    SUPPORT_PRIORITY = "SUPPORT_PRIORITY"
    SUPPORT_DEDICATED_MANAGER = "SUPPORT_DEDICATED_MANAGER"
    SUPPORT_SLA = "SUPPORT_SLA"
    
    # Job Seeker Interaction
    SEEKER_PRIORITY_ACCESS = "SEEKER_PRIORITY_ACCESS"
    SEEKER_HOT_ALERTS = "SEEKER_HOT_ALERTS"


class AddonId(str, Enum):
    """Add-on identifiers for purchasable features"""
    CANDIDATE_NOTES = "addon_candidate_notes"
    TALENT_ALERTS = "addon_talent_alerts"
    WHATSAPP_DIST = "addon_whatsapp_dist"
    SOCIAL_DIST = "addon_social_dist"
    MONTHLY_CAMPAIGNS = "addon_monthly_campaigns"
    FEATURED_LISTINGS = "addon_featured_listings"
    EMPLOYER_VIDEO = "addon_employer_video"
    BRANDING_PACK = "addon_branding_pack"
    INTERVIEW_SCHED = "addon_interview_sched"
    ATS_EXPORT = "addon_ats_export"
    PRIORITY_ACCESS = "addon_priority_access"
    HOT_ALERTS = "addon_hot_alerts"


# ============================================
# Job Related Enums
# ============================================

class JobType(str, Enum):
    PERMANENT = "Permanent"
    CONTRACT = "Contract"


class WorkType(str, Enum):
    REMOTE = "Remote"
    ONSITE = "Onsite"
    HYBRID = "Hybrid"


class ExperienceLevel(str, Enum):
    ENTRY = "Entry Level"
    JUNIOR = "Junior"
    MID = "Mid Level"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXECUTIVE = "Executive"


class JobCategory(str, Enum):
    ENGINEERING = "Engineering, Technical"
    PRODUCTION = "Production & Manufacturing"
    IT_TELECOM = "IT & Telecommunications"
    SALES = "Sales & Purchasing"
    ACCOUNTING = "Accounting, Auditing"
    BANKING = "Banking, Finance, Insurance"
    MARKETING = "Marketing & Communications"
    HUMAN_RESOURCES = "Human Resources"
    OPERATIONS = "Operations"
    CUSTOMER_SERVICE = "Customer Service"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    CERTIFICATE = "Certificate"
    DIPLOMA = "Diploma"
    BACHELORS = "Bachelor's Degree"
    MASTERS = "Master's Degree"
    PHD = "PhD"
    OTHER = "Other"


# ============================================
# Payment Enums
# ============================================

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentProvider(str, Enum):
    PAYFAST = "payfast"
    STRIPE = "stripe"


# ============================================
# Invitation Enums
# ============================================

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# ============================================
# Discount Enums
# ============================================

class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class DiscountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
