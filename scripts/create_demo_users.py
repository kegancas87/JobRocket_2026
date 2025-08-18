#!/usr/bin/env python3
"""
Job Rocket Demo Users Creation Script
Creates comprehensive demo users with realistic data for testing
"""

import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "https://jrocket-mvp.preview.emergentagent.com/api"

# Demo user credentials
DEMO_USERS = {
    "job_seekers": [
        {
            "email": "sarah.johnson@demo.com",
            "password": "demo123",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "profile_level": "beginner"  # Low completion
        },
        {
            "email": "michael.chen@demo.com", 
            "password": "demo123",
            "first_name": "Michael",
            "last_name": "Chen",
            "profile_level": "advanced"  # High completion
        },
        {
            "email": "alex.rodriguez@demo.com",
            "password": "demo123", 
            "first_name": "Alex",
            "last_name": "Rodriguez",
            "profile_level": "intermediate"  # Medium completion
        }
    ],
    "recruiters": [
        {
            "email": "lisa.martinez@techcorp.demo",
            "password": "demo123",
            "first_name": "Lisa",
            "last_name": "Martinez",
            "company": "TechCorp Solutions"
        },
        {
            "email": "david.wilson@innovate.demo",
            "password": "demo123",
            "first_name": "David", 
            "last_name": "Wilson",
            "company": "Innovate Digital"
        }
    ],
    "admins": [
        {
            "email": "admin@jobrocket.demo",
            "password": "admin123",
            "first_name": "John",
            "last_name": "Administrator"
        }
    ]
}

def register_user(user_data):
    """Register a new user"""
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": user_data["email"],
            "password": user_data["password"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "role": "job_seeker" if "profile_level" in user_data else "recruiter" if "company" in user_data else "admin"
        })
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error registering {user_data['email']}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception registering {user_data['email']}: {e}")
        return None

def get_auth_headers(token):
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def populate_beginner_profile(token):
    """Populate beginner profile (20-30 points)"""
    headers = get_auth_headers(token)
    
    # Basic info update (about_me not enough for points)
    requests.put(f"{BASE_URL}/profile", 
        json={
            "location": "Cape Town, South Africa",
            "phone": "+27 21 456 7890",
            "about_me": "I'm passionate about technology."  # Too short for points
        }, 
        headers=headers
    )
    
    # Add only 3 skills (not enough for 20 points)
    requests.put(f"{BASE_URL}/profile", 
        json={"skills": ["Python", "HTML", "CSS"]}, 
        headers=headers
    )
    
    print("✅ Beginner profile created - Sarah Johnson (Low completion)")

def populate_intermediate_profile(token):
    """Populate intermediate profile (50-60 points)"""
    headers = get_auth_headers(token)
    
    # Complete basic info with proper about_me
    requests.put(f"{BASE_URL}/profile", 
        json={
            "location": "Johannesburg, Gauteng",
            "phone": "+27 11 123 4567",
            "about_me": "Experienced software developer with 3 years in web development. Passionate about creating user-friendly applications and solving complex problems. Looking to grow my career in a dynamic tech environment where I can contribute to innovative projects."
        }, 
        headers=headers
    )
    
    # Add 5+ skills for points
    requests.put(f"{BASE_URL}/profile", 
        json={"skills": ["JavaScript", "React", "Node.js", "Python", "Git", "SQL"]}, 
        headers=headers
    )
    
    # Add work experience
    requests.post(f"{BASE_URL}/profile/work-experience",
        json={
            "company": "WebTech Solutions",
            "position": "Junior Developer", 
            "start_date": (datetime.now() - timedelta(days=730)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=365)).isoformat(),
            "current": False,
            "description": "Developed responsive web applications using React and Node.js. Collaborated with design teams to implement user interfaces.",
            "location": "Johannesburg, SA"
        },
        headers=headers
    )
    
    print("✅ Intermediate profile created - Alex Rodriguez (Medium completion)")

