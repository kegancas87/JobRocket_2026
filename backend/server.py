from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from enum import Enum
import jwt
from passlib.context import CryptContext
import secrets
import pandas as pd
import io
import csv
import hashlib
import urllib.parse


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Payfast Configuration
PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
PAYFAST_SANDBOX = os.environ.get('PAYFAST_SANDBOX', 'False').lower() == 'true'
BASE_URL = os.environ.get('BASE_URL', 'https://job-expiry-fix.preview.emergentagent.com')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Job Rocket API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Payfast utility functions
def generate_payfast_signature(data: dict, passphrase: str = None) -> str:
    """
    Generate PayFast signature for payment requests
    """
    # Remove empty values and signature field if it exists
    filtered_data = {k: str(v) for k, v in data.items() if v is not None and v != '' and k != 'signature'}
    
    # Sort parameters alphabetically
    sorted_params = sorted(filtered_data.items())
    
    # Create parameter string
    param_string = '&'.join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
    
    # Add passphrase if provided
    if passphrase:
        param_string += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
    
    # Generate MD5 hash
    signature = hashlib.md5(param_string.encode('utf-8')).hexdigest()
    
    return signature


def verify_payfast_signature(data: dict, passphrase: str = None) -> bool:
    """
    Verify PayFast signature for webhook notifications
    """
    if 'signature' not in data:
        return False
    
    received_signature = data['signature']
    calculated_signature = generate_payfast_signature(data, passphrase)
    
    return received_signature == calculated_signature


# Enums for job-related data
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

class UserRole(str, Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    CERTIFICATE = "Certificate"
    DIPLOMA = "Diploma"
    BACHELORS = "Bachelor's Degree"
    MASTERS = "Master's Degree"
    PHD = "PhD"
    OTHER = "Other"

class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class DiscountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


# Authentication Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.JOB_SEEKER

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

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
    profile_picture: bool = False  # 5 points
    about_me: bool = False         # 10 points
    work_history: bool = False     # 10 points
    skills: bool = False           # 20 points (5+ skills)
    education: bool = False        # 10 points
    achievements: bool = False     # 10 points
    intro_video: bool = False      # 20 points
    job_applications: int = 0      # 10 points (5 applications)
    email_alerts: bool = False     # 5 points
    total_points: int = 0

class CompanyProfile(BaseModel):
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_cover_image_url: Optional[str] = None
    company_description: Optional[str] = None
    company_website: Optional[str] = None
    company_linkedin: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    company_location: Optional[str] = None

class CompanyBranch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    name: str
    location: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_headquarters: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TeamMemberRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    MANAGER = "manager"
    VIEWER = "viewer"

class CompanyMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    user_id: str
    role: TeamMemberRole = TeamMemberRole.RECRUITER
    branch_ids: List[str] = []  # Can be associated with multiple branches
    invited_by: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class TeamInvitation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: TeamMemberRole = TeamMemberRole.RECRUITER
    branch_ids: List[str] = []
    invited_by: str
    invitation_token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    status: InvitationStatus = InvitationStatus.PENDING
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RecruiterProgress(BaseModel):
    company_logo: bool = False         # 15 points
    cover_image: bool = False          # 10 points
    company_description: bool = False  # 20 points (100+ chars)
    company_size: bool = False         # 10 points
    website_link: bool = False         # 15 points
    linkedin_link: bool = False        # 10 points
    first_job_posted: bool = False     # 20 points
    # New company structure points
    headquarters_setup: bool = False   # 5 points (automatic when company is created)
    first_branch_added: bool = False   # 10 points
    first_team_member: bool = False    # 15 points
    total_points: int = 0

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.JOB_SEEKER
    
    # Profile fields (for job seekers)
    profile_picture_url: Optional[str] = None
    about_me: Optional[str] = None
    phone: Optional[str] = None
    location: str = ""
    current_salary_range: Optional[str] = None
    desired_salary_range: Optional[str] = None
    skills: List[str] = []
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    achievements: List[Achievement] = []
    intro_video_url: Optional[str] = None
    
    # Company profile fields (for recruiters)
    company_profile: Optional[CompanyProfile] = Field(default_factory=CompanyProfile)
    
    # Gamification
    profile_progress: Optional[ProfileProgress] = Field(default_factory=ProfileProgress)
    recruiter_progress: Optional[RecruiterProgress] = Field(default_factory=RecruiterProgress)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class UserProfileUpdate(BaseModel):
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

class CompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_cover_image_url: Optional[str] = None
    company_description: Optional[str] = None
    company_website: Optional[str] = None
    company_linkedin: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    company_location: Optional[str] = None

class BranchCreate(BaseModel):
    name: str
    location: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_headquarters: bool = False

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_headquarters: Optional[bool] = None

class TeamInvitationCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: TeamMemberRole = TeamMemberRole.RECRUITER
    branch_ids: List[str] = []

class TeamMemberUpdate(BaseModel):
    role: Optional[TeamMemberRole] = None
    branch_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None


# Authentication helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    
    # Remove MongoDB _id field to avoid serialization issues
    if "_id" in user:
        del user["_id"]
    
    # Handle legacy data formats for education and achievements
    if "education" in user and user["education"]:
        cleaned_education = []
        for edu in user["education"]:
            if isinstance(edu, dict):
                # Add missing level field if not present
                if "level" not in edu:
                    edu["level"] = EducationLevel.BACHELORS  # Default value
                # Ensure dates are datetime objects
                if "start_date" in edu and isinstance(edu["start_date"], str):
                    try:
                        edu["start_date"] = datetime.fromisoformat(edu["start_date"])
                    except:
                        edu["start_date"] = datetime.utcnow()
                if "end_date" in edu and isinstance(edu["end_date"], str):
                    try:
                        edu["end_date"] = datetime.fromisoformat(edu["end_date"])
                    except:
                        edu["end_date"] = None
                cleaned_education.append(edu)
        user["education"] = cleaned_education
    
    # Handle legacy achievements (convert strings to Achievement objects)
    if "achievements" in user and user["achievements"]:
        cleaned_achievements = []
        for achievement in user["achievements"]:
            if isinstance(achievement, str):
                # Convert string to Achievement object
                achievement_obj = {
                    "title": achievement,
                    "description": achievement,
                    "date_achieved": datetime.utcnow(),
                    "issuer": None,
                    "credential_url": None
                }
                cleaned_achievements.append(achievement_obj)
            elif isinstance(achievement, dict):
                # Ensure required fields exist
                if "title" not in achievement:
                    achievement["title"] = "Achievement"
                if "description" not in achievement:
                    achievement["description"] = achievement.get("title", "Achievement")
                if "date_achieved" not in achievement:
                    achievement["date_achieved"] = datetime.utcnow()
                elif isinstance(achievement["date_achieved"], str):
                    try:
                        achievement["date_achieved"] = datetime.fromisoformat(achievement["date_achieved"])
                    except:
                        achievement["date_achieved"] = datetime.utcnow()
                cleaned_achievements.append(achievement)
        user["achievements"] = cleaned_achievements
    
    return User(**user)

def calculate_profile_progress(user: User) -> ProfileProgress:
    """Calculate and update user's profile completion progress"""
    progress = ProfileProgress()
    points = 0
    
    # Profile picture (5 points)
    if user.profile_picture_url:
        progress.profile_picture = True
        points += 5
    
    # About me (10 points)
    if user.about_me and len(user.about_me.strip()) >= 50:
        progress.about_me = True
        points += 10
    
    # Work history (10 points)
    if user.work_experience and len(user.work_experience) > 0:
        progress.work_history = True
        points += 10
    
    # Skills - at least 5 (20 points)
    if user.skills and len(user.skills) >= 5:
        progress.skills = True
        points += 20
    
    # Education with document (10 points)
    if user.education and any(edu.document_url for edu in user.education):
        progress.education = True
        points += 10
    
    # Achievements (10 points)
    if user.achievements and len(user.achievements) > 0:
        progress.achievements = True
        points += 10
    
    # Intro video (20 points)
    if user.intro_video_url:
        progress.intro_video = True
        points += 20
    
    # Job applications (10 points for 5+ applications)
    if progress.job_applications >= 5:
        points += 10
    
    # Email alerts setup (5 points)
    if progress.email_alerts:
        points += 5
    
    progress.total_points = points
    return progress

def calculate_recruiter_progress(user: User) -> RecruiterProgress:
    """Calculate and update recruiter's company profile completion progress"""
    progress = RecruiterProgress()
    points = 0
    
    if not user.company_profile:
        progress.total_points = 0
        return progress
    
    company = user.company_profile
    
    # Company logo (15 points)
    if company.company_logo_url:
        progress.company_logo = True
        points += 15
    
    # Cover image (10 points)
    if company.company_cover_image_url:
        progress.cover_image = True
        points += 10
    
    # Company description - at least 100 characters (20 points)
    if company.company_description and len(company.company_description.strip()) >= 100:
        progress.company_description = True
        points += 20
    
    # Company size (10 points)
    if company.company_size:
        progress.company_size = True
        points += 10
    
    # Website link (15 points)
    if company.company_website:
        progress.website_link = True
        points += 15
    
    # LinkedIn link (10 points)
    if company.company_linkedin:
        progress.linkedin_link = True
        points += 10
    
    # Headquarters setup (5 points) - automatic when company is created
    if company.company_name and company.company_location:
        progress.headquarters_setup = True
        points += 5
    
    # First job posted (20 points) - we'll track this separately
    # First branch added (10 points) - we'll check this from database
    # First team member (15 points) - we'll check this from database
    
    progress.total_points = points
    return progress

async def calculate_recruiter_progress_with_structure(user: User) -> RecruiterProgress:
    """Calculate recruiter progress including company structure"""
    progress = calculate_recruiter_progress(user)
    
    if user.role != UserRole.RECRUITER:
        return progress
    
    # Check for branches
    branches = await db.company_branches.find({"company_id": user.id}).to_list(1000)
    if branches and len(branches) > 0:
        progress.first_branch_added = True
        progress.total_points += 10
    
    # Check for team members
    members = await db.company_members.find({"company_id": user.id, "is_active": True}).to_list(1000)
    if members and len(members) > 0:
        progress.first_team_member = True
        progress.total_points += 15
    
    # Cap at 100 points
    progress.total_points = min(progress.total_points, 100)
    
    return progress


# Models
class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company_id: str
    company_name: str
    description: str
    location: str
    salary: str
    job_type: JobType
    work_type: WorkType
    industry: str
    experience: Optional[str] = None
    qualifications: Optional[str] = None
    posted_by: str  # User ID who posted the job
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=35))
    closing_date: Optional[datetime] = None
    is_active: bool = True
    featured: bool = False
    logo_url: Optional[str] = None  # Company logo URL
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expiry_date
    
    @property
    def days_since_posted(self) -> int:
        return (datetime.utcnow() - self.posted_date).days

class JobCreate(BaseModel):
    title: str
    company_id: str
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
    # expiry_date will be automatically set to 35 days from now

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class JobApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    applicant_id: str  # User ID of the job seeker
    company_id: str
    status: ApplicationStatus = ApplicationStatus.PENDING
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    additional_info: Optional[str] = None
    applicant_snapshot: Optional[dict] = None  # Snapshot of applicant profile at time of application
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None  # Recruiter who reviewed
    notes: Optional[str] = None  # Internal recruiter notes

