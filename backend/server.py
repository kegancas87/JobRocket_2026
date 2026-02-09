"""
JobRocket API - Main Server
Refactored for multi-tenant SaaS architecture
"""

from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import secrets
import hashlib
import urllib.parse

# Import models
from models import (
    UserRole, AccountRole, SubscriptionStatus, BillingCycle,
    TierId, FeatureId, AddonId,
    JobType, WorkType, ApplicationStatus,
    PaymentStatus, PaymentProvider, InvitationStatus,
    Account, AccountCreate, AccountUpdate,
    User, UserRegister, UserLogin, Token, UserProfileUpdate,
    TeamInvitation, TeamInvitationCreate,
    Job, JobCreate, JobApplication, JobApplicationCreate,
    Payment, SubscriptionPaymentRequest, AddonPaymentRequest,
    DiscountCode, DiscountCodeCreate,
    get_tier_config, get_all_tiers, get_addon_config, tier_has_feature,
    TIER_CONFIG, ADDON_CONFIG
)

# Import services
from services import (
    FeatureAccessService, create_feature_service,
    AccountService, create_account_service
)

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Payment Configuration
PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.environ.get('PAYFAST_PASSPHRASE')
PAYFAST_SANDBOX = os.environ.get('PAYFAST_SANDBOX', 'True').lower() == 'true'

# Production Configuration
BASE_URL = os.environ.get('BASE_URL', 'https://jobrocket.co.za')
UPLOAD_PATH = os.environ.get('UPLOAD_PATH', str(ROOT_DIR / 'uploads'))
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', '10485760'))

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create services
feature_service = create_feature_service(db)
account_service = create_account_service(db)

# Create app
app = FastAPI(title="JobRocket API", version="2.0.0")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
Path(UPLOAD_PATH).mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_PATH), name="uploads")


# ============================================
# Authentication Helpers
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current authenticated user"""
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
    
    if "_id" in user:
        del user["_id"]
    
    return User(**user)


async def get_current_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a recruiter with an active account"""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access this resource"
        )
    
    if not current_user.account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No account associated with this user"
        )
    
    return current_user


async def verify_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def check_feature(
    current_user: User,
    feature_id: FeatureId
) -> bool:
    """Check if user's account has access to a feature"""
    if not current_user.account_id:
        return False
    
    has_access, error = await feature_service.check_feature_access(
        current_user.account_id, 
        feature_id
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Feature not available on your current plan"
        )
    
    return True


# ============================================
# Auth Endpoints
# ============================================

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user. For recruiters, an account is auto-created."""
    
    # Check if email exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": user_data.role,
        "account_id": None,
        "account_role": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    await db.users.insert_one(user_dict)
    
    # For recruiters, auto-create an account
    if user_data.role == UserRole.RECRUITER:
        company_name = user_data.company_name or f"{user_data.first_name}'s Company"
        account = await account_service.create_account_for_user(
            user_id=user_dict["id"],
            company_name=company_name
        )
        user_dict["account_id"] = account.id
        user_dict["account_role"] = AccountRole.OWNER
    
    # Create token
    access_token = create_access_token(data={"sub": user_dict["id"]})
    
    # Prepare user response (remove sensitive data)
    user_response = {k: v for k, v in user_dict.items() if k != "password_hash"}
    if "_id" in user_response:
        del user_response["_id"]
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login with email and password"""
    
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create token
    access_token = create_access_token(data={"sub": user["id"]})
    
    # Prepare user response
    if "_id" in user:
        del user["_id"]
    if "password_hash" in user:
        del user["password_hash"]
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile with account details"""
    
    user_dict = current_user.dict()
    user_dict.pop("password_hash", None)
    
    # Add account details for recruiters
    if current_user.account_id:
        account = await account_service.get_account(current_user.account_id)
        if account:
            tier_config = get_tier_config(TierId(account["tier_id"]))
            features, active_addons = await feature_service.get_account_features(current_user.account_id)
            
            user_dict["account"] = {
                "id": account["id"],
                "name": account["name"],
                "tier_id": account["tier_id"],
                "tier_name": tier_config["name"],
                "subscription_status": account["subscription_status"],
                "subscription_end_date": account.get("subscription_end_date"),
                "company_logo_url": account.get("company_logo_url"),
                "company_description": account.get("company_description"),
                "included_users": tier_config["included_users"],
                "current_user_count": account.get("current_user_count", 1),
                "features": [f.value if hasattr(f, 'value') else f for f in features],
                "active_addons": [a.value if hasattr(a, 'value') else a for a in active_addons],
            }
    
    return user_dict


# ============================================
# Account Endpoints
# ============================================

@api_router.get("/account")
async def get_account(current_user: User = Depends(get_current_recruiter)):
    """Get current user's account details"""
    
    account = await account_service.get_account(current_user.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_config = get_tier_config(TierId(account["tier_id"]))
    features, active_addons = await feature_service.get_account_features(current_user.account_id)
    available_addons = await feature_service.get_available_addons(current_user.account_id)
    
    return {
        **account,
        "tier_name": tier_config["name"],
        "tier_price": tier_config["price_monthly"],
        "included_users": tier_config["included_users"],
        "extra_user_price": tier_config["extra_user_price"],
        "max_users": tier_config["included_users"] + account.get("extra_users_count", 0),
        "features": [f.value if hasattr(f, 'value') else f for f in features],
        "active_addons": [a.value if hasattr(a, 'value') else a for a in active_addons],
        "available_addons": available_addons,
        "company_profile_level": tier_config["company_profile_level"].value,
    }


@api_router.put("/account")
async def update_account(
    update_data: AccountUpdate,
    current_user: User = Depends(get_current_recruiter)
):
    """Update account details (company branding, etc.)"""
    
    # Check permission
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only account owner or admin can update account details"
        )
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    updated = await account_service.update_account(current_user.account_id, update_dict)
    
    return updated