def populate_advanced_profile(token):
    """Populate advanced profile (90-100 points)"""
    headers = get_auth_headers(token)
    
    # Complete profile update
    requests.put(f"{BASE_URL}/profile", 
        json={
            "location": "Durban, KwaZulu-Natal", 
            "phone": "+27 31 789 0123",
            "about_me": "Senior Full-Stack Developer with 5+ years of experience building scalable web applications. Expertise in React, Node.js, Python, and cloud technologies. Led multiple successful projects from conception to deployment. Passionate about mentoring junior developers and implementing best practices. Seeking challenging opportunities in fintech or e-commerce sectors.",
            "profile_picture_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "intro_video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "current_salary_range": "R60,000 - R80,000",
            "desired_salary_range": "R80,000 - R120,000"
        }, 
        headers=headers
    )
    
    # Add comprehensive skills
    requests.put(f"{BASE_URL}/profile", 
        json={"skills": ["React", "Node.js", "Python", "TypeScript", "AWS", "Docker", "MongoDB", "PostgreSQL", "GraphQL", "Jest"]}, 
        headers=headers
    )
    
    # Add multiple work experiences
    experiences = [
        {
            "company": "Digital Innovations Ltd",
            "position": "Senior Full-Stack Developer",
            "start_date": (datetime.now() - timedelta(days=1095)).isoformat(),
            "current": True,
            "description": "Lead developer for e-commerce platform serving 100k+ users. Architected microservices using Node.js and Python. Implemented CI/CD pipelines and mentored 3 junior developers.",
            "location": "Durban, SA"
        },
        {
            "company": "StartupHub SA",
            "position": "Full-Stack Developer", 
            "start_date": (datetime.now() - timedelta(days=1825)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=1095)).isoformat(),
            "current": False,
            "description": "Developed multiple web applications for startup clients. Built RESTful APIs and responsive frontends. Worked with React, Node.js, and PostgreSQL.",
            "location": "Cape Town, SA"
        }
    ]
    
    for exp in experiences:
        requests.post(f"{BASE_URL}/profile/work-experience", json=exp, headers=headers)
    
    # Add education with document
    requests.post(f"{BASE_URL}/profile/education",
        json={
            "institution": "University of Cape Town",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "level": "Bachelors",
            "start_date": (datetime.now() - timedelta(days=2920)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=1825)).isoformat(),
            "current": False,
            "grade": "Cum Laude",
            "document_url": "https://example.com/certificate.pdf"
        },
        headers=headers
    )
    
    # Add achievements
    achievements = [
        {
            "title": "AWS Certified Developer",
            "description": "Professional certification in AWS cloud development services",
            "date_achieved": (datetime.now() - timedelta(days=365)).isoformat(),
            "issuer": "Amazon Web Services",
            "credential_url": "https://aws.amazon.com/certification/"
        },
        {
            "title": "Best Innovation Award",
            "description": "Recognized for developing an AI-powered customer service chatbot that reduced response time by 60%",
            "date_achieved": (datetime.now() - timedelta(days=200)).isoformat(),
            "issuer": "Digital Innovations Ltd"
        }
    ]
    
    for achievement in achievements:
        requests.post(f"{BASE_URL}/profile/achievement", json=achievement, headers=headers)
    
    # Setup email alerts
    requests.post(f"{BASE_URL}/profile/email-alerts", headers=headers)
    
    # Simulate job applications (5 for points)
    for i in range(5):
        requests.post(f"{BASE_URL}/profile/job-application/job-{i+1}", headers=headers)
    
    print("✅ Advanced profile created - Michael Chen (High completion)")

def create_demo_companies():
    """Create demo companies for job postings"""
    companies = [
        {
            "name": "TechCorp Solutions",
            "description": "Leading technology consulting firm specializing in digital transformation",
            "website": "https://techcorp-solutions.demo",
            "logo_url": "https://images.unsplash.com/photo-1496200186974-4293800e2c20?w=100&h=100&fit=crop",
            "industry": "Technology Consulting",
            "size": "201-500 employees",
            "location": "Johannesburg, Gauteng"
        },
        {
            "name": "Innovate Digital",
            "description": "Creative digital agency building next-generation web and mobile applications",
            "website": "https://innovate-digital.demo", 
            "logo_url": "https://images.unsplash.com/photo-1621831337128-35676ca30868?w=100&h=100&fit=crop",
            "industry": "Digital Marketing",
            "size": "51-200 employees",
            "location": "Cape Town, Western Cape"
        },
        {
            "name": "FinTech Solutions SA",
            "description": "Revolutionary fintech company transforming banking in South Africa",
            "website": "https://fintech-sa.demo",
            "logo_url": "https://images.unsplash.com/photo-1712159018726-4564d92f3ec2?w=100&h=100&fit=crop",
            "industry": "Financial Technology",
            "size": "101-200 employees", 
            "location": "Sandton, Gauteng"
        }
    ]
    
    for company in companies:
        try:
            response = requests.post(f"{BASE_URL}/companies", json=company)
            if response.status_code == 200:
                print(f"✅ Created company: {company['name']}")
            else:
                print(f"❌ Error creating company {company['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Exception creating company {company['name']}: {e}")