class JobApplicationCreate(BaseModel):
    job_id: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    additional_info: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None

class PackageType(str, Enum):
    TWO_LISTINGS = "two_listings"
    FIVE_LISTINGS = "five_listings" 
    UNLIMITED_LISTINGS = "unlimited_listings"
    CV_SEARCH_10 = "cv_search_10"
    CV_SEARCH_20 = "cv_search_20"
    CV_SEARCH_UNLIMITED = "cv_search_unlimited"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class Package(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    package_type: PackageType
    price: float  # In South African Rand
    is_subscription: bool = False
    duration_days: Optional[int] = None  # For subscriptions
    job_listings_included: Optional[int] = None  # None = unlimited
    cv_searches_included: Optional[int] = None  # None = unlimited  
    job_expiry_days: int = 35  # Default job expiry
    is_active: bool = True

class UserPackage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    package_id: str
    package_type: PackageType
    purchased_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None  # For subscriptions
    job_listings_remaining: Optional[int] = None  # None = unlimited
    cv_searches_remaining: Optional[int] = None  # None = unlimited
    is_active: bool = True
    subscription_status: Optional[SubscriptionStatus] = None

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    package_id: str
    amount: float  # Original package amount
    discount_code: Optional[str] = None  # Applied discount code
    discount_amount: float = 0.0  # Discount amount applied
    final_amount: float  # Final amount after discount
    currency: str = "ZAR"
    payment_method: str = "payfast"
    payment_reference: Optional[str] = None  # Payfast payment reference
    status: PaymentStatus = PaymentStatus.PENDING
    created_date: datetime = Field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None
    failure_reason: Optional[str] = None

class DiscountCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # The discount code (e.g., "WELCOME20")
    name: str  # Human-friendly name (e.g., "Welcome 20% Off")
    description: Optional[str] = None
    discount_type: DiscountType  # percentage or fixed_amount
    discount_value: float  # 20 (for 20%) or 500 (for R500 off)
    minimum_amount: Optional[float] = None  # Minimum purchase amount
    maximum_discount: Optional[float] = None  # Max discount for percentage types
    usage_limit: Optional[int] = None  # Total usage limit (None = unlimited)
    usage_count: int = 0  # Current usage count
    user_limit: Optional[int] = None  # Usage limit per user (None = unlimited)
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None  # Expiry date (None = no expiry)
    applicable_packages: Optional[List[PackageType]] = None  # Specific packages (None = all)
    status: DiscountStatus = DiscountStatus.ACTIVE
    created_by: str  # Admin user ID
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: Optional[datetime] = None

class DiscountCodeCreate(BaseModel):
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
    applicable_packages: Optional[List[PackageType]] = None

class DiscountCodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    discount_value: Optional[float] = None
    minimum_amount: Optional[float] = None
    maximum_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_packages: Optional[List[PackageType]] = None
    status: Optional[DiscountStatus] = None

class BulkJobCreate(BaseModel):
    jobs: List[JobCreate]
    company_id: Optional[str] = None  # Can override individual job company_id

class DiscountValidationRequest(BaseModel):
    code: str
    package_type: PackageType
    package_price: Optional[float] = None

# Initialize default packages
DEFAULT_PACKAGES = [
    {
        "name": "Two Listings Package",
        "description": "Perfect for smaller companies. Two job listings that never expire until used.",
        "package_type": PackageType.TWO_LISTINGS,
        "price": 2800.00,
        "is_subscription": False,
        "job_listings_included": 2,
        "job_expiry_days": 30,
        "cv_searches_included": 0
    },
    {
        "name": "Five Listings Package", 
        "description": "Great for growing companies. Five job listings available whenever you need them.",
        "package_type": PackageType.FIVE_LISTINGS,
        "price": 4150.00,
        "is_subscription": False,
        "job_listings_included": 5,
        "job_expiry_days": 30,
        "cv_searches_included": 0
    },
    {
        "name": "Unlimited Listings Package",
        "description": "For hiring at scale. Unlimited job postings plus 10 free CV searches monthly.",
        "package_type": PackageType.UNLIMITED_LISTINGS,
        "price": 3899.00,
        "is_subscription": True,
        "duration_days": 30,
        "job_listings_included": None,  # Unlimited
        "job_expiry_days": 35,
        "cv_searches_included": 10
    },
    {
        "name": "10 CV Searches",
        "description": "Search through 10 candidate CVs to find the perfect match.",
        "package_type": PackageType.CV_SEARCH_10,
        "price": 699.00,
        "is_subscription": False,
        "job_listings_included": 0,
        "cv_searches_included": 10
    },
    {
        "name": "20 CV Searches",
        "description": "Extended CV search access for thorough candidate screening.",
        "package_type": PackageType.CV_SEARCH_20,
        "price": 1299.00,
        "is_subscription": False,
        "job_listings_included": 0,
        "cv_searches_included": 20
    },
    {
        "name": "Unlimited CV Searches",
        "description": "Unlimited access to our CV database for comprehensive talent acquisition.",
        "package_type": PackageType.CV_SEARCH_UNLIMITED,
        "price": 2899.00,
        "is_subscription": True,
        "duration_days": 30,
        "job_listings_included": 0,
        "cv_searches_included": None  # Unlimited
    }
]

class JobSearchFilters(BaseModel):
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    category: Optional[JobCategory] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    featured_only: Optional[bool] = None

class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: str

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


async def validate_discount_code(code: str, user_id: str, package_type: PackageType, package_price: float):
    """
    Validate discount code and calculate discount amount
    Returns dict with validation result and discount details
    """
    if not code:
        return {"valid": False, "error": "No discount code provided"}
    
    # Get discount code from database
    discount_doc = await db.discount_codes.find_one({"code": code.upper()})
    if not discount_doc:
        return {"valid": False, "error": "Invalid discount code"}
    
    if "_id" in discount_doc:
        del discount_doc["_id"]
    
    discount = DiscountCode(**discount_doc)
    
    # Check if discount code is active
    if discount.status != DiscountStatus.ACTIVE:
        return {"valid": False, "error": "Discount code is inactive"}
    
    # Check validity dates
    now = datetime.utcnow()
    if discount.valid_from > now:
        return {"valid": False, "error": "Discount code is not yet valid"}
    
    if discount.valid_until and discount.valid_until < now:
        return {"valid": False, "error": "Discount code has expired"}
    
    # Check usage limits
    if discount.usage_limit and discount.usage_count >= discount.usage_limit:
        return {"valid": False, "error": "Discount code usage limit exceeded"}
    
    # Check user-specific usage limit
    if discount.user_limit:
        user_usage_count = await db.payments.count_documents({
            "user_id": user_id,
            "discount_code": code.upper(),
            "status": PaymentStatus.COMPLETED
        })
        if user_usage_count >= discount.user_limit:
            return {"valid": False, "error": "Personal usage limit for this discount code exceeded"}
    
    # Check if package is applicable
    if discount.applicable_packages and package_type not in discount.applicable_packages:
        return {"valid": False, "error": "Discount code not applicable to this package"}
    
    # Check minimum amount requirement
    if discount.minimum_amount and package_price < discount.minimum_amount:
        return {"valid": False, "error": f"Minimum purchase amount of R{discount.minimum_amount:.2f} required"}
    
    # Calculate discount amount
    if discount.discount_type == DiscountType.PERCENTAGE:
        discount_amount = package_price * (discount.discount_value / 100)
        if discount.maximum_discount:
            discount_amount = min(discount_amount, discount.maximum_discount)
    else:  # FIXED_AMOUNT
        discount_amount = min(discount.discount_value, package_price)
    
    # Ensure discount doesn't exceed package price
    discount_amount = min(discount_amount, package_price)
    
    return {
        "valid": True,
        "discount": discount,
        "discount_amount": discount_amount,
        "final_price": package_price - discount_amount
    }


# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user_dict = user_data.dict()
    del user_dict['password']
    user_dict['password_hash'] = hashed_password
    
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_obj.id}, expires_delta=access_token_expires
    )
    
    # Return token and user info (without password)
    user_dict = user_obj.dict()
    del user_dict['password_hash']
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user"""
    user = await db.users.find_one({"email": login_data.email})
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    # Return token and user info (without password and _id)
    user_dict = user.copy()
    if "_id" in user_dict:
        del user_dict["_id"]
    del user_dict['password_hash']
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile with progress"""
    # Calculate and update progress based on user role
    if current_user.role == UserRole.JOB_SEEKER:
        progress = calculate_profile_progress(current_user)
        # Update progress in database
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"profile_progress": progress.dict()}}
        )
        current_user.profile_progress = progress
    elif current_user.role == UserRole.RECRUITER:
        progress = await calculate_recruiter_progress_with_structure(current_user)
        # Update progress in database
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"recruiter_progress": progress.dict()}}
        )
        current_user.recruiter_progress = progress
    
    # Return user without password hash
    user_dict = current_user.dict()
    return user_dict


# Company Structure Routes
@api_router.post("/company/branches", response_model=CompanyBranch)
async def create_branch(
    branch_data: BranchCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new company branch"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can create branches"
        )
    
    # Use user ID as company ID (each recruiter represents their company)
    branch_dict = branch_data.dict()
    branch_dict["company_id"] = current_user.id
    
    branch_obj = CompanyBranch(**branch_dict)
    await db.company_branches.insert_one(branch_obj.dict())
    
    return branch_obj

@api_router.get("/company/branches", response_model=List[CompanyBranch])
async def get_branches(current_user: User = Depends(get_current_user)):
    """Get all branches for the current company"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view branches"
        )
    
    branches = await db.company_branches.find({"company_id": current_user.id}).to_list(1000)
    return [CompanyBranch(**branch) for branch in branches]

@api_router.put("/company/branches/{branch_id}", response_model=CompanyBranch)
async def update_branch(
    branch_id: str,
    branch_update: BranchUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a company branch"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update branches"
        )
    
    # Check if branch belongs to current user's company
    existing_branch = await db.company_branches.find_one({
        "id": branch_id,
        "company_id": current_user.id
    })
    
    if not existing_branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    update_data = {k: v for k, v in branch_update.dict().items() if v is not None}
    
    await db.company_branches.update_one(
        {"id": branch_id},
        {"$set": update_data}
    )
    
    updated_branch = await db.company_branches.find_one({"id": branch_id})
    return CompanyBranch(**updated_branch)

@api_router.delete("/company/branches/{branch_id}")
async def delete_branch(
    branch_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a company branch"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can delete branches"
        )
    
    # Check if branch belongs to current user's company
    existing_branch = await db.company_branches.find_one({
        "id": branch_id,
        "company_id": current_user.id
    })
    
    if not existing_branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    # Remove branch associations from team members
    await db.company_members.update_many(
        {"company_id": current_user.id},
        {"$pull": {"branch_ids": branch_id}}
    )
    
    # Delete the branch
    await db.company_branches.delete_one({"id": branch_id})
    
    return {"message": "Branch deleted successfully"}


# Team Management Routes
@api_router.post("/company/invite", response_model=TeamInvitation)
async def invite_team_member(
    invitation_data: TeamInvitationCreate,
    current_user: User = Depends(get_current_user)
):
    """Invite a new team member to the company"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can invite team members"
        )
    
    # Check if user is already invited or exists
    existing_invitation = await db.team_invitations.find_one({
        "email": invitation_data.email,
        "company_id": current_user.id,
        "status": InvitationStatus.PENDING
    })
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a pending invitation"
        )
    
    # Check if user already exists in the company
    existing_user = await db.users.find_one({"email": invitation_data.email})
    if existing_user:
        existing_member = await db.company_members.find_one({
            "company_id": current_user.id,
            "user_id": existing_user["id"],
            "is_active": True
        })
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a team member"
            )
    
    # Validate branch IDs
    if invitation_data.branch_ids:
        for branch_id in invitation_data.branch_ids:
            branch = await db.company_branches.find_one({
                "id": branch_id,
                "company_id": current_user.id
            })
            if not branch:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Branch {branch_id} not found"
                )
    
    # Create invitation
    invitation_dict = invitation_data.dict()
    invitation_dict["company_id"] = current_user.id
    invitation_dict["invited_by"] = current_user.id
    
    invitation_obj = TeamInvitation(**invitation_dict)
    await db.team_invitations.insert_one(invitation_obj.dict())
    
    # TODO: Send email invitation (will be implemented with SendGrid later)
    # For now, we'll just create the invitation and show success
    # Later: send_invitation_email(invitation_obj)
    
    return invitation_obj

