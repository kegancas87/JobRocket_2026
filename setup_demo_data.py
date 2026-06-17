#!/usr/bin/env python3
"""
Setup comprehensive demo data for Job Rocket platform
Creates users, companies, jobs, and discount codes for testing
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta
import random

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def setup_demo_data():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'jobrocket')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🚀 Setting up Job Rocket demo data...")
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("Clearing existing demo data...")
    await db.users.delete_many({"email": {"$regex": "@demo.com|@example.com|admin@jobrocket.com"}})
    await db.companies.delete_many({"name": {"$regex": "Demo|Test|Example"}})
    await db.jobs.delete_many({"title": {"$regex": "Demo|Test|Sample"}})
    await db.discount_codes.delete_many({"code": {"$in": ["DEMO20", "WELCOME15", "NEWUSER10", "SAVE25"]}})
    
    # 1. CREATE ADMIN USER
    print("👑 Creating admin user...")
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": "admin@jobrocket.com",
        "password_hash": pwd_context.hash("admin123"),
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    await db.users.insert_one(admin_user)
    print("✅ Admin user created: admin@jobrocket.com / admin123")
    
    # 2. CREATE JOB SEEKERS
    print("👤 Creating job seeker users...")
    
    job_seekers = [
        {
            "email": "sarah.beginner@demo.com",
            "password": "demo123",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "location": "Cape Town, South Africa",
            "phone": "+27123456789",
            "about_me": "Recent graduate looking for my first opportunity in tech.",
            "skills": ["HTML", "CSS", "JavaScript"],
            "work_history": [],
            "education": [
                {
                    "institution": "University of Cape Town",
                    "degree": "Bachelor of Computer Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2020-01-01",
                    "end_date": "2023-12-01",
                    "grade": "Distinction"
                }
            ],
            "achievements": [],
            "progress_points": 25  # Beginner level
        },
        {
            "email": "alex.intermediate@demo.com", 
            "password": "demo123",
            "first_name": "Alex",
            "last_name": "Rodriguez",
            "location": "Johannesburg, South Africa",
            "phone": "+27123456790",
            "about_me": "Mid-level developer with 2 years experience in full-stack development. Passionate about React and Node.js.",
            "skills": ["React", "Node.js", "Python", "MongoDB", "Express", "JavaScript", "TypeScript"],
            "work_history": [
                {
                    "company": "StartupCo",
                    "position": "Junior Developer",
                    "start_date": "2022-01-01",
                    "end_date": "2024-01-01",
                    "description": "Developed web applications using React and Node.js"
                }
            ],
            "education": [
                {
                    "institution": "Wits University",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Information Technology",
                    "start_date": "2018-01-01",
                    "end_date": "2021-12-01",
                    "grade": "Cum Laude"
                }
            ],
            "achievements": ["Employee of the Month", "Hackathon Winner"],
            "progress_points": 65  # Intermediate level
        },
        {
            "email": "mike.senior@demo.com",
            "password": "demo123", 
            "first_name": "Mike",
            "last_name": "Thompson",
            "location": "Durban, South Africa",
            "phone": "+27123456791",
            "about_me": "Senior full-stack developer with 5+ years experience. Expert in React, Python, and cloud technologies. Looking for leadership opportunities.",
            "skills": ["React", "Python", "Django", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redux", "TypeScript", "GraphQL"],
            "work_history": [
                {
                    "company": "TechCorp",
                    "position": "Senior Developer",
                    "start_date": "2020-01-01",
                    "end_date": "2024-01-01", 
                    "description": "Led development team of 5 developers, architected scalable web applications"
                },
                {
                    "company": "DevStudio",
                    "position": "Full Stack Developer", 
                    "start_date": "2018-01-01",
                    "end_date": "2019-12-01",
                    "description": "Built responsive web applications using modern frameworks"
                }
            ],
            "education": [
                {
                    "institution": "Stellenbosch University",
                    "degree": "Bachelor of Engineering",
                    "field_of_study": "Computer Engineering",
                    "start_date": "2014-01-01",
                    "end_date": "2017-12-01",
                    "grade": "First Class Honours"
                }
            ],
            "achievements": ["AWS Certified", "Scrum Master Certified", "Tech Lead of the Year"],
            "progress_points": 100  # Complete profile
        }
    ]
    
    seeker_ids = []
    for seeker_data in job_seekers:
        user_id = str(uuid.uuid4())
        seeker_ids.append(user_id)
        
        user = {
            "id": user_id,
            "email": seeker_data["email"],
            "password_hash": pwd_context.hash(seeker_data["password"]),
            "first_name": seeker_data["first_name"],
            "last_name": seeker_data["last_name"],
            "role": "job_seeker",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "location": seeker_data["location"],
            "phone": seeker_data["phone"],
            "about_me": seeker_data["about_me"],
            "skills": seeker_data["skills"],
            "work_history": seeker_data["work_history"],
            "education": seeker_data["education"],
            "achievements": seeker_data["achievements"],
            "job_seeker_progress": {
                "total_points": seeker_data["progress_points"],
                "profile_picture": seeker_data["progress_points"] >= 100,
                "about_me": True,
                "work_history": len(seeker_data["work_history"]) > 0,
                "skills": len(seeker_data["skills"]) >= 5,
                "education": len(seeker_data["education"]) > 0,
                "achievements": len(seeker_data["achievements"]) > 0,
                "intro_video": seeker_data["progress_points"] >= 100,
                "applications_submitted": 0,
                "email_alerts": False
            }
        }
        await db.users.insert_one(user)
        print(f"✅ Job seeker created: {seeker_data['email']} / demo123 ({seeker_data['progress_points']} points)")
    
    # 3. CREATE COMPANIES
    print("🏢 Creating demo companies...")
    
    companies = [
        {
            "name": "TechCorp Solutions",
            "description": "Leading technology consulting firm specializing in digital transformation and enterprise solutions.",
            "industry": "Technology Consulting",
            "website": "https://techcorp-demo.com",
            "linkedin": "https://linkedin.com/company/techcorp-demo",
            "employee_count": "50-200",
            "location": "Cape Town, South Africa",
            "logo_url": "https://via.placeholder.com/200x200/4F46E5/FFFFFF?text=TC"
        },
        {
            "name": "Innovate Digital Agency",
            "description": "Creative digital agency focused on cutting-edge web development and digital marketing solutions.",
            "industry": "Digital Marketing & Development", 
            "website": "https://innovate-demo.com",
            "linkedin": "https://linkedin.com/company/innovate-demo",
            "employee_count": "10-50",
            "location": "Johannesburg, South Africa",
            "logo_url": "https://via.placeholder.com/200x200/10B981/FFFFFF?text=ID"
        },
        {
            "name": "DataFlow Analytics",
            "description": "Data science and analytics company helping businesses make data-driven decisions.",
            "industry": "Data Science & Analytics",
            "website": "https://dataflow-demo.com", 
            "linkedin": "https://linkedin.com/company/dataflow-demo",
            "employee_count": "20-100",
            "location": "Durban, South Africa",
            "logo_url": "https://via.placeholder.com/200x200/F59E0B/FFFFFF?text=DF"
        }
    ]
    
    company_ids = []
    for company_data in companies:
        company_id = str(uuid.uuid4())
        company_ids.append(company_id)
        
        company = {
            "id": company_id,
            **company_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        await db.companies.insert_one(company)
        print(f"✅ Company created: {company_data['name']}")
    
    # 4. CREATE RECRUITERS
    print("👔 Creating recruiter users...")
    
    recruiters = [
        {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123",
            "first_name": "Lisa", 
            "last_name": "Martinez",
            "company_id": company_ids[0],  # TechCorp Solutions
            "job_title": "Senior Talent Acquisition Specialist",
            "phone": "+27123456792"
        },
        {
            "email": "david.wilson@innovate.demo",
            "password": "demo123",
            "first_name": "David",
            "last_name": "Wilson", 
            "company_id": company_ids[1],  # Innovate Digital Agency
            "job_title": "Head of Human Resources",
            "phone": "+27123456793"
        },
        {
            "email": "emma.davis@dataflow.demo",
            "password": "demo123",
            "first_name": "Emma",
            "last_name": "Davis",
            "company_id": company_ids[2],  # DataFlow Analytics  
            "job_title": "Talent Acquisition Manager",
            "phone": "+27123456794"
        }
    ]
    
    recruiter_ids = []
    for recruiter_data in recruiters:
        user_id = str(uuid.uuid4())
        recruiter_ids.append(user_id)
        
        user = {
            "id": user_id,
            "email": recruiter_data["email"],
            "password_hash": pwd_context.hash(recruiter_data["password"]),
            "first_name": recruiter_data["first_name"],
            "last_name": recruiter_data["last_name"],
            "role": "recruiter",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "phone": recruiter_data["phone"],
            "job_title": recruiter_data["job_title"],
            "company_id": recruiter_data["company_id"],
            "recruiter_progress": {
                "total_points": 100,  # Complete profile
                "company_logo": True,
                "cover_image": True,
                "about_company": True,
                "employee_count": True,
                "website_linkedin": True
            }
        }
        await db.users.insert_one(user)
        print(f"✅ Recruiter created: {recruiter_data['email']} / demo123")
    
    # 5. CREATE DEMO JOBS
    print("💼 Creating demo jobs...")
    
    job_templates = [
        {
            "title": "Senior React Developer",
            "location": "Cape Town, South Africa",
            "salary_min": 450000,
            "salary_max": 650000,
            "job_type": "full_time",
            "work_type": "hybrid",
            "industry": "Technology",
            "experience_level": "senior",
            "description": """We are looking for a Senior React Developer to join our dynamic team at TechCorp Solutions. 
            
