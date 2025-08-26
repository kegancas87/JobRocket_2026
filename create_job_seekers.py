#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import bcrypt
import random

# Add the current directory to Python path to import server modules
sys.path.append('/app/backend')

async def create_job_seekers():
    """Create 15 diverse job seeker users for CV search testing"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/job_portal')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.job_portal
    
    print("👥 Creating 15 Job Seeker Users for CV Search Testing...")
    print("=" * 60)
    
    # Diverse job seeker profiles
    job_seekers = [
        {
            "first_name": "Thabo",
            "last_name": "Mthembu",
            "email": "thabo.mthembu@testcv.com",
            "password": "demo123",
            "desired_job_title": "Full Stack Developer",
            "location": "Johannesburg",
            "phone": "+27123456001",
            "skills": ["JavaScript", "React", "Node.js", "Python", "MongoDB", "Git"],
            "experience": [
                {
                    "job_title": "Junior Developer",
                    "company": "Tech Solutions JHB",
                    "start_date": "2022-01-15",
                    "end_date": "2024-03-30",
                    "description": "Developed web applications using React and Node.js"
                }
            ],
            "education": [
                {
                    "institution": "University of Witwatersrand",
                    "degree": "BSc Computer Science",
                    "start_date": "2018-01-01",
                    "end_date": "2021-12-01"
                }
            ]
        },
        {
            "first_name": "Nomsa",
            "last_name": "Dlamini",
            "email": "nomsa.dlamini@testcv.com",
            "password": "demo123",
            "desired_job_title": "UX/UI Designer",
            "location": "Cape Town",
            "phone": "+27123456002",
            "skills": ["Figma", "Adobe XD", "Sketch", "Photoshop", "User Research", "Prototyping"],
            "experience": [
                {
                    "job_title": "UI Designer",
                    "company": "Digital Creative Agency",
                    "start_date": "2021-06-01",
                    "end_date": "2024-08-15",
                    "description": "Designed user interfaces for mobile and web applications"
                }
            ],
            "education": [
                {
                    "institution": "Cape Peninsula University of Technology",
                    "degree": "BTech Graphic Design",
                    "start_date": "2017-01-01",
                    "end_date": "2020-12-01"
                }
            ]
        },
        {
            "first_name": "Pieter",
            "last_name": "van der Merwe",
            "email": "pieter.vandermerwe@testcv.com",
            "password": "demo123",
            "desired_job_title": "Data Analyst",
            "location": "Pretoria",
            "phone": "+27123456003",
            "skills": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics"],
            "experience": [
                {
                    "job_title": "Business Analyst",
                    "company": "Financial Services Corp",
                    "start_date": "2020-03-01",
                    "end_date": "2024-06-30",
                    "description": "Analyzed business data and created reports for management decisions"
                }
            ],
            "education": [
                {
                    "institution": "University of Pretoria",
                    "degree": "BCom Statistics",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-01"
                }
            ]
        },
        {
            "first_name": "Zanele",
            "last_name": "Khumalo",
            "email": "zanele.khumalo@testcv.com",
            "password": "demo123",
            "desired_job_title": "Marketing Manager",
            "location": "Durban",
            "phone": "+27123456004",
            "skills": ["Digital Marketing", "SEO", "Google Ads", "Social Media", "Content Strategy", "Analytics"],
            "experience": [
                {
                    "job_title": "Marketing Coordinator",
                    "company": "FMCG Company KZN",
                    "start_date": "2019-07-01",
                    "end_date": "2024-04-15",
                    "description": "Managed social media campaigns and digital marketing initiatives"
                }
            ],
            "education": [
                {
                    "institution": "University of KwaZulu-Natal",
                    "degree": "BCom Marketing",
                    "start_date": "2015-01-01",
                    "end_date": "2018-12-01"
                }
            ]
        },
        {
            "first_name": "Johan",
            "last_name": "Steyn",
            "email": "johan.steyn@testcv.com",
            "password": "demo123",
            "desired_job_title": "DevOps Engineer",
            "location": "Stellenbosch",
            "phone": "+27123456005",
            "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform", "Linux"],
            "experience": [
                {
                    "job_title": "System Administrator",
                    "company": "Wine Tech Solutions",
                    "start_date": "2021-02-01",
                    "end_date": "2024-07-31",
                    "description": "Managed cloud infrastructure and deployment pipelines"
                }
            ],
            "education": [
                {
                    "institution": "Stellenbosch University",
                    "degree": "BEng Computer Engineering",
                    "start_date": "2017-01-01",
                    "end_date": "2020-12-01"
                }
            ]
        },
        {
            "first_name": "Lerato",
            "last_name": "Molefe",
            "email": "lerato.molefe@testcv.com",
            "password": "demo123",
            "desired_job_title": "Product Manager",
            "location": "Sandton",
            "phone": "+27123456006",
            "skills": ["Product Strategy", "Agile", "Scrum", "User Stories", "Analytics", "Roadmapping"],
            "experience": [
                {
                    "job_title": "Product Owner",
                    "company": "Fintech StartUp",
                    "start_date": "2020-09-01",
                    "end_date": "2024-05-20",
                    "description": "Led product development for mobile banking application"
                }
            ],
            "education": [
                {
                    "institution": "University of the Witwatersrand",
                    "degree": "BSc Information Systems",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-01"
                }
            ]
        },
        {
            "first_name": "Andile",
            "last_name": "Ngcobo",
            "email": "andile.ngcobo@testcv.com",
            "password": "demo123",
            "desired_job_title": "Mobile Developer",
            "location": "Port Elizabeth",
            "phone": "+27123456007",
            "skills": ["Flutter", "Dart", "React Native", "Swift", "Kotlin", "Firebase"],
            "experience": [
                {
                    "job_title": "Mobile App Developer",
                    "company": "Mobile Solutions PE",
                    "start_date": "2021-11-01",
                    "end_date": "2024-08-10",
                    "description": "Developed cross-platform mobile applications for various clients"
                }
            ],
            "education": [
                {
                    "institution": "Nelson Mandela University",
                    "degree": "BTech Information Technology",
                    "start_date": "2017-01-01",
                    "end_date": "2020-12-01"
                }
            ]
        },
        {
            "first_name": "Michelle",
            "last_name": "Adams",
            "email": "michelle.adams@testcv.com",
            "password": "demo123",
            "desired_job_title": "HR Manager",
            "location": "Cape Town",
            "phone": "+27123456008",
            "skills": ["Recruitment", "Performance Management", "Employee Relations", "HR Policies", "Training"],
            "experience": [
                {
                    "job_title": "HR Coordinator",
                    "company": "Corporate Solutions CT",
                    "start_date": "2019-04-01",
                    "end_date": "2024-03-15",
                    "description": "Managed recruitment processes and employee development programs"
                }
            ],
            "education": [
                {
                    "institution": "University of Cape Town",
                    "degree": "BA Psychology",
                    "start_date": "2015-01-01",
                    "end_date": "2018-12-01"
                }
            ]
        },
        {
            "first_name": "Sipho",
            "last_name": "Radebe", 
            "email": "sipho.radebe@testcv.com",
            "password": "demo123",
            "desired_job_title": "Software Engineer",
            "location": "Johannesburg",
            "phone": "+27123456009",
            "skills": ["Java", "Spring Boot", "Microservices", "PostgreSQL", "Docker", "REST APIs"],
            "experience": [
                {
                    "job_title": "Backend Developer",
                    "company": "Enterprise Systems JHB",
                    "start_date": "2020-01-15",
                    "end_date": "2024-06-30",
                    "description": "Built scalable backend systems using Java and Spring framework"
                }
            ],
            "education": [
                {
                    "institution": "University of Johannesburg",
                    "degree": "BSc Computer Science",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-01"
                }
            ]
        },
        {
            "first_name": "Carmen",
            "last_name": "Botha",
            "email": "carmen.botha@testcv.com",
            "password": "demo123",
            "desired_job_title": "Graphic Designer",
            "location": "Bloemfontein",
            "phone": "+27123456010",
            "skills": ["Adobe Creative Suite", "InDesign", "Illustrator", "Brand Design", "Print Design"],
            "experience": [
                {
                    "job_title": "Junior Graphic Designer",
                    "company": "Creative Agency OFS",
                    "start_date": "2021-03-01",
                    "end_date": "2024-07-20",
                    "description": "Created visual designs for print and digital media"
                }
            ],
            "education": [
                {
                    "institution": "Central University of Technology",
                    "degree": "National Diploma Graphic Design",
                    "start_date": "2018-01-01",
                    "end_date": "2020-12-01"
                }
            ]
        },
        {
            "first_name": "Tshepo",
            "last_name": "Motaung",
            "email": "tshepo.motaung@testcv.com", 
            "password": "demo123",
            "desired_job_title": "Data Scientist",
            "location": "Johannesburg",
            "phone": "+27123456011",
            "skills": ["Python", "Machine Learning", "TensorFlow", "Pandas", "Numpy", "Data Visualization"],
            "experience": [
                {
                    "job_title": "Data Analyst",
                    "company": "Mining Analytics JHB",
                    "start_date": "2021-08-01",
                    "end_date": "2024-05-31",
                    "description": "Analyzed mining data and built predictive models"
                }
            ],
            "education": [
                {
                    "institution": "University of the Witwatersrand",
                    "degree": "MSc Data Science",
                    "start_date": "2019-01-01",
                    "end_date": "2020-12-01"
                }
            ]
        },
        {
            "first_name": "Kelly",
            "last_name": "Williams",
            "email": "kelly.williams@testcv.com",
            "password": "demo123", 
            "desired_job_title": "Business Analyst",
            "location": "Cape Town",
            "phone": "+27123456012",
            "skills": ["Business Process Mapping", "Requirements Analysis", "Stakeholder Management", "SQL", "Visio"],
            "experience": [
                {
                    "job_title": "Junior Business Analyst",
                    "company": "Consulting Firm CT",
                    "start_date": "2020-06-01",
                    "end_date": "2024-04-30",
                    "description": "Analyzed business processes and recommended improvements"
                }
            ],
            "education": [
                {
                    "institution": "University of Cape Town",
                    "degree": "BCom Business Science",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-01"
                }
            ]
        },
        {
            "first_name": "Mandla",
            "last_name": "Zungu",
            "email": "mandla.zungu@testcv.com",
            "password": "demo123",
            "desired_job_title": "Frontend Developer", 
            "location": "Durban",
            "phone": "+27123456013",
            "skills": ["React", "Vue.js", "TypeScript", "CSS3", "HTML5", "Webpack"],
            "experience": [
                {
                    "job_title": "Web Developer",
                    "company": "Digital Agency KZN",
                    "start_date": "2021-01-01",
                    "end_date": "2024-08-15",
                    "description": "Built responsive web applications using modern frameworks"
                }
            ],
            "education": [
                {
                    "institution": "Durban University of Technology",
                    "degree": "BTech Web Development",
                    "start_date": "2017-01-01",
                    "end_date": "2020-12-01"
                }
            ]
        },
        {
            "first_name": "Angie",
            "last_name": "Fourie",
            "email": "angie.fourie@testcv.com",
            "password": "demo123",
            "desired_job_title": "Project Manager",
            "location": "Pretoria",
            "phone": "+27123456014",
            "skills": ["Project Management", "PMP", "Agile", "Risk Management", "MS Project", "Leadership"],
            "experience": [
                {
                    "job_title": "Assistant Project Manager",
                    "company": "Construction Co PTA", 
                    "start_date": "2019-11-01",
                    "end_date": "2024-07-31",
                    "description": "Managed construction projects from planning to completion"
                }
            ],
            "education": [
                {
                    "institution": "University of South Africa",
                    "degree": "BCom Project Management",
                    "start_date": "2015-01-01",
                    "end_date": "2018-12-01"
                }
            ]
        },
        {
            "first_name": "Bongani",
            "last_name": "Mahlangu",
            "email": "bongani.mahlangu@testcv.com",
            "password": "demo123",
            "desired_job_title": "Cybersecurity Analyst",
            "location": "Johannesburg",
            "phone": "+27123456015",
            "skills": ["Network Security", "Penetration Testing", "CISSP", "Firewall Management", "Incident Response"],
            "experience": [
                {
                    "job_title": "IT Security Specialist",
                    "company": "Bank Security JHB",
                    "start_date": "2020-05-01",
                    "end_date": "2024-06-15",
                    "description": "Monitored security threats and implemented security measures"
                }
            ],
            "education": [
                {
                    "institution": "University of Johannesburg",
                    "degree": "BTech Information Security",
                    "start_date": "2016-01-01",
                    "end_date": "2019-12-01"
                }
            ]
        }
    ]
    
    try:
        created_count = 0
        
        for profile in job_seekers:
            print(f"\n👤 Creating job seeker: {profile['first_name']} {profile['last_name']}")
            
            # Check if user already exists
            existing_user = await db.users.find_one({"email": profile["email"]})
            if existing_user:
                print(f"   ⚠️  User {profile['email']} already exists, skipping...")
                continue
            
            # Hash password
            hashed_password = bcrypt.hashpw(profile["password"].encode('utf-8'), bcrypt.gensalt())
            
            # Calculate profile completeness
            profile_completeness = 85 + random.randint(0, 15)  # 85-100% completion
            
            # Create user document
            user_doc = {
                "id": str(uuid.uuid4()),
                "email": profile["email"],
                "password_hash": hashed_password.decode('utf-8'),
                "first_name": profile["first_name"],
                "last_name": profile["last_name"],
                "role": "job_seeker",
                "is_verified": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "phone": profile["phone"],
                "profile": {
                    "location": profile["location"],
                    "desired_job_title": profile["desired_job_title"],
                    "skills": profile["skills"],
                    "experience": profile["experience"],
                    "education": profile["education"],
                    "profile_completeness": profile_completeness
                },
                "job_seeker_progress": {
                    "profile_completion": True,
                    "skills_added": True,
                    "experience_added": True,
                    "education_added": True,
                    "first_application": False,
                    "total_points": profile_completeness
                }
            }
            
            # Insert user
            result = await db.users.insert_one(user_doc)
            
            if result.inserted_id:
                print(f"   ✅ Created: {profile['email']}")
                print(f"      📍 Location: {profile['location']}")
                print(f"      💼 Role: {profile['desired_job_title']}")
                print(f"      🎯 Skills: {', '.join(profile['skills'][:3])}...")
                print(f"      📊 Profile: {profile_completeness}% complete")
                created_count += 1
            else:
                print(f"   ❌ Failed to create {profile['email']}")
        
        print(f"\n🎉 Successfully created {created_count} job seeker users!")
        
        # Summary statistics
        total_job_seekers = await db.users.count_documents({"role": "job_seeker"})
        print(f"📊 Total job seekers in database: {total_job_seekers}")
        
        # Show skill distribution
        print(f"\n📋 Sample profiles created:")
        sample_users = await db.users.find({"role": "job_seeker"}).limit(5).to_list(5)
        
        for user in sample_users:
            profile = user.get("profile", {})
            skills = profile.get("skills", [])
            print(f"   • {user['first_name']} {user['last_name']} - {profile.get('desired_job_title', 'No title')} ({profile.get('location', 'No location')})")
            
    except Exception as e:
        print(f"❌ Error creating job seekers: {str(e)}")
        return False
    
    finally:
        client.close()
    
    return True

async def main():
    """Main function"""
    print("🚀 Job Seeker Creation Script for CV Search Testing")
    print("=" * 60)
    
    success = await create_job_seekers()
    
    if success:
        print("\n✅ Job seeker creation completed successfully!")
        print("🔍 CV search functionality now has diverse test data")
        print("\n💡 Test the CV search with various filters:")
        print("   - Position: 'developer', 'designer', 'manager', 'analyst'")
        print("   - Location: 'johannesburg', 'cape town', 'durban', 'pretoria'")
        print("   - Skills: 'javascript', 'python', 'react', 'sql', 'marketing'")
    else:
        print("\n❌ Creation failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())