@api_router.get("/company/invitations", response_model=List[TeamInvitation])
async def get_company_invitations(current_user: User = Depends(get_current_user)):
    """Get all pending invitations for the company"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view invitations"
        )
    
    invitations = await db.team_invitations.find({
        "company_id": current_user.id
    }).sort("created_at", -1).to_list(1000)
    
    return [TeamInvitation(**inv) for inv in invitations]

@api_router.post("/company/invitations/{invitation_id}/cancel")
async def cancel_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a pending invitation"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can cancel invitations"
        )
    
    result = await db.team_invitations.update_one(
        {
            "id": invitation_id,
            "company_id": current_user.id,
            "status": InvitationStatus.PENDING
        },
        {"$set": {"status": InvitationStatus.CANCELLED}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already processed"
        )
    
    return {"message": "Invitation cancelled successfully"}

@api_router.get("/company/members", response_model=List[dict])
async def get_team_members(current_user: User = Depends(get_current_user)):
    """Get all team members for the company"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view team members"
        )
    
    # Get company members with user details
    members = await db.company_members.find({
        "company_id": current_user.id,
        "is_active": True
    }).to_list(1000)
    
    result = []
    for member in members:
        user = await db.users.find_one({"id": member["user_id"]})
        if user:
            if "_id" in user:
                del user["_id"]
            
            # Get branch details
            branches = []
            if member["branch_ids"]:
                for branch_id in member["branch_ids"]:
                    branch = await db.company_branches.find_one({"id": branch_id})
                    if branch:
                        branches.append(CompanyBranch(**branch))
            
            member_info = {
                "member_id": member["id"],
                "user": user,
                "role": member["role"],
                "branches": branches,
                "joined_at": member["joined_at"],
                "is_active": member["is_active"]
            }
            result.append(member_info)
    
    return result