**Responsibilities:**
- Develop and maintain high-quality React applications
- Collaborate with cross-functional teams to deliver exceptional user experiences
- Mentor junior developers and contribute to technical decisions
- Implement best practices for code quality and performance

**Requirements:**
- 5+ years of React development experience
- Strong knowledge of JavaScript, TypeScript, and modern web technologies
- Experience with state management (Redux, Context API)
- Familiarity with testing frameworks (Jest, React Testing Library)
- Excellent problem-solving and communication skills

**Benefits:**
- Competitive salary and performance bonuses
- Flexible working hours and remote work options
- Professional development opportunities
- Health and wellness benefits""",
            "qualifications": "Bachelor's degree in Computer Science or related field, 5+ years React experience",
            "company_id": company_ids[0],
            "posted_by": recruiter_ids[0]
        },
        {
            "title": "UX/UI Designer", 
            "location": "Johannesburg, South Africa",
            "salary_min": 300000,
            "salary_max": 450000,
            "job_type": "full_time",
            "work_type": "hybrid",
            "industry": "Design",
            "experience_level": "mid_level",
            "description": """Join Innovate Digital Agency as a UX/UI Designer and help create amazing digital experiences.

**What You'll Do:**
- Design user-centered digital products and interfaces
- Conduct user research and usability testing  
- Create wireframes, prototypes, and high-fidelity designs
- Collaborate with developers to ensure design implementation
- Maintain and evolve design systems

