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
from services.email_service import email_service, EmailType, EmailTemplates

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

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

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
for subdir in ["cvs", "profile_pictures", "documents", "images"]:
    (Path(UPLOAD_PATH) / subdir).mkdir(parents=True, exist_ok=True)

# NOTE: Static files mount is done AFTER router include to avoid shadowing upload POST endpoints
# See end of file for static file mount


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
    
    # Check subscription status
    account = await db.accounts.find_one({"id": current_user.account_id})
    if account:
        subscription_status = account.get("subscription_status", "inactive")
        
        # Allow active and trial status
        if subscription_status not in ["active", "trial", "past_due"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription inactive. Please make a payment to continue using JobRocket."
            )
        
        # For past_due, check if still in grace period
        if subscription_status == "past_due":
            grace_period_start = account.get("grace_period_start")
            if grace_period_start:
                grace_end = grace_period_start + timedelta(days=7)
                if datetime.utcnow() > grace_end:
                    # Grace period expired
                    await db.accounts.update_one(
                        {"id": current_user.account_id},
                        {"$set": {"subscription_status": "inactive"}}
                    )
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail="Grace period expired. Please make a payment to reactivate your account."
                    )
    
    # Check if user is an extra seat user with inactive seat
    extra_seat = await db.extra_seats.find_one({"user_id": current_user.id})
    if extra_seat:
        if not extra_seat.get("is_active") or extra_seat.get("payment_status") != "paid":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Your user seat is inactive. Please contact your account owner to make a payment."
            )
    
    return current_user


async def get_recruiter_read_only(current_user: User = Depends(get_current_user)) -> tuple:
    """
    Get recruiter with read-only flag for users with inactive seats.
    Returns (user, is_read_only) tuple.
    """
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
    
    is_read_only = False
    
    # Check subscription status
    account = await db.accounts.find_one({"id": current_user.account_id})
    if account:
        subscription_status = account.get("subscription_status", "inactive")
        
        # Inactive subscription blocks access completely
        if subscription_status not in ["active", "trial", "past_due"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription inactive. Please make a payment to continue using JobRocket."
            )
    
    # Check if user is an extra seat user with inactive seat - give read-only access
    extra_seat = await db.extra_seats.find_one({"user_id": current_user.id})
    if extra_seat:
        if not extra_seat.get("is_active") or extra_seat.get("payment_status") != "paid":
            is_read_only = True
    
    return current_user, is_read_only


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