@api_router.put("/company/members/{member_id}")
async def update_team_member(
    member_id: str,
    member_update: TeamMemberUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update team member details"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update team members"
        )
    
    # Validate branch IDs if provided
    if member_update.branch_ids:
        for branch_id in member_update.branch_ids:
            branch = await db.company_branches.find_one({
                "id": branch_id,
                "company_id": current_user.id
            })
            if not branch:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Branch {branch_id} not found"
                )
    
    update_data = {k: v for k, v in member_update.dict().items() if v is not None}
    
    result = await db.company_members.update_one(
        {"id": member_id, "company_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    return {"message": "Team member updated successfully"}

@api_router.delete("/company/members/{member_id}")
async def remove_team_member(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove team member from company"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can remove team members"
        )
    
    result = await db.company_members.update_one(
        {"id": member_id, "company_id": current_user.id},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    return {"message": "Team member removed successfully"}


# Invitation Acceptance Route (for invited users)
@api_router.post("/invitations/{invitation_token}/accept")
async def accept_invitation(
    invitation_token: str,
    current_user: User = Depends(get_current_user)
):
    """Accept a team invitation"""
    # Find invitation by token
    invitation = await db.team_invitations.find_one({
        "invitation_token": invitation_token,
        "status": InvitationStatus.PENDING
    })
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired"
        )
    
    # Check if invitation is expired
    if datetime.utcnow() > invitation["expires_at"]:
        await db.team_invitations.update_one(
            {"id": invitation["id"]},
            {"$set": {"status": InvitationStatus.EXPIRED}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Check if user email matches invitation
    if current_user.email != invitation["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation is not for your email address"
        )
    
    # Create company member
    member_data = {
        "company_id": invitation["company_id"],
        "user_id": current_user.id,
        "role": invitation["role"],
        "branch_ids": invitation["branch_ids"],
        "invited_by": invitation["invited_by"]
    }
    
    member_obj = CompanyMember(**member_data)
    await db.company_members.insert_one(member_obj.dict())
    
    # Mark invitation as accepted
    await db.team_invitations.update_one(
        {"id": invitation["id"]},
        {"$set": {"status": InvitationStatus.ACCEPTED}}
    )
    
    return {"message": "Invitation accepted successfully"}


# Public Invitation Routes (no authentication required)
class InvitationResponse(BaseModel):
    invitation_id: str
    company_name: str
    first_name: str
    last_name: str
    role: str
    branches: List[dict] = []
    expires_at: datetime
    
class InvitationRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

@api_router.get("/public/invitations/{invitation_token}", response_model=InvitationResponse)
async def get_invitation_details(invitation_token: str):
    """Get invitation details for public registration (no auth required)"""
    # Find invitation by token
    invitation = await db.team_invitations.find_one({
        "invitation_token": invitation_token,
        "status": InvitationStatus.PENDING
    })
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired"
        )
    
    # Check if invitation is expired
    if datetime.utcnow() > invitation["expires_at"]:
        await db.team_invitations.update_one(
            {"id": invitation["id"]},
            {"$set": {"status": InvitationStatus.EXPIRED}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Get company details
    company_user = await db.users.find_one({"id": invitation["company_id"]})
    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get branch details
    branches = []
    if invitation["branch_ids"]:
        for branch_id in invitation["branch_ids"]:
            branch = await db.company_branches.find_one({"id": branch_id})
            if branch:
                branches.append({
                    "id": branch["id"],
                    "name": branch["name"], 
                    "location": branch["location"]
                })
    
    return InvitationResponse(
        invitation_id=invitation["id"],
        company_name=company_user.get("company_profile", {}).get("company_name", "Unknown Company"),
        first_name=invitation["first_name"],
        last_name=invitation["last_name"],
        role=invitation["role"],
        branches=branches,
        expires_at=invitation["expires_at"]
    )

@api_router.post("/public/invitations/{invitation_token}/register", response_model=Token)
async def register_via_invitation(
    invitation_token: str,
    registration_data: InvitationRegistration
):
    """Register new user via invitation token"""
    # Find and validate invitation
    invitation = await db.team_invitations.find_one({
        "invitation_token": invitation_token,
        "status": InvitationStatus.PENDING
    })
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired"
        )
    
    # Check if invitation is expired
    if datetime.utcnow() > invitation["expires_at"]:
        await db.team_invitations.update_one(
            {"id": invitation["id"]},
            {"$set": {"status": InvitationStatus.EXPIRED}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Check if email matches invitation
    if registration_data.email != invitation["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address must match the invitation"
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": registration_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists. Please use the login page."
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(registration_data.password)
    
    user_data = {
        "email": registration_data.email,
        "password_hash": hashed_password,
        "first_name": registration_data.first_name,
        "last_name": registration_data.last_name,
        "role": UserRole.RECRUITER,  # Invited users become recruiters
    }
    
    user_obj = User(**user_data)
    await db.users.insert_one(user_obj.dict())
    
    # Create company member relationship
    member_data = {
        "company_id": invitation["company_id"],
        "user_id": user_obj.id,
        "role": invitation["role"],
        "branch_ids": invitation["branch_ids"],
        "invited_by": invitation["invited_by"]
    }
    
    member_obj = CompanyMember(**member_data)
    await db.company_members.insert_one(member_obj.dict())
    
    # Mark invitation as accepted
    await db.team_invitations.update_one(
        {"id": invitation["id"]},
        {"$set": {"status": InvitationStatus.ACCEPTED}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_obj.id}, expires_delta=access_token_expires
    )
    
    # Return token and user info
    user_dict = user_obj.dict()
    del user_dict['password_hash']
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }


# Company Profile Routes (existing)
@api_router.put("/profile/company", response_model=User)
async def update_company_profile(
    company_update: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update company profile (for recruiters)"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update company profiles"
        )
    
    update_data = {f"company_profile.{k}": v for k, v in company_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user in database
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": current_user.id})
    if "_id" in updated_user:
        del updated_user["_id"]
    
    user_obj = User(**updated_user)
    
    # Calculate and update progress
    progress = calculate_recruiter_progress(user_obj)
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"recruiter_progress": progress.dict()}}
    )
    
    user_obj.recruiter_progress = progress
    return user_obj

@api_router.post("/profile/job-posted")
async def track_job_posted(
    current_user: User = Depends(get_current_user)
):
    """Mark first job as posted for recruiter gamification"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can track job postings"
        )
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"recruiter_progress.first_job_posted": True}}
    )
    return {"message": "First job posting tracked successfully"}


# Job Posting Routes
@api_router.post("/jobs", response_model=Job)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new job posting"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can post jobs"
        )
    
    # Check if user has available job listings in their packages
    user_packages = await db.user_packages.find({
        "user_id": current_user.id,
        "is_active": True,
        "$or": [
            {"job_listings_remaining": {"$gt": 0}},  # Has remaining listings
            {"job_listings_remaining": None}  # Unlimited listings
        ]
    }).to_list(1000)
    
    # Filter out expired subscriptions
    valid_packages = []
    for user_package in user_packages:
        if user_package.get("expiry_date"):
            if datetime.utcnow() <= user_package["expiry_date"]:
                valid_packages.append(user_package)
        else:
            # One-time packages (no expiry)
            valid_packages.append(user_package)
    
    if not valid_packages:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No job listing credits available. Please purchase a package to post jobs."
        )
    
    # Get company details for the job
    if job_data.company_id == current_user.id:
        # Using current user's company
        company_name = "Company Name Not Set"
        company_logo_url = None
        if current_user.company_profile and current_user.company_profile.company_name:
            company_name = current_user.company_profile.company_name
        if current_user.company_profile and current_user.company_profile.company_logo_url:
            company_logo_url = current_user.company_profile.company_logo_url
    else:
        # Check if user is a member of this company
        member = await db.company_members.find_one({
            "user_id": current_user.id,
            "company_id": job_data.company_id,
            "is_active": True
        })
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to post jobs for this company"
            )
        
        # Get company details from the company owner
        company_owner = await db.users.find_one({"id": job_data.company_id})
        if not company_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        company_name = company_owner.get("company_profile", {}).get("company_name", "Company Name Not Set")
        company_logo_url = company_owner.get("company_profile", {}).get("company_logo_url")
    
    # Find the best package to use (prioritize non-unlimited packages first to preserve unlimited)
    selected_package = None
    for pkg in valid_packages:
        if pkg.get("job_listings_remaining") and pkg["job_listings_remaining"] > 0:
            selected_package = pkg
            break
    
    # If no limited packages, use unlimited package
    if not selected_package:
        for pkg in valid_packages:
            if pkg.get("job_listings_remaining") is None:  # Unlimited
                selected_package = pkg
                break
    
    if not selected_package:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No job listing credits available"
        )
    
    # Get the package details to determine job expiry
    package = await db.packages.find_one({"id": selected_package["package_id"]})
    job_expiry_days = package.get("job_expiry_days", 35) if package else 35
    
    # Create job object with appropriate expiry
    job_dict = job_data.dict()
    job_dict["company_name"] = company_name
    job_dict["logo_url"] = company_logo_url
    job_dict["posted_by"] = current_user.id
    job_dict["expiry_date"] = datetime.utcnow() + timedelta(days=job_expiry_days)
    
    job_obj = Job(**job_dict)
    await db.jobs.insert_one(job_obj.dict())
    
    # Deduct job listing credit (if not unlimited)
    if selected_package.get("job_listings_remaining") is not None:
        new_count = selected_package["job_listings_remaining"] - 1
        await db.user_packages.update_one(
            {"id": selected_package["id"]},
            {"$set": {"job_listings_remaining": new_count}}
        )
        
        # Deactivate package if no listings remaining
        if new_count <= 0:
            await db.user_packages.update_one(
                {"id": selected_package["id"]},
                {"$set": {"is_active": False}}
            )
    
    # Update recruiter progress for first job posting
    if not current_user.recruiter_progress or not current_user.recruiter_progress.first_job_posted:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"recruiter_progress.first_job_posted": True}}
        )
    
    return job_obj

@api_router.post("/jobs/bulk")
async def create_jobs_bulk(
    file: UploadFile = File(...),
    company_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Create multiple jobs from CSV/Excel file"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can post jobs"
        )
    
    # Check file type
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV or Excel format"
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        if file.filename.lower().endswith('.csv'):
            # Try multiple encodings for CSV files
            df = None
            encodings_to_try = ['utf-8', 'utf-8-sig', 'windows-1252', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings_to_try:
                try:
                    text_content = contents.decode(encoding)
                    
                    # Try multiple CSV parsing strategies
                    parsing_strategies = [
                        # Strategy 1: Standard parsing
                        lambda content: pd.read_csv(io.StringIO(content)),
                        # Strategy 2: Skip bad lines and warn
                        lambda content: pd.read_csv(io.StringIO(content), on_bad_lines='skip'),
                        # Strategy 3: More flexible parsing with quoting
                        lambda content: pd.read_csv(io.StringIO(content), quoting=1, skipinitialspace=True),
                        # Strategy 4: Use different separator detection
                        lambda content: pd.read_csv(io.StringIO(content), sep=None, engine='python'),
                        # Strategy 5: Very permissive parsing
                        lambda content: pd.read_csv(io.StringIO(content), on_bad_lines='skip', quoting=1, skipinitialspace=True, engine='python')
                    ]
                    
                    for i, strategy in enumerate(parsing_strategies):
                        try:
                            df = strategy(text_content)
                            if len(df.columns) > 1 and len(df) > 0:  # Basic validation
                                break
                        except Exception as parse_error:
                            if i == len(parsing_strategies) - 1:  # Last strategy failed
                                raise parse_error
                            continue
                    
                    if df is not None and len(df.columns) > 1:
                        break
                        
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception as e:
                    # If this encoding worked but parsing failed, continue to next encoding
                    continue
            
            if df is None:
                # If all encodings fail, try with error handling
                try:
                    text_content = contents.decode('utf-8', errors='replace')
                    df = pd.read_csv(io.StringIO(text_content), on_bad_lines='skip', engine='python')
                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unable to read CSV file. Please ensure it's properly formatted with consistent columns and properly quoted text fields. Common issues: commas in text fields should be within quotes, consistent number of columns per row."
                    )
        else:
            # Excel files are binary, no encoding issues
            try:
                df = pd.read_excel(io.BytesIO(contents))
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unable to read Excel file: {str(e)}"
                )
        
        # Validate required columns
        required_columns = ['title', 'location', 'salary', 'job_type', 'work_type', 'industry', 'description']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        jobs_created = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Use provided company_id or fall back to current user
                job_company_id = company_id if company_id else current_user.id
                
                # Validate company access
                if job_company_id != current_user.id:
                    member = await db.company_members.find_one({
                        "user_id": current_user.id,
                        "company_id": job_company_id,
                        "is_active": True
                    })
                    if not member:
                        errors.append(f"Row {index + 1}: No permission for company {job_company_id}")
                        continue
                
                # Get company name and logo
                if job_company_id == current_user.id:
                    company_name = "Company Name Not Set"
                    company_logo_url = None
                    if current_user.company_profile and current_user.company_profile.company_name:
                        company_name = current_user.company_profile.company_name
                    if current_user.company_profile and current_user.company_profile.company_logo_url:
                        company_logo_url = current_user.company_profile.company_logo_url
                else:
                    company_owner = await db.users.find_one({"id": job_company_id})
                    company_name = company_owner.get("company_profile", {}).get("company_name", "Company Name Not Set") if company_owner else "Unknown Company"
                    company_logo_url = company_owner.get("company_profile", {}).get("company_logo_url") if company_owner else None
                
                # Validate enum values
                try:
                    job_type = JobType(row['job_type'])
                    work_type = WorkType(row['work_type'])
                except ValueError as e:
                    errors.append(f"Row {index + 1}: Invalid job_type or work_type - {str(e)}")
                    continue
                
                # Create job object
                job_data = {
                    "title": str(row['title']),
                    "location": str(row['location']),
                    "salary": str(row['salary']),
                    "job_type": job_type,
                    "work_type": work_type,
                    "industry": str(row['industry']),
                    "description": str(row['description']),
                    "experience": str(row.get('experience', '')) if pd.notna(row.get('experience')) else None,
                    "qualifications": str(row.get('qualifications', '')) if pd.notna(row.get('qualifications')) else None,
                    "application_url": str(row.get('application_url', '')) if pd.notna(row.get('application_url')) else None,
                    "application_email": str(row.get('application_email', '')) if pd.notna(row.get('application_email')) else None,
                    "company_id": job_company_id,
                    "company_name": company_name,
                    "logo_url": company_logo_url,
                    "posted_by": current_user.id,
                    "posted_date": datetime.utcnow(),
                    "expiry_date": datetime.utcnow() + timedelta(days=35)  # Set proper expiry date
                }
                
                job_obj = Job(**job_data)
                await db.jobs.insert_one(job_obj.dict())
                jobs_created.append(job_obj.id)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Update recruiter progress for first job posting
        if jobs_created and (not current_user.recruiter_progress or not current_user.recruiter_progress.first_job_posted):
            await db.users.update_one(
                {"id": current_user.id},
                {"$set": {"recruiter_progress.first_job_posted": True}}
            )
        
        return {
            "message": f"Bulk upload completed",
            "jobs_created": len(jobs_created),
            "total_rows": len(df),
            "errors": errors
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty or has no data"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )

@api_router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload CV/Resume file for job applications"""
    
    # Validate file type
    allowed_types = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC, and DOCX files are allowed"
        )
    
    # Validate file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    try:
        # Create uploads directory if it doesn't exist (relative to backend directory)
        backend_dir = Path(__file__).parent
        uploads_dir = backend_dir / "uploads" / "cvs"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
        unique_filename = f"{current_user.id}_{uuid.uuid4()}.{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return file URL for use in applications
        base_url = os.getenv('BASE_URL', 'http://localhost:8001')
        file_url = f"{base_url}/api/uploads/cvs/{unique_filename}"
        
        return {
            "message": "CV uploaded successfully",
            "file_url": file_url,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@api_router.get("/jobs", response_model=List[Job])
async def get_jobs(
    company_id: Optional[str] = Query(None),
    include_archived: Optional[bool] = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get jobs for recruiter (all jobs they have access to)"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view job listings"
        )
    
    # Build query based on user's company access
    query = {}
    
    if company_id:
        # Check if user has access to this company
        if company_id != current_user.id:
            member = await db.company_members.find_one({
                "user_id": current_user.id,
                "company_id": company_id,
                "is_active": True
            })
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this company's jobs"
                )
        query["company_id"] = company_id
    else:
        # Get all companies the user has access to
        accessible_companies = [current_user.id]  # Always include own company
        
        # Add companies where user is a member
        memberships = await db.company_members.find({
            "user_id": current_user.id,
            "is_active": True
        }).to_list(1000)
        
        for membership in memberships:
            accessible_companies.append(membership["company_id"])
        
        query["company_id"] = {"$in": accessible_companies}
    
    # Filter by expiry status if not including archived
    if not include_archived:
        query["expiry_date"] = {"$gt": datetime.utcnow()}
    
    # Get jobs
    jobs = await db.jobs.find(query).sort("posted_date", -1).to_list(1000)
    
    # Convert to Job objects and remove MongoDB _id
    result = []
    for job in jobs:
        if "_id" in job:
            del job["_id"]
        result.append(Job(**job))
    
    return result

@api_router.get("/public/jobs", response_model=List[Job])
async def get_public_jobs(
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    work_type: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(1000)
):
    """Get active jobs for job seekers (public endpoint with filtering)"""
    query = {
        "is_active": True,
        "expiry_date": {"$gt": datetime.utcnow()}  # Only show non-expired jobs
    }
    
    # Apply filters
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    if job_type:
        query["job_type"] = job_type
    
    if work_type:
        query["work_type"] = work_type
    
    if industry:
        query["industry"] = {"$regex": industry, "$options": "i"}
    
    if search:
        # Search in title and description
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Get jobs
    jobs = await db.jobs.find(query).sort("posted_date", -1).limit(limit).to_list(limit)
    
    # Convert to Job objects and remove MongoDB _id
    result = []
    for job in jobs:
        if "_id" in job:
            del job["_id"]
        result.append(Job(**job))
    
    return result

@api_router.get("/public/company/{company_id}")
async def get_public_company_profile(company_id: str):
    """Get public company profile information"""
    company_user = await db.users.find_one({"id": company_id, "role": "recruiter"})
    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if "_id" in company_user:
        del company_user["_id"]
    
    # Get active jobs count for this company
    active_jobs_count = await db.jobs.count_documents({
        "company_id": company_id,
        "is_active": True,
        "expiry_date": {"$gt": datetime.utcnow()}
    })
    
    # Get company profile information
    company_profile = company_user.get("company_profile", {})
    
    return {
        "id": company_user["id"],
        "company_name": company_profile.get("company_name", "Company Name Not Set"),
        "company_logo_url": company_profile.get("company_logo_url"),
        "company_cover_image_url": company_profile.get("company_cover_image_url"),
        "company_description": company_profile.get("company_description"),
        "company_website": company_profile.get("company_website"),
        "company_linkedin": company_profile.get("company_linkedin"),
        "company_size": company_profile.get("company_size"),
        "company_industry": company_profile.get("company_industry"),
        "company_location": company_profile.get("company_location"),
        "active_jobs_count": active_jobs_count,
        "created_at": company_user.get("created_at")
    }

@api_router.get("/public/company/{company_id}/jobs", response_model=List[Job])
async def get_company_jobs(
    company_id: str,
    limit: Optional[int] = Query(100)
):
    """Get active jobs for a specific company"""
    query = {
        "company_id": company_id,
        "is_active": True,
        "expiry_date": {"$gt": datetime.utcnow()}
    }
    
    jobs = await db.jobs.find(query).sort("posted_date", -1).limit(limit).to_list(limit)
    
    result = []
    for job in jobs:
        if "_id" in job:
            del job["_id"]
        result.append(Job(**job))
    
    return result


async def get_archived_jobs(
    company_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get archived (expired) jobs for recruiter"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view archived jobs"
        )
    
    # Build query for expired jobs
    query = {
        "expiry_date": {"$lte": datetime.utcnow()}  # Only expired jobs
    }
    
    if company_id:
        # Check if user has access to this company
        if company_id != current_user.id:
            member = await db.company_members.find_one({
                "user_id": current_user.id,
                "company_id": company_id,
                "is_active": True
            })
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this company's jobs"
                )
        query["company_id"] = company_id
    else:
        # Get all companies the user has access to
        accessible_companies = [current_user.id]
        
        memberships = await db.company_members.find({
            "user_id": current_user.id,
            "is_active": True
        }).to_list(1000)
        
        for membership in memberships:
            accessible_companies.append(membership["company_id"])
        
        query["company_id"] = {"$in": accessible_companies}
    
    # Get archived jobs
    jobs = await db.jobs.find(query).sort("expiry_date", -1).to_list(1000)
    
    # Convert to Job objects and remove MongoDB _id
    result = []
    for job in jobs:
        if "_id" in job:
            del job["_id"]
        result.append(Job(**job))
    
    return result

@api_router.put("/jobs/{job_id}/repost")
async def repost_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Repost an expired job (extends expiry by 35 days)"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can repost jobs"
        )
    
    # Find the job
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user has permission to repost this job
    if job["company_id"] != current_user.id:
        member = await db.company_members.find_one({
            "user_id": current_user.id,
            "company_id": job["company_id"],
            "is_active": True
        })
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to repost this job"
            )
    
    # Extend expiry by 35 days
    new_expiry_date = datetime.utcnow() + timedelta(days=35)
    
    await db.jobs.update_one(
        {"id": job_id},
        {"$set": {
            "expiry_date": new_expiry_date,
            "posted_date": datetime.utcnow(),  # Update posted date too
            "is_active": True
        }}
    )
    
    return {
        "message": "Job reposted successfully",
        "new_expiry_date": new_expiry_date.isoformat()
    }