**What We're Looking For:**
- 3+ years of UX/UI design experience
- Proficiency in Figma, Sketch, or similar design tools
- Strong portfolio showcasing design thinking and process
- Understanding of web technologies and responsive design
- Excellent communication and collaboration skills

**Perks:**
- Creative and collaborative work environment
- Latest design tools and equipment
- Professional conference attendance
- Flexible PTO policy""",
            "qualifications": "Design degree preferred, 3+ years UX/UI experience, strong portfolio",
            "company_id": company_ids[1],
            "posted_by": recruiter_ids[1]
        },
        {
            "title": "Data Scientist",
            "location": "Durban, South Africa", 
            "salary_min": 400000,
            "salary_max": 600000,
            "job_type": "full_time",
            "work_type": "on_site",
            "industry": "Data Science",
            "experience_level": "mid_level",
            "description": """DataFlow Analytics is seeking a talented Data Scientist to join our analytics team.

**Role Overview:**
- Analyze complex datasets to extract actionable business insights
- Develop and deploy machine learning models
- Create data visualizations and reports for stakeholders
- Collaborate with business teams to solve real-world problems

**Technical Requirements:**
- Strong experience with Python, R, or similar languages
- Knowledge of machine learning frameworks (scikit-learn, TensorFlow, PyTorch)
- Experience with data visualization tools (Tableau, Power BI, matplotlib)
- SQL and database management skills
- Statistical analysis and hypothesis testing experience