@api_router.post("/auth/google")
async def google_auth(request: Request):
    """Authenticate or register via Google OAuth"""
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    
    body = await request.json()
    credential = body.get("credential")
    role = body.get("role", "job_seeker")
    company_name = body.get("company_name")
    
    if not credential:
        raise HTTPException(status_code=400, detail="Missing Google credential")
    
    # REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    try:
        idinfo = id_token.verify_oauth2_token(credential, google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception as e:
        logger.error(f"Google token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    google_email = idinfo.get("email")
    if not google_email:
        raise HTTPException(status_code=400, detail="Google account has no email")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": google_email})
    
    if existing_user:
        # Login existing user
        await db.users.update_one(
            {"id": existing_user["id"]},
            {"$set": {"last_login": datetime.utcnow(), "profile_picture_url": existing_user.get("profile_picture_url") or idinfo.get("picture")}}
        )
        access_token = create_access_token(data={"sub": existing_user["id"]})
        if "_id" in existing_user:
            del existing_user["_id"]
        if "password_hash" in existing_user:
            del existing_user["password_hash"]
        return Token(access_token=access_token, token_type="bearer", user=existing_user)
    
    # Register new user
    first_name = idinfo.get("given_name", google_email.split("@")[0])
    last_name = idinfo.get("family_name", "")
    picture_url = idinfo.get("picture")
    
    # Create a random password hash for Google users (they won't use password login)
    random_password_hash = get_password_hash(secrets.token_urlsafe(32))
    
    new_user = User(
        email=google_email,
        password_hash=random_password_hash,
        first_name=first_name,
        last_name=last_name,
        role=UserRole(role) if role in [r.value for r in UserRole] else UserRole.JOB_SEEKER,
        profile_picture_url=picture_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=datetime.utcnow(),
    )
    
    user_dict = new_user.dict()
    user_dict["google_id"] = idinfo.get("sub")
    user_dict["auth_provider"] = "google"
    
    # For recruiters, create account
    if new_user.role == UserRole.RECRUITER:
        account_name = company_name or f"{first_name}'s Company"
        new_account = Account(
            name=account_name,
            owner_user_id=new_user.id,
            tier_id=TierId.STARTER,
            subscription_status=SubscriptionStatus.ACTIVE,
            subscription_start_date=datetime.utcnow(),
            subscription_end_date=datetime.utcnow() + timedelta(days=30),
        )
        await db.accounts.insert_one(new_account.dict())
        user_dict["account_id"] = new_account.id
        user_dict["account_role"] = AccountRole.OWNER.value
    
    await db.users.insert_one(user_dict)
    
    access_token = create_access_token(data={"sub": new_user.id})
    
    # Clean response
    if "_id" in user_dict:
        del user_dict["_id"]
    if "password_hash" in user_dict:
        del user_dict["password_hash"]
    
    return Token(access_token=access_token, token_type="bearer", user=user_dict)


@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile with account details"""
    
    # Fetch fresh user data from DB to get all fields including arrays
    user_data = await db.users.find_one({"id": current_user.id})
    if user_data and "_id" in user_data:
        del user_data["_id"]
    
    user_dict = user_data if user_data else current_user.dict()
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
            "job_post_limit": tier.get("job_post_limit"),
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
    
    # Check job post limit for Starter tier
    tier_config = get_tier_config(TierId(account.get("tier_id", "starter")))
    job_post_limit = tier_config.get("job_post_limit")
    if job_post_limit:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        job_count = await db.jobs.count_documents({
            "account_id": current_user.account_id,
            "posted_date": {"$gte": thirty_days_ago}
        })
        if job_count >= job_post_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Job posting limit reached ({job_post_limit} posts/month). Upgrade to Growth for unlimited posting."
            )
    
    job_dict = {
        "id": str(uuid.uuid4()),
        "account_id": current_user.account_id,
        "posted_by": current_user.id,
        "company_name": account["name"],
        "logo_url": account.get("company_logo_url"),
        "posted_date": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "expiry_date": datetime.utcnow() + timedelta(days=35),
        "is_active": True,
        **job_data.dict()
    }
    
    # Also store employment_type for alert matching (based on job_type)
    job_dict["employment_type"] = job_dict.get("job_type", "")
    
    await db.jobs.insert_one(job_dict)
    
    if "_id" in job_dict:
        del job_dict["_id"]
    
    # Trigger job alert notifications (async background task simulation)
    await check_and_send_job_alerts(job_dict)
    
    return job_dict


async def check_and_send_job_alerts(job: dict):
    """Check job alerts and send email notifications for matching alerts"""
    try:
        base_url = os.environ.get("BASE_URL", "https://jobrocket.co.za")
        
        # Find all active job alerts that might match this job
        cursor = db.job_alerts.find({"is_active": True})
        
        async for alert in cursor:
            # Check if all criteria match (strict matching)
            
            # 1. Job Title Match
            job_title_match = alert.get("job_title", "").lower() in job.get("title", "").lower() or \
                              job.get("title", "").lower() in alert.get("job_title", "").lower()
            
            # 2. Location Match
            location_match = alert.get("location", "").lower() in job.get("location", "").lower() or \
                             job.get("location", "").lower() in alert.get("location", "").lower()
            
            # 3. Employment Type matching (Permanent/Contract) - OR logic within selected types
            job_employment_type = job.get("employment_type", "").lower()
            alert_employment_types = [et.lower() for et in alert.get("employment_types", [])]
            employment_type_match = False
            for alert_et in alert_employment_types:
                if alert_et in job_employment_type or \
                   (alert_et == "permanent" and ("full" in job_employment_type or "permanent" in job_employment_type)) or \
                   (alert_et == "contract" and "contract" in job_employment_type):
                    employment_type_match = True
                    break
            
            # 4. Work Type matching (In Office/Hybrid/Remote) - OR logic within selected types
            job_work_type = job.get("work_type", "").lower()
            alert_work_types = [wt.lower() for wt in alert.get("work_types", [])]
            work_type_match = False
            for alert_wt in alert_work_types:
                if (alert_wt == "in office" and ("onsite" in job_work_type or "office" in job_work_type)) or \
                   (alert_wt == "hybrid" and "hybrid" in job_work_type) or \
                   (alert_wt == "remote" and "remote" in job_work_type):
                    work_type_match = True
                    break
            
            # All criteria must match (but within employment_types and work_types, it's OR)
            if job_title_match and location_match and employment_type_match and work_type_match:
                # Get user name for personalization
                user = await db.users.find_one({"id": alert["user_id"]})
                user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else "Job Seeker"
                
                # Create notification record
                notification = {
                    "id": str(uuid.uuid4()),
                    "alert_id": alert["id"],
                    "user_id": alert["user_id"],
                    "user_email": alert["user_email"],
                    "job_id": job["id"],
                    "job_title": job.get("title"),
                    "company_name": job.get("company_name"),
                    "location": job.get("location"),
                    "work_type": job.get("work_type"),
                    "employment_type": job.get("employment_type"),
                    "status": "pending",
                    "created_at": datetime.utcnow()
                }
                
                # Generate email content
                job_url = f"{base_url}/jobs/{job['id']}"
                email_content = EmailTemplates.job_alert_notification(
                    user_name=user_name,
                    job_title=job.get("title", ""),
                    company_name=job.get("company_name", ""),
                    location=job.get("location", ""),
                    work_type=job.get("work_type", ""),
                    salary_range=job.get("salary_range", ""),
                    job_url=job_url,
                    alert_name=alert.get("job_title", "Job Alert")
                )
                
                # Send email
                result = email_service.send_email(
                    email_type=EmailType.JOB_ALERTS,
                    to_email=alert["user_email"],
                    subject=f"🎯 New Job Match: {job.get('title')} at {job.get('company_name')}",
                    html_content=email_content["html"],
                    plain_content=email_content["plain"]
                )
                
                # Update notification status based on email result
                notification["status"] = "sent" if result["success"] else "failed"
                notification["email_result"] = result
                notification["sent_at"] = datetime.utcnow() if result["success"] else None
                
                await db.job_alert_notifications.insert_one(notification)
                
                # Log the result
                if result["success"]:
                    print(f"Job alert email sent: {alert['job_title']} -> {job['title']} to {alert['user_email']}")
                else:
                    print(f"Job alert email failed: {alert['user_email']} - {result.get('error', 'Unknown error')}")
                    
    except Exception as e:
        print(f"Error checking job alerts: {e}")


@api_router.get("/jobs")
async def get_jobs(
    current_user: User = Depends(get_current_recruiter),
    skip: int = 0,
    limit: int = 100,
    include_archived: bool = False
):
    """Get jobs for current account"""
    
    query = {"account_id": current_user.account_id}
    
    # Filter out inactive/deleted jobs unless include_archived is True
    if not include_archived:
        query["is_active"] = True
    
    jobs = []
    cursor = db.jobs.find(query).sort("posted_date", -1).skip(skip).limit(limit)
    
    async for job in cursor:
        if "_id" in job:
            del job["_id"]
        jobs.append(job)
    
    return jobs


@api_router.get("/jobs/archived")
async def get_archived_jobs(
    current_user: User = Depends(get_current_recruiter),
    skip: int = 0,
    limit: int = 100
):
    """Get archived/deleted jobs for current account"""
    
    jobs = []
    cursor = db.jobs.find({
        "account_id": current_user.account_id,
        "is_active": False
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
# Jobs Dashboard Endpoints
# ============================================

@api_router.get("/jobs/dashboard")
async def get_jobs_dashboard(
    current_user: User = Depends(get_current_recruiter),
    include_expired: bool = False,
    search: str = None,
    sort_by: str = "newest"
):
    """Get jobs dashboard data with stats and activity indicators"""
    
    now = datetime.utcnow()
    
    # Build query based on filters
    base_query = {"account_id": current_user.account_id}
    
    if not include_expired:
        # Only show active jobs that haven't expired
        base_query["is_active"] = True
        base_query["expiry_date"] = {"$gt": now}
    
    if search:
        base_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"location": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Determine sort order
    sort_field = "posted_date"
    sort_direction = -1  # Descending (newest first)
    
    if sort_by == "expiring_soon":
        sort_field = "expiry_date"
        sort_direction = 1  # Ascending (soonest expiring first)
    elif sort_by == "most_applications":
        sort_field = "application_count"  # Will be calculated
        sort_direction = -1
    elif sort_by == "posted_date":
        sort_field = "posted_date"
        sort_direction = -1
    
    # Fetch jobs
    jobs_cursor = db.jobs.find(base_query).sort(sort_field, sort_direction)
    jobs = []
    
    async for job in jobs_cursor:
        if "_id" in job:
            del job["_id"]
        
        job_id = job["id"]
        
        # Get application stats for this job
        application_stats = await db.job_applications.aggregate([
            {"$match": {"job_id": job_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]).to_list(None)
        
        # Process stats
        total_applications = 0
        shortlisted = 0
        interviewed = 0
        offered = 0
        pending = 0
        
        for stat in application_stats:
            count = stat["count"]
            total_applications += count
            if stat["_id"] == "shortlisted":
                shortlisted = count
            elif stat["_id"] == "interviewed":
                interviewed = count
            elif stat["_id"] == "offered":
                offered = count
            elif stat["_id"] == "pending":
                pending = count
        
        # Calculate days until expiry
        expiry_date = job.get("expiry_date", now)
        days_until_expiry = (expiry_date - now).days
        is_expired = days_until_expiry < 0
        is_expiring_soon = 0 <= days_until_expiry <= 7
        
        job["stats"] = {
            "total_applications": total_applications,
            "pending": pending,
            "shortlisted": shortlisted,
            "interviewed": interviewed,
            "offered": offered
        }
        job["days_until_expiry"] = days_until_expiry
        job["is_expired"] = is_expired
        job["is_expiring_soon"] = is_expiring_soon
        
        jobs.append(job)
    
    # Sort by application count if requested (need to do it after fetching)
    if sort_by == "most_applications":
        jobs.sort(key=lambda x: x["stats"]["total_applications"], reverse=True)
    
    # Calculate overall dashboard stats
    total_active_jobs = await db.jobs.count_documents({
        "account_id": current_user.account_id,
        "is_active": True,
        "expiry_date": {"$gt": now}
    })
    
    total_expired_jobs = await db.jobs.count_documents({
        "account_id": current_user.account_id,
        "$or": [
            {"is_active": False},
            {"expiry_date": {"$lte": now}}
        ]
    })
    
    # Get application counts for this month
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_applications_this_month = await db.job_applications.count_documents({
        "account_id": current_user.account_id,
        "applied_date": {"$gte": start_of_month}
    })
    
    # Get total interviews scheduled (applications with interviewed status)
    total_interviews = await db.job_applications.count_documents({
        "account_id": current_user.account_id,
        "status": "interviewed"
    })
    
    return {
        "jobs": jobs,
        "dashboard_stats": {
            "total_active_jobs": total_active_jobs,
            "total_expired_jobs": total_expired_jobs,
            "total_applications_this_month": total_applications_this_month,
            "total_interviews": total_interviews
        }
    }


@api_router.put("/jobs/{job_id}/notes")
async def update_job_notes(
    job_id: str,
    request: Request,
    current_user: User = Depends(get_current_recruiter)
):
    """Update notes for a job"""
    
    body = await request.json()
    notes = body.get("notes", "")
    
    result = await db.jobs.update_one(
        {"id": job_id, "account_id": current_user.account_id},
        {"$set": {
            "recruiter_notes": notes,
            "notes_updated_at": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Notes updated successfully", "notes": notes}


@api_router.put("/jobs/{job_id}/reactivate")
async def reactivate_job(
    job_id: str,
    request: Request,
    current_user: User = Depends(get_current_recruiter)
):
    """Reactivate an expired job with a new expiry date"""
    
    body = await request.json()
    extension_days = body.get("extension_days", 35)  # Default to 35 days
    
    # Find the job
    job = await db.jobs.find_one({
        "id": job_id,
        "account_id": current_user.account_id
    })
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Set new expiry date from today
    new_expiry_date = datetime.utcnow() + timedelta(days=extension_days)
    
    await db.jobs.update_one(
        {"id": job_id},
        {"$set": {
            "is_active": True,
            "expiry_date": new_expiry_date,
            "reactivated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Job reactivated successfully",
        "new_expiry_date": new_expiry_date.isoformat()
    }


@api_router.get("/jobs/{job_id}/applicants")
async def get_job_applicants(
    job_id: str,
    current_user: User = Depends(get_current_recruiter),
    status_filter: str = None
):
    """Get all applicants for a specific job with full profile info"""
    
    # Verify job belongs to account
    job = await db.jobs.find_one({
        "id": job_id,
        "account_id": current_user.account_id
    })
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if "_id" in job:
        del job["_id"]
    
    # Build application query
    app_query = {"job_id": job_id}
    if status_filter and status_filter != "all":
        app_query["status"] = status_filter
    
    # Fetch applications
    applications = []
    cursor = db.job_applications.find(app_query).sort("applied_date", -1)
    
    async for app in cursor:
        if "_id" in app:
            del app["_id"]
        
        # Get full applicant profile
        applicant = await db.users.find_one({"id": app["applicant_id"]})
        if applicant:
            if "_id" in applicant:
                del applicant["_id"]
            # Remove sensitive data
            applicant.pop("password_hash", None)
            app["applicant_profile"] = applicant
        
        applications.append(app)
    
    return {
        "job": job,
        "applications": applications,
        "total_count": len(applications)
    }




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
    
    # Send email notifications (non-blocking)
    try:
        base_url = os.environ.get("FRONTEND_URL", "https://jobrocket.co.za")
        applicant_name = f"{current_user.first_name} {current_user.last_name}"
        job_title = job.get("title", "Position")
        company_name = job.get("company_name", "Company")
        
        # 1. Email to Job Seeker - Application Confirmation
        seeker_email_content = EmailTemplates.application_submitted_confirmation(
            applicant_name=current_user.first_name,
            job_title=job_title,
            company_name=company_name,
            job_url=f"{base_url}/jobs"
        )
        email_service.send_email(
            email_type=EmailType.JOB_ALERTS,
            to_email=current_user.email,
            subject=f"Application Submitted - {job_title} at {company_name}",
            html_content=seeker_email_content["html"],
            plain_content=seeker_email_content["plain"]
        )
        
        # 2. Email to Recruiter - New Application Notification
        account = await db.accounts.find_one({"id": job["account_id"]})
        if account:
            owner = await db.users.find_one({"id": account.get("owner_id")})
            if owner and owner.get("email"):
                recruiter_email_content = EmailTemplates.job_application_received(
                    recruiter_name=owner.get("first_name", "Hiring Manager"),
                    applicant_name=applicant_name,
                    job_title=job_title,
                    application_url=f"{base_url}/jobs-dashboard"
                )
                email_service.send_email(
                    email_type=EmailType.JOB_ALERTS,
                    to_email=owner["email"],
                    subject=f"New Application - {applicant_name} applied for {job_title}",
                    html_content=recruiter_email_content["html"],
                    plain_content=recruiter_email_content["plain"]
                )
    except Exception as e:
        print(f"Email notification error: {str(e)}")
    
    return application_dict


@api_router.get("/jobs/{job_id}/application-status")
async def check_job_application_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Check if current user has already applied to a specific job"""
    
    # Find existing application
    application = await db.job_applications.find_one({
        "job_id": job_id,
        "applicant_id": current_user.id
    })
    
    if application:
        return {
            "has_applied": True,
            "applied_date": application.get("applied_date", application.get("created_at")),
            "status": application.get("status", "pending"),
            "application_id": application.get("id")
        }
    
    return {
        "has_applied": False,
        "applied_date": None,
        "status": None,
        "application_id": None
    }


@api_router.post("/jobs/{job_id}/apply")
async def apply_to_job_by_id(
    job_id: str,
    application_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Apply to a specific job (job seekers only) - Alternative endpoint"""
    
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can apply to jobs"
        )
    
    # Get job
    job = await db.jobs.find_one({"id": job_id, "is_active": True})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already applied
    existing = await db.job_applications.find_one({
        "job_id": job_id,
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
        "job_id": job_id,
        "applicant_id": current_user.id,
        "account_id": job["account_id"],
        "status": ApplicationStatus.PENDING,
        "cover_letter": application_data.get("cover_letter", ""),
        "resume_url": application_data.get("resume_url", ""),
        "additional_info": application_data.get("additional_info", ""),
        "applicant_snapshot": applicant_snapshot,
        "applied_date": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
    }
    
    await db.job_applications.insert_one(application_dict)
    
    if "_id" in application_dict:
        del application_dict["_id"]
    
    # Send email notifications (non-blocking)
    try:
        base_url = os.environ.get("FRONTEND_URL", "https://jobrocket.co.za")
        applicant_name = f"{current_user.first_name} {current_user.last_name}"
        job_title = job.get("title", "Position")
        company_name = job.get("company_name", "Company")
        
        # 1. Email to Job Seeker - Application Confirmation
        seeker_email_content = EmailTemplates.application_submitted_confirmation(
            applicant_name=current_user.first_name,
            job_title=job_title,
            company_name=company_name,
            job_url=f"{base_url}/jobs"
        )
        email_service.send_email(
            email_type=EmailType.JOB_ALERTS,  # Using job alerts email for all notifications
            to_email=current_user.email,
            subject=f"Application Submitted - {job_title} at {company_name}",
            html_content=seeker_email_content["html"],
            plain_content=seeker_email_content["plain"]
        )
        
        # 2. Email to Recruiter - New Application Notification
        # Get recruiter/account owner email
        account = await db.accounts.find_one({"id": job["account_id"]})
        if account:
            owner = await db.users.find_one({"id": account.get("owner_id")})
            if owner and owner.get("email"):
                recruiter_email_content = EmailTemplates.job_application_received(
                    recruiter_name=owner.get("first_name", "Hiring Manager"),
                    applicant_name=applicant_name,
                    job_title=job_title,
                    application_url=f"{base_url}/jobs-dashboard"
                )
                email_service.send_email(
                    email_type=EmailType.JOB_ALERTS,
                    to_email=owner["email"],
                    subject=f"New Application - {applicant_name} applied for {job_title}",
                    html_content=recruiter_email_content["html"],
                    plain_content=recruiter_email_content["plain"]
                )
    except Exception as e:
        # Log error but don't fail the application
        print(f"Email notification error: {str(e)}")
    
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
        job_details = None
        job = await db.jobs.find_one({"id": app["job_id"]})
        if job:
            job_details = {
                "id": job["id"],
                "title": job["title"],
                "company_name": job["company_name"],
                "location": job.get("location", ""),
                "salary_range": job.get("salary_range", ""),
                "employment_type": job.get("employment_type", ""),
            }
        
        # Return in format expected by frontend: { application: {...}, job: {...} }
        applications.append({
            "application": app,
            "job": job_details
        })
    
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
    
    # Get the application first to have applicant info for email
    application = await db.job_applications.find_one({
        "id": application_id, 
        "account_id": current_user.account_id
    })
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    result = await db.job_applications.update_one(
        {"id": application_id, "account_id": current_user.account_id},
        {"$set": {
            "status": status,
            "notes": notes,
            "reviewed_by": current_user.id,
            "last_updated": datetime.utcnow()
        }}
    )
    
    # Send rejection email if status is rejected
    if status == ApplicationStatus.REJECTED:
        try:
            base_url = os.environ.get("FRONTEND_URL", "https://jobrocket.co.za")
            
            # Get applicant details
            applicant_snapshot = application.get("applicant_snapshot", {})
            applicant_email = applicant_snapshot.get("email")
            applicant_first_name = applicant_snapshot.get("first_name", "Candidate")
            
            # If no snapshot email, try to get from user record
            if not applicant_email:
                applicant = await db.users.find_one({"id": application["applicant_id"]})
                if applicant:
                    applicant_email = applicant.get("email")
                    applicant_first_name = applicant.get("first_name", "Candidate")
            
            if applicant_email:
                # Get job details
                job = await db.jobs.find_one({"id": application["job_id"]})
                job_title = job.get("title", "Position") if job else "Position"
                company_name = job.get("company_name", "Company") if job else "Company"
                
                rejection_email_content = EmailTemplates.application_rejected(
                    applicant_name=applicant_first_name,
                    job_title=job_title,
                    company_name=company_name,
                    jobs_url=f"{base_url}/jobs"
                )
                
                email_service.send_email(
                    email_type=EmailType.JOB_ALERTS,
                    to_email=applicant_email,
                    subject=f"Update on your application - {job_title} at {company_name}",
                    html_content=rejection_email_content["html"],
                    plain_content=rejection_email_content["plain"]
                )
        except Exception as e:
            # Log error but don't fail the status update
            print(f"Rejection email error: {str(e)}")
    
    return {"message": "Application status updated"}


@api_router.put("/applications/{application_id}/withdraw")
async def withdraw_application(
    application_id: str,
    current_user: User = Depends(get_current_user)
):
    """Withdraw an application (job seekers only)"""
    
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can withdraw applications"
        )
    
    # Find and verify the application belongs to this user
    application = await db.job_applications.find_one({
        "id": application_id,
        "applicant_id": current_user.id
    })
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if already withdrawn or in final state
    if application.get("status") in ["withdrawn", "rejected", "offered"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw application that is already {application.get('status')}"
        )
    
    # Update status to withdrawn
    result = await db.job_applications.update_one(
        {"id": application_id},
        {"$set": {
            "status": "withdrawn",
            "withdrawn_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }}
    )
    
    return {"message": "Application withdrawn successfully"}


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


@api_router.post("/profile/work-experience")
async def add_work_experience(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Add work experience to user profile"""
    body = await request.json()
    
    work_entry = {
        "id": str(uuid.uuid4()),
        "company": body.get("company", ""),
        "position": body.get("position", ""),
        "location": body.get("location", ""),
        "start_date": body.get("start_date"),
        "end_date": body.get("end_date"),
        "current": body.get("current", False),
        "description": body.get("description", ""),
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$push": {"work_experience": work_entry},
            "$set": {
                "updated_at": datetime.utcnow(),
                "profile_progress.work_history": True
            }
        }
    )
    
    return {"message": "Work experience added successfully", "work_experience": work_entry}


@api_router.delete("/profile/work-experience/{experience_id}")
async def delete_work_experience(
    experience_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete work experience entry from user profile"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"work_experience": {"id": experience_id}}}
    )
    return {"message": "Work experience deleted successfully"}


@api_router.post("/profile/education")
async def add_education(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Add education to user profile"""
    body = await request.json()
    
    education_entry = {
        "id": str(uuid.uuid4()),
        "institution": body.get("institution", ""),
        "degree": body.get("degree", ""),
        "field_of_study": body.get("field_of_study", ""),
        "level": body.get("level", "Bachelors"),
        "start_date": body.get("start_date"),
        "end_date": body.get("end_date"),
        "current": body.get("current", False),
        "grade": body.get("grade", ""),
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$push": {"education": education_entry},
            "$set": {
                "updated_at": datetime.utcnow(),
                "profile_progress.education": True
            }
        }
    )
    
    return {"message": "Education added successfully", "education": education_entry}


@api_router.delete("/profile/education/{education_id}")
async def delete_education(
    education_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete education entry from user profile"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"education": {"id": education_id}}}
    )
    return {"message": "Education deleted successfully"}


@api_router.post("/profile/achievement")
async def add_achievement(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Add achievement to user profile"""
    body = await request.json()
    
    achievement_entry = {
        "id": str(uuid.uuid4()),
        "title": body.get("title", ""),
        "description": body.get("description", ""),
        "date_achieved": body.get("date_achieved"),
        "issuer": body.get("issuer", ""),
        "credential_url": body.get("credential_url", ""),
        "created_at": datetime.utcnow().isoformat()
    }
    
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$push": {"achievements": achievement_entry},
            "$set": {
                "updated_at": datetime.utcnow(),
                "profile_progress.achievements": True
            }
        }
    )
    
    return {"message": "Achievement added successfully", "achievement": achievement_entry}


@api_router.delete("/profile/achievement/{achievement_id}")
async def delete_achievement(
    achievement_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete achievement entry from user profile"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"achievements": {"id": achievement_id}}}
    )
    return {"message": "Achievement deleted successfully"}


@api_router.post("/profile/email-alerts")
async def setup_email_alerts(
    current_user: User = Depends(get_current_user)
):
    """Enable email alerts for job seeker"""
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$set": {
                "email_alerts_enabled": True,
                "updated_at": datetime.utcnow(),
                "profile_progress.email_alerts": True
            }
        }
    )
    return {"message": "Email alerts enabled successfully"}