def create_demo_jobs():
    """Create diverse demo job postings"""
    jobs = [
        {
            "title": "Senior React Developer",
            "company_id": "comp-tech-1",
            "company_name": "TechCorp Solutions",
            "description": "We're looking for a Senior React Developer to join our growing team. You'll be working on cutting-edge projects using the latest technologies.",
            "requirements": ["5+ years React experience", "TypeScript proficiency", "Redux/Context API", "Testing experience"],
            "responsibilities": ["Lead frontend development", "Mentor junior developers", "Code reviews", "Architecture decisions"],
            "location": "Johannesburg, Gauteng",
            "job_type": "Full-time",
            "experience_level": "Senior", 
            "category": "IT & Telecommunications",
            "salary_min": 60000,
            "salary_max": 90000,
            "is_remote": True,
            "is_hybrid": False,
            "logo_url": "https://images.unsplash.com/photo-1496200186974-4293800e2c20?w=100&h=100&fit=crop",
            "featured": True
        },
        {
            "title": "Product Manager",
            "company_id": "comp-innovate-1", 
            "company_name": "Innovate Digital",
            "description": "Exciting opportunity for a Product Manager to drive our digital product strategy and work with cross-functional teams.",
            "requirements": ["3+ years product management", "Agile methodology", "Data analysis skills", "Stakeholder management"],
            "responsibilities": ["Product roadmap planning", "Feature prioritization", "Market research", "Team coordination"],
            "location": "Cape Town, Western Cape",
            "job_type": "Full-time",
            "experience_level": "Mid Level",
            "category": "Operations",
            "salary_min": 45000,
            "salary_max": 70000,
            "is_remote": False,
            "is_hybrid": True,
            "logo_url": "https://images.unsplash.com/photo-1621831337128-35676ca30868?w=100&h=100&fit=crop",
            "featured": False
        },
        {
            "title": "DevOps Engineer", 
            "company_id": "comp-fintech-1",
            "company_name": "FinTech Solutions SA",
            "description": "Join our mission to revolutionize fintech infrastructure. We need a DevOps Engineer to scale our cloud systems.",
            "requirements": ["AWS/Azure experience", "Kubernetes", "CI/CD pipelines", "Infrastructure as Code"],
            "responsibilities": ["Manage cloud infrastructure", "Automate deployments", "Monitor systems", "Security compliance"],
            "location": "Sandton, Gauteng",
            "job_type": "Full-time", 
            "experience_level": "Senior",
            "category": "IT & Telecommunications",
            "salary_min": 70000,
            "salary_max": 100000,
            "is_remote": True,
            "is_hybrid": False, 
            "logo_url": "https://images.unsplash.com/photo-1712159018726-4564d92f3ec2?w=100&h=100&fit=crop",
            "featured": True
        },
        {
            "title": "Junior Frontend Developer",
            "company_id": "comp-tech-1",
            "company_name": "TechCorp Solutions", 
            "description": "Perfect role for a junior developer looking to grow their skills in a supportive environment with modern tech stack.",
            "requirements": ["HTML/CSS/JavaScript", "React basics", "Git knowledge", "Eager to learn"],
            "responsibilities": ["Build UI components", "Bug fixes", "Code maintenance", "Learn from seniors"],
            "location": "Johannesburg, Gauteng",
            "job_type": "Full-time",
            "experience_level": "Junior",
            "category": "IT & Telecommunications", 
            "salary_min": 25000,
            "salary_max": 35000,
            "is_remote": False,
            "is_hybrid": True,
            "logo_url": "https://images.unsplash.com/photo-1496200186974-4293800e2c20?w=100&h=100&fit=crop",
            "featured": False
        },
        {
            "title": "UX/UI Designer",
            "company_id": "comp-innovate-1",
            "company_name": "Innovate Digital",
            "description": "Creative UX/UI Designer wanted to craft beautiful and intuitive user experiences for our diverse client portfolio.",
            "requirements": ["Figma/Sketch proficiency", "User research skills", "Prototyping experience", "Portfolio required"],
            "responsibilities": ["Design user interfaces", "Conduct user research", "Create prototypes", "Collaborate with developers"],
            "location": "Cape Town, Western Cape",
            "job_type": "Full-time",
            "experience_level": "Mid Level", 
            "category": "Marketing & Communications",
            "salary_min": 40000,
            "salary_max": 60000,
            "is_remote": True,
            "is_hybrid": False,
            "logo_url": "https://images.unsplash.com/photo-1621831337128-35676ca30868?w=100&h=100&fit=crop",
            "featured": False
        }
    ]
    
    for job in jobs:
        try:
            response = requests.post(f"{BASE_URL}/jobs", json=job)
            if response.status_code == 200:
                print(f"✅ Created job: {job['title']} at {job['company_name']}")
            else:
                print(f"❌ Error creating job {job['title']}: {response.text}")
        except Exception as e:
            print(f"❌ Exception creating job {job['title']}: {e}")