@api_router.get("/account/users")
async def get_account_users(current_user: User = Depends(get_current_recruiter)):
    """Get all users in the current account"""
    
    users = await account_service.get_account_users(current_user.account_id)
    return users


@api_router.post("/account/invite")
async def invite_user(
    invitation_data: TeamInvitationCreate,
    current_user: User = Depends(get_current_recruiter)
):
    """Invite a new user to the account"""
    
    # Check permission
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only account owner or admin can invite users"
        )
    
    # Check if can add user
    can_add, error = await feature_service.can_add_user(current_user.account_id)
    if not can_add:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error)
    
    invitation, error = await account_service.create_invitation(
        account_id=current_user.account_id,
        inviter_user_id=current_user.id,
        email=invitation_data.email,
        first_name=invitation_data.first_name,
        last_name=invitation_data.last_name,
        account_role=invitation_data.account_role
    )
    
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return {
        "message": "Invitation sent successfully",
        "invitation_token": invitation.invitation_token,
        # In production, send this via email instead of returning it
    }


@api_router.get("/account/invitations")
async def get_invitations(current_user: User = Depends(get_current_recruiter)):
    """Get pending invitations for the account"""
    
    invitations = await account_service.get_pending_invitations(current_user.account_id)
    return invitations


@api_router.post("/invitations/{token}/accept")
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """Accept a team invitation"""
    
    success, error = await account_service.accept_invitation(token, current_user.id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return {"message": "Invitation accepted successfully"}


@api_router.delete("/account/users/{user_id}")
async def remove_user(
    user_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Remove a user from the account"""
    
    success, error = await account_service.remove_user_from_account(
        current_user.account_id,
        user_id,
        current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return {"message": "User removed successfully"}


# ============================================
# Tier Endpoints
# ============================================

@api_router.get("/tiers")
async def get_tiers():
    """Get all available subscription tiers"""
    
    tiers = []
    for tier in get_all_tiers():
        tiers.append({
            "id": tier["id"].value,
            "name": tier["name"],
            "price_monthly": tier["price_monthly"],
            "currency": tier["currency"],
            "included_users": tier["included_users"],
            "extra_user_price": tier["extra_user_price"],
            "multi_user_access": tier["multi_user_access"],
            "company_profile_level": tier["company_profile_level"].value,
            "features": [f.value for f in tier["features"]],
            "available_addons": [a.value for a in tier["available_addons"]],
        })
    
    return tiers


@api_router.get("/tiers/{tier_id}")
async def get_tier(tier_id: str):
    """Get details for a specific tier"""
    
    try:
        tier = get_tier_config(TierId(tier_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    return {
        "id": tier["id"].value,
        "name": tier["name"],
        "price_monthly": tier["price_monthly"],
        "currency": tier["currency"],
        "included_users": tier["included_users"],
        "extra_user_price": tier["extra_user_price"],
        "multi_user_access": tier["multi_user_access"],
        "company_profile_level": tier["company_profile_level"].value,
        "features": [f.value for f in tier["features"]],
        "available_addons": [a.value for a in tier["available_addons"]],
    }


@api_router.get("/addons")
async def get_addons(current_user: User = Depends(get_current_recruiter)):
    """Get add-ons available for purchase by current account"""
    
    addons = await feature_service.get_available_addons(current_user.account_id)
    return addons


# ============================================
# Job Endpoints
# ============================================

@api_router.post("/jobs", response_model=dict)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_recruiter)
):
    """Create a new job listing"""
    
    # Get account for company details
    account = await account_service.get_account(current_user.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check subscription status
    if account.get("subscription_status") not in [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value, "active", "trial"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required to post jobs"
        )
    
    job_dict = {
        "id": str(uuid.uuid4()),
        "account_id": current_user.account_id,
        "posted_by": current_user.id,
        "company_name": account["name"],
        "logo_url": account.get("company_logo_url"),
        "posted_date": datetime.utcnow(),
        "expiry_date": datetime.utcnow() + timedelta(days=35),
        "is_active": True,
        **job_data.dict()
    }
    
    await db.jobs.insert_one(job_dict)
    
    if "_id" in job_dict:
        del job_dict["_id"]
    
    return job_dict


@api_router.get("/jobs")
async def get_jobs(
    current_user: User = Depends(get_current_recruiter),
    skip: int = 0,
    limit: int = 100
):
    """Get jobs for current account"""
    
    jobs = []
    cursor = db.jobs.find({
        "account_id": current_user.account_id
    }).sort("posted_date", -1).skip(skip).limit(limit)
    
    async for job in cursor:
        if "_id" in job:
            del job["_id"]
        jobs.append(job)
    
    return jobs


@api_router.get("/public/jobs")
async def get_public_jobs(
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    work_type: Optional[str] = None
):
    """Get all active public job listings"""
    
    query = {
        "is_active": True,
        "expiry_date": {"$gt": datetime.utcnow()}
    }
    
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if job_type:
        query["job_type"] = job_type
    if work_type:
        query["work_type"] = work_type
    
    jobs = []
    cursor = db.jobs.find(query).sort("posted_date", -1).skip(skip).limit(limit)
    
    async for job in cursor:
        if "_id" in job:
            del job["_id"]
        jobs.append(job)
    
    total = await db.jobs.count_documents(query)
    
    return {"jobs": jobs, "total": total}


@api_router.get("/public/jobs/{job_id}")
async def get_public_job(job_id: str):
    """Get a specific job listing"""
    
    job = await db.jobs.find_one({"id": job_id, "is_active": True})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if "_id" in job:
        del job["_id"]
    
    # Get account info for company page link
    account = await db.accounts.find_one({"id": job["account_id"]})
    if account:
        job["company"] = {
            "id": account["id"],
            "name": account["name"],
            "logo_url": account.get("company_logo_url"),
            "industry": account.get("company_industry"),
            "location": account.get("company_location"),
        }
    
    return job


@api_router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    job_data: JobCreate,
    current_user: User = Depends(get_current_recruiter)
):
    """Update a job listing"""
    
    job = await db.jobs.find_one({
        "id": job_id,
        "account_id": current_user.account_id
    })
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_dict = job_data.dict()
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.jobs.update_one(
        {"id": job_id},
        {"$set": update_dict}
    )
    
    return {"message": "Job updated successfully"}


@api_router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Deactivate a job listing"""
    
    result = await db.jobs.update_one(
        {"id": job_id, "account_id": current_user.account_id},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


# ============================================
# Job Applications Endpoints
# ============================================

@api_router.post("/applications")
async def apply_to_job(
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_user)
):
    """Apply to a job (job seekers only)"""
    
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can apply to jobs"
        )
    
    # Get job
    job = await db.jobs.find_one({"id": application_data.job_id, "is_active": True})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    existing = await db.job_applications.find_one({
        "job_id": application_data.job_id,
        "applicant_id": current_user.id
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )
    
    # Create application snapshot
    applicant_snapshot = {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "skills": current_user.skills,
        "location": current_user.location,
        "about_me": current_user.about_me,
    }
    
    application_dict = {
        "id": str(uuid.uuid4()),
        "job_id": application_data.job_id,
        "applicant_id": current_user.id,
        "account_id": job["account_id"],
        "status": ApplicationStatus.PENDING,
        "cover_letter": application_data.cover_letter,
        "resume_url": application_data.resume_url,
        "additional_info": application_data.additional_info,
        "applicant_snapshot": applicant_snapshot,
        "applied_date": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
    }
    
    await db.job_applications.insert_one(application_dict)
    
    if "_id" in application_dict:
        del application_dict["_id"]
    
    return application_dict


@api_router.get("/applications")
async def get_my_applications(current_user: User = Depends(get_current_user)):
    """Get applications for current user (job seekers see their applications, recruiters see applications to their jobs)"""
    
    if current_user.role == UserRole.JOB_SEEKER:
        query = {"applicant_id": current_user.id}
    else:
        query = {"account_id": current_user.account_id}
    
    applications = []
    cursor = db.job_applications.find(query).sort("applied_date", -1)
    
    async for app in cursor:
        if "_id" in app:
            del app["_id"]
        
        # Add job details
        job = await db.jobs.find_one({"id": app["job_id"]})
        if job:
            app["job"] = {
                "title": job["title"],
                "company_name": job["company_name"],
                "location": job["location"],
            }
        
        applications.append(app)
    
    return applications


@api_router.get("/jobs/{job_id}/applications")
async def get_job_applications(
    job_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Get applications for a specific job"""
    
    # Verify job belongs to account
    job = await db.jobs.find_one({
        "id": job_id,
        "account_id": current_user.account_id
    })
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    applications = []
    cursor = db.job_applications.find({"job_id": job_id}).sort("applied_date", -1)
    
    async for app in cursor:
        if "_id" in app:
            del app["_id"]
        applications.append(app)
    
    return applications


@api_router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status: ApplicationStatus,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_recruiter)
):
    """Update application status (recruiters only)"""
    
    # Check feature access for status tracking
    await check_feature(current_user, FeatureId.CANDIDATE_STATUS_TRACKING)
    
    result = await db.job_applications.update_one(
        {"id": application_id, "account_id": current_user.account_id},
        {"$set": {
            "status": status,
            "notes": notes,
            "reviewed_by": current_user.id,
            "last_updated": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": "Application status updated"}


# ============================================
# Public Company Profile Endpoints
# ============================================

@api_router.get("/public/company/{account_id}")
async def get_public_company(account_id: str):
    """Get public company profile"""
    
    account = await db.accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Return only public information
    return {
        "id": account["id"],
        "name": account["name"],
        "company_logo_url": account.get("company_logo_url"),
        "company_cover_image_url": account.get("company_cover_image_url"),
        "company_description": account.get("company_description"),
        "company_website": account.get("company_website"),
        "company_linkedin": account.get("company_linkedin"),
        "company_industry": account.get("company_industry"),
        "company_size": account.get("company_size"),
        "company_location": account.get("company_location"),
    }


@api_router.get("/public/company/{account_id}/jobs")
async def get_company_jobs(account_id: str):
    """Get active jobs for a company"""
    
    jobs = []
    cursor = db.jobs.find({
        "account_id": account_id,
        "is_active": True,
        "expiry_date": {"$gt": datetime.utcnow()}
    }).sort("posted_date", -1)
    
    async for job in cursor:
        if "_id" in job:
            del job["_id"]
        jobs.append(job)
    
    return jobs


# ============================================
# User Profile Endpoints
# ============================================

@api_router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    
    update_dict = {k: v for k, v in profile_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_dict}
    )
    
    return {"message": "Profile updated successfully"}


# ============================================
# Payment Endpoints (Payfast)
# ============================================

def generate_payfast_signature(data: dict, passphrase: str = None) -> str:
    """Generate PayFast signature"""
    filtered_data = {k: str(v) for k, v in data.items() if v is not None and v != '' and k != 'signature'}
    sorted_params = sorted(filtered_data.items())
    param_string = '&'.join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params])
    
    if passphrase:
        param_string += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
    
    return hashlib.md5(param_string.encode('utf-8')).hexdigest()


@api_router.post("/payments/subscription")
async def initiate_subscription_payment(
    payment_data: SubscriptionPaymentRequest,
    current_user: User = Depends(get_current_recruiter)
):
    """Initiate subscription payment via Payfast"""
    
    tier = get_tier_config(payment_data.tier_id)
    amount = tier["price_monthly"]
    
    # Create payment record
    payment_id = str(uuid.uuid4())
    payment_dict = {
        "id": payment_id,
        "account_id": current_user.account_id,
        "user_id": current_user.id,
        "payment_type": "subscription",
        "tier_id": payment_data.tier_id,
        "amount": amount,
        "final_amount": amount,
        "currency": "ZAR",
        "provider": PaymentProvider.PAYFAST,
        "status": PaymentStatus.PENDING,
        "created_at": datetime.utcnow(),
    }
    
    await db.payments.insert_one(payment_dict)
    
    # Generate Payfast data
    payfast_data = {
        "merchant_id": PAYFAST_MERCHANT_ID,
        "merchant_key": PAYFAST_MERCHANT_KEY,
        "return_url": f"{BASE_URL}/payment/success?payment_id={payment_id}",
        "cancel_url": f"{BASE_URL}/payment/cancel?payment_id={payment_id}",
        "notify_url": f"{BASE_URL}/api/payments/webhook",
        "name_first": current_user.first_name,
        "name_last": current_user.last_name,
        "email_address": current_user.email,
        "m_payment_id": payment_id,
        "amount": f"{amount:.2f}",
        "item_name": f"JobRocket {tier['name']} Subscription",
        "item_description": f"Monthly subscription to {tier['name']} plan",
    }
    
    payfast_data["signature"] = generate_payfast_signature(payfast_data, PAYFAST_PASSPHRASE)
    
    payfast_url = "https://sandbox.payfast.co.za/eng/process" if PAYFAST_SANDBOX else "https://www.payfast.co.za/eng/process"
    
    return {
        "payment_id": payment_id,
        "payfast_url": payfast_url,
        "payfast_data": payfast_data,
    }


@api_router.post("/payments/webhook")
async def payment_webhook(request: Request):
    """Handle Payfast payment notification for all payment types"""
    
    form_data = await request.form()
    data = dict(form_data)
    
    payment_id = data.get("m_payment_id")
    payment_status = data.get("payment_status")
    
    if not payment_id:
        return {"status": "error", "message": "Missing payment ID"}
    
    payment = await db.payments.find_one({"id": payment_id})
    if not payment:
        return {"status": "error", "message": "Payment not found"}
    
    if payment_status == "COMPLETE":
        # Use billing service to complete payment (handles all types)
        success, result = await billing_service.complete_payment(
            payment_id,
            data.get("pf_payment_id", "")
        )
        
        if not success:
            logger.error(f"Failed to complete payment {payment_id}")
    else:
        await billing_service.fail_payment(
            payment_id,
            data.get("payment_status", "Unknown error")
        )
    
    return {"status": "ok"}


# ============================================
# Admin Stats Endpoints
# ============================================

from services.admin_stats_service import create_admin_stats_service
admin_stats_service = create_admin_stats_service(db)

@api_router.get("/admin/stats")
async def get_admin_stats(
    force_refresh: bool = False,
    current_user: User = Depends(verify_admin_user)
):
    """Get admin dashboard statistics (cached, refreshes at 6am/6pm SAST)"""
    stats = await admin_stats_service.get_stats(force_refresh=force_refresh)
    return stats


# ============================================
# AI Matching Endpoints
# ============================================

from services.ai_matching_service import get_ai_matching_service, set_ai_matching_enabled
ai_service = get_ai_matching_service(db)

@api_router.get("/ai-matching/status")
async def get_ai_matching_status_public(current_user: User = Depends(get_current_user)):
    """Check if AI matching is enabled (for any authenticated user)"""
    return {
        "ai_enabled": ai_service.is_ai_enabled,
        "method": "ai" if ai_service.is_ai_enabled else "keyword"
    }

@api_router.get("/admin/ai-matching/status")
async def get_ai_matching_status(current_user: User = Depends(verify_admin_user)):
    """Check if AI matching is enabled"""
    return {
        "ai_enabled": ai_service.is_ai_enabled,
        "method": "ai" if ai_service.is_ai_enabled else "keyword"
    }

@api_router.post("/admin/ai-matching/toggle")
async def toggle_ai_matching(
    enabled: bool,
    current_user: User = Depends(verify_admin_user)
):
    """Enable/disable AI matching (kill switch)"""
    set_ai_matching_enabled(enabled)
    return {
        "success": True,
        "ai_enabled": enabled,
        "message": f"AI matching {'enabled' if enabled else 'disabled'}. Using {'AI' if enabled else 'keyword'} matching."
    }

@api_router.post("/cv-search/match")
async def match_candidates(
    job_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Get AI/keyword match scores for candidates against a job"""
    # Check feature access
    await check_feature(current_user, FeatureId.TALENT_CV_DATABASE)
    
    # Get job
    job = await db.jobs.find_one({"id": job_id, "account_id": current_user.account_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all job seekers
    candidates = []
    cursor = db.users.find({"role": "job_seeker"}).limit(100)
    async for user in cursor:
        if "_id" in user:
            del user["_id"]
        if "password_hash" in user:
            del user["password_hash"]
        candidates.append(user)
    
    # Get match scores
    results = await ai_service.batch_match(job, candidates)
    
    return {
        "job_id": job_id,
        "job_title": job.get("title"),
        "matching_method": "ai" if ai_service.is_ai_enabled else "keyword",
        "candidates": results
    }


# ============================================
# CV Database / Talent Pool Endpoints
# ============================================

@api_router.get("/cv-search")
async def search_candidates(
    current_user: User = Depends(get_current_recruiter),
    q: Optional[str] = None,
    skills: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Search the CV database / talent pool"""
    # Check feature access
    await check_feature(current_user, FeatureId.TALENT_CV_DATABASE)
    
    # Build query
    query = {"role": "job_seeker"}
    
    if q:
        query["$or"] = [
            {"first_name": {"$regex": q, "$options": "i"}},
            {"last_name": {"$regex": q, "$options": "i"}},
            {"about_me": {"$regex": q, "$options": "i"}},
            {"skills": {"$elemMatch": {"$regex": q, "$options": "i"}}}
        ]
    
    if skills:
        skill_list = [s.strip() for s in skills.split(",")]
        query["skills"] = {"$in": skill_list}
    
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    # Execute search
    candidates = []
    cursor = db.users.find(query).skip(skip).limit(limit)
    async for user in cursor:
        if "_id" in user:
            del user["_id"]
        if "password_hash" in user:
            del user["password_hash"]
        candidates.append(user)
    
    total = await db.users.count_documents(query)
    
    return {
        "candidates": candidates,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ============================================
# Bulk Upload Endpoints
# ============================================

from services.bulk_upload_service import create_bulk_upload_service
bulk_upload_service = create_bulk_upload_service(db)

@api_router.post("/jobs/bulk")
async def bulk_upload_jobs(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_recruiter)
):
    """Bulk upload jobs from CSV or Excel file (Pro+ only)"""
    # Check feature access
    await check_feature(current_user, FeatureId.JOB_BULK_UPLOAD)
    
    # Get account for company details
    account = await account_service.get_account(current_user.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Read file content
    content = await file.read()
    
    # Process file
    result = await bulk_upload_service.process_file(
        file_content=content,
        filename=file.filename,
        account_id=current_user.account_id,
        user_id=current_user.id,
        company_name=account["name"],
        logo_url=account.get("company_logo_url")
    )
    
    return result

@api_router.get("/jobs/bulk/template")
async def get_bulk_upload_template(
    format: str = "csv",
    current_user: User = Depends(get_current_recruiter)
):
    """Download bulk upload template file"""
    from fastapi.responses import Response
    
    try:
        content, filename = bulk_upload_service.generate_template(format)
        
        content_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Billing Endpoints
# ============================================

from services.billing_service import create_billing_service
billing_service = create_billing_service(db)

@api_router.get("/billing")
async def get_billing_summary(current_user: User = Depends(get_current_recruiter)):
    """Get billing summary for current account"""
    return await billing_service.get_billing_summary(current_user.account_id)

@api_router.get("/billing/history")
async def get_billing_history(
    current_user: User = Depends(get_current_recruiter),
    limit: int = 50,
    skip: int = 0
):
    """Get payment/billing history"""
    history = await billing_service.get_billing_history(
        current_user.account_id, limit, skip
    )
    return {"history": history, "total": len(history)}

@api_router.post("/billing/addon")
async def purchase_addon(
    addon_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Initiate add-on purchase via Payfast"""
    from models.tiers import get_addon_config
    from models.enums import AddonId
    
    try:
        addon = get_addon_config(AddonId(addon_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid add-on")
    
    if not addon:
        raise HTTPException(status_code=404, detail="Add-on not found")
    
    # Calculate price
    amount = addon.get("price_monthly") or addon.get("price_once", 0)
    
    # Create payment record
    payment = await billing_service.create_payment_record(
        account_id=current_user.account_id,
        user_id=current_user.id,
        payment_type="addon",
        amount=amount,
        addon_id=AddonId(addon_id)
    )
    
    # Generate Payfast data
    payfast_data = {
        "merchant_id": PAYFAST_MERCHANT_ID,
        "merchant_key": PAYFAST_MERCHANT_KEY,
        "return_url": f"{BASE_URL}/payment/success?payment_id={payment['id']}",
        "cancel_url": f"{BASE_URL}/payment/cancel?payment_id={payment['id']}",
        "notify_url": f"{BASE_URL}/api/payments/webhook",
        "name_first": current_user.first_name,
        "name_last": current_user.last_name,
        "email_address": current_user.email,
        "m_payment_id": payment['id'],
        "amount": f"{amount:.2f}",
        "item_name": f"JobRocket Add-on: {addon['name']}",
        "item_description": addon.get("description", "Feature add-on"),
    }
    
    payfast_data["signature"] = generate_payfast_signature(payfast_data, PAYFAST_PASSPHRASE)
    payfast_url = "https://sandbox.payfast.co.za/eng/process" if PAYFAST_SANDBOX else "https://www.payfast.co.za/eng/process"
    
    return {
        "payment_id": payment['id'],
        "payfast_url": payfast_url,
        "payfast_data": payfast_data
    }

@api_router.delete("/billing/addon/{addon_purchase_id}")
async def cancel_addon(
    addon_purchase_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Cancel an add-on subscription"""
    result = await billing_service.cancel_addon(
        current_user.account_id, addon_purchase_id
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@api_router.post("/billing/extra-seats")
async def purchase_extra_seats(
    quantity: int,
    current_user: User = Depends(get_current_recruiter)
):
    """Purchase extra user seats via Payfast"""
    if quantity < 1 or quantity > 100:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 100")
    
    amount = quantity * billing_service.EXTRA_USER_PRICE
    
    # Create payment record
    payment = await billing_service.create_payment_record(
        account_id=current_user.account_id,
        user_id=current_user.id,
        payment_type="extra_seats",
        amount=amount,
        extra_seats=quantity
    )
    
    # Generate Payfast data
    payfast_data = {
        "merchant_id": PAYFAST_MERCHANT_ID,
        "merchant_key": PAYFAST_MERCHANT_KEY,
        "return_url": f"{BASE_URL}/payment/success?payment_id={payment['id']}",
        "cancel_url": f"{BASE_URL}/payment/cancel?payment_id={payment['id']}",
        "notify_url": f"{BASE_URL}/api/payments/webhook",
        "name_first": current_user.first_name,
        "name_last": current_user.last_name,
        "email_address": current_user.email,
        "m_payment_id": payment['id'],
        "amount": f"{amount:.2f}",
        "item_name": f"JobRocket Extra User Seats ({quantity})",
        "item_description": f"{quantity} additional user seat(s) at R899/month each",
    }
    
    payfast_data["signature"] = generate_payfast_signature(payfast_data, PAYFAST_PASSPHRASE)
    payfast_url = "https://sandbox.payfast.co.za/eng/process" if PAYFAST_SANDBOX else "https://www.payfast.co.za/eng/process"
    
    return {
        "payment_id": payment['id'],
        "quantity": quantity,
        "total": amount,
        "payfast_url": payfast_url,
        "payfast_data": payfast_data
    }

@api_router.get("/billing/extra-seats")
async def get_extra_seats(current_user: User = Depends(get_current_recruiter)):
    """Get extra user seats for account"""
    seats = await billing_service.get_extra_seats(current_user.account_id)
    return {"seats": seats, "total": len(seats)}

@api_router.delete("/billing/extra-seats/{seat_id}")
async def cancel_extra_seat(
    seat_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Cancel an extra user seat"""
    result = await billing_service.cancel_extra_seat(
        current_user.account_id, seat_id
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============================================
# Health Check
# ============================================

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# Include router
app.include_router(api_router)


# Root redirect
@app.get("/")
async def root():
    return {"message": "JobRocket API v2.0.0", "docs": "/docs"}
