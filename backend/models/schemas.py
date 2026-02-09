"""
JobRocket - Pydantic Models
All database models and request/response schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from .enums import (
    UserRole, AccountRole, SubscriptionStatus, BillingCycle,
    TierId, CompanyProfileLevel, FeatureId, AddonId,
    JobType, WorkType, ExperienceLevel, JobCategory,
    ApplicationStatus, EducationLevel,
    PaymentStatus, PaymentProvider,
    InvitationStatus, DiscountType, DiscountStatus
)


# ============================================
# Account Models (NEW - Multi-tenant core)
# ============================================

class Account(BaseModel):
    """
    Account/Tenant - The billing entity that owns subscriptions.
    Recruiters belong to an account, jobs are posted under accounts.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Company/Organization name
    owner_user_id: str  # User who created/owns the account
    
    # Subscription
    tier_id: TierId = TierId.STARTER
    subscription_status: SubscriptionStatus = SubscriptionStatus.PENDING
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    
    # Company Branding
    company_logo_url: Optional[str] = None
    company_cover_image_url: Optional[str] = None
    company_description: Optional[str] = None
    company_website: Optional[str] = None
    company_linkedin: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_location: Optional[str] = None
    
    # Usage Tracking
    current_user_count: int = 1
    extra_users_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AccountCreate(BaseModel):
    """Request model for creating an account"""
    name: str
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_location: Optional[str] = None


class AccountUpdate(BaseModel):
    """Request model for updating account details"""
    name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_cover_image_url: Optional[str] = None
    company_description: Optional[str] = None
    company_website: Optional[str] = None
    company_linkedin: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_location: Optional[str] = None


class AccountAddon(BaseModel):
    """Purchased add-on for an account"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    addon_id: AddonId
    feature_id: FeatureId  # The feature this unlocks
    purchased_date: datetime = Field(default_factory=datetime.utcnow)
    expires_date: Optional[datetime] = None  # None for one-time purchases
    is_active: bool = True
    price_paid: float
    payment_id: Optional[str] = None


# ============================================
# User Models (Updated for multi-tenancy)
# ============================================

class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: datetime
    end_date: Optional[datetime] = None
    current: bool = False
    description: str
    location: str


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    level: EducationLevel
    start_date: datetime
    end_date: Optional[datetime] = None
    current: bool = False
    grade: Optional[str] = None
    document_url: Optional[str] = None


class Achievement(BaseModel):
    title: str
    description: str
    date_achieved: datetime
    issuer: Optional[str] = None
    credential_url: Optional[str] = None


class ProfileProgress(BaseModel):
    """Job seeker profile completion tracking"""
    profile_picture: bool = False
    about_me: bool = False
    work_history: bool = False
    skills: bool = False
    education: bool = False
    achievements: bool = False
    intro_video: bool = False
    job_applications: int = 0
    email_alerts: bool = False
    total_points: int = 0


class User(BaseModel):
    """User model - both job seekers and recruiters"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.JOB_SEEKER
    
    # Account relationship (for recruiters only)
    account_id: Optional[str] = None
    account_role: Optional[AccountRole] = None  # owner, admin, recruiter, viewer
    
    # Profile fields (for job seekers)
    profile_picture_url: Optional[str] = None
    about_me: Optional[str] = None
    phone: Optional[str] = None
    location: str = ""
    current_salary_range: Optional[str] = None
    desired_salary_range: Optional[str] = None
    skills: List[str] = []
    work_experience: List[dict] = []  # List of WorkExperience as dicts
    education: List[dict] = []  # List of Education as dicts
    achievements: List[dict] = []  # List of Achievement as dicts
    intro_video_url: Optional[str] = None
    
    # Gamification (job seekers)
    profile_progress: Optional[ProfileProgress] = Field(default_factory=ProfileProgress)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class UserRegister(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.JOB_SEEKER
    # For recruiters - auto-create account with this name
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Response model for authentication"""
    access_token: str
    token_type: str
    user: dict


class UserProfileUpdate(BaseModel):
    """Request model for updating user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    about_me: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_salary_range: Optional[str] = None
    desired_salary_range: Optional[str] = None
    skills: Optional[List[str]] = None
    profile_picture_url: Optional[str] = None
    intro_video_url: Optional[str] = None


# ============================================
# Team & Invitation Models
# ============================================

class TeamInvitation(BaseModel):
    """Invitation to join an account"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    email: EmailStr
    first_name: str
    last_name: str
    account_role: AccountRole = AccountRole.RECRUITER
    invited_by: str  # User ID who sent invitation
    invitation_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: InvitationStatus = InvitationStatus.PENDING
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamInvitationCreate(BaseModel):
    """Request model for sending team invitation"""
    email: EmailStr
    first_name: str
    last_name: str
    account_role: AccountRole = AccountRole.RECRUITER


# ============================================
# Job Models
# ============================================

class Job(BaseModel):
    """Job listing model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str  # The account that owns this job
    posted_by: str  # User ID who posted the job
    
    # Job details
    title: str
    company_name: str  # Denormalized from account
    description: str
    location: str
    salary: str
    job_type: JobType
    work_type: WorkType
    industry: str
    experience: Optional[str] = None
    qualifications: Optional[str] = None
    
    # Application settings
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    
    # Dates
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=35))
    closing_date: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    featured: bool = False
    
    # Branding (denormalized from account)
    logo_url: Optional[str] = None


