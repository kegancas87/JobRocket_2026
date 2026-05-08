#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import bcrypt
import random

# Add the current directory to Python path
sys.path.append('/app/backend')

class ProductionDataPopulator:
    def __init__(self, mongo_url=None):
        self.mongo_url = mongo_url or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            # Use production database name
            db_name = os.environ.get('DB_NAME', 'jobrocket')
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {db_name}")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    async def create_admin_user(self):
        """Create admin@jobrocket.co.za as administrator"""
        print("\n👑 Creating Administrator User...")
        
        admin_email = "admin@jobrocket.co.za"
        
        # Check if admin already exists
        existing_admin = await self.db.users.find_one({"email": admin_email})
        if existing_admin:
            print(f"⚠️  Admin user {admin_email} already exists")
            return existing_admin
        
        # Hash password
        password = "admin123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password_hash": hashed_password.decode('utf-8'),
            "first_name": "Job Rocket",
            "last_name": "Administrator",
            "role": "admin",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "admin_permissions": {
                "user_management": True,
                "discount_codes": True,
                "analytics": True,
                "system_settings": True,
                "platform_management": True
            }
        }
        
        result = await self.db.users.insert_one(admin_user)
        if result.inserted_id:
            print(f"✅ Created admin user: {admin_email}")
            print(f"   Password: {password}")
            return admin_user
        else:
            print(f"❌ Failed to create admin user")
            return None
    
    async def create_recruiter_users(self):
        """Create realistic recruiting companies and users"""
        print("\n👔 Creating Recruiter Users & Companies...")
        
        recruiters_data = [
            {
                "email": "hr@techcorp.co.za",
                "password": "demo123",
                "first_name": "Lisa",
                "last_name": "Martinez",
                "company": {
                    "company_name": "TechCorp Solutions",
                    "company_industry": "Technology",
                    "company_size": "201-500 employees",
                    "company_location": "Johannesburg, Gauteng",
                    "company_description": "Leading technology consulting firm specializing in digital transformation, cloud solutions, and enterprise software development. We help businesses leverage cutting-edge technology to drive growth and innovation.",
                    "company_website": "https://techcorp.co.za",
                    "company_linkedin": "https://linkedin.com/company/techcorp-solutions"
                }
            },
            {
                "email": "talent@innovatedigital.co.za",
                "password": "demo123",
                "first_name": "David",
                "last_name": "Wilson",
                "company": {
                    "company_name": "Innovate Digital Agency",
                    "company_industry": "Digital Marketing",
                    "company_size": "51-200 employees",
                    "company_location": "Cape Town, Western Cape",
                    "company_description": "Creative digital agency focused on cutting-edge web development, UI/UX design, and digital marketing strategies. We create memorable digital experiences that drive business results.",
                    "company_website": "https://innovatedigital.co.za",
                    "company_linkedin": "https://linkedin.com/company/innovate-digital"
                }
            },
            {
                "email": "careers@fintechsa.co.za",
                "password": "demo123",
                "first_name": "Emma",
                "last_name": "Davis",
                "company": {
                    "company_name": "FinTech Solutions SA",
                    "company_industry": "Financial Technology",
                    "company_size": "101-200 employees",
                    "company_location": "Sandton, Gauteng",
                    "company_description": "Innovative fintech company revolutionizing financial services in South Africa. We develop cutting-edge payment solutions, digital banking platforms, and financial analytics tools.",
                    "company_website": "https://fintechsa.co.za",
                    "company_linkedin": "https://linkedin.com/company/fintech-sa"
                }
            },
            {
                "email": "people@datainsights.co.za",
                "password": "demo123",
                "first_name": "Michael",
                "last_name": "Johnson",
                "company": {
                    "company_name": "DataFlow Analytics",
                    "company_industry": "Data Science & Analytics",
                    "company_size": "51-100 employees",
                    "company_location": "Durban, KwaZulu-Natal",
                    "company_description": "Data science company helping businesses make data-driven decisions through advanced analytics, machine learning, and business intelligence solutions.",
                    "company_website": "https://dataflow.co.za",
                    "company_linkedin": "https://linkedin.com/company/dataflow-analytics"
                }
            },
            {
                "email": "hr@creativestudio.co.za",
                "password": "demo123",
                "first_name": "Sarah",
                "last_name": "Thompson",
                "company": {
                    "company_name": "Creative Studio SA",
                    "company_industry": "Design & Creative",
                    "company_size": "11-50 employees",
                    "company_location": "Stellenbosch, Western Cape",
                    "company_description": "Award-winning creative studio specializing in brand identity, graphic design, and digital experiences. We bring brands to life through innovative design solutions.",
                    "company_website": "https://creativestudio.co.za",
                    "company_linkedin": "https://linkedin.com/company/creative-studio-sa"
                }
            },
            {
                "email": "talent@healthtech.co.za",
                "password": "demo123",
                "first_name": "Dr. James",
                "last_name": "Smith",
                "company": {
                    "company_name": "HealthTech Innovations",
                    "company_industry": "Healthcare Technology",
                    "company_size": "101-200 employees",
                    "company_location": "Pretoria, Gauteng",
                    "company_description": "Healthcare technology company developing innovative solutions for medical professionals and patients. Our platforms improve healthcare delivery and patient outcomes.",
                    "company_website": "https://healthtech.co.za",
                    "company_linkedin": "https://linkedin.com/company/healthtech-innovations"
                }
            }
        ]
        
        created_recruiters = []
        
        for recruiter_data in recruiters_data:
            # Check if recruiter already exists
            existing = await self.db.users.find_one({"email": recruiter_data["email"]})
            if existing:
                print(f"⚠️  Recruiter {recruiter_data['email']} already exists")
                created_recruiters.append(existing)
                continue
            
            # Hash password
            hashed_password = bcrypt.hashpw(
                recruiter_data["password"].encode('utf-8'),
                bcrypt.gensalt()
            )
            
            # Calculate completion score
            company = recruiter_data["company"]
            completion_score = 85  # Base score for complete company info
            
            recruiter = {
                "id": str(uuid.uuid4()),
                "email": recruiter_data["email"],
                "password_hash": hashed_password.decode('utf-8'),
                "first_name": recruiter_data["first_name"],
                "last_name": recruiter_data["last_name"],
                "role": "recruiter",
                "is_verified": True,
                "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 180)),
                "updated_at": datetime.utcnow(),
                "company_profile": company,
                "recruiter_progress": {
                    "company_name": True,
                    "company_description": True,
                    "company_info": True,
                    "first_job_posted": False,
                    "total_points": completion_score
                }
            }
            
            result = await self.db.users.insert_one(recruiter)
            if result.inserted_id:
                print(f"✅ Created recruiter: {recruiter_data['email']} - {company['company_name']}")
                created_recruiters.append(recruiter)
            else:
                print(f"❌ Failed to create recruiter: {recruiter_data['email']}")
        
        return created_recruiters
    
    async def create_job_seeker_users(self):
        """Create diverse job seeker profiles"""
        print("\n👤 Creating Job Seeker Users...")
        
        # South African names and diverse backgrounds
        job_seekers_data = [
            {
                "email": "thabo.mthembu@gmail.com",
                "first_name": "Thabo",
                "last_name": "Mthembu",
                "location": "Johannesburg, Gauteng",
                "desired_job_title": "Software Developer",
                "skills": ["JavaScript", "React", "Node.js", "Python", "Git", "MongoDB"],
                "experience_level": "mid",
                "education": "BSc Computer Science - University of the Witwatersrand"
            },
            {
                "email": "nomsa.dlamini@gmail.com",
                "first_name": "Nomsa",
                "last_name": "Dlamini",
                "location": "Cape Town, Western Cape",
                "desired_job_title": "UX/UI Designer",
                "skills": ["Figma", "Adobe XD", "Sketch", "User Research", "Prototyping", "HTML", "CSS"],
                "experience_level": "senior",
                "education": "BTech Graphic Design - Cape Peninsula University of Technology"
            },
            {
                "email": "pieter.vandermerwe@gmail.com",
                "first_name": "Pieter",
                "last_name": "van der Merwe",
                "location": "Pretoria, Gauteng",
                "desired_job_title": "Data Analyst",
                "skills": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics", "R"],
                "experience_level": "mid",
                "education": "BCom Statistics - University of Pretoria"
            },
            {
                "email": "zanele.khumalo@gmail.com",
                "first_name": "Zanele",
                "last_name": "Khumalo",
                "location": "Durban, KwaZulu-Natal",
                "desired_job_title": "Digital Marketing Manager",
                "skills": ["Digital Marketing", "SEO", "SEM", "Google Ads", "Social Media", "Analytics"],
                "experience_level": "senior",
                "education": "BCom Marketing - University of KwaZulu-Natal"
            },
            {
                "email": "johan.steyn@gmail.com",
                "first_name": "Johan",
                "last_name": "Steyn",
                "location": "Stellenbosch, Western Cape",
                "desired_job_title": "DevOps Engineer",
                "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform", "Linux", "Python"],
                "experience_level": "senior",
                "education": "BEng Computer Engineering - Stellenbosch University"
            },
            {
                "email": "lerato.molefe@gmail.com",
                "first_name": "Lerato",
                "last_name": "Molefe",
                "location": "Sandton, Gauteng",
                "desired_job_title": "Product Manager",
                "skills": ["Product Strategy", "Agile", "Scrum", "Analytics", "User Stories", "Roadmapping"],
                "experience_level": "senior",
                "education": "MBA - University of the Witwatersrand"
            },
            {
                "email": "michelle.adams@gmail.com",
                "first_name": "Michelle",
                "last_name": "Adams",
                "location": "Cape Town, Western Cape",
                "desired_job_title": "HR Manager",
                "skills": ["HR Management", "Recruitment", "Performance Management", "Training", "HRIS"],
                "experience_level": "senior",
                "education": "BA Psychology - University of Cape Town"
            },
            {
                "email": "sipho.radebe@gmail.com",
                "first_name": "Sipho",
                "last_name": "Radebe",
                "location": "Johannesburg, Gauteng",
                "desired_job_title": "Backend Developer",
                "skills": ["Java", "Spring Boot", "PostgreSQL", "Docker", "Microservices", "REST APIs"],
                "experience_level": "mid",
                "education": "BSc Computer Science - University of Johannesburg"
            },
            {
                "email": "tshepo.motaung@gmail.com",
                "first_name": "Tshepo",
                "last_name": "Motaung",
                "location": "Johannesburg, Gauteng",
                "desired_job_title": "Data Scientist",
                "skills": ["Python", "Machine Learning", "TensorFlow", "Pandas", "NumPy", "Jupyter"],
                "experience_level": "senior",
                "education": "MSc Data Science - University of the Witwatersrand"
            },
            {
                "email": "sarah.johnson@gmail.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "location": "Cape Town, Western Cape",
                "desired_job_title": "Junior Developer",
                "skills": ["HTML", "CSS", "JavaScript", "React", "Git"],
                "experience_level": "entry",
                "education": "BSc Computer Science - University of Cape Town"
            }
        ]
        
        created_job_seekers = []
        
        for seeker_data in job_seekers_data:
            # Check if user already exists
            existing = await self.db.users.find_one({"email": seeker_data["email"]})
            if existing:
                print(f"⚠️  Job seeker {seeker_data['email']} already exists")
                created_job_seekers.append(existing)
                continue
            
            # Hash password
            password = "demo123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Generate experience based on level
            experience = []
            if seeker_data["experience_level"] != "entry":
                years = {"mid": 3, "senior": 6, "expert": 10}[seeker_data["experience_level"]]
                experience = [{
                    "job_title": seeker_data["desired_job_title"],
                    "company": f"Previous Company {random.randint(1, 5)}",
                    "start_date": f"{2024 - years}-01-01",
                    "end_date": "2024-06-30",
                    "description": f"Worked as {seeker_data['desired_job_title']} with focus on {', '.join(seeker_data['skills'][:3])}"
                }]
            
            # Calculate profile completion
            completion_score = random.randint(70, 95)
            
            job_seeker = {
                "id": str(uuid.uuid4()),
                "email": seeker_data["email"],
                "password_hash": hashed_password.decode('utf-8'),
                "first_name": seeker_data["first_name"],
                "last_name": seeker_data["last_name"],
                "role": "job_seeker",
                "is_verified": True,
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                "updated_at": datetime.utcnow(),
                "phone": f"+2771{random.randint(1000000, 9999999)}",
                "profile": {
                    "location": seeker_data["location"],
                    "desired_job_title": seeker_data["desired_job_title"],
                    "skills": seeker_data["skills"],
                    "experience": experience,
                    "education": [{
                        "institution": seeker_data["education"].split(" - ")[1],
                        "degree": seeker_data["education"].split(" - ")[0],
                        "start_date": "2020-01-01",
                        "end_date": "2023-12-01"
                    }],
                    "profile_completeness": completion_score
                },
                "job_seeker_progress": {
                    "profile_completion": completion_score > 80,
                    "skills_added": True,
                    "experience_added": len(experience) > 0,
                    "education_added": True,
                    "first_application": False,
                    "total_points": completion_score
                }
            }
            
            result = await self.db.users.insert_one(job_seeker)
            if result.inserted_id:
                print(f"✅ Created job seeker: {seeker_data['email']} - {seeker_data['desired_job_title']}")
                created_job_seekers.append(job_seeker)
            else:
                print(f"❌ Failed to create job seeker: {seeker_data['email']}")
        
        return created_job_seekers
    
    async def create_realistic_jobs(self, recruiters):
        """Create realistic job postings from recruiter companies"""
        print("\n💼 Creating Realistic Job Postings...")
        
        if not recruiters:
            print("❌ No recruiters available to create jobs")
            return []
        
        # Job templates based on company types
        job_templates = {
            "TechCorp Solutions": [
                {
                    "title": "Senior React Developer",
                    "job_type": "Full-time",
                    "work_type": "Hybrid",
                    "salary": "R45,000 - R65,000",
                    "industry": "Technology",
                    "description": "Join our dynamic team as a Senior React Developer and contribute to cutting-edge web applications. We're looking for passionate developers who thrive in collaborative environments.",
                    "requirements": [
                        "5+ years React development experience",
                        "Strong JavaScript and TypeScript skills",
                        "Experience with Redux and modern React patterns",
                        "Knowledge of REST APIs and GraphQL",
                        "Agile development experience"
                    ]
                },
                {
                    "title": "Python Backend Developer",
                    "job_type": "Full-time",
                    "work_type": "Remote",
                    "salary": "R40,000 - R60,000",
                    "industry": "Technology",
                    "description": "Seeking an experienced Python developer to build scalable backend systems and APIs for our enterprise clients.",
                    "requirements": [
                        "3+ years Python development experience",
                        "Django or FastAPI framework experience",
                        "PostgreSQL and database design",
                        "Docker and containerization",
                        "AWS or cloud platform experience"
                    ]
                }
            ],
            "Innovate Digital Agency": [
                {
                    "title": "UX/UI Designer",
                    "job_type": "Full-time",
                    "work_type": "Hybrid",
                    "salary": "R35,000 - R50,000",
                    "industry": "Design",
                    "description": "Creative UX/UI Designer to join our award-winning team and create exceptional digital experiences for leading brands.",
                    "requirements": [
                        "3+ years UX/UI design experience",
                        "Proficiency in Figma and Adobe Creative Suite",
                        "Strong portfolio of web and mobile designs",
                        "User research and usability testing experience",
                        "Understanding of frontend development"
                    ]
                },
                {
                    "title": "Digital Marketing Specialist",
                    "job_type": "Full-time",
                    "work_type": "On-site",
                    "salary": "R25,000 - R40,000",
                    "industry": "Marketing",
                    "description": "Drive digital marketing campaigns for our diverse client portfolio and help brands achieve their online growth objectives.",
                    "requirements": [
                        "2+ years digital marketing experience",
                        "Google Ads and Facebook Ads certification",
                        "SEO and content marketing knowledge",
                        "Analytics and reporting skills",
                        "Creative and strategic thinking"
                    ]
                }
            ],
            "FinTech Solutions SA": [
                {
                    "title": "DevOps Engineer",
                    "job_type": "Full-time",
                    "work_type": "Remote",
                    "salary": "R50,000 - R75,000",
                    "industry": "Financial Technology",
                    "description": "Lead our DevOps initiatives and help build secure, scalable infrastructure for our fintech platform serving millions of users.",
                    "requirements": [
                        "4+ years DevOps experience",
                        "Kubernetes and Docker expertise",
                        "AWS/Azure cloud platform experience",
                        "CI/CD pipeline management",
                        "Security and compliance knowledge"
                    ]
                }
            ],
            "DataFlow Analytics": [
                {
                    "title": "Data Scientist",
                    "job_type": "Full-time",
                    "work_type": "Hybrid",
                    "salary": "R45,000 - R70,000",
                    "industry": "Data Science",
                    "description": "Join our data science team to build predictive models and analytics solutions that drive business insights for our clients.",
                    "requirements": [
                        "MSc in Data Science or related field",
                        "3+ years Python and R experience",
                        "Machine learning and statistical modeling",
                        "SQL and database management",
                        "Data visualization tools (Tableau, Power BI)"
                    ]
                }
            ]
        }
        
        created_jobs = []
        current_date = datetime.utcnow()
        
        for recruiter in recruiters:
            company_name = recruiter.get("company_profile", {}).get("company_name", "Unknown Company")
            
            if company_name in job_templates:
                jobs_for_company = job_templates[company_name]
                
                for job_template in jobs_for_company:
                    # Generate expiry date (2-4 weeks from now)
                    days_to_expiry = random.randint(14, 30)
                    expiry_date = current_date + timedelta(days=days_to_expiry)
                    
                    # Generate posting date (1-7 days ago)
                    days_ago = random.randint(1, 7)
                    posted_date = current_date - timedelta(days=days_ago)
                    
                    job = {
                        "id": str(uuid.uuid4()),
                        "title": job_template["title"],
                        "company_id": recruiter["id"],
                        "company_name": company_name,
                        "logo_url": recruiter.get("company_profile", {}).get("company_logo_url"),
                        "location": recruiter.get("company_profile", {}).get("company_location", "South Africa"),
                        "job_type": job_template["job_type"],
                        "work_type": job_template["work_type"],
                        "industry": job_template["industry"],
                        "salary": job_template["salary"],
                        "description": job_template["description"],
                        "requirements": job_template["requirements"],
                        "posted_by": recruiter["id"],
                        "posted_date": posted_date,
                        "expiry_date": expiry_date,
                        "is_active": True,
                        "featured": random.random() < 0.2,  # 20% chance of being featured
                        "created_at": posted_date,
                        "updated_at": posted_date
                    }
                    
                    result = await self.db.jobs.insert_one(job)
                    if result.inserted_id:
                        print(f"✅ Created job: {job_template['title']} at {company_name}")
                        created_jobs.append(job)
                        
                        # Update recruiter's first_job_posted status
                        await self.db.users.update_one(
                            {"id": recruiter["id"]},
                            {"$set": {
                                "recruiter_progress.first_job_posted": True,
                                "recruiter_progress.total_points": 100
                            }}
                        )
                    else:
                        print(f"❌ Failed to create job: {job_template['title']}")
        
        return created_jobs
    
    async def create_sample_packages(self):
        """Create sample packages for testing"""
        print("\n📦 Creating Sample Packages...")
        
        packages = [
            {
                "id": str(uuid.uuid4()),
                "package_type": "two_listings",
                "name": "Two Job Listings",
                "description": "Post 2 job listings with 30-day expiry",
                "price": 2800.00,
                "currency": "ZAR",
                "job_listings_included": 2,
                "cv_searches_included": 0,
                "duration_days": 30,
                "job_expiry_days": 30,
                "is_active": True,
                "features": ["2 job postings", "30-day job expiry", "Basic analytics"]
            },
            {
                "id": str(uuid.uuid4()),
                "package_type": "five_listings",
                "name": "Five Job Listings",
                "description": "Post 5 job listings with 30-day expiry",
                "price": 4150.00,
                "currency": "ZAR",
                "job_listings_included": 5,
                "cv_searches_included": 0,
                "duration_days": 30,
                "job_expiry_days": 30,
                "is_active": True,
                "features": ["5 job postings", "30-day job expiry", "Advanced analytics", "Priority support"]
            },
            {
                "id": str(uuid.uuid4()),
                "package_type": "unlimited_listings",
                "name": "Unlimited Job Listings",
                "description": "Unlimited job listings for one month",
                "price": 3899.00,
                "currency": "ZAR",
                "job_listings_included": None,
                "cv_searches_included": 0,
                "duration_days": 30,
                "job_expiry_days": 35,
                "is_subscription": True,
                "is_active": True,
                "features": ["Unlimited job postings", "35-day job expiry", "Premium analytics", "Priority support", "Featured job highlighting"]
            },
            {
                "id": str(uuid.uuid4()),
                "package_type": "cv_search_10",
                "name": "10 CV Searches",
                "description": "Search through candidate CVs with 10 search credits",
                "price": 699.00,
                "currency": "ZAR",
                "job_listings_included": 0,
                "cv_searches_included": 10,
                "duration_days": 30,
                "job_expiry_days": 35,
                "is_active": True,
                "features": ["10 CV searches", "Advanced filtering", "Contact candidates"]
            },
            {
                "id": str(uuid.uuid4()),
                "package_type": "cv_search_unlimited",
                "name": "Unlimited CV Searches",
                "description": "Unlimited CV searches for one month",
                "price": 2899.00,
                "currency": "ZAR",
                "job_listings_included": 0,
                "cv_searches_included": None,
                "duration_days": 30,
                "job_expiry_days": 35,
                "is_subscription": True,
                "is_active": True,
                "features": ["Unlimited CV searches", "Advanced filtering", "Contact candidates", "Priority support"]
            }
        ]
        
        created_packages = []
        
        for package in packages:
            # Check if package already exists
            existing = await self.db.packages.find_one({"package_type": package["package_type"]})
            if existing:
                print(f"⚠️  Package {package['package_type']} already exists")
                continue
            
            result = await self.db.packages.insert_one(package)
            if result.inserted_id:
                print(f"✅ Created package: {package['name']}")
                created_packages.append(package)
            else:
                print(f"❌ Failed to create package: {package['name']}")
        
        return created_packages

