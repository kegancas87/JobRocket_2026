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


# Job Routes
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