**Ideal Candidate:**
- Master's degree in Data Science, Statistics, or related field
- 2-4 years of industry experience
- Strong analytical and problem-solving mindset
- Excellent communication skills to present findings

**What We Offer:**
- Cutting-edge data science projects
- Access to large-scale datasets
- Professional development budget
- Collaborative team environment""",
            "qualifications": "Master's in Data Science or related field, 2-4 years experience, Python/R proficiency",
            "company_id": company_ids[2],
            "posted_by": recruiter_ids[2]
        },
        {
            "title": "Junior Frontend Developer",
            "location": "Cape Town, South Africa",
            "salary_min": 250000,
            "salary_max": 350000, 
            "job_type": "full_time",
            "work_type": "hybrid",
            "industry": "Technology",
            "experience_level": "entry_level",
            "description": """Perfect opportunity for a junior developer to grow their career at TechCorp Solutions.

**What You'll Learn:**
- Modern frontend development with React and TypeScript
- Best practices for responsive web design
- Version control with Git and collaborative development
- Testing and debugging techniques
- Agile development methodologies

**Requirements:**
- 0-2 years of professional experience
- Solid understanding of HTML, CSS, and JavaScript
- Some experience with React (personal projects or bootcamp)
- Enthusiasm for learning and growth
- Good communication and teamwork skills

**We Provide:**
- Comprehensive mentorship program
- Structured learning path and career development
- Exposure to enterprise-level projects
- Supportive team environment
- Competitive entry-level compensation

This is an excellent opportunity for recent graduates or career changers to establish themselves in tech.""",
            "qualifications": "Basic web development knowledge, some React experience, willingness to learn",
            "company_id": company_ids[0],
            "posted_by": recruiter_ids[0]
        },
        {
            "title": "Product Manager",
            "location": "Johannesburg, South Africa",
            "salary_min": 500000,
            "salary_max": 700000,
            "job_type": "full_time", 
            "work_type": "hybrid",
            "industry": "Product Management",
            "experience_level": "senior",
            "description": """Lead product strategy and development at Innovate Digital Agency.

**Key Responsibilities:**
- Define product vision, strategy, and roadmap
- Conduct market research and competitive analysis  
- Work closely with engineering, design, and marketing teams
- Gather and prioritize product requirements
- Track and analyze product performance metrics

**Qualifications:**
- 4+ years of product management experience
- Strong analytical and strategic thinking skills
- Experience with agile development methodologies
- Excellent stakeholder management abilities
- Background in digital products or tech industry

**Leadership Opportunity:**
- Build and lead product initiatives
- Shape company product direction
- Mentor junior team members
- Direct impact on business growth

