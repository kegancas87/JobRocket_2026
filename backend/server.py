from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Job Rocket API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums for job-related data
class JobType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    INTERNSHIP = "Internship"

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
    
    # First job posted (20 points) - we'll track this separately
    # This will be set when recruiter posts their first job
    
    progress.total_points = points
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
    requirements: List[str] = []
    responsibilities: List[str] = []
    location: str
    job_type: JobType
    experience_level: ExperienceLevel
    category: JobCategory
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "ZAR"
    is_remote: bool = False
    is_hybrid: bool = False
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    closing_date: Optional[datetime] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    featured: bool = False

class JobCreate(BaseModel):
    title: str
    company_id: str
    company_name: str
    description: str
    requirements: List[str] = []
    responsibilities: List[str] = []
    location: str
    job_type: JobType
    experience_level: ExperienceLevel
    category: JobCategory
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "ZAR"
    is_remote: bool = False
    is_hybrid: bool = False
    application_url: Optional[str] = None
    application_email: Optional[str] = None
    closing_date: Optional[datetime] = None
    logo_url: Optional[str] = None
    featured: bool = False

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
        progress = calculate_recruiter_progress(current_user)
        # Update progress in database
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"recruiter_progress": progress.dict()}}
        )
        current_user.recruiter_progress = progress
    
    # Return user without password hash
    user_dict = current_user.dict()
    return user_dict


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
        progress = calculate_recruiter_progress(user_obj)
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


# Include the router in the main app
app.include_router(api_router)

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