class JobCreate(BaseModel):
    """Request model for creating a job"""
    title: str
    description: str
    location: str
    salary: str
    job_type: JobType
    work_type: WorkType
    industry: str
    experience: Optional[str] = None
    qualifications: Optional[str] = None
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    closing_date: Optional[datetime] = None
    featured: bool = False


class JobApplication(BaseModel):
    """Job application model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    applicant_id: str  # User ID of the job seeker
    account_id: str  # Account that owns the job
    
    status: ApplicationStatus = ApplicationStatus.PENDING
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    additional_info: Optional[str] = None
    applicant_snapshot: Optional[dict] = None  # Profile snapshot at application time
    
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None


class JobApplicationCreate(BaseModel):
    """Request model for applying to a job"""
    job_id: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    additional_info: Optional[str] = None


# ============================================
# Payment Models
# ============================================

class Payment(BaseModel):
    """Payment record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    user_id: str  # User who made the payment
    
    # What was purchased
    payment_type: str  # "subscription", "addon", "extra_user"
    tier_id: Optional[TierId] = None  # For subscription payments
    addon_id: Optional[AddonId] = None  # For add-on payments
    
    # Amounts
    amount: float
    discount_code: Optional[str] = None
    discount_amount: float = 0.0
    final_amount: float
    currency: str = "ZAR"
    
    # Provider details
    provider: PaymentProvider = PaymentProvider.PAYFAST
    provider_reference: Optional[str] = None
    
    # Status
    status: PaymentStatus = PaymentStatus.PENDING
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


class SubscriptionPaymentRequest(BaseModel):
    """Request to initiate subscription payment"""
    tier_id: TierId
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    discount_code: Optional[str] = None


class AddonPaymentRequest(BaseModel):
    """Request to purchase an add-on"""
    addon_id: AddonId
    discount_code: Optional[str] = None


# ============================================
# Discount Models
# ============================================

class DiscountCode(BaseModel):
    """Discount code model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: float
    minimum_amount: Optional[float] = None
    maximum_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    usage_count: int = 0
    user_limit: Optional[int] = None
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    applicable_tiers: Optional[List[TierId]] = None
    status: DiscountStatus = DiscountStatus.ACTIVE
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class DiscountCodeCreate(BaseModel):
    """Request model for creating discount code"""
    code: str
    name: str
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: float
    minimum_amount: Optional[float] = None
    maximum_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_tiers: Optional[List[TierId]] = None


# ============================================
# Response Models
# ============================================

class AccountResponse(BaseModel):
    """Response model for account details"""
    id: str
    name: str
    tier_id: TierId
    tier_name: str
    subscription_status: SubscriptionStatus
    subscription_end_date: Optional[datetime]
    
    # Company info
    company_logo_url: Optional[str]
    company_description: Optional[str]
    company_website: Optional[str]
    company_industry: Optional[str]
    company_location: Optional[str]
    
    # User counts
    included_users: int
    current_user_count: int
    extra_users_count: int
    max_users: int
    
    # Features
    features: List[str]
    active_addons: List[str]
    available_addons: List[dict]


class TierResponse(BaseModel):
    """Response model for tier information"""
    id: str
    name: str
    price_monthly: int
    currency: str
    included_users: int
    extra_user_price: int
    features: List[str]
    company_profile_level: str
    is_current: bool = False