def main():
    """Main function to create all demo data"""
    print("🚀 Creating Job Rocket Demo Users & Data...")
    print("=" * 50)
    
    # Create job seekers
    print("\n👤 Creating Job Seeker Demo Users...")
    
    # Sarah Johnson - Beginner (already exists, just populate)
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "sarah.johnson@demo.com",
            "password": "demo123"
        })
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            populate_beginner_profile(token)
    except:
        print("❌ Could not populate Sarah Johnson profile")
    
    # Create Alex Rodriguez - Intermediate
    alex_data = register_user({
        "email": "alex.rodriguez@demo.com",
        "password": "demo123",
        "first_name": "Alex", 
        "last_name": "Rodriguez",
        "profile_level": "intermediate"
    })
    if alex_data:
        populate_intermediate_profile(alex_data["access_token"])
    
    # Michael Chen - Advanced (already exists, just populate)
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "michael.chen@demo.com",
            "password": "demo123"
        })
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            populate_advanced_profile(token)
    except:
        print("❌ Could not populate Michael Chen profile")
    
    # Create recruiters
    print("\n👔 Creating Recruiter Demo Users...")
    for recruiter in DEMO_USERS["recruiters"][1:]:  # Skip first one (already created)
        register_user(recruiter)
        print(f"✅ Created recruiter: {recruiter['first_name']} {recruiter['last_name']}")
    
    # Create demo companies and jobs
    print("\n🏢 Creating Demo Companies...")
    create_demo_companies()
    
    print("\n💼 Creating Demo Jobs...")  
    create_demo_jobs()
    
    print("\n" + "=" * 50)
    print("🎉 Demo Data Creation Complete!")
    print("\n📋 DEMO USER CREDENTIALS:")
    print("=" * 50)
    
    print("\n👤 JOB SEEKERS:")
    print("1. BEGINNER (20-30 points)")
    print("   Email: sarah.johnson@demo.com")
    print("   Password: demo123")
    print("   Profile: Basic info, few skills")
    
    print("\n2. INTERMEDIATE (50-60 points)")  
    print("   Email: alex.rodriguez@demo.com")
    print("   Password: demo123")
    print("   Profile: Complete info, work experience")
    
    print("\n3. ADVANCED (90-100 points)")
    print("   Email: michael.chen@demo.com") 
    print("   Password: demo123")
    print("   Profile: Full completion, all features")
    
    print("\n👔 RECRUITERS:")
    print("1. Email: lisa.martinez@techcorp.demo")
    print("   Password: demo123")
    print("   Company: TechCorp Solutions")
    
    print("\n2. Email: david.wilson@innovate.demo")
    print("   Password: demo123") 
    print("   Company: Innovate Digital")
    
    print("\n🔧 ADMIN:")
    print("   Email: admin@jobrocket.demo")
    print("   Password: admin123")
    print("   Role: System Administrator")
    
    print("\n" + "=" * 50)
    print("🚀 Ready to test Job Rocket!")

if __name__ == "__main__":
    main()