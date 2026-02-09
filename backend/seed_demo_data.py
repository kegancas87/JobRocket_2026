"""
JobRocket - Demo Data Seeder
Creates test accounts, users, and jobs for all tiers
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from passlib.context import CryptContext
import uuid

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Demo data
DEMO_ACCOUNTS = [
    {
        "company_name": "TechCorp Solutions",
        "tier": "starter",
        "owner": {
            "email": "hr@techcorp.co.za",
            "first_name": "Lisa",
            "last_name": "Martinez",
            "password": "demo123"
        },
        "description": "Leading technology solutions provider in South Africa, specializing in enterprise software development.",
        "industry": "Technology",
        "size": "51-200",
        "location": "Johannesburg, Gauteng",
        "website": "https://techcorp.co.za"
    },
    {
        "company_name": "Innovate Digital Agency",
        "tier": "growth",
        "owner": {
            "email": "talent@innovatedigital.co.za",
            "first_name": "David",
            "last_name": "Wilson",
            "password": "demo123"
        },
        "team_members": [
            {"email": "recruiter@innovatedigital.co.za", "first_name": "Sarah", "last_name": "Jones", "role": "recruiter"}
        ],
        "description": "Award-winning digital marketing agency helping brands grow their online presence.",
        "industry": "Digital Marketing",
        "size": "11-50",
        "location": "Cape Town, Western Cape",
        "website": "https://innovatedigital.co.za"
    },
    {
        "company_name": "FinTech Solutions SA",
        "tier": "pro",
        "owner": {
            "email": "careers@fintechsa.co.za",
            "first_name": "Emma",
            "last_name": "Davis",
            "password": "demo123"
        },
        "team_members": [
            {"email": "hr@fintechsa.co.za", "first_name": "Michael", "last_name": "Brown", "role": "admin"},
            {"email": "recruiter@fintechsa.co.za", "first_name": "Jennifer", "last_name": "Taylor", "role": "recruiter"}
        ],
        "description": "Pioneering financial technology solutions for the African market. We're building the future of finance.",
        "industry": "Financial Technology",
        "size": "201-500",
        "location": "Sandton, Gauteng",
        "website": "https://fintechsa.co.za"
    },
    {
        "company_name": "Global Recruitment Agency",
        "tier": "enterprise",
        "owner": {
            "email": "admin@globalrecruit.co.za",
            "first_name": "James",
            "last_name": "Anderson",
            "password": "demo123"
        },
        "team_members": [
            {"email": "senior@globalrecruit.co.za", "first_name": "Robert", "last_name": "Smith", "role": "admin"},
            {"email": "tech@globalrecruit.co.za", "first_name": "Emily", "last_name": "Johnson", "role": "recruiter"},
            {"email": "finance@globalrecruit.co.za", "first_name": "William", "last_name": "Williams", "role": "recruiter"},
            {"email": "viewer@globalrecruit.co.za", "first_name": "Olivia", "last_name": "Brown", "role": "viewer"}
        ],
        "description": "Enterprise-grade recruitment solutions for multinational corporations. 20+ years of experience.",
        "industry": "Recruitment",
        "size": "500+",
        "location": "Johannesburg, Gauteng",
        "website": "https://globalrecruit.co.za"
    }
]


JOB_SEEKERS = [
    {
        "email": "thabo.mthembu@gmail.com",
        "first_name": "Thabo",
        "last_name": "Mthembu",
        "password": "demo123",
        "location": "Johannesburg, Gauteng",
        "about_me": "Passionate software developer with 5 years of experience in full-stack development.",
        "skills": ["JavaScript", "React", "Node.js", "Python", "MongoDB", "Git"]
    },
    {
        "email": "nomsa.dlamini@gmail.com",
        "first_name": "Nomsa",
        "last_name": "Dlamini",
        "password": "demo123",
        "location": "Cape Town, Western Cape",
        "about_me": "Senior UX/UI Designer with a passion for creating beautiful, user-centered digital experiences.",
        "skills": ["Figma", "Adobe XD", "Sketch", "User Research", "Prototyping", "Design Systems"]
    },
    {
        "email": "pieter.vandermerwe@gmail.com",
        "first_name": "Pieter",
        "last_name": "van der Merwe",
        "password": "demo123",
        "location": "Pretoria, Gauteng",
        "about_me": "Data Analyst with strong analytical skills and experience in business intelligence.",
        "skills": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics", "R"]
    },
    {
        "email": "zanele.khumalo@gmail.com",
        "first_name": "Zanele",
        "last_name": "Khumalo",
        "password": "demo123",
        "location": "Durban, KwaZulu-Natal",
        "about_me": "Results-driven Digital Marketing Manager with expertise in growth strategies.",
        "skills": ["Digital Marketing", "SEO", "SEM", "Google Ads", "Social Media Marketing", "Analytics"]
    },
    {
        "email": "johan.steyn@gmail.com",
        "first_name": "Johan",
        "last_name": "Steyn",
        "password": "demo123",
        "location": "Stellenbosch, Western Cape",
        "about_me": "DevOps Engineer passionate about automation and cloud infrastructure.",
        "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform", "Linux", "CI/CD"]
    }
]


SAMPLE_JOBS = [
    {
        "title": "Senior Software Developer",
        "description": "We're looking for an experienced software developer to join our team...",
        "location": "Johannesburg, Gauteng",
        "salary": "R70,000 - R90,000 per month",
        "job_type": "Permanent",
        "work_type": "Hybrid",
        "industry": "Technology",
        "experience": "5+ years",
        "qualifications": "BSc Computer Science or related degree"
    },
    {
        "title": "UX/UI Designer",
        "description": "Join our creative team as a UX/UI Designer...",
        "location": "Cape Town, Western Cape",
        "salary": "R50,000 - R65,000 per month",
        "job_type": "Permanent",
        "work_type": "Remote",
        "industry": "Digital Marketing",
        "experience": "3+ years",
        "qualifications": "Relevant design qualification"
    },
    {
        "title": "Data Analyst",
        "description": "We need a skilled Data Analyst to help us make data-driven decisions...",
        "location": "Sandton, Gauteng",
        "salary": "R45,000 - R60,000 per month",
        "job_type": "Permanent",
        "work_type": "Onsite",
        "industry": "Financial Technology",
        "experience": "2+ years",
        "qualifications": "Degree in Statistics, Mathematics, or related field"
    },
    {
        "title": "DevOps Engineer",
        "description": "Looking for a DevOps Engineer to improve our deployment pipeline...",
        "location": "Johannesburg, Gauteng",
        "salary": "R65,000 - R85,000 per month",
        "job_type": "Contract",
        "work_type": "Hybrid",
        "industry": "Technology",
        "experience": "4+ years",
        "qualifications": "AWS/Azure certification preferred"
    },
    {
        "title": "Digital Marketing Manager",
        "description": "Lead our digital marketing initiatives and grow our online presence...",
        "location": "Cape Town, Western Cape",
        "salary": "R55,000 - R70,000 per month",
        "job_type": "Permanent",
        "work_type": "Hybrid",
        "industry": "Marketing",
        "experience": "4+ years",
        "qualifications": "Marketing degree or equivalent experience"
    }
]


ADMIN_USER = {
    "email": "admin@jobrocket.co.za",
    "first_name": "System",
    "last_name": "Administrator",
    "password": "admin123",
    "role": "admin"
}


async def create_admin(db):
    """Create admin user"""
    print("\nCreating admin user...")
    
    admin_dict = {
        "id": str(uuid.uuid4()),
        "email": ADMIN_USER["email"],
        "password_hash": get_password_hash(ADMIN_USER["password"]),
        "first_name": ADMIN_USER["first_name"],
        "last_name": ADMIN_USER["last_name"],
        "role": "admin",
        "account_id": None,
        "account_role": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    await db.users.insert_one(admin_dict)
    print(f"  Created admin: {ADMIN_USER['email']} / {ADMIN_USER['password']}")


async def create_job_seekers(db):
    """Create job seeker users"""
    print("\nCreating job seekers...")
    
    for seeker in JOB_SEEKERS:
        user_dict = {
            "id": str(uuid.uuid4()),
            "email": seeker["email"],
            "password_hash": get_password_hash(seeker["password"]),
            "first_name": seeker["first_name"],
            "last_name": seeker["last_name"],
            "role": "job_seeker",
            "account_id": None,
            "account_role": None,
            "location": seeker["location"],
            "about_me": seeker["about_me"],
            "skills": seeker["skills"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await db.users.insert_one(user_dict)
        print(f"  Created job seeker: {seeker['email']}")


async def create_accounts_and_recruiters(db):
    """Create accounts with owners and team members"""
    print("\nCreating accounts and recruiters...")
    
    for company in DEMO_ACCOUNTS:
        # Create owner user
        owner = company["owner"]
        owner_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())
        
        owner_dict = {
            "id": owner_id,
            "email": owner["email"],
            "password_hash": get_password_hash(owner["password"]),
            "first_name": owner["first_name"],
            "last_name": owner["last_name"],
            "role": "recruiter",
            "account_id": account_id,
            "account_role": "owner",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await db.users.insert_one(owner_dict)
        
        # Create account
        tier_users = {"starter": 1, "growth": 2, "pro": 3, "enterprise": 5}
        team_count = 1 + len(company.get("team_members", []))
        
        account_dict = {
            "id": account_id,
            "name": company["company_name"],
            "owner_user_id": owner_id,
            "tier_id": company["tier"],
            "subscription_status": "active",
            "subscription_start_date": datetime.utcnow(),
            "subscription_end_date": datetime.utcnow() + timedelta(days=30),
            "billing_cycle": "monthly",
            "company_description": company["description"],
            "company_website": company["website"],
            "company_industry": company["industry"],
            "company_size": company["size"],
            "company_location": company["location"],
            "current_user_count": team_count,
            "extra_users_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await db.accounts.insert_one(account_dict)
        print(f"  Created account: {company['company_name']} ({company['tier'].upper()} tier)")
        print(f"    Owner: {owner['email']} / {owner['password']}")
        
        # Create team members
        for member in company.get("team_members", []):
            member_id = str(uuid.uuid4())
            member_dict = {
                "id": member_id,
                "email": member["email"],
                "password_hash": get_password_hash("demo123"),
                "first_name": member["first_name"],
                "last_name": member["last_name"],
                "role": "recruiter",
                "account_id": account_id,
                "account_role": member["role"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            await db.users.insert_one(member_dict)
            print(f"    Team member: {member['email']} ({member['role']})")


async def create_sample_jobs(db):
    """Create sample jobs for each account"""
    print("\nCreating sample jobs...")
    
    # Get all accounts
    accounts = await db.accounts.find({"subscription_status": "active"}).to_list(100)
    
    for account in accounts:
        # Get owner for posted_by
        owner = await db.users.find_one({"id": account["owner_user_id"]})
        
        # Create 2-3 jobs per account
        num_jobs = 2 if account["tier_id"] == "starter" else 3
        
        for i in range(num_jobs):
            job_template = SAMPLE_JOBS[i % len(SAMPLE_JOBS)]
            
            job_dict = {
                "id": str(uuid.uuid4()),
                "account_id": account["id"],
                "posted_by": owner["id"],
                "company_name": account["name"],
                "logo_url": account.get("company_logo_url"),
                "title": job_template["title"],
                "description": job_template["description"],
                "location": account.get("company_location", job_template["location"]),
                "salary": job_template["salary"],
                "job_type": job_template["job_type"],
                "work_type": job_template["work_type"],
                "industry": account.get("company_industry", job_template["industry"]),
                "experience": job_template["experience"],
                "qualifications": job_template["qualifications"],
                "posted_date": datetime.utcnow() - timedelta(days=i * 3),
                "expiry_date": datetime.utcnow() + timedelta(days=35 - i * 3),
                "is_active": True,
                "featured": i == 0,  # First job is featured
            }
            
            await db.jobs.insert_one(job_dict)
        
        print(f"  Created {num_jobs} jobs for {account['name']}")


async def main():
    """Main seeding function"""
    print("=" * 60)
    print("JobRocket Demo Data Seeder")
    print("=" * 60)
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    await create_admin(db)
    await create_job_seekers(db)
    await create_accounts_and_recruiters(db)
    await create_sample_jobs(db)
    
    print("\n" + "=" * 60)
    print("Demo data seeding complete!")
    print("=" * 60)
    
    # Summary
    print("\n📊 Summary:")
    print(f"  Admin users: {await db.users.count_documents({'role': 'admin'})}")
    print(f"  Recruiters: {await db.users.count_documents({'role': 'recruiter'})}")
    print(f"  Job seekers: {await db.users.count_documents({'role': 'job_seeker'})}")
    print(f"  Accounts: {await db.accounts.count_documents({})}")
    print(f"  Jobs: {await db.jobs.count_documents({})}")
    
    print("\n🔑 Quick Login Credentials:")
    print("  Admin:      admin@jobrocket.co.za / admin123")
    print("  Starter:    hr@techcorp.co.za / demo123")
    print("  Growth:     talent@innovatedigital.co.za / demo123")
    print("  Pro:        careers@fintechsa.co.za / demo123")
    print("  Enterprise: admin@globalrecruit.co.za / demo123")
    print("  Job Seeker: thabo.mthembu@gmail.com / demo123")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