@api_router.get("/companies", response_model=List[dict])
async def get_accessible_companies(current_user: User = Depends(get_current_user)):
    """Get all companies the user has access to for job posting"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access company information"
        )
    
    companies = []
    
    # Add user's own company
    companies.append({
        "id": current_user.id,
        "name": current_user.company_profile.company_name if current_user.company_profile else "Your Company",
        "role": "owner",
        "is_default": True
    })
    
    # Add companies where user is a member
    memberships = await db.company_members.find({
        "user_id": current_user.id,
        "is_active": True
    }).to_list(1000)
    
    for membership in memberships:
        company_owner = await db.users.find_one({"id": membership["company_id"]})
        if company_owner:
            companies.append({
                "id": membership["company_id"],
                "name": company_owner.get("company_profile", {}).get("company_name", "Unknown Company"),
                "role": membership["role"],
                "is_default": False
            })
    
    return companies


# Job Application Routes
@api_router.post("/jobs/{job_id}/apply", response_model=JobApplication)
async def apply_for_job(
    job_id: str,
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_user)
):
    """Apply for a job (Easy Apply functionality)"""
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can apply for jobs"
        )
    
    # Check if job exists and is active
    job = await db.jobs.find_one({
        "id": job_id,
        "is_active": True,
        "expiry_date": {"$gt": datetime.utcnow()}
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or expired"
        )
    
    # Check if job supports easy apply (no external application_url)
    if job.get("application_url"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job requires external application. Please use the company website."
        )
    
    # Check if user already applied
    existing_application = await db.job_applications.find_one({
        "job_id": job_id,
        "applicant_id": current_user.id
    })
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    # Create application
    application_dict = application_data.dict()
    application_dict["applicant_id"] = current_user.id
    application_dict["company_id"] = job["company_id"]
    
    # Store applicant snapshot for quick access (capture profile at time of application)
    applicant_snapshot = {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "location": getattr(current_user, 'location', None),
        "phone": getattr(current_user, 'phone', None),
        "skills": getattr(current_user, 'skills', []),
        "profile_picture_url": getattr(current_user, 'profile_picture_url', None)
    }
    
    # Add resume URL from application or profile
    if application_data.resume_url:
        applicant_snapshot["resume_url"] = application_data.resume_url
    else:
        # Try to get from user profile
        applicant_snapshot["resume_url"] = getattr(current_user, 'resume_url', None) or getattr(current_user, 'cv_url', None)
    
    application_dict["applicant_snapshot"] = applicant_snapshot
    
    application_obj = JobApplication(**application_dict)
    await db.job_applications.insert_one(application_obj.dict())
    
    # Update job seeker progress (applications count)
    current_applications = await db.job_applications.count_documents({
        "applicant_id": current_user.id
    })
    
    # Update profile progress if this is one of their first 5 applications
    if current_applications <= 5:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"profile_progress.job_applications": current_applications}}
        )
    
    return application_obj

@api_router.get("/applications", response_model=List[dict])
async def get_my_applications(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get job seeker's applications"""
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view their applications"
        )
    
    query = {"applicant_id": current_user.id}
    if status:
        query["status"] = status
    
    applications = await db.job_applications.find(query).sort("applied_date", -1).to_list(1000)
    
    # Enrich with job details
    result = []
    for app in applications:
        job = await db.jobs.find_one({"id": app["job_id"]})
        if job:
            if "_id" in job:
                del job["_id"]
            if "_id" in app:
                del app["_id"]
            
            result.append({
                "application": app,
                "job": job
            })
    
    return result

@api_router.get("/jobs/{job_id}/applications", response_model=List[dict])
async def get_job_applications(
    job_id: str,
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get applications for a specific job (recruiters only)"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view job applications"
        )
    
    # Check if user has access to this job
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permission
    if job["company_id"] != current_user.id:
        member = await db.company_members.find_one({
            "user_id": current_user.id,
            "company_id": job["company_id"],
            "is_active": True
        })
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view applications for this job"
            )
    
    # Get applications
    query = {"job_id": job_id}
    if status:
        query["status"] = status
    
    applications = await db.job_applications.find(query).sort("applied_date", -1).to_list(1000)
    
    # Enrich with applicant details
    result = []
    for app in applications:
        applicant = await db.users.find_one({"id": app["applicant_id"]})
        if applicant:
            if "_id" in applicant:
                del applicant["_id"]
            if "_id" in app:
                del app["_id"]
            
            # Remove sensitive information
            applicant_safe = {
                "id": applicant["id"],
                "first_name": applicant["first_name"],
                "last_name": applicant["last_name"],
                "email": applicant["email"],
                "profile_picture_url": applicant.get("profile_picture_url"),
                "skills": applicant.get("skills", []),
                "location": applicant.get("location"),
                "work_experience": applicant.get("work_experience", []),
                "education": applicant.get("education", []),
                "profile_progress": applicant.get("profile_progress", {})
            }
            
            result.append({
                "application": app,
                "applicant": applicant_safe,
                "job": {"id": job["id"], "title": job["title"]}
            })
    
    return result

@api_router.put("/applications/{application_id}", response_model=JobApplication)
async def update_application_status(
    application_id: str,
    application_update: JobApplicationUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update job application status (recruiters only)"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can update application status"
        )
    
    # Get application
    application = await db.job_applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permission
    if application["company_id"] != current_user.id:
        member = await db.company_members.find_one({
            "user_id": current_user.id,
            "company_id": application["company_id"],
            "is_active": True
        })
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this application"
            )
    
    # Update application
    update_data = {k: v for k, v in application_update.dict().items() if v is not None}
    update_data["last_updated"] = datetime.utcnow()
    update_data["reviewed_by"] = current_user.id
    
    await db.job_applications.update_one(
        {"id": application_id},
        {"$set": update_data}
    )
    
    # Get updated application
    updated_application = await db.job_applications.find_one({"id": application_id})
    if "_id" in updated_application:
        del updated_application["_id"]
    
    return JobApplication(**updated_application)

@api_router.get("/company/applications", response_model=List[dict])
async def get_all_company_applications(
    status: Optional[str] = Query(None),
    job_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get all applications for recruiter's companies"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view company applications"
        )
    
    # Get accessible companies
    accessible_companies = [current_user.id]
    memberships = await db.company_members.find({
        "user_id": current_user.id,
        "is_active": True
    }).to_list(1000)
    
    for membership in memberships:
        accessible_companies.append(membership["company_id"])
    
    # Build query
    query = {"company_id": {"$in": accessible_companies}}
    if status:
        query["status"] = status
    if job_id:
        query["job_id"] = job_id
    
    applications = await db.job_applications.find(query).sort("applied_date", -1).to_list(1000)
    
    # Enrich with job and applicant details
    result = []
    for app in applications:
        # Get job details
        job = await db.jobs.find_one({"id": app["job_id"]})
        # Get applicant details
        applicant = await db.users.find_one({"id": app["applicant_id"]})
        
        if job and applicant:
            if "_id" in job:
                del job["_id"]
            if "_id" in applicant:
                del applicant["_id"]
            if "_id" in app:
                del app["_id"]
            
            # Create safe applicant data
            applicant_safe = {
                "id": applicant["id"],
                "first_name": applicant["first_name"],
                "last_name": applicant["last_name"],
                "email": applicant["email"],
                "profile_picture_url": applicant.get("profile_picture_url"),
                "skills": applicant.get("skills", []),
                "location": applicant.get("location"),
                "profile_progress": applicant.get("profile_progress", {})
            }
            
            result.append({
                "application": app,
                "job": {
                    "id": job["id"],
                    "title": job["title"],
                    "company_name": job["company_name"],
                    "location": job["location"],
                    "job_type": job["job_type"]
                },
                "applicant": applicant_safe
            })
    
    return result