@api_router.put("/profile/email-alerts")
async def update_email_alerts(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Update email alert preferences"""
    body = await request.json()
    
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$set": {
                "email_alerts_enabled": body.get("enabled", True),
                "email_alert_preferences": body.get("preferences", {}),
                "updated_at": datetime.utcnow(),
                "profile_progress.email_alerts": True
            }
        }
    )
    return {"message": "Email alert preferences updated successfully"}


# ============================================
# Job Alerts Endpoints
# ============================================

@api_router.get("/profile/job-alerts")
async def get_job_alerts(current_user: User = Depends(get_current_user)):
    """Get all job alerts for current user"""
    alerts = []
    cursor = db.job_alerts.find({"user_id": current_user.id}).sort("created_at", -1)
    async for alert in cursor:
        if "_id" in alert:
            del alert["_id"]
        alerts.append(alert)
    return alerts


@api_router.post("/profile/job-alerts")
async def create_job_alert(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Create a new job alert"""
    body = await request.json()
    
    alert = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "user_email": current_user.email,
        "job_title": body.get("job_title", ""),
        "location": body.get("location", ""),
        "employment_types": body.get("employment_types", []),
        "work_types": body.get("work_types", []),
        "salary_range": body.get("salary_range", ""),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.job_alerts.insert_one(alert)
    
    # Update profile progress
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"profile_progress.email_alerts": True, "updated_at": datetime.utcnow()}}
    )
    
    if "_id" in alert:
        del alert["_id"]
    
    return {"message": "Job alert created successfully", "alert": alert}