async def main():
    """Main function to populate production database"""
    print("🚀 Job Rocket Production Database Population")
    print("=" * 60)
    
    # Allow custom MongoDB URL for production
    mongo_url = input("Enter MongoDB URL (press Enter for default): ").strip()
    if not mongo_url:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    
    populator = ProductionDataPopulator(mongo_url)
    
    try:
        # Connect to database
        connected = await populator.connect()
        if not connected:
            return
        
        print(f"\n🎯 Starting database population for jobrocket.co.za...")
        
        # Create admin user
        admin = await populator.create_admin_user()
        
        # Create recruiter users
        recruiters = await populator.create_recruiter_users()
        
        # Create job seeker users
        job_seekers = await populator.create_job_seeker_users()
        
        # Create realistic jobs
        jobs = await populator.create_realistic_jobs(recruiters)
        
        # Create sample packages
        packages = await populator.create_sample_packages()
        
        # Summary
        print(f"\n🎉 Database Population Complete!")
        print(f"=" * 60)
        print(f"✅ Admin user: 1 (admin@jobrocket.co.za)")
        print(f"✅ Recruiters: {len(recruiters)}")
        print(f"✅ Job seekers: {len(job_seekers)}")
        print(f"✅ Jobs: {len(jobs)}")
        print(f"✅ Packages: {len(packages)}")
        
        print(f"\n🔑 Login Credentials:")
        print(f"   Admin: admin@jobrocket.co.za / admin123")
        print(f"   Recruiters: hr@techcorp.co.za / demo123 (and others)")
        print(f"   Job Seekers: thabo.mthembu@gmail.com / demo123 (and others)")
        
        print(f"\n🌐 Your site should now be ready at jobrocket.co.za!")
        
    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
    finally:
        await populator.close()

if __name__ == "__main__":
    asyncio.run(main())