# Package and Payment Routes
@api_router.get("/packages", response_model=List[Package])
async def get_available_packages():
    """Get all available packages for purchase"""
    packages = await db.packages.find({"is_active": True}).to_list(1000)
    
    # If no packages exist, initialize default packages
    if not packages:
        print("Initializing default packages...")
        for package_data in DEFAULT_PACKAGES:
            package_obj = Package(**package_data)
            await db.packages.insert_one(package_obj.dict())
            packages.append(package_obj.dict())
    
    # Convert to Package objects and remove MongoDB _id
    result = []
    for package in packages:
        if "_id" in package:
            del package["_id"]
        result.append(Package(**package))
    
    return result

@api_router.get("/packages/{package_type}", response_model=Package)
async def get_package_by_type(package_type: PackageType):
    """Get specific package by type"""
    package = await db.packages.find_one({
        "package_type": package_type,
        "is_active": True
    })
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    if "_id" in package:
        del package["_id"]
    
    return Package(**package)

@api_router.post("/payments/initiate")
async def initiate_payment(
    package_type: PackageType,
    discount_code: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Initiate payment for a package with optional discount code"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can purchase packages"
        )
    
    # Get package details
    package = await db.packages.find_one({
        "package_type": package_type,
        "is_active": True
    })
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    original_amount = package["price"]
    discount_amount = 0.0
    final_amount = original_amount
    discount_info = None
    
    # Validate and apply discount code if provided
    if discount_code:
        validation_result = await validate_discount_code(
            discount_code, 
            current_user.id, 
            package_type, 
            original_amount
        )
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result["error"]
            )
        
        discount_amount = validation_result["discount_amount"]
        final_amount = validation_result["final_price"]
        discount_info = {
            "code": discount_code.upper(),
            "type": validation_result["discount"]["discount_type"],
            "value": validation_result["discount"]["discount_value"],
            "amount": discount_amount
        }
    
    # Create payment record
    payment_data = {
        "user_id": current_user.id,
        "package_id": package["id"],
        "amount": original_amount,
        "discount_code": discount_code.upper() if discount_code else None,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "currency": "ZAR",
        "payment_method": "payfast"
    }
    
    payment_obj = Payment(**payment_data)
    await db.payments.insert_one(payment_obj.dict())
    
    # Prepare Payfast payment parameters
    payfast_data = {
        'merchant_id': PAYFAST_MERCHANT_ID,
        'merchant_key': PAYFAST_MERCHANT_KEY,
        'return_url': f"{BASE_URL}/payment/success",
        'cancel_url': f"{BASE_URL}/payment/cancel",
        'notify_url': f"{BASE_URL}/api/webhooks/payfast",
        'amount': f"{final_amount:.2f}",
        'item_name': package['name'],
        'item_description': package.get('description', package['name']),
        'custom_str1': payment_obj.id,  # Payment ID for tracking
        'custom_str2': current_user.id,  # User ID for tracking
        'email_confirmation': '1',
        'confirmation_address': current_user.email
    }
    
    # Add discount information to description if applicable
    if discount_info:
        payfast_data['item_description'] += f" (Discount: {discount_info['code']})"
    
    # Generate signature (no passphrase for sandbox)
    passphrase = PAYFAST_PASSPHRASE if PAYFAST_PASSPHRASE else None
    signature = generate_payfast_signature(payfast_data, passphrase)
    payfast_data['signature'] = signature
    
    # Determine Payfast URL based on environment
    if PAYFAST_SANDBOX:
        payfast_base_url = "https://sandbox.payfast.co.za/eng/process"
    else:
        payfast_base_url = "https://www.payfast.co.za/eng/process"
    
    # Create payment URL with parameters
    param_string = '&'.join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in payfast_data.items()])
    payfast_url = f"{payfast_base_url}?{param_string}"
    
    response_data = {
        "payment_id": payment_obj.id,
        "payment_url": payfast_url,
        "original_amount": original_amount,
        "final_amount": final_amount,
        "currency": "ZAR",
        "package_name": package["name"]
    }
    
    # Add discount information to response if applicable
    if discount_info:
        response_data["discount"] = discount_info
    
    return response_data

@api_router.post("/payments/{payment_id}/complete")
async def complete_payment(
    payment_id: str,
    payment_reference: str,
    current_user: User = Depends(get_current_user)
):
    """Complete payment and activate package"""
    # Get payment
    payment = await db.payments.find_one({"id": payment_id})
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify payment belongs to current user
    if payment["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment does not belong to current user"
        )
    
    # Get package details
    package = await db.packages.find_one({"id": payment["package_id"]})
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    # Update payment status
    await db.payments.update_one(
        {"id": payment_id},
        {"$set": {
            "status": PaymentStatus.COMPLETED,
            "payment_reference": payment_reference,
            "completed_date": datetime.utcnow()
        }}
    )
    
    # Create user package
    user_package_data = {
        "user_id": current_user.id,
        "package_id": package["id"],
        "package_type": package["package_type"],
        "job_listings_remaining": package["job_listings_included"],
        "cv_searches_remaining": package["cv_searches_included"]
    }
    
    # Set expiry for subscriptions
    if package["is_subscription"]:
        user_package_data["expiry_date"] = datetime.utcnow() + timedelta(days=package["duration_days"])
        user_package_data["subscription_status"] = SubscriptionStatus.ACTIVE
    
    user_package_obj = UserPackage(**user_package_data)
    await db.user_packages.insert_one(user_package_obj.dict())
    
    return {
        "message": "Payment completed successfully",
        "package_activated": package["name"],
        "job_listings_remaining": user_package_data["job_listings_remaining"],
        "cv_searches_remaining": user_package_data["cv_searches_remaining"]
    }

@api_router.post("/webhooks/payfast")
async def payfast_webhook(request: Request):
    """Handle PayFast webhook notifications for automatic package activation"""
    try:
        # Get form data from PayFast
        form_data = await request.form()
        data = dict(form_data)
        
        # Log the webhook data for debugging
        logging.info(f"PayFast webhook received: {data}")
        
        # Verify signature
        if not verify_payfast_signature(data, PAYFAST_PASSPHRASE):
            logging.error("PayFast webhook signature verification failed")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Extract payment information
        payment_status = data.get('payment_status')
        custom_str1 = data.get('custom_str1')  # Payment ID
        custom_str2 = data.get('custom_str2')  # User ID
        pf_payment_id = data.get('pf_payment_id')
        amount_gross = float(data.get('amount_gross', 0))
        
        # Only process completed payments
        if payment_status != 'COMPLETE':
            logging.info(f"PayFast payment not complete: {payment_status}")
            return {"status": "ignored", "reason": f"Payment status: {payment_status}"}
        
        if not custom_str1:
            logging.error("PayFast webhook missing payment ID")
            return {"status": "error", "reason": "Missing payment ID"}
        
        # Get payment record
        payment = await db.payments.find_one({"id": custom_str1})
        if not payment:
            logging.error(f"PayFast webhook: Payment not found: {custom_str1}")
            return {"status": "error", "reason": "Payment not found"}
        
        # Check if payment is already completed
        if payment.get("status") == PaymentStatus.COMPLETED:
            logging.info(f"PayFast webhook: Payment already completed: {custom_str1}")
            return {"status": "success", "reason": "Payment already processed"}
        
        # Verify amount matches (should match final_amount after discount)
        expected_amount = payment.get("final_amount", payment["amount"])
        if abs(expected_amount - amount_gross) > 0.01:  # Allow small floating point differences
            logging.error(f"PayFast webhook: Amount mismatch. Expected: {expected_amount}, Received: {amount_gross}")
            return {"status": "error", "reason": "Amount mismatch"}
        
        # Get package details
        package = await db.packages.find_one({"id": payment["package_id"]})
        if not package:
            logging.error(f"PayFast webhook: Package not found: {payment['package_id']}")
            return {"status": "error", "reason": "Package not found"}
        
        # Update payment status
        await db.payments.update_one(
            {"id": custom_str1},
            {"$set": {
                "status": PaymentStatus.COMPLETED,
                "payment_reference": pf_payment_id,
                "completed_date": datetime.utcnow(),
                "webhook_data": data
            }}
        )
        
        # Update discount code usage count if discount was applied
        if payment.get("discount_code"):
            await db.discount_codes.update_one(
                {"code": payment["discount_code"]},
                {"$inc": {"usage_count": 1}}
            )
        
        # Create/activate user package
        user_package_data = {
            "user_id": payment["user_id"],
            "package_id": package["id"],
            "package_type": package["package_type"],
            "purchased_date": datetime.utcnow(),
            "is_active": True,
            "job_listings_remaining": package["job_listings_included"],
            "cv_searches_remaining": package["cv_searches_included"]
        }
        
        # Set expiry date for subscription packages
        if package.get("duration_days"):
            user_package_data["expiry_date"] = datetime.utcnow() + timedelta(days=package["duration_days"])
            user_package_data["subscription_status"] = SubscriptionStatus.ACTIVE
        
        user_package = UserPackage(**user_package_data)
        await db.user_packages.insert_one(user_package.dict())
        
        logging.info(f"PayFast webhook: Successfully activated package {package['name']} for user {payment['user_id']}")
        
        return {"status": "success", "message": "Package activated successfully"}
        
    except Exception as e:
        logging.error(f"PayFast webhook error: {str(e)}")
        return {"status": "error", "reason": str(e)}

@api_router.get("/my-packages", response_model=List[dict])
async def get_my_packages(current_user: User = Depends(get_current_user)):
    """Get user's purchased packages"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view packages"
        )
    
    # Get user packages
    user_packages = await db.user_packages.find({
        "user_id": current_user.id,
        "is_active": True
    }).sort("purchased_date", -1).to_list(1000)
    
    result = []
    for user_package in user_packages:
        # Get package details
        package = await db.packages.find_one({"id": user_package["package_id"]})
        
        if package:
            if "_id" in package:
                del package["_id"]
            if "_id" in user_package:
                del user_package["_id"]
            
            # Check if subscription is expired
            is_expired = False
            if user_package.get("expiry_date") and datetime.utcnow() > user_package["expiry_date"]:
                is_expired = True
                # Update subscription status
                await db.user_packages.update_one(
                    {"id": user_package["id"]},
                    {"$set": {"subscription_status": SubscriptionStatus.EXPIRED}}
                )
            
            result.append({
                "user_package": user_package,
                "package": package,
                "is_expired": is_expired
            })
    
    return result


# User Profile Routes (existing)
@api_router.put("/profile", response_model=User)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user in database
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": current_user.id})
    if "_id" in updated_user:
        del updated_user["_id"]
    
    user_obj = User(**updated_user)
    
    # Calculate and update progress based on role
    if user_obj.role == UserRole.JOB_SEEKER:
        progress = calculate_profile_progress(user_obj)
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"profile_progress": progress.dict()}}
        )
        user_obj.profile_progress = progress
    elif user_obj.role == UserRole.RECRUITER:
        progress = await calculate_recruiter_progress_with_structure(user_obj)
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"recruiter_progress": progress.dict()}}
        )
        user_obj.recruiter_progress = progress
    
    return user_obj

@api_router.post("/profile/work-experience")
async def add_work_experience(
    experience: WorkExperience,
    current_user: User = Depends(get_current_user)
):
    """Add work experience"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"work_experience": experience.dict()}}
    )
    return {"message": "Work experience added successfully"}