@api_router.delete("/profile/job-alerts/{alert_id}")
async def delete_job_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a job alert"""
    result = await db.job_alerts.delete_one({
        "id": alert_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job alert not found")
    
    return {"message": "Job alert deleted successfully"}


# ============================================
# Onboarding Endpoints
# ============================================

ONBOARDING_STEP_PROGRESS = {0: 0, 1: 15, 2: 35, 3: 55, 4: 75, 5: 90, 6: 100}
RECRUITER_STEP_PROGRESS = {0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 90, 6: 100}
ONBOARDING_BADGES = {2: "profile_started", 5: "almost_there", 6: "profile_complete"}
RECRUITER_BADGES = {1: "company_live", 3: "sourcing_ready", 6: "ready_to_hire"}

@api_router.get("/onboarding/status")
async def get_onboarding_status(current_user: User = Depends(get_current_user)):
    """Get current onboarding status"""
    return {
        "onboarding_completed": current_user.onboarding_completed,
        "onboarding_step": current_user.onboarding_step,
        "onboarding_progress": current_user.onboarding_progress,
        "badges": getattr(current_user, 'badges', []),
    }

@api_router.put("/onboarding/step/{step}")
async def save_onboarding_step(
    step: int,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Save data for a specific onboarding step"""
    if step < 0 or step > 6:
        raise HTTPException(status_code=400, detail="Invalid step number")
    
    body = await request.json()
    is_recruiter = current_user.role == UserRole.RECRUITER
    step_progress = RECRUITER_STEP_PROGRESS if is_recruiter else ONBOARDING_STEP_PROGRESS
    step_badges = RECRUITER_BADGES if is_recruiter else ONBOARDING_BADGES
    progress = step_progress.get(step, 0)
    
    update_data = {
        "onboarding_step": max(step, current_user.onboarding_step),
        "onboarding_progress": max(progress, current_user.onboarding_progress),
        "updated_at": datetime.utcnow(),
    }
    
    # Add badge if applicable
    current_badges = list(getattr(current_user, 'badges', []))
    badge = step_badges.get(step)
    if badge and badge not in current_badges:
        current_badges.append(badge)
        update_data["badges"] = current_badges
    
    # Account update data (for recruiter company fields)
    account_update = {}
    
    if is_recruiter:
        # Recruiter step field mappings
        if step == 1:
            # Company basics - update account
            for field in ["company_size", "company_industry", "company_location"]:
                if field in body:
                    account_update[field] = body[field]
            if "company_name" in body:
                account_update["name"] = body["company_name"]
        elif step == 2:
            # Hiring preferences - store on user
            for field in ["hiring_roles", "hiring_locations", "hiring_employment_types", "hiring_volume"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 3:
            # Candidate access setup
            for field in ["sourcing_methods", "alerts_enabled", "match_preferences"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 4:
            # Post first job or browse - just record the action taken
            if "action_taken" in body:
                update_data["onboarding_action_step4"] = body["action_taken"]
        elif step == 5:
            # Distribution & visibility
            for field in ["distribution_email", "distribution_whatsapp", "distribution_social"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 6:
            update_data["onboarding_completed"] = True
            update_data["onboarding_progress"] = 100
    else:
        # Job seeker step field mappings
        if step == 1:
            if "location" in body:
                update_data["location"] = body["location"]
        elif step == 2:
            for field in ["desired_job_title", "years_of_experience", "industry_preference", "employment_type_preference"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 3:
            for field in ["skills", "seniority_level", "key_strengths"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 4:
            for field in ["resume_url", "linkedin_url", "desired_salary_range"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 5:
            for field in ["work_experience", "availability", "notice_period"]:
                if field in body:
                    update_data[field] = body[field]
        elif step == 6:
            for field in ["profile_picture_url", "about_me", "open_to_opportunities", "additional_documents"]:
                if field in body:
                    update_data[field] = body[field]
            update_data["onboarding_completed"] = True
            update_data["onboarding_progress"] = 100
    
    await db.users.update_one({"id": current_user.id}, {"$set": update_data})
    
    # Update account if needed (recruiter company info)
    if account_update and current_user.account_id:
        account_update["updated_at"] = datetime.utcnow()
        await db.accounts.update_one({"id": current_user.account_id}, {"$set": account_update})
    
    return {
        "success": True,
        "step": step,
        "progress": update_data.get("onboarding_progress", progress),
        "badges": update_data.get("badges", current_badges),
    }

@api_router.post("/onboarding/skip")
async def skip_onboarding(current_user: User = Depends(get_current_user)):
    """Mark onboarding as skipped"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"onboarding_completed": True, "updated_at": datetime.utcnow()}}
    )
    return {"success": True}

@api_router.post("/uploads/cv")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a CV file"""
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are allowed")
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    cv_dir = Path(UPLOAD_PATH) / "cvs"
    cv_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix
    filename = f"{current_user.id}_cv_{uuid.uuid4().hex[:8]}{ext}"
    filepath = cv_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    file_url = f"/api/uploads/cvs/{filename}"
    await db.users.update_one({"id": current_user.id}, {"$set": {"resume_url": file_url, "updated_at": datetime.utcnow()}})
    
    return {"url": file_url, "filename": file.filename}

@api_router.post("/uploads/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a profile picture"""
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP images are allowed")
    
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    pic_dir = Path(UPLOAD_PATH) / "profile_pictures"
    pic_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix
    filename = f"{current_user.id}_avatar_{uuid.uuid4().hex[:8]}{ext}"
    filepath = pic_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    file_url = f"/api/uploads/profile_pictures/{filename}"
    await db.users.update_one({"id": current_user.id}, {"$set": {"profile_picture_url": file_url, "updated_at": datetime.utcnow()}})
    
    return {"url": file_url, "filename": file.filename}

@api_router.post("/uploads/document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload an additional document (certificate, award, etc.)"""
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    doc_dir = Path(UPLOAD_PATH) / "documents"
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix
    filename = f"{current_user.id}_doc_{uuid.uuid4().hex[:8]}{ext}"
    filepath = doc_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    file_url = f"/api/uploads/documents/{filename}"
    return {"url": file_url, "filename": file.filename}


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
    from services.payfast_subscription_service import create_payfast_subscription_service
    
    form_data = await request.form()
    data = dict(form_data)
    
    payment_id = data.get("m_payment_id")
    payment_status = data.get("payment_status")
    
    logger.info(f"PayFast webhook received: payment_id={payment_id}, status={payment_status}")
    
    if not payment_id:
        return {"status": "error", "message": "Missing payment ID"}
    
    payment = await db.payments.find_one({"id": payment_id})
    if not payment:
        return {"status": "error", "message": "Payment not found"}
    
    # Use the PayFast subscription service for comprehensive handling
    payfast_service = create_payfast_subscription_service(db)
    result = await payfast_service.process_itn(data)
    
    if result.get("success"):
        logger.info(f"Payment {payment_id} processed successfully: {payment_status}")
    else:
        logger.error(f"Payment {payment_id} processing failed: {result.get('error')}")
    
    return {"status": "ok"}


@api_router.get("/subscription/status")
async def get_subscription_status(current_user: User = Depends(get_current_user)):
    """Check current subscription status for the user's account"""
    from services.payfast_subscription_service import create_payfast_subscription_service
    
    if not current_user.account_id:
        return {"status": "no_account", "needs_payment": True}
    
    payfast_service = create_payfast_subscription_service(db)
    status = await payfast_service.check_subscription_status(current_user.account_id)
    
    return status


@api_router.post("/subscription/reactivate")
async def reactivate_subscription(
    current_user: User = Depends(get_current_recruiter)
):
    """Initiate payment to reactivate a suspended subscription"""
    from services.payfast_subscription_service import create_payfast_subscription_service
    
    account = await db.accounts.find_one({"id": current_user.account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_id = account.get("tier_id", "starter")
    
    payfast_service = create_payfast_subscription_service(db)
    
    result = await payfast_service.initiate_subscription(
        account_id=current_user.account_id,
        tier_id=tier_id,
        user_email=current_user.email,
        user_name=f"{current_user.first_name} {current_user.last_name}",
        return_url=f"{BASE_URL}/billing?payment=success",
        cancel_url=f"{BASE_URL}/billing?payment=cancelled",
        notify_url=f"{BASE_URL}/api/payments/webhook"
    )
    
    return result


@api_router.post("/payments/extra-seat")
async def initiate_extra_seat_payment(
    seat_data: dict,
    current_user: User = Depends(get_current_recruiter)
):
    """Initiate payment for an extra user seat"""
    from services.payfast_subscription_service import create_payfast_subscription_service
    from models.tiers import TIER_CONFIG
    
    # Get extra user price (R899/month)
    extra_user_price = 89900  # In cents
    
    seat_id = seat_data.get("seat_id")
    user_id = seat_data.get("user_id")
    
    payfast_service = create_payfast_subscription_service(db)
    
    result = await payfast_service.initiate_addon_payment(
        account_id=current_user.account_id,
        addon_type="extra_seat",
        amount=extra_user_price,
        description="Extra User Seat - Monthly",
        user_email=current_user.email,
        user_name=f"{current_user.first_name} {current_user.last_name}",
        return_url=f"{BASE_URL}/billing?payment=success&type=seat",
        cancel_url=f"{BASE_URL}/billing?payment=cancelled",
        notify_url=f"{BASE_URL}/api/payments/webhook",
        extra_data={"seat_id": seat_id, "user_id": user_id}
    )
    
    return result


@api_router.get("/seat/status")
async def get_seat_status(current_user: User = Depends(get_current_user)):
    """Check if current user's seat is active (for extra seat users)"""
    from services.payfast_subscription_service import create_payfast_subscription_service
    
    payfast_service = create_payfast_subscription_service(db)
    status = await payfast_service.check_seat_status(current_user.id)
    
    return status


# ============================================
# Payment History & Statements
# ============================================

from services.statement_service import create_statement_service
from fastapi.responses import HTMLResponse

@api_router.get("/billing/history")
async def get_billing_history(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_recruiter)
):
    """Get payment history for the current user's account"""
    statement_service = create_statement_service(db)
    
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    history = await statement_service.get_payment_history(
        account_id=current_user.account_id,
        start_date=start_dt,
        end_date=end_dt,
        limit=limit,
        skip=skip
    )
    
    return history


@api_router.get("/billing/statement")
async def generate_statement(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    format: str = Query("html", description="Output format: html or json"),
    current_user: User = Depends(get_current_recruiter)
):
    """Generate a billing statement for a date range"""
    statement_service = create_statement_service(db)
    
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Ensure end date is end of day
    end_dt = end_dt.replace(hour=23, minute=59, second=59)
    
    statement_data = await statement_service.generate_statement_data(
        account_id=current_user.account_id,
        start_date=start_dt,
        end_date=end_dt
    )
    
    if format == "html":
        html = statement_service.generate_html_statement(statement_data)
        return HTMLResponse(content=html, media_type="text/html")
    
    return statement_data


@api_router.get("/billing/summary")
async def get_billing_summary(
    months: int = Query(12, ge=1, le=24),
    current_user: User = Depends(get_current_recruiter)
):
    """Get billing summary for the last N months"""
    statement_service = create_statement_service(db)
    
    summary = await statement_service.get_billing_summary_for_period(
        account_id=current_user.account_id,
        months=months
    )
    
    return summary


@api_router.post("/billing/extra-seats")
async def purchase_extra_seats(
    quantity: int = Query(1, ge=1, le=100),
    current_user: User = Depends(get_current_recruiter)
):
    """Purchase extra user seats with pro-rata calculation"""
    from services.payfast_subscription_service import create_payfast_subscription_service
    
    payfast_service = create_payfast_subscription_service(db)
    
    result = await payfast_service.initiate_extra_seat_payment(
        account_id=current_user.account_id,
        quantity=quantity,
        user_email=current_user.email,
        user_name=f"{current_user.first_name} {current_user.last_name}",
        return_url=f"{BASE_URL}/billing?payment=success&type=seats",
        cancel_url=f"{BASE_URL}/billing?payment=cancelled",
        notify_url=f"{BASE_URL}/api/payments/webhook"
    )
    
    return result


@api_router.get("/billing/account-info")
async def get_billing_account_info(current_user: User = Depends(get_current_recruiter)):
    """Get billing-specific account information"""
    account = await db.accounts.find_one({"id": current_user.account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_config = get_tier_config(TierId(account.get("tier_id", "starter")))
    
    return {
        "account_id": account.get("id"),
        "company_name": account.get("company_name"),
        "tier_id": account.get("tier_id"),
        "tier_name": tier_config["name"],
        "subscription_status": account.get("subscription_status"),
        "billing_day": account.get("billing_day"),
        "next_billing_date": account.get("next_billing_date"),
        "subscription_start_date": account.get("subscription_start_date"),
        "subscription_end_date": account.get("subscription_end_date"),
        "grace_period_start": account.get("grace_period_start"),
        "extra_users_count": account.get("extra_users_count", 0),
        "monthly_amount": tier_config["price_monthly"] / 100,
        "currency": "ZAR"
    }


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


@api_router.get("/admin/analytics")
async def get_admin_analytics(current_user: User = Depends(verify_admin_user)):
    """Get detailed analytics data for admin analytics dashboard"""
    now = datetime.utcnow()
    
    # --- Time-series data: last 6 months ---
    months_data = []
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            month_end = now
        
        label = month_start.strftime("%b %Y")
        
        new_accounts = await db.accounts.count_documents({"created_at": {"$gte": month_start, "$lt": month_end}})
        new_users = await db.users.count_documents({"created_at": {"$gte": month_start, "$lt": month_end}})
        new_jobs = await db.jobs.count_documents({"posted_date": {"$gte": month_start, "$lt": month_end}})
        new_apps = await db.job_applications.count_documents({"applied_date": {"$gte": month_start, "$lt": month_end}})
        
        months_data.append({
            "month": label,
            "accounts": new_accounts,
            "users": new_users,
            "jobs": new_jobs,
            "applications": new_apps,
        })
    
    # --- Job analytics ---
    # By industry
    job_industry_pipeline = [
        {"$group": {"_id": "$industry", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    industry_data = await db.jobs.aggregate(job_industry_pipeline).to_list(10)
    
    # By location
    job_location_pipeline = [
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    location_data = await db.jobs.aggregate(job_location_pipeline).to_list(10)
    
    # By work type
    work_type_pipeline = [
        {"$group": {"_id": "$work_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    work_type_data = await db.jobs.aggregate(work_type_pipeline).to_list(10)
    
    # By job type
    job_type_pipeline = [
        {"$group": {"_id": "$job_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    job_type_data = await db.jobs.aggregate(job_type_pipeline).to_list(10)
    
    # --- Application analytics ---
    app_status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    app_status_data = await db.job_applications.aggregate(app_status_pipeline).to_list(20)
    
    # --- User analytics ---
    # Onboarding completion
    onboarded_seekers = await db.users.count_documents({"role": "job_seeker", "onboarding_completed": True})
    total_seekers = await db.users.count_documents({"role": "job_seeker"})
    onboarded_recruiters = await db.users.count_documents({"role": "recruiter", "onboarding_completed": True})
    total_recruiters = await db.users.count_documents({"role": "recruiter"})
    
    # --- Account detail table ---
    accounts_detail = []
    async for acc in db.accounts.find({}).sort("created_at", -1):
        if "_id" in acc:
            del acc["_id"]
        owner = await db.users.find_one({"id": acc.get("owner_user_id", "")}, {"_id": 0, "email": 1, "first_name": 1, "last_name": 1})
        job_count = await db.jobs.count_documents({"account_id": acc["id"]})
        app_count = await db.job_applications.count_documents({"account_id": acc["id"]})
        
        tier_prices = {"starter": 6899, "growth": 10499, "pro": 19999, "enterprise": 39999}
        extra = acc.get("extra_users_count", 0)
        mrr = tier_prices.get(acc.get("tier_id", "starter"), 0) + (extra * 899)
        
        accounts_detail.append({
            "id": acc["id"],
            "name": acc.get("name", ""),
            "tier_id": acc.get("tier_id", "starter"),
            "subscription_status": acc.get("subscription_status", "pending"),
            "owner_name": f"{owner.get('first_name','')} {owner.get('last_name','')}" if owner else "N/A",
            "owner_email": owner.get("email", "N/A") if owner else "N/A",
            "user_count": acc.get("current_user_count", 1),
            "extra_users": extra,
            "job_count": job_count,
            "application_count": app_count,
            "mrr": mrr,
            "created_at": acc.get("created_at", now).isoformat() if isinstance(acc.get("created_at"), datetime) else str(acc.get("created_at", "")),
        })
    
    # --- Top jobs by applications ---
    top_jobs_pipeline = [
        {"$group": {"_id": "$job_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_jobs_raw = await db.job_applications.aggregate(top_jobs_pipeline).to_list(10)
    top_jobs = []
    for tj in top_jobs_raw:
        job = await db.jobs.find_one({"id": tj["_id"]}, {"_id": 0, "title": 1, "company_name": 1, "location": 1})
        if job:
            top_jobs.append({**job, "application_count": tj["count"]})
    
    return {
        "monthly_trends": months_data,
        "jobs_by_industry": [{"name": d["_id"] or "Other", "count": d["count"]} for d in industry_data],
        "jobs_by_location": [{"name": d["_id"] or "Other", "count": d["count"]} for d in location_data],
        "jobs_by_work_type": [{"name": d["_id"] or "Other", "count": d["count"]} for d in work_type_data],
        "jobs_by_job_type": [{"name": d["_id"] or "Other", "count": d["count"]} for d in job_type_data],
        "applications_by_status": [{"name": d["_id"] or "Other", "count": d["count"]} for d in app_status_data],
        "onboarding": {
            "job_seekers": {"completed": onboarded_seekers, "total": total_seekers},
            "recruiters": {"completed": onboarded_recruiters, "total": total_recruiters},
        },
        "accounts_detail": accounts_detail,
        "top_jobs": top_jobs,
    }


# ============================================
# Admin Account Management Endpoints
# ============================================

@api_router.get("/admin/accounts/{account_id}")
async def admin_get_account(account_id: str, current_user: User = Depends(verify_admin_user)):
    """Get detailed account info for admin management"""
    account = await db.accounts.find_one({"id": account_id}, {"_id": 0})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_config = get_tier_config(TierId(account.get("tier_id", "starter")))
    owner = await db.users.find_one({"id": account.get("owner_user_id", "")}, {"_id": 0, "email": 1, "first_name": 1, "last_name": 1})
    job_count = await db.jobs.count_documents({"account_id": account_id})
    
    # Get active addons
    addons = []
    async for addon in db.account_addons.find({"account_id": account_id, "is_active": True}, {"_id": 0}):
        addons.append(addon)
    
    # Get audit log
    audit_log = []
    async for log in db.admin_audit_log.find({"account_id": account_id}, {"_id": 0}).sort("created_at", -1).limit(50):
        if isinstance(log.get("created_at"), datetime):
            log["created_at"] = log["created_at"].isoformat()
        audit_log.append(log)
    
    return {
        **account,
        "tier_name": tier_config["name"],
        "tier_price": tier_config["price_monthly"],
        "owner": owner,
        "job_count": job_count,
        "active_addons": addons,
        "credit_balance": account.get("credit_balance", 0),
        "audit_log": audit_log,
    }

async def _admin_audit(account_id: str, admin_id: str, action: str, details: dict):
    """Log an admin action to the audit trail"""
    await db.admin_audit_log.insert_one({
        "id": str(uuid.uuid4()),
        "account_id": account_id,
        "admin_user_id": admin_id,
        "action": action,
        "details": details,
        "created_at": datetime.utcnow(),
    })

@api_router.put("/admin/accounts/{account_id}/tier")
async def admin_change_tier(
    account_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_user)
):
    """Change an account's subscription tier"""
    body = await request.json()
    new_tier_id = body.get("tier_id")
    reason = body.get("reason", "Admin override")
    
    if new_tier_id not in ["starter", "growth", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid tier ID")
    
    account = await db.accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    old_tier = account.get("tier_id", "starter")
    new_tier_config = get_tier_config(TierId(new_tier_id))
    
    await db.accounts.update_one({"id": account_id}, {"$set": {
        "tier_id": new_tier_id,
        "subscription_status": "active",
        "subscription_start_date": datetime.utcnow(),
        "subscription_end_date": datetime.utcnow() + timedelta(days=30),
        "updated_at": datetime.utcnow(),
    }})
    
    await _admin_audit(account_id, current_user.id, "tier_change", {
        "old_tier": old_tier, "new_tier": new_tier_id, "reason": reason
    })
    
    return {"success": True, "message": f"Tier changed from {old_tier} to {new_tier_id}", "tier_id": new_tier_id}

@api_router.post("/admin/accounts/{account_id}/addon")
async def admin_grant_addon(
    account_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_user)
):
    """Grant an add-on feature to an account for free"""
    body = await request.json()
    addon_id = body.get("addon_id")
    reason = body.get("reason", "Admin grant")
    
    account = await db.accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    addon_config = None
    for aid, cfg in ADDON_CONFIG.items():
        if aid.value == addon_id:
            addon_config = cfg
            break
    
    if not addon_config:
        raise HTTPException(status_code=400, detail="Invalid add-on ID")
    
    # Check if already active
    existing = await db.account_addons.find_one({"account_id": account_id, "addon_id": addon_id, "is_active": True})
    if existing:
        raise HTTPException(status_code=400, detail="Add-on already active on this account")
    
    addon_doc = {
        "id": str(uuid.uuid4()),
        "account_id": account_id,
        "addon_id": addon_id,
        "feature_id": addon_config["feature_id"].value,
        "purchased_date": datetime.utcnow(),
        "expires_date": datetime.utcnow() + timedelta(days=365),
        "is_active": True,
        "price_paid": 0,
        "payment_id": None,
        "admin_granted": True,
    }
    await db.account_addons.insert_one(addon_doc)
    
    await _admin_audit(account_id, current_user.id, "addon_grant", {
        "addon_id": addon_id, "addon_name": addon_config["name"], "reason": reason
    })
    
    return {"success": True, "message": f"Add-on '{addon_config['name']}' granted", "addon_id": addon_id}

@api_router.delete("/admin/accounts/{account_id}/addon/{addon_purchase_id}")
async def admin_revoke_addon(
    account_id: str,
    addon_purchase_id: str,
    current_user: User = Depends(verify_admin_user)
):
    """Revoke an add-on from an account"""
    result = await db.account_addons.update_one(
        {"id": addon_purchase_id, "account_id": account_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Add-on not found")
    
    await _admin_audit(account_id, current_user.id, "addon_revoke", {"addon_purchase_id": addon_purchase_id})
    return {"success": True, "message": "Add-on revoked"}

@api_router.post("/admin/accounts/{account_id}/seats")
async def admin_add_seats(
    account_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_user)
):
    """Add extra user seats to an account for free"""
    body = await request.json()
    quantity = body.get("quantity", 1)
    reason = body.get("reason", "Admin grant")
    
    if quantity < 1 or quantity > 50:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 50")
    
    account = await db.accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    current_extra = account.get("extra_users_count", 0)
    await db.accounts.update_one({"id": account_id}, {"$set": {
        "extra_users_count": current_extra + quantity,
        "updated_at": datetime.utcnow(),
    }})
    
    await _admin_audit(account_id, current_user.id, "seats_added", {
        "quantity": quantity, "previous_extra": current_extra, "reason": reason
    })
    
    return {"success": True, "message": f"{quantity} seat(s) added", "total_extra_seats": current_extra + quantity}

@api_router.post("/admin/accounts/{account_id}/credits")
async def admin_add_credits(
    account_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_user)
):
    """Add credit balance to an account"""
    body = await request.json()
    amount = body.get("amount", 0)
    reason = body.get("reason", "Admin credit")
    
    if amount <= 0 or amount > 1000000:
        raise HTTPException(status_code=400, detail="Amount must be between R1 and R1,000,000")
    
    account = await db.accounts.find_one({"id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    current_balance = account.get("credit_balance", 0)
    new_balance = current_balance + amount
    
    await db.accounts.update_one({"id": account_id}, {"$set": {
        "credit_balance": new_balance,
        "updated_at": datetime.utcnow(),
    }})
    
    await _admin_audit(account_id, current_user.id, "credit_added", {
        "amount": amount, "previous_balance": current_balance, "new_balance": new_balance, "reason": reason
    })
    
    return {"success": True, "message": f"R{amount:,.0f} credited", "credit_balance": new_balance}

@api_router.get("/admin/accounts/{account_id}/audit-log")
async def admin_get_audit_log(account_id: str, current_user: User = Depends(verify_admin_user)):
    """Get audit log for an account"""
    logs = []
    async for log in db.admin_audit_log.find({"account_id": account_id}, {"_id": 0}).sort("created_at", -1).limit(100):
        if isinstance(log.get("created_at"), datetime):
            log["created_at"] = log["created_at"].isoformat()
        logs.append(log)
    return {"logs": logs}


@api_router.post("/admin/test-email")
async def admin_test_email(
    request: Request,
    current_user: User = Depends(verify_admin_user)
):
    """Test email sending functionality (Admin only)"""
    body = await request.json()
    test_email = body.get("email")
    email_type = body.get("type", "job_alerts")
    
    if not test_email:
        raise HTTPException(status_code=400, detail="Email address required")
    
    # Send a test email
    email_content = EmailTemplates.job_alert_notification(
        user_name="Test User",
        job_title="Senior Software Developer",
        company_name="Test Company",
        location="Cape Town",
        work_type="Remote",
        salary_range="R60,000 - R90,000",
        job_url="https://jobrocket.co.za/jobs/test",
        alert_name="Software Developer"
    )
    
    result = email_service.send_email(
        email_type=EmailType.JOB_ALERTS,
        to_email=test_email,
        subject="🧪 Job Rocket Email Test - Job Alert",
        html_content=email_content["html"],
        plain_content=email_content["plain"]
    )
    
    return {
        "success": result["success"],
        "message": result.get("message") or result.get("error"),
        "sent_to": test_email
    }


@api_router.get("/admin/email-notifications")
async def get_email_notifications(
    current_user: User = Depends(verify_admin_user),
    status: Optional[str] = None,
    limit: int = 50
):
    """Get job alert email notifications (Admin only)"""
    query = {}
    if status:
        query["status"] = status
    
    notifications = []
    async for notif in db.job_alert_notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit):
        if isinstance(notif.get("created_at"), datetime):
            notif["created_at"] = notif["created_at"].isoformat()
        if isinstance(notif.get("sent_at"), datetime):
            notif["sent_at"] = notif["sent_at"].isoformat()
        notifications.append(notif)
    
    return {"notifications": notifications, "total": len(notifications)}


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

# Contact reveal limits by tier (monthly)
CONTACT_REVEAL_LIMITS = {
    "starter": 0,
    "growth": 1500,
    "pro": 5000,
    "enterprise": 10000
}

# High usage threshold for admin notification
CV_SEARCH_HIGH_USAGE_THRESHOLD = 20000


@api_router.get("/cv-search/access")
async def check_cv_search_access(current_user: User = Depends(get_current_recruiter)):
    """Check if user has CV search access and their usage limits"""
    account = await db.accounts.find_one({"id": current_user.account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_id = account.get("tier_id", "starter")
    tier_config = get_tier_config(TierId(tier_id))
    
    # Get current month usage
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get contact reveals this month
    reveals_count = await db.contact_reveals.count_documents({
        "account_id": current_user.account_id,
        "revealed_at": {"$gte": month_start}
    })
    
    # Get searches this month
    searches_count = await db.cv_search_usage.count_documents({
        "account_id": current_user.account_id,
        "searched_at": {"$gte": month_start}
    })
    
    has_access = tier_config.get("cv_search_enabled", False)
    contact_limit = tier_config.get("contact_reveals_limit", 0)
    
    return {
        "has_access": has_access,
        "tier": tier_id,
        "tier_name": tier_config.get("name"),
        "contact_reveals_limit": contact_limit,
        "contact_reveals_used": reveals_count,
        "contact_reveals_remaining": max(0, contact_limit - reveals_count),
        "searches_this_month": searches_count,
        "upgrade_required": not has_access
    }


@api_router.get("/cv-search")
async def search_candidates(
    current_user: User = Depends(get_current_recruiter),
    q: Optional[str] = None,
    skills: Optional[str] = None,
    location: Optional[str] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    industry: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    availability: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Search the CV database / talent pool"""
    
    # Get account and tier info
    account = await db.accounts.find_one({"id": current_user.account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_id = account.get("tier_id", "starter")
    tier_config = get_tier_config(TierId(tier_id))
    
    # Check if tier has CV search access
    if not tier_config.get("cv_search_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "upgrade_required",
                "message": "CV Search is available on Growth plan and above. Upgrade to access the talent pool.",
                "upgrade_to": "growth"
            }
        )
    
    # Build query
    query = {"role": "job_seeker"}
    
    if q:
        query["$or"] = [
            {"first_name": {"$regex": q, "$options": "i"}},
            {"last_name": {"$regex": q, "$options": "i"}},
            {"about_me": {"$regex": q, "$options": "i"}},
            {"headline": {"$regex": q, "$options": "i"}},
            {"skills": {"$elemMatch": {"$regex": q, "$options": "i"}}}
        ]
    
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",")]
        query["skills"] = {"$elemMatch": {"$regex": "|".join(skill_list), "$options": "i"}}
    
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    if industry:
        industry_query = [
            {"industry": {"$regex": industry, "$options": "i"}},
            {"preferred_industry": {"$regex": industry, "$options": "i"}}
        ]
        if "$or" in query:
            query["$and"] = [{"$or": query.pop("$or")}, {"$or": industry_query}]
        else:
            query["$or"] = industry_query
    
    if experience_min is not None:
        query["years_experience"] = query.get("years_experience", {})
        query["years_experience"]["$gte"] = experience_min
    
    if experience_max is not None:
        query["years_experience"] = query.get("years_experience", {})
        query["years_experience"]["$lte"] = experience_max
    
    if salary_min is not None:
        query["expected_salary"] = query.get("expected_salary", {})
        query["expected_salary"]["$gte"] = salary_min
    
    if salary_max is not None:
        query["expected_salary"] = query.get("expected_salary", {})
        query["expected_salary"]["$lte"] = salary_max
    
    if availability:
        query["availability_status"] = availability
    
    # Execute search
    candidates = []
    cursor = db.users.find(query).skip(skip).limit(limit)
    
    # Get already revealed contacts for this account
    revealed_ids = set()
    reveals_cursor = db.contact_reveals.find({"account_id": current_user.account_id})
    async for reveal in reveals_cursor:
        revealed_ids.add(reveal.get("candidate_id"))
    
    async for user in cursor:
        if "_id" in user:
            del user["_id"]
        if "password_hash" in user:
            del user["password_hash"]
        
        # Mask contact info if not revealed
        candidate_id = user.get("id")
        is_revealed = candidate_id in revealed_ids
        
        if not is_revealed:
            # Mask email and phone
            if user.get("email"):
                email_parts = user["email"].split("@")
                if len(email_parts) == 2:
                    masked = email_parts[0][:2] + "***@" + email_parts[1]
                    user["email_masked"] = masked
                user["email"] = None
            if user.get("phone"):
                user["phone_masked"] = user["phone"][:3] + "****" + user["phone"][-2:] if len(user.get("phone", "")) > 5 else "****"
                user["phone"] = None
        
        user["contact_revealed"] = is_revealed
        candidates.append(user)
    
    total = await db.users.count_documents(query)
    
    # Track this search
    await db.cv_search_usage.insert_one({
        "account_id": current_user.account_id,
        "user_id": current_user.id,
        "searched_at": datetime.utcnow(),
        "query_params": {
            "q": q,
            "skills": skills,
            "location": location,
            "experience_min": experience_min,
            "experience_max": experience_max,
            "industry": industry,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "availability": availability
        },
        "results_count": total
    })
    
    # Check for high usage notification
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    searches_this_month = await db.cv_search_usage.count_documents({
        "account_id": current_user.account_id,
        "searched_at": {"$gte": month_start}
    })
    
    if searches_this_month == CV_SEARCH_HIGH_USAGE_THRESHOLD:
        # Create admin notification for high usage
        await db.admin_notifications.insert_one({
            "id": str(uuid.uuid4()),
            "type": "high_cv_search_usage",
            "account_id": current_user.account_id,
            "company_name": account.get("company_name"),
            "tier": tier_id,
            "searches_count": searches_this_month,
            "threshold": CV_SEARCH_HIGH_USAGE_THRESHOLD,
            "message": f"Account {account.get('company_name')} has exceeded {CV_SEARCH_HIGH_USAGE_THRESHOLD:,} CV searches this month",
            "created_at": now,
            "is_read": False
        })
    
    return {
        "candidates": candidates,
        "total": total,
        "skip": skip,
        "limit": limit,
        "searches_this_month": searches_this_month
    }


@api_router.post("/cv-search/reveal/{candidate_id}")
async def reveal_candidate_contact(
    candidate_id: str,
    current_user: User = Depends(get_current_recruiter)
):
    """Reveal a candidate's contact information (counts against monthly limit)"""
    
    # Get account and tier info
    account = await db.accounts.find_one({"id": current_user.account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tier_id = account.get("tier_id", "starter")
    tier_config = get_tier_config(TierId(tier_id))
    
    # Check if tier has CV search access
    if not tier_config.get("cv_search_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CV Search is not available on your plan"
        )
    
    # Check if already revealed
    existing_reveal = await db.contact_reveals.find_one({
        "account_id": current_user.account_id,
        "candidate_id": candidate_id
    })
    
    if existing_reveal:
        # Already revealed - return the candidate info without counting
        candidate = await db.users.find_one({"id": candidate_id})
        if candidate:
            if "_id" in candidate:
                del candidate["_id"]
            if "password_hash" in candidate:
                del candidate["password_hash"]
            return {
                "success": True,
                "already_revealed": True,
                "candidate": candidate
            }
    
    # Check monthly limit
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    reveals_count = await db.contact_reveals.count_documents({
        "account_id": current_user.account_id,
        "revealed_at": {"$gte": month_start}
    })
    
    contact_limit = tier_config.get("contact_reveals_limit", 0)
    
    if reveals_count >= contact_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "limit_reached",
                "message": f"You have used all {contact_limit:,} contact reveals for this month. Upgrade your plan for more reveals.",
                "used": reveals_count,
                "limit": contact_limit,
                "upgrade_to": "pro" if tier_id == "growth" else "enterprise"
            }
        )
    
    # Get candidate
    candidate = await db.users.find_one({"id": candidate_id, "role": "job_seeker"})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Record the reveal
    await db.contact_reveals.insert_one({
        "id": str(uuid.uuid4()),
        "account_id": current_user.account_id,
        "user_id": current_user.id,
        "candidate_id": candidate_id,
        "revealed_at": now
    })
    
    # Clean response
    if "_id" in candidate:
        del candidate["_id"]
    if "password_hash" in candidate:
        del candidate["password_hash"]
    
    return {
        "success": True,
        "already_revealed": False,
        "candidate": candidate,
        "reveals_used": reveals_count + 1,
        "reveals_remaining": contact_limit - reveals_count - 1
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

@api_router.get("/my-packages")
async def get_my_packages(current_user: User = Depends(get_current_user)):
    """Get current user's subscription packages and tier info"""
    if not current_user.account_id:
        return []
    
    # Get account details
    account = await db.accounts.find_one({"id": current_user.account_id})
    if not account:
        return []
    
    # Get tier configuration
    from models.tiers import get_tier_config, TIER_CONFIG
    from models.enums import TierId
    
    tier_id_str = account.get("tier_id", "starter")
    
    # Convert string to enum
    try:
        tier_enum = TierId(tier_id_str)
    except ValueError:
        tier_enum = TierId.STARTER
    
    tier_config = get_tier_config(tier_enum)
    
    # Check if subscription is active and not expired
    subscription_status = account.get("subscription_status", "inactive")
    subscription_end = account.get("subscription_end_date")
    is_expired = False
    
    if subscription_end:
        from datetime import datetime
        if isinstance(subscription_end, str):
            subscription_end = datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
        is_expired = subscription_end < datetime.utcnow()
    
    # Build package response
    job_credits = account.get("job_credits", 0)
    
    # Determine job listings - Pro and above have unlimited
    if tier_enum in [TierId.PRO, TierId.ENTERPRISE]:
        job_listings_remaining = None  # null = unlimited
    else:
        job_listings_remaining = job_credits if job_credits else tier_config.get("job_post_limit", 0)
    
    user_package = {
        "id": account.get("id"),
        "account_id": account.get("id"),
        "tier_id": tier_id_str,
        "subscription_status": subscription_status,
        "is_active": subscription_status == "active" and not is_expired,
        "job_listings_remaining": job_listings_remaining,
        "subscription_start_date": account.get("subscription_start_date"),
        "subscription_end_date": subscription_end,
        "purchased_date": account.get("subscription_start_date") or account.get("created_at"),
        "expiry_date": subscription_end,
        "created_at": account.get("created_at"),
    }
    
    package_info = {
        "id": tier_id_str,
        "name": tier_config.get("name", "Starter"),
        "package_type": tier_id_str,
        "price": tier_config.get("price_monthly", 0),
        "currency": tier_config.get("currency", "ZAR"),
        "features": [str(f) for f in tier_config.get("features", [])],
        "included_users": tier_config.get("included_users", 1),
        "job_post_limit": tier_config.get("job_post_limit"),
        "is_subscription": True,
    }
    
    return [{
        "user_package": user_package,
        "package": package_info,
        "is_expired": is_expired
    }]

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
# ============================================
# Company Structure - Branches, Team, Invitations
# ============================================

@api_router.get("/company/branches")
async def get_company_branches(current_user: User = Depends(get_current_user)):
    """Get all branches for the current user's company"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    branches = await db.branches.find({"account_id": current_user.account_id}).to_list(100)
    for branch in branches:
        branch["id"] = str(branch.pop("_id"))
    return branches

@api_router.post("/company/branches")
async def create_company_branch(
    branch_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new branch for the company"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    # Check if user has permission (owner or admin)
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only owners and admins can create branches")
    
    branch = {
        "account_id": current_user.account_id,
        "name": branch_data.get("name", ""),
        "location": branch_data.get("location", ""),
        "email": branch_data.get("email"),
        "phone": branch_data.get("phone"),
        "is_headquarters": branch_data.get("is_headquarters", False),
        "created_at": datetime.utcnow(),
        "created_by": current_user.id
    }
    
    # If marking as headquarters, unset other headquarters
    if branch["is_headquarters"]:
        await db.branches.update_many(
            {"account_id": current_user.account_id},
            {"$set": {"is_headquarters": False}}
        )
    
    result = await db.branches.insert_one(branch)
    branch["id"] = str(result.inserted_id)
    if "_id" in branch:
        del branch["_id"]
    
    return branch

@api_router.put("/company/branches/{branch_id}")
async def update_company_branch(
    branch_id: str,
    branch_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update a branch"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only owners and admins can update branches")
    
    from bson import ObjectId
    
    # Verify branch belongs to user's account
    branch = await db.branches.find_one({
        "_id": ObjectId(branch_id),
        "account_id": current_user.account_id
    })
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    update_data = {
        "name": branch_data.get("name", branch["name"]),
        "location": branch_data.get("location", branch["location"]),
        "email": branch_data.get("email", branch.get("email")),
        "phone": branch_data.get("phone", branch.get("phone")),
        "is_headquarters": branch_data.get("is_headquarters", branch.get("is_headquarters", False)),
        "updated_at": datetime.utcnow()
    }
    
    # If marking as headquarters, unset other headquarters
    if update_data["is_headquarters"]:
        await db.branches.update_many(
            {"account_id": current_user.account_id, "_id": {"$ne": ObjectId(branch_id)}},
            {"$set": {"is_headquarters": False}}
        )
    
    await db.branches.update_one({"_id": ObjectId(branch_id)}, {"$set": update_data})
    
    return {"message": "Branch updated successfully"}

@api_router.delete("/company/branches/{branch_id}")
async def delete_company_branch(
    branch_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a branch"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only owners and admins can delete branches")
    
    from bson import ObjectId
    
    result = await db.branches.delete_one({
        "_id": ObjectId(branch_id),
        "account_id": current_user.account_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return {"message": "Branch deleted successfully"}

@api_router.get("/company/members")
async def get_company_members(current_user: User = Depends(get_current_user)):
    """Get all team members for the current user's company"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    members = await db.users.find(
        {"account_id": current_user.account_id},
        {"password": 0, "_id": 0}
    ).to_list(100)
    
    return members

@api_router.get("/company/invitations")
async def get_company_invitations(current_user: User = Depends(get_current_user)):
    """Get all pending invitations for the current user's company"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    invitations = await db.invitations.find({
        "account_id": current_user.account_id,
        "status": "pending"
    }).to_list(100)
    
    for inv in invitations:
        inv["id"] = str(inv.pop("_id"))
    
    return invitations

@api_router.post("/company/invitations")
async def create_company_invitation(
    invitation_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new team member invitation"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only owners and admins can invite team members")
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": invitation_data.get("email")})
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    
    # Check for existing pending invitation
    existing_invitation = await db.invitations.find_one({
        "email": invitation_data.get("email"),
        "account_id": current_user.account_id,
        "status": "pending"
    })
    if existing_invitation:
        raise HTTPException(status_code=400, detail="An invitation has already been sent to this email")
    
    invitation = {
        "account_id": current_user.account_id,
        "email": invitation_data.get("email"),
        "role": invitation_data.get("role", "member"),
        "branch_id": invitation_data.get("branch_id"),
        "token": secrets.token_urlsafe(32),
        "status": "pending",
        "created_at": datetime.utcnow(),
        "created_by": current_user.id,
        "expires_at": datetime.utcnow() + timedelta(days=7)
    }
    
    result = await db.invitations.insert_one(invitation)
    invitation["id"] = str(result.inserted_id)
    if "_id" in invitation:
        del invitation["_id"]
    
    # TODO: Send invitation email
    
    return invitation

@api_router.delete("/company/invitations/{invitation_id}")
async def cancel_company_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a pending invitation"""
    if not current_user.account_id:
        raise HTTPException(status_code=400, detail="User not associated with an account")
    
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only owners and admins can cancel invitations")
    
    from bson import ObjectId
    
    result = await db.invitations.delete_one({
        "_id": ObjectId(invitation_id),
        "account_id": current_user.account_id,
        "status": "pending"
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    return {"message": "Invitation cancelled successfully"}


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


# ============================================
# Recruiter Reports API Endpoints
# ============================================

@api_router.get("/reports/time-to-fill")
async def get_time_to_fill_report(
    current_user: User = Depends(get_current_recruiter),
    start_date: str = None,
    end_date: str = None,
    job_id: str = None,
    recruiter_id: str = None,
    include_open: bool = False,
    page: int = 1,
    limit: int = 50
):
    """
    Time-to-Fill Report
    Measures how long it takes to successfully close roles.
    Time to fill = Offer Accepted Date - Job Open Date
    """
    
    now = datetime.utcnow()
    
    # Parse date filters
    date_start = datetime.fromisoformat(start_date) if start_date else now - timedelta(days=90)
    date_end = datetime.fromisoformat(end_date) if end_date else now
    
    # Build query for jobs
    job_query = {
        "account_id": current_user.account_id,
        "posted_date": {"$gte": date_start, "$lte": date_end}
    }
    
    if job_id:
        job_query["id"] = job_id
    
    if recruiter_id:
        job_query["posted_by"] = recruiter_id
    
    # Fetch jobs
    jobs_cursor = db.jobs.find(job_query).sort("posted_date", -1)
    jobs_list = await jobs_cursor.to_list(None)
    
    report_data = []
    total_days_to_fill = []
    
    for job in jobs_list:
        job_id_val = job["id"]
        job_open_date = job.get("posted_date", job.get("created_at", now))
        
        # Check if job has been filled (has an accepted offer)
        filled_app = await db.job_applications.find_one({
            "job_id": job_id_val,
            "status": {"$in": ["offered", "hired"]}
        })
        
        is_filled = filled_app is not None
        offer_accepted_date = filled_app.get("last_updated") if filled_app else None
        
        # Calculate time to fill
        if is_filled and offer_accepted_date:
            days_to_fill = (offer_accepted_date - job_open_date).days
        else:
            days_to_fill = (now - job_open_date).days  # Days open
        
        # Skip open jobs if not requested
        if not is_filled and not include_open:
            continue
        
        if is_filled:
            total_days_to_fill.append(days_to_fill)
        
        # Get recruiter info
        recruiter = await db.users.find_one({"id": job.get("posted_by")})
        recruiter_name = f"{recruiter.get('first_name', '')} {recruiter.get('last_name', '')}" if recruiter else "Unknown"
        
        report_data.append({
            "job_id": job_id_val,
            "job_title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "recruiter_id": job.get("posted_by"),
            "recruiter_name": recruiter_name,
            "job_open_date": job_open_date.isoformat(),
            "offer_accepted_date": offer_accepted_date.isoformat() if offer_accepted_date else None,
            "days_to_fill": days_to_fill,
            "is_filled": is_filled,
            "status": "Filled" if is_filled else "Open"
        })
    
    # Calculate summary metrics
    avg_time_to_fill = sum(total_days_to_fill) / len(total_days_to_fill) if total_days_to_fill else 0
    sorted_days = sorted(total_days_to_fill)
    median_time_to_fill = sorted_days[len(sorted_days) // 2] if sorted_days else 0
    
    # Pagination
    total_count = len(report_data)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_data = report_data[start_idx:end_idx]
    
    return {
        "report_type": "time_to_fill",
        "generated_at": now.isoformat(),
        "filters": {
            "start_date": date_start.isoformat(),
            "end_date": date_end.isoformat(),
            "job_id": job_id,
            "recruiter_id": recruiter_id,
            "include_open": include_open
        },
        "summary": {
            "total_jobs": total_count,
            "filled_jobs": len(total_days_to_fill),
            "open_jobs": total_count - len(total_days_to_fill),
            "average_days_to_fill": round(avg_time_to_fill, 1),
            "median_days_to_fill": median_time_to_fill
        },
        "data": paginated_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        }
    }


@api_router.get("/reports/pipeline-conversion")
async def get_pipeline_conversion_report(
    current_user: User = Depends(get_current_recruiter),
    start_date: str = None,
    end_date: str = None,
    job_id: str = None,
    recruiter_id: str = None,
    page: int = 1,
    limit: int = 50
):
    """
    Pipeline Conversion Report
    Identifies bottlenecks and drop-off points within hiring pipelines.
    Stage-to-stage conversion = candidates moved to next stage / candidates in previous stage
    """
    
    now = datetime.utcnow()
    
    # Parse date filters
    date_start = datetime.fromisoformat(start_date) if start_date else now - timedelta(days=90)
    date_end = datetime.fromisoformat(end_date) if end_date else now
    
    # Define pipeline stages in order
    pipeline_stages = ["pending", "reviewed", "shortlisted", "interviewed", "offered"]
    
    # Build application query
    app_query = {
        "account_id": current_user.account_id,
        "applied_date": {"$gte": date_start, "$lte": date_end}
    }
    
    if job_id:
        app_query["job_id"] = job_id
    
    # Get job filter by recruiter
    job_ids_filter = None
    if recruiter_id:
        jobs = await db.jobs.find({"posted_by": recruiter_id, "account_id": current_user.account_id}).to_list(None)
        job_ids_filter = [j["id"] for j in jobs]
        if job_ids_filter:
            app_query["job_id"] = {"$in": job_ids_filter}
    
    # Aggregate applications by status
    pipeline = [
        {"$match": app_query},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    status_counts = await db.job_applications.aggregate(pipeline).to_list(None)
    status_map = {item["_id"]: item["count"] for item in status_counts}
    
    # Calculate stage metrics
    stage_data = []
    total_applications = sum(status_map.values())
    
    for i, stage in enumerate(pipeline_stages):
        count = status_map.get(stage, 0)
        
        # For conversion calculation, we need cumulative counts
        # Candidates "at or past" this stage
        at_or_past = sum(status_map.get(s, 0) for s in pipeline_stages[i:])
        
        # Previous stage count (for conversion rate)
        if i == 0:
            conversion_rate = 100.0  # First stage always 100%
            prev_count = total_applications
        else:
            prev_stage = pipeline_stages[i-1]
            prev_at_or_past = sum(status_map.get(s, 0) for s in pipeline_stages[i-1:])
            conversion_rate = (at_or_past / prev_at_or_past * 100) if prev_at_or_past > 0 else 0
            prev_count = prev_at_or_past
        
        # Drop-off rate
        drop_off = 100 - conversion_rate if i > 0 else 0
        
        stage_data.append({
            "stage": stage,
            "stage_label": stage.replace("_", " ").title(),
            "count": count,
            "cumulative_count": at_or_past,
            "conversion_rate": round(conversion_rate, 1),
            "drop_off_rate": round(drop_off, 1)
        })
    
    # Add rejected/withdrawn stats
    rejected_count = status_map.get("rejected", 0)
    withdrawn_count = status_map.get("withdrawn", 0)
    
    # Per-job breakdown if no specific job selected
    job_breakdown = []
    if not job_id:
        job_pipeline = [
            {"$match": app_query},
            {"$group": {
                "_id": "$job_id",
                "total": {"$sum": 1},
                "pending": {"$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}},
                "reviewed": {"$sum": {"$cond": [{"$eq": ["$status", "reviewed"]}, 1, 0]}},
                "shortlisted": {"$sum": {"$cond": [{"$eq": ["$status", "shortlisted"]}, 1, 0]}},
                "interviewed": {"$sum": {"$cond": [{"$eq": ["$status", "interviewed"]}, 1, 0]}},
                "offered": {"$sum": {"$cond": [{"$eq": ["$status", "offered"]}, 1, 0]}},
                "rejected": {"$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}}
            }},
            {"$sort": {"total": -1}},
            {"$limit": limit}
        ]
        
        job_stats = await db.job_applications.aggregate(job_pipeline).to_list(None)
        
        for js in job_stats:
            job = await db.jobs.find_one({"id": js["_id"]})
            if job:
                job_breakdown.append({
                    "job_id": js["_id"],
                    "job_title": job.get("title", "Unknown"),
                    "total_applications": js["total"],
                    "stages": {
                        "pending": js["pending"],
                        "reviewed": js["reviewed"],
                        "shortlisted": js["shortlisted"],
                        "interviewed": js["interviewed"],
                        "offered": js["offered"],
                        "rejected": js["rejected"]
                    }
                })
    
    return {
        "report_type": "pipeline_conversion",
        "generated_at": now.isoformat(),
        "filters": {
            "start_date": date_start.isoformat(),
            "end_date": date_end.isoformat(),
            "job_id": job_id,
            "recruiter_id": recruiter_id
        },
        "summary": {
            "total_applications": total_applications,
            "rejected": rejected_count,
            "withdrawn": withdrawn_count,
            "overall_conversion_to_offer": round(
                (status_map.get("offered", 0) / total_applications * 100) if total_applications > 0 else 0, 1
            )
        },
        "pipeline_stages": stage_data,
        "job_breakdown": job_breakdown,
        "pagination": {
            "page": page,
            "limit": limit
        }
    }


@api_router.get("/reports/recruiter-workload")
async def get_recruiter_workload_report(
    current_user: User = Depends(get_current_recruiter),
    start_date: str = None,
    end_date: str = None,
    recruiter_id: str = None,
    page: int = 1,
    limit: int = 50
):
    """
    Recruiter Workload Report
    Monitors recruiter capacity and prevents overload or SLA breaches.
    """
    
    now = datetime.utcnow()
    
    # Parse date filters
    date_start = datetime.fromisoformat(start_date) if start_date else now - timedelta(days=30)
    date_end = datetime.fromisoformat(end_date) if end_date else now
    
    # Get recruiters in account
    recruiter_query = {
        "account_id": current_user.account_id,
        "role": "recruiter"
    }
    
    if recruiter_id:
        recruiter_query["id"] = recruiter_id
    
    # Check access - recruiters see only their own, admins see all
    if current_user.account_role not in [AccountRole.OWNER, AccountRole.ADMIN]:
        recruiter_query["id"] = current_user.id
    
    recruiters = await db.users.find(recruiter_query).to_list(None)
    
    workload_data = []
    
    for recruiter in recruiters:
        rec_id = recruiter["id"]
        rec_name = f"{recruiter.get('first_name', '')} {recruiter.get('last_name', '')}"
        
        # Active jobs (jobs with candidates in pipeline, status Open)
        active_jobs = await db.jobs.count_documents({
            "posted_by": rec_id,
            "is_active": True,
            "expiry_date": {"$gt": now}
        })
        
        # Get job IDs for this recruiter
        rec_job_ids = []
        async for job in db.jobs.find({"posted_by": rec_id}, {"id": 1}):
            rec_job_ids.append(job["id"])
        
        # Candidates actively managed (applications not rejected/withdrawn)
        active_candidates = await db.job_applications.count_documents({
            "job_id": {"$in": rec_job_ids},
            "status": {"$nin": ["rejected", "withdrawn"]}
        }) if rec_job_ids else 0
        
        # Interviews scheduled (candidates with interviewed status in date range)
        interviews_scheduled = await db.job_applications.count_documents({
            "job_id": {"$in": rec_job_ids},
            "status": "interviewed",
            "last_updated": {"$gte": date_start, "$lte": date_end}
        }) if rec_job_ids else 0
        
        # Pending reviews (applications in pending status for > 48 hours - overdue)
        overdue_threshold = now - timedelta(hours=48)
        overdue_reviews = await db.job_applications.count_documents({
            "job_id": {"$in": rec_job_ids},
            "status": "pending",
            "applied_date": {"$lt": overdue_threshold}
        }) if rec_job_ids else 0
        
        # New applications in date range
        new_applications = await db.job_applications.count_documents({
            "job_id": {"$in": rec_job_ids},
            "applied_date": {"$gte": date_start, "$lte": date_end}
        }) if rec_job_ids else 0
        
        # Offers pending response
        offers_pending = await db.job_applications.count_documents({
            "job_id": {"$in": rec_job_ids},
            "status": "offered"
        }) if rec_job_ids else 0
        
        workload_data.append({
            "recruiter_id": rec_id,
            "recruiter_name": rec_name,
            "email": recruiter.get("email", ""),
            "metrics": {
                "active_jobs": active_jobs,
                "active_candidates": active_candidates,
                "interviews_scheduled": interviews_scheduled,
                "new_applications": new_applications,
                "overdue_reviews": overdue_reviews,
                "offers_pending": offers_pending
            },
            "workload_score": active_jobs * 10 + active_candidates + overdue_reviews * 5,  # Simple scoring
            "has_overdue": overdue_reviews > 0
        })
    
    # Sort by workload score descending
    workload_data.sort(key=lambda x: x["workload_score"], reverse=True)
    
    # Calculate summary
    total_active_jobs = sum(w["metrics"]["active_jobs"] for w in workload_data)
    total_active_candidates = sum(w["metrics"]["active_candidates"] for w in workload_data)
    total_overdue = sum(w["metrics"]["overdue_reviews"] for w in workload_data)
    recruiters_with_overdue = sum(1 for w in workload_data if w["has_overdue"])
    
    # Pagination
    total_count = len(workload_data)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_data = workload_data[start_idx:end_idx]
    
    return {
        "report_type": "recruiter_workload",
        "generated_at": now.isoformat(),
        "filters": {
            "start_date": date_start.isoformat(),
            "end_date": date_end.isoformat(),
            "recruiter_id": recruiter_id
        },
        "summary": {
            "total_recruiters": total_count,
            "total_active_jobs": total_active_jobs,
            "total_active_candidates": total_active_candidates,
            "total_overdue_tasks": total_overdue,
            "recruiters_with_overdue": recruiters_with_overdue
        },
        "data": paginated_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        }
    }


@api_router.get("/reports/export/{report_type}")
async def export_report_csv(
    report_type: str,
    current_user: User = Depends(get_current_recruiter),
    start_date: str = None,
    end_date: str = None,
    job_id: str = None,
    recruiter_id: str = None
):
    """Export report data as CSV"""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    # Get report data based on type
    if report_type == "time-to-fill":
        report = await get_time_to_fill_report(
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            job_id=job_id,
            recruiter_id=recruiter_id,
            include_open=True,
            limit=10000
        )
        headers = ["Job Title", "Company", "Recruiter", "Open Date", "Fill Date", "Days to Fill", "Status"]
        rows = [
            [d["job_title"], d["company_name"], d["recruiter_name"], d["job_open_date"], 
             d["offer_accepted_date"] or "", d["days_to_fill"], d["status"]]
            for d in report["data"]
        ]
    elif report_type == "pipeline-conversion":
        report = await get_pipeline_conversion_report(
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            job_id=job_id,
            recruiter_id=recruiter_id,
            limit=10000
        )
        headers = ["Stage", "Count", "Cumulative", "Conversion Rate %", "Drop-off Rate %"]
        rows = [
            [s["stage_label"], s["count"], s["cumulative_count"], s["conversion_rate"], s["drop_off_rate"]]
            for s in report["pipeline_stages"]
        ]
    elif report_type == "recruiter-workload":
        report = await get_recruiter_workload_report(
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            recruiter_id=recruiter_id,
            limit=10000
        )
        headers = ["Recruiter", "Email", "Active Jobs", "Active Candidates", "Interviews", "New Apps", "Overdue", "Offers Pending"]
        rows = [
            [d["recruiter_name"], d["email"], d["metrics"]["active_jobs"], d["metrics"]["active_candidates"],
             d["metrics"]["interviews_scheduled"], d["metrics"]["new_applications"], 
             d["metrics"]["overdue_reviews"], d["metrics"]["offers_pending"]]
            for d in report["data"]
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    
    # Return as streaming response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_type}_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
    )


# Include router
app.include_router(api_router)

# Mount static files AFTER router include to avoid shadowing upload POST endpoints
# The StaticFiles mount was previously shadowing /api/uploads/cv, /api/uploads/profile-picture etc.
app.mount("/api/uploads", StaticFiles(directory=UPLOAD_PATH), name="uploads")


# Root redirect
@app.get("/")
async def root():
    return {"message": "JobRocket API v2.0.0", "docs": "/docs"}