**Benefits Package:**
- Equity participation
- Flexible work arrangements
- Professional development budget
- Health and wellness programs""",
            "qualifications": "4+ years product management experience, strong analytical skills, tech industry background",
            "company_id": company_ids[1],
            "posted_by": recruiter_ids[1]
        }
    ]
    
    job_ids = []
    for i, job_data in enumerate(job_templates):
        job_id = str(uuid.uuid4())
        job_ids.append(job_id)
        
        # Vary posting dates
        posted_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        expiry_date = posted_date + timedelta(days=35)
        
        job = {
            "id": job_id,
            **job_data,
            "external_application_link": None,  # Use easy apply
            "posted_date": posted_date,
            "expiry_date": expiry_date,
            "is_active": True,
            "application_count": random.randint(5, 25),
            "view_count": random.randint(50, 200)
        }
        await db.jobs.insert_one(job)
        print(f"✅ Job created: {job_data['title']} at {companies[job_data['company_id'] == company_ids[0] and 0 or job_data['company_id'] == company_ids[1] and 1 or 2]['name']}")
    
    # 6. CREATE SAMPLE APPLICATIONS
    print("📝 Creating sample job applications...")
    
    # Create some applications from job seekers to jobs
    applications = [
        {
            "job_id": job_ids[0],  # Senior React Developer
            "applicant_id": seeker_ids[2],  # Mike (senior)
            "status": "reviewed"
        },
        {
            "job_id": job_ids[0],  # Senior React Developer  
            "applicant_id": seeker_ids[1],  # Alex (intermediate)
            "status": "pending"
        },
        {
            "job_id": job_ids[3],  # Junior Frontend Developer
            "applicant_id": seeker_ids[0],  # Sarah (beginner)
            "status": "pending"
        },
        {
            "job_id": job_ids[3],  # Junior Frontend Developer
            "applicant_id": seeker_ids[1],  # Alex (intermediate) 
            "status": "shortlisted"
        },
        {
            "job_id": job_ids[2],  # Data Scientist
            "applicant_id": seeker_ids[2],  # Mike (senior)
            "status": "interviewed"
        }
    ]
    
    for app_data in applications:
        application_id = str(uuid.uuid4())
        
        # Get applicant details for snapshot
        applicant = next(user for user in job_seekers if seeker_ids[job_seekers.index(user)] == app_data["applicant_id"])
        
        application = {
            "id": application_id,
            "job_id": app_data["job_id"],
            "applicant_id": app_data["applicant_id"],
            "status": app_data["status"],
            "applied_date": datetime.utcnow() - timedelta(days=random.randint(1, 14)),
            "cover_letter": f"I am very interested in this position and believe my skills in {', '.join(applicant['skills'][:3])} make me a great fit.",
            "applicant_snapshot": {
                "first_name": applicant["first_name"],
                "last_name": applicant["last_name"],
                "email": applicant["email"],
                "location": applicant["location"],
                "phone": applicant["phone"],
                "skills": applicant["skills"],
                "profile_picture_url": None,
                "cv_url": f"https://example.com/cv/{applicant['first_name'].lower()}-{applicant['last_name'].lower()}.pdf"
            }
        }
        await db.job_applications.insert_one(application)
    
    print(f"✅ Created {len(applications)} sample applications")
    
    # 7. CREATE DISCOUNT CODES
    print("🏷️ Creating demo discount codes...")
    
    discount_codes = [
        {
            "code": "WELCOME20",
            "name": "Welcome 20% Discount",
            "description": "20% off for new customers",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "minimum_amount": 1000.0,
            "maximum_discount": 1000.0,
            "usage_limit": 100,
            "user_limit": 1,
            "valid_until": datetime.utcnow() + timedelta(days=90),
            "status": "active"
        },
        {
            "code": "NEWUSER15",
            "name": "New User 15% Off",
            "description": "Special discount for first-time users",
            "discount_type": "percentage", 
            "discount_value": 15.0,
            "minimum_amount": 500.0,
            "usage_limit": 50,
            "user_limit": 1,
            "valid_until": datetime.utcnow() + timedelta(days=60),
            "status": "active"
        },
        {
            "code": "SAVE500",
            "name": "Save R500",
            "description": "Fixed R500 discount on premium packages",
            "discount_type": "fixed_amount",
            "discount_value": 500.0,
            "minimum_amount": 2000.0,
            "usage_limit": 25,
            "user_limit": 1,
            "valid_until": datetime.utcnow() + timedelta(days=30),
            "status": "active"
        },
        {
            "code": "EXPIRED10", 
            "name": "Expired 10% Off",
            "description": "This code has expired for testing",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "minimum_amount": 100.0,
            "usage_limit": 10,
            "user_limit": 1,
            "valid_until": datetime.utcnow() - timedelta(days=5),  # Expired
            "status": "active"
        }
    ]
    
    for discount_data in discount_codes:
        discount_id = str(uuid.uuid4())
        
        discount = {
            "id": discount_id,
            **discount_data,
            "usage_count": random.randint(0, discount_data.get("usage_limit", 10) // 2),
            "applicable_packages": None,  # Apply to all packages
            "created_by": admin_user["id"],
            "created_date": datetime.utcnow(),
            "valid_from": datetime.utcnow() - timedelta(days=1)
        }
        await db.discount_codes.insert_one(discount)
        print(f"✅ Discount code created: {discount_data['code']} ({discount_data['discount_value']}{'%' if discount_data['discount_type'] == 'percentage' else ' ZAR'} off)")
    
    # 8. CREATE SAMPLE PACKAGES (Initialize if not exists)
    print("📦 Ensuring packages are initialized...")
    
    existing_packages = await db.packages.count_documents({})
    if existing_packages == 0:
        print("No packages found, initializing default packages...")
        
        default_packages = [
            {
                "id": str(uuid.uuid4()),
                "package_type": "two_listings",
                "name": "Two Listings Package",
                "description": "Perfect for small businesses or testing the platform",
                "price": 2800.00,
                "currency": "ZAR",
                "is_subscription": False,
                "subscription_period_days": None,
                "job_listings_included": 2,
                "cv_searches_included": 0,
                "job_expiry_days": 30,
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "package_type": "five_listings",
                "name": "Five Listings Package", 
                "description": "Great value for growing companies",
                "price": 4150.00,
                "currency": "ZAR",
                "is_subscription": False,
                "subscription_period_days": None,
                "job_listings_included": 5,
                "cv_searches_included": 0,
                "job_expiry_days": 30,
                "is_active": True
            },
            {
                "id": str(uuid.uuid4()),
                "package_type": "unlimited_listings",
                "name": "Unlimited Listings Package",
                "description": "Best for enterprises and high-volume recruiters",
                "price": 3899.00,
                "currency": "ZAR", 
                "is_subscription": True,
                "subscription_period_days": 30,
                "job_listings_included": None,  # Unlimited
                "cv_searches_included": 10,
                "job_expiry_days": 35,
                "is_active": True
            }
        ]
        
        for package in default_packages:
            await db.packages.insert_one(package)
        
        print(f"✅ Initialized {len(default_packages)} default packages")
    else:
        print(f"✅ Found {existing_packages} existing packages")
    
    print("\n🎉 Demo data setup complete!")
    print("\n📋 DEMO USERS CREATED:")
    print("\n👑 ADMIN:")
    print("   Email: admin@jobrocket.com")
    print("   Password: admin123")
    
    print("\n👤 JOB SEEKERS:")
    print("   📧 sarah.beginner@demo.com / demo123 (Beginner - 25 points)")
    print("   📧 alex.intermediate@demo.com / demo123 (Intermediate - 65 points)")  
    print("   📧 mike.senior@demo.com / demo123 (Senior - 100 points)")
    
    print("\n👔 RECRUITERS:")
    print("   📧 lisa.martinez@techcorp.demo / demo123 (TechCorp Solutions)")
    print("   📧 david.wilson@innovate.demo / demo123 (Innovate Digital Agency)")
    print("   📧 emma.davis@dataflow.demo / demo123 (DataFlow Analytics)")
    
    print("\n🏢 COMPANIES CREATED:")
    print("   • TechCorp Solutions (Technology Consulting)")
    print("   • Innovate Digital Agency (Digital Marketing & Development)")
    print("   • DataFlow Analytics (Data Science & Analytics)")
    
    print("\n💼 SAMPLE JOBS:")
    print("   • Senior React Developer (TechCorp)")
    print("   • UX/UI Designer (Innovate Digital)")
    print("   • Data Scientist (DataFlow)")
    print("   • Junior Frontend Developer (TechCorp)")
    print("   • Product Manager (Innovate Digital)")
    
    print("\n🏷️ DISCOUNT CODES:")
    print("   • WELCOME20 (20% off, min R1000)")
    print("   • NEWUSER15 (15% off, min R500)")
    print("   • SAVE500 (R500 off, min R2000)")
    print("   • EXPIRED10 (Expired - for testing)")
    
    print("\n📝 SAMPLE DATA:")
    print(f"   • {len(applications)} job applications created")
    print("   • Job posting history and application tracking ready")
    print("   • Discount code usage analytics ready")
    
    print("\n🚀 Ready to test the full Job Rocket platform!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_demo_data())