@api_router.post("/profile/education")
async def add_education(
    education: Education,
    current_user: User = Depends(get_current_user)
):
    """Add education"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"education": education.dict()}}
    )
    return {"message": "Education added successfully"}

@api_router.post("/profile/achievement")
async def add_achievement(
    achievement: Achievement,
    current_user: User = Depends(get_current_user)
):
    """Add achievement"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"achievements": achievement.dict()}}
    )
    return {"message": "Achievement added successfully"}

@api_router.post("/profile/job-application/{job_id}")
async def track_job_application(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Track job application for gamification"""
    # Increment job applications count
    await db.users.update_one(
        {"id": current_user.id},
        {"$inc": {"profile_progress.job_applications": 1}}
    )
    
    # You can also store actual job applications here
    # For now, we're just tracking the count for gamification
    
    return {"message": "Job application tracked successfully"}

@api_router.post("/profile/email-alerts")
async def setup_email_alerts(
    current_user: User = Depends(get_current_user)
):
    """Mark email alerts as setup"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"profile_progress.email_alerts": True}}
    )
    return {"message": "Email alerts setup completed"}


# Job Routes (existing)
@api_router.post("/jobs", response_model=Job)
async def create_job(job_data: JobCreate):
    """Create a new job posting"""
    job_dict = job_data.dict()
    job_obj = Job(**job_dict)
    await db.jobs.insert_one(job_obj.dict())
    return job_obj

@api_router.get("/jobs", response_model=List[Job])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in job title, company name, or description"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[JobType] = Query(None, description="Filter by job type"),
    category: Optional[JobCategory] = Query(None, description="Filter by job category"),
    experience_level: Optional[ExperienceLevel] = Query(None, description="Filter by experience level"),
    is_remote: Optional[bool] = Query(None, description="Filter remote jobs only"),
    featured_only: Optional[bool] = Query(None, description="Show featured jobs only"),
    salary_min: Optional[int] = Query(None, description="Minimum salary filter")
):
    """Get job listings with optional filtering and pagination"""
    
    # Build query
    query = {"is_active": True}
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"company_name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    if job_type:
        query["job_type"] = job_type
    
    if category:
        query["category"] = category
    
    if experience_level:
        query["experience_level"] = experience_level
    
    if is_remote is not None:
        query["is_remote"] = is_remote
    
    if featured_only:
        query["featured"] = True
    
    if salary_min:
        query["salary_min"] = {"$gte": salary_min}
    
    # Execute query with pagination
    cursor = db.jobs.find(query).sort("posted_date", -1).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    return [Job(**job) for job in jobs]

@api_router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a specific job by ID"""
    job = await db.jobs.find_one({"id": job_id, "is_active": True})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**job)

@api_router.put("/jobs/{job_id}", response_model=Job)
async def update_job(job_id: str, job_data: JobCreate):
    """Update a job posting"""
    existing_job = await db.jobs.find_one({"id": job_id})
    if not existing_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    updated_data = job_data.dict()
    updated_data["id"] = job_id
    updated_data["posted_date"] = existing_job["posted_date"]
    
    job_obj = Job(**updated_data)
    await db.jobs.replace_one({"id": job_id}, job_obj.dict())
    return job_obj

@api_router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Soft delete a job (mark as inactive)"""
    result = await db.jobs.update_one(
        {"id": job_id}, 
        {"$set": {"is_active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}


# Company Routes
@api_router.post("/companies", response_model=Company)
async def create_company(company_data: CompanyCreate):
    """Create a new company"""
    company_dict = company_data.dict()
    company_obj = Company(**company_dict)
    await db.companies.insert_one(company_obj.dict())
    return company_obj

@api_router.get("/companies", response_model=List[Company])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search company names")
):
    """Get companies with optional search and pagination"""
    query = {}
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    cursor = db.companies.find(query).sort("name", 1).skip(skip).limit(limit)
    companies = await cursor.to_list(length=limit)
    
    return [Company(**company) for company in companies]

@api_router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str):
    """Get a specific company by ID"""
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(**company)

@api_router.get("/companies/{company_id}/jobs", response_model=List[Job])
async def get_company_jobs(company_id: str):
    """Get all active jobs for a specific company"""
    jobs = await db.jobs.find({"company_id": company_id, "is_active": True}).sort("posted_date", -1).to_list(1000)
    return [Job(**job) for job in jobs]


# Statistics and Analytics Routes
@api_router.get("/stats/jobs")
async def get_job_stats():
    """Get job statistics"""
    total_jobs = await db.jobs.count_documents({"is_active": True})
    featured_jobs = await db.jobs.count_documents({"is_active": True, "featured": True})
    remote_jobs = await db.jobs.count_documents({"is_active": True, "is_remote": True})
    
    # Jobs by category
    category_pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    category_stats = await db.jobs.aggregate(category_pipeline).to_list(100)
    
    # Jobs by location
    location_pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    location_stats = await db.jobs.aggregate(location_pipeline).to_list(10)
    
    return {
        "total_jobs": total_jobs,
        "featured_jobs": featured_jobs,
        "remote_jobs": remote_jobs,
        "jobs_by_category": category_stats,
        "top_locations": location_stats
    }


# Legacy routes (keep for backwards compatibility)
@api_router.get("/")
async def root():
    return {"message": "Job Rocket API - Your gateway to career opportunities"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# Seed data endpoint (for development)
@api_router.post("/seed-data")
async def seed_data():
    """Seed the database with sample data"""
    
    # Sample companies
    sample_companies = [
        {
            "id": "comp-1",
            "name": "ESG Recruitment",
            "description": "Leading recruitment agency specializing in engineering and technical roles",
            "logo_url": "https://images.unsplash.com/photo-1496200186974-4293800e2c20?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxjb21wYW55JTIwbG9nb3N8ZW58MHx8fHwxNzU1MzUzMDk0fDA&ixlib=rb-4.1.0&q=85",
            "industry": "Recruitment",
            "location": "Johannesburg",
            "created_at": datetime.utcnow()
        },
        {
            "id": "comp-2", 
            "name": "R & D Contracting",
            "description": "Construction and contracting company with focus on infrastructure projects",
            "logo_url": "https://images.unsplash.com/photo-1621831337128-35676ca30868?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw0fHxvZmZpY2UlMjBidWlsZGluZ3N8ZW58MHx8fHwxNzU1MzUzMDk5fDA&ixlib=rb-4.1.0&q=85",
            "industry": "Construction",
            "location": "Durban",
            "created_at": datetime.utcnow()
        },
        {
            "id": "comp-3",
            "name": "E and D Recruiters", 
            "description": "Technology recruitment specialists",
            "logo_url": "https://images.unsplash.com/photo-1712159018726-4564d92f3ec2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHx0ZWNoJTIwY29tcGFuaWVzfGVufDB8fHx8MTc1NTM1MzEwNHww&ixlib=rb-4.1.0&q=85",
            "industry": "Technology",
            "location": "Cape Town",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert companies
    await db.companies.delete_many({})  # Clear existing
    await db.companies.insert_many(sample_companies)
    
    # Sample jobs
    sample_jobs = [
        {
            "id": "job-1",
            "title": "R & D Manager / Workshop",
            "company_id": "comp-1",
            "company_name": "ESG Recruitment",
            "description": "Experience as a R & D Manager / Workshop * 5 - 8 years experience in R & D Management / workshop more",
            "requirements": ["5-8 years R&D experience", "Workshop management", "Team leadership"],
            "responsibilities": ["Manage R&D operations", "Lead workshop activities", "Drive innovation"],
            "location": "JHB - Eastern Suburbs",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.SENIOR,
            "category": JobCategory.ENGINEERING,
            "is_remote": False,
            "is_hybrid": False,
            "logo_url": "https://images.unsplash.com/photo-1496200186974-4293800e2c20?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxjb21wYW55JTIwbG9nb3N8ZW58MHx8fHwxNzU1MzUzMDk0fDA&ixlib=rb-4.1.0&q=85",
            "posted_date": datetime.utcnow(),
            "is_active": True,
            "featured": True
        },
        {
            "id": "job-2",
            "title": "Senior Site Manager (Construction)",
            "company_id": "comp-2",
            "company_name": "R & D Contracting",
            "description": "R & D Contracting seeks experienced site manager for major construction projects",
            "requirements": ["Construction management experience", "Site management", "Safety certification"],
            "responsibilities": ["Manage construction sites", "Ensure safety compliance", "Coordinate teams"],
            "location": "Johannesburg / Durban", 
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.SENIOR,
            "category": JobCategory.ENGINEERING,
            "salary_min": 18000,
            "salary_max": 21000,
            "is_remote": False,
            "is_hybrid": False,
            "logo_url": "https://images.unsplash.com/photo-1621831337128-35676ca30868?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw0fHxvZmZpY2UlMjBidWlsZGluZ3N8ZW58MHx8fHwxNzU1MzUzMDk5fDA&ixlib=rb-4.1.0&q=85",
            "posted_date": datetime.utcnow(),
            "is_active": True,
            "featured": False
        },
        {
            "id": "job-3",
            "title": "Principal Development Engineer (Software)",
            "company_id": "comp-3",
            "company_name": "E and D Recruiters",
            "description": "Leading software development role for innovative tech company",
            "requirements": ["Senior software development experience", "Architecture design", "Team leadership"],
            "responsibilities": ["Lead development teams", "Design system architecture", "Mentor developers"],
            "location": "Somerset West",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.SENIOR,
            "category": JobCategory.IT_TELECOM,
            "is_remote": True,
            "is_hybrid": False,
            "logo_url": "https://images.unsplash.com/photo-1712159018726-4564d92f3ec2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHw0fHx0ZWNoJTIwY29tcGFuaWVzfGVufDB8fHx8MTc1NTM1MzEwNHww&ixlib=rb-4.1.0&q=85",
            "posted_date": datetime.utcnow(),
            "is_active": True,
            "featured": True
        }
    ]
    
    # Insert jobs
    await db.jobs.delete_many({})  # Clear existing  
    await db.jobs.insert_many(sample_jobs)
    
    return {"message": "Sample data seeded successfully", "companies": len(sample_companies), "jobs": len(sample_jobs)}


# Public discount code validation endpoint
@api_router.post("/discount-codes/validate")
async def validate_discount_code_endpoint(
    validation_request: DiscountValidationRequest
):
    """Validate a discount code for a specific package (Public endpoint - no auth required)"""
    code = validation_request.code
    package_type = validation_request.package_type
    package_price = validation_request.package_price
    
    if not code or not code.strip():
        return {
            "valid": False,
            "error": "Discount code is required"
        }
    
    # Get package details to get the price if not provided
    if package_price is None:
        package = await db.packages.find_one({
            "package_type": package_type,
            "is_active": True
        })
        
        if not package:
            return {
                "valid": False,
                "error": "Package not found"
            }
        package_price = package["price"]
    
    # Use a dummy user ID for public validation (we'll use "public" as user_id)
    validation_result = await validate_discount_code(
        code.strip(), 
        "public",  # Use dummy user ID for public validation
        package_type, 
        package_price
    )
    
    if not validation_result["valid"]:
        return {
            "valid": False,
            "error": validation_result["error"]
        }
    
    discount_info = validation_result["discount"]
    
    return {
        "valid": True,
        "discount_details": {
            "code": code.upper(),
            "name": discount_info.name,
            "description": discount_info.description,
            "discount_type": discount_info.discount_type,
            "discount_value": discount_info.discount_value
        },
        "original_price": package_price,
        "discount_amount": validation_result["discount_amount"],
        "final_price": validation_result["final_price"]
    }

# Admin Routes for Discount Codes
async def verify_admin_user(current_user: User = Depends(get_current_user)):
    """Verify that the current user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@api_router.post("/admin/discount-codes", response_model=DiscountCode)
async def create_discount_code(
    discount_data: DiscountCodeCreate,
    admin_user: User = Depends(verify_admin_user)
):
    """Create a new discount code (Admin only)"""
    # Check if code already exists
    existing_code = await db.discount_codes.find_one({"code": discount_data.code.upper()})
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount code already exists"
        )
    
    # Validate discount value
    if discount_data.discount_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount value must be greater than 0"
        )
    
    if discount_data.discount_type == DiscountType.PERCENTAGE and discount_data.discount_value > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Percentage discount cannot exceed 100%"
        )
    
    # Create discount code
    discount_code_data = discount_data.dict()
    discount_code_data["code"] = discount_data.code.upper()
    discount_code_data["created_by"] = admin_user.id
    discount_code_data["status"] = DiscountStatus.ACTIVE
    
    # Set valid_from to now if not provided
    if not discount_code_data.get("valid_from"):
        discount_code_data["valid_from"] = datetime.utcnow()
    
    discount_code = DiscountCode(**discount_code_data)
    await db.discount_codes.insert_one(discount_code.dict())
    
    return discount_code

@api_router.get("/admin/discount-codes", response_model=List[DiscountCode])
async def list_discount_codes(
    status_filter: Optional[DiscountStatus] = None,
    admin_user: User = Depends(verify_admin_user)
):
    """List all discount codes (Admin only)"""
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    discount_codes = await db.discount_codes.find(query).sort("created_date", -1).to_list(1000)
    
    result = []
    for code_doc in discount_codes:
        if "_id" in code_doc:
            del code_doc["_id"]
        result.append(DiscountCode(**code_doc))
    
    return result

@api_router.get("/cv-search")
async def search_cvs(
    position: Optional[str] = Query(None, description="Job title or position"),
    location: Optional[str] = Query(None, description="Location"),
    skills: Optional[str] = Query(None, description="Skills (comma-separated)"),
    current_user: User = Depends(get_current_user)
):
    """Search CVs/profiles with filters - requires CV search package credits"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can search CVs"
        )
    
    # Check if user has active CV search package with remaining credits
    active_cv_package = await db.user_packages.find_one({
        "user_id": current_user.id,
        "package_type": {"$in": ["cv_search_10", "cv_search_20", "cv_search_unlimited", "unlimited_listings"]},
        "is_active": True,
        "$or": [
            {"expiry_date": {"$gt": datetime.utcnow()}},  # For subscription packages
            {"expiry_date": None}  # For one-time packages
        ],
        "$or": [
            {"cv_searches_remaining": {"$gt": 0}},
            {"cv_searches_remaining": None}  # Unlimited
        ]
    })
    
    if not active_cv_package:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No active CV search credits available. Please purchase a CV search package."
        )
    
    # Build search query for job seekers
    query = {"role": "job_seeker"}
    search_conditions = []
    
    if position:
        # Search in desired job title, skills, and experience
        position_regex = {"$regex": position, "$options": "i"}
        search_conditions.append({
            "$or": [
                {"profile.desired_job_title": position_regex},
                {"profile.skills": {"$elemMatch": position_regex}},
                {"profile.experience.0.job_title": position_regex},
                {"profile.experience.1.job_title": position_regex},
                {"profile.experience.2.job_title": position_regex}
            ]
        })
    
    if location:
        location_regex = {"$regex": location, "$options": "i"}
        search_conditions.append({
            "$or": [
                {"profile.location": location_regex},
                {"profile.experience.0.company": location_regex}
            ]
        })
    
    if skills:
        skill_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
        if skill_list:
            skill_conditions = []
            for skill in skill_list:
                skill_regex = {"$regex": skill, "$options": "i"}
                skill_conditions.append({"profile.skills": {"$elemMatch": skill_regex}})
            search_conditions.append({"$or": skill_conditions})
    
    if search_conditions:
        query["$and"] = search_conditions
    
    # Execute search with limit of 10
    cv_results = await db.users.find(query).limit(10).to_list(10)
    
    # Process results to return relevant profile information
    processed_results = []
    for user in cv_results:
        if "_id" in user:
            del user["_id"]
        
        profile = user.get("profile", {})
        
        cv_result = {
            "id": user["id"],
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "email": user.get("email", ""),
            "profile_picture_url": user.get("profile_picture_url"),
            "location": profile.get("location", ""),
            "phone": profile.get("phone", ""),
            "desired_job_title": profile.get("desired_job_title", ""),
            "skills": profile.get("skills", []),
            "experience": profile.get("experience", []),
            "education": profile.get("education", []),
            "resume_url": profile.get("resume_url", ""),
            "profile_completeness": profile.get("profile_completeness", 0),
            "created_at": user.get("created_at")
        }
        processed_results.append(cv_result)
    
    # Deduct search credit (only if not unlimited)
    if active_cv_package.get("cv_searches_remaining") is not None:
        new_count = active_cv_package["cv_searches_remaining"] - 1
        
        # Update package credits
        update_data = {"cv_searches_remaining": new_count}
        
        # Deactivate package if no credits left
        if new_count <= 0:
            update_data["is_active"] = False
        
        await db.user_packages.update_one(
            {"_id": active_cv_package["_id"]},
            {"$set": update_data}
        )
    
    return {
        "results": processed_results,
        "total_found": len(processed_results),
        "search_criteria": {
            "position": position,
            "location": location,
            "skills": skills
        },
        "remaining_searches": active_cv_package.get("cv_searches_remaining", "unlimited") if active_cv_package.get("cv_searches_remaining") != 1 else 0
    }

@api_router.get("/admin/discount-codes/{code_id}", response_model=DiscountCode)
async def get_discount_code(
    code_id: str,
    admin_user: User = Depends(verify_admin_user)
):
    """Get a specific discount code (Admin only)"""
    discount_code = await db.discount_codes.find_one({"id": code_id})
    if not discount_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount code not found"
        )
    
    if "_id" in discount_code:
        del discount_code["_id"]
    
    return DiscountCode(**discount_code)

@api_router.put("/admin/discount-codes/{code_id}", response_model=DiscountCode)
async def update_discount_code(
    code_id: str,
    discount_update: DiscountCodeUpdate,
    admin_user: User = Depends(verify_admin_user)
):
    """Update a discount code (Admin only)"""
    # Check if discount code exists
    existing_code = await db.discount_codes.find_one({"id": code_id})
    if not existing_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount code not found"
        )
    
    # Validate discount value if provided
    update_data = {k: v for k, v in discount_update.dict().items() if v is not None}
    
    if "discount_value" in update_data:
        if update_data["discount_value"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount value must be greater than 0"
            )
        
        # Check percentage limit
        current_type = existing_code.get("discount_type", DiscountType.PERCENTAGE)
        if current_type == DiscountType.PERCENTAGE and update_data["discount_value"] > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentage discount cannot exceed 100%"
            )
    
    update_data["updated_date"] = datetime.utcnow()
    
    # Update the discount code
    await db.discount_codes.update_one(
        {"id": code_id},
        {"$set": update_data}
    )
    
    # Get updated discount code
    updated_code = await db.discount_codes.find_one({"id": code_id})
    if "_id" in updated_code:
        del updated_code["_id"]
    
    return DiscountCode(**updated_code)

@api_router.delete("/admin/discount-codes/{code_id}")
async def delete_discount_code(
    code_id: str,
    admin_user: User = Depends(verify_admin_user)
):
    """Delete a discount code (Admin only)"""
    result = await db.discount_codes.delete_one({"id": code_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount code not found"
        )
    
    return {"message": "Discount code deleted successfully"}

@api_router.post("/admin/discount-codes/{code_id}/deactivate")
async def deactivate_discount_code(
    code_id: str,
    admin_user: User = Depends(verify_admin_user)
):
    """Deactivate a discount code (Admin only)"""
    result = await db.discount_codes.update_one(
        {"id": code_id},
        {"$set": {
            "status": DiscountStatus.INACTIVE,
            "updated_date": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount code not found"
        )
    
    return {"message": "Discount code deactivated successfully"}

@api_router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    image_type: str = Form(...),  # 'profile', 'cover', or 'logo'
    current_user: User = Depends(get_current_user)
):
    """Upload profile, cover, or logo images"""
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed"
        )
    
    # Validate file size (max 10MB for images)
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    
    # Validate image type
    if image_type not in ['profile', 'cover', 'logo']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image type must be 'profile', 'cover', or 'logo'"
        )
    
    try:
        # Create uploads directory if it doesn't exist
        backend_dir = Path(__file__).parent
        uploads_dir = backend_dir / "uploads" / "images"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{current_user.id}_{image_type}_{uuid.uuid4()}.{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return file URL
        base_url = os.getenv('BASE_URL', 'http://localhost:8001')
        file_url = f"{base_url}/api/uploads/images/{unique_filename}"
        
        return {
            "message": f"{image_type.title()} image uploaded successfully",
            "file_url": file_url,
            "filename": file.filename,
            "image_type": image_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )

@api_router.get("/admin/discount-codes/stats/usage")
async def get_discount_code_usage_stats(
    admin_user: User = Depends(verify_admin_user)
):
    """Get discount code usage statistics (Admin only)"""
    # Get total discount codes
    total_codes = await db.discount_codes.count_documents({})
    active_codes = await db.discount_codes.count_documents({"status": DiscountStatus.ACTIVE})
    
    # Get usage statistics from payments
    pipeline = [
        {"$match": {"discount_code": {"$ne": None}, "status": PaymentStatus.COMPLETED}},
        {"$group": {
            "_id": "$discount_code",
            "usage_count": {"$sum": 1},
            "total_discount_amount": {"$sum": "$discount_amount"},
            "total_original_amount": {"$sum": "$amount"},
            "total_final_amount": {"$sum": "$final_amount"}
        }},
        {"$sort": {"usage_count": -1}}
    ]
    
    usage_stats = await db.payments.aggregate(pipeline).to_list(1000)
    
    # Calculate total savings
    total_savings = sum(stat["total_discount_amount"] for stat in usage_stats)
    total_transactions = sum(stat["usage_count"] for stat in usage_stats)
    
    return {
        "total_codes": total_codes,
        "active_codes": active_codes,
        "total_transactions_with_discounts": total_transactions,
        "total_savings": total_savings,
        "code_usage": usage_stats
    }

# Include the router in the main app
app.include_router(api_router)

# Mount static files for uploaded files (using /api prefix for proper routing)
backend_dir = Path(__file__).parent
uploads_path = backend_dir / "uploads"
app.mount("/api/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()