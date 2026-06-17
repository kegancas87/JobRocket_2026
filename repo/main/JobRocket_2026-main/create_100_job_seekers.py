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

async def create_100_job_seekers():
    """Create 100 diverse job seeker profiles for comprehensive CV search testing"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/job_portal')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.job_portal
    
    print("👥 Creating 100 Diverse Job Seeker Profiles for CV Search Testing...")
    print("=" * 70)
    
    # South African cities
    locations = [
        "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", 
        "Bloemfontein", "Kimberley", "Polokwane", "Nelspruit", "Pietermaritzburg",
        "East London", "George", "Rustenburg", "Witbank", "Vereeniging",
        "Welkom", "Klerksdorp", "Potchefstroom", "Stellenbosch", "Paarl",
        "Midrand", "Sandton", "Rosebank", "Century City", "Umhlanga"
    ]
    
    # Diverse South African names
    first_names = [
        # Traditional African names
        "Thabo", "Nomsa", "Sipho", "Zanele", "Mandla", "Lerato", "Andile", "Busisiwe",
        "Tshepo", "Nomthandazo", "Bongani", "Precious", "Justice", "Faith", "Blessing",
        "Thandiwe", "Kagiso", "Palesa", "Ntombi", "Sello", "Refiloe", "Tebogo",
        
        # Afrikaans names
        "Pieter", "Angie", "Johan", "Marlize", "Francois", "Elmarie", "Hendrik", "Elize",
        "Danie", "Juanita", "Riaan", "Chantelle", "Werner", "Mariska", "Andre", "Leanne",
        
        # English names
        "Michael", "Sarah", "David", "Michelle", "James", "Kelly", "Robert", "Nicole",
        "Christopher", "Jessica", "Matthew", "Lauren", "Daniel", "Emma", "Andrew", "Chloe",
        
        # Indian names
        "Priya", "Arjun", "Kavitha", "Rajesh", "Deepika", "Vikram", "Meera", "Ravi",
        "Anjali", "Kiran", "Suresh", "Nisha", "Amit", "Shreya", "Rohan", "Pooja",
        
        # Coloured community names
        "Ashley", "Ryan", "Candice", "Shane", "Bianca", "Dean", "Taryn", "Kyle",
        "Rochelle", "Brandon", "Charlene", "Donovan", "Shireen", "Gareth", "Natalie"
    ]
    
    last_names = [
        # Nguni surnames
        "Mthembu", "Dlamini", "Nkomo", "Zungu", "Radebe", "Khumalo", "Ngcobo", "Mhlongo",
        "Ndlovu", "Mbeki", "Zuma", "Mabena", "Mahlangu", "Mokoena", "Mokwena", "Molefe",
        
        # Afrikaans surnames  
        "van der Merwe", "Steyn", "Botha", "Fourie", "van Wyk", "Pretorius", "Venter", "du Plessis",
        "Bosman", "Kruger", "Potgieter", "Oosthuizen", "van Zyl", "Marais", "Coetzee", "Grobler",
        
        # English surnames
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        
        # Indian surnames
        "Patel", "Sharma", "Kumar", "Singh", "Reddy", "Nair", "Iyer", "Menon",
        "Gupta", "Agarwal", "Jain", "Khanna", "Chandra", "Verma", "Rao", "Pillai",
        
        # Other surnames
        "Adams", "February", "September", "October", "Davids", "Hendricks", "Jacobs", "Moses"
    ]
    
    # Job profiles with realistic skills and experience
    job_profiles = [
        {
            "title": "Software Developer",
            "industry": "Technology",
            "skills": ["JavaScript", "React", "Node.js", "Python", "Git", "SQL", "HTML", "CSS"],
            "companies": ["Tech Solutions", "Digital Innovations", "Code Factory", "App Builders"],
            "education": ["BSc Computer Science", "BTech Information Technology", "National Diploma IT"]
        },
        {
            "title": "Data Analyst",
            "industry": "Analytics",
            "skills": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics", "R", "Data Mining"],
            "companies": ["Analytics Corp", "Data Insights", "Business Intelligence", "Stats Solutions"],
            "education": ["BSc Statistics", "BCom Economics", "BTech Data Analytics"]
        },
        {
            "title": "Marketing Manager",
            "industry": "Marketing",
            "skills": ["Digital Marketing", "SEO", "Google Ads", "Social Media", "Content Strategy", "Analytics", "Brand Management"],
            "companies": ["Marketing Plus", "Brand Builders", "Digital Agency", "Creative Solutions"],
            "education": ["BCom Marketing", "BA Communications", "National Diploma Marketing"]
        },
        {
            "title": "UX/UI Designer",
            "industry": "Design",
            "skills": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "User Research", "Prototyping", "Wireframing"],
            "companies": ["Design Studio", "Creative Agency", "UX Lab", "Digital Design"],
            "education": ["BTech Graphic Design", "BA Fine Arts", "National Diploma Design"]
        },
        {
            "title": "Project Manager",
            "industry": "Management",
            "skills": ["Project Management", "Agile", "Scrum", "MS Project", "Risk Management", "Leadership", "Stakeholder Management"],
            "companies": ["Project Solutions", "Management Consulting", "Build Corp", "Construction Co"],
            "education": ["BCom Project Management", "MBA", "BTech Construction Management"]
        },
        {
            "title": "Financial Analyst",
            "industry": "Finance",
            "skills": ["Financial Analysis", "Excel", "SAP", "Budgeting", "Forecasting", "Investment Analysis", "Risk Assessment"],
            "companies": ["Financial Services", "Investment Bank", "Accounting Firm", "Asset Management"],
            "education": ["BCom Finance", "CA(SA)", "BCom Accounting"]
        },
        {
            "title": "HR Manager",
            "industry": "Human Resources",
            "skills": ["Recruitment", "Performance Management", "Employee Relations", "HR Policies", "Training", "Compensation"],
            "companies": ["HR Solutions", "People First", "Corporate HR", "Talent Management"],
            "education": ["BA Psychology", "BCom Human Resources", "Postgraduate Diploma HR"]
        },
        {
            "title": "Sales Representative",
            "industry": "Sales",
            "skills": ["Sales", "CRM", "Negotiation", "Customer Service", "Lead Generation", "Account Management", "Communication"],
            "companies": ["Sales Solutions", "Direct Sales", "FMCG Company", "B2B Sales"],
            "education": ["BCom Sales Management", "National Diploma Sales", "BA Communications"]
        },
        {
            "title": "Mechanical Engineer",
            "industry": "Engineering",
            "skills": ["AutoCAD", "SolidWorks", "Manufacturing", "Quality Control", "Project Management", "Problem Solving"],
            "companies": ["Engineering Firm", "Manufacturing Co", "Industrial Solutions", "Mechanical Systems"],
            "education": ["BEng Mechanical Engineering", "BTech Mechanical Engineering", "National Diploma Engineering"]
        },
        {
            "title": "Accountant",
            "industry": "Accounting",
            "skills": ["Accounting", "Tax", "Auditing", "Financial Reporting", "Excel", "SAP", "Sage", "IFRS"],
            "companies": ["Accounting Firm", "Corporate Finance", "Tax Specialists", "Audit Company"],
            "education": ["BCom Accounting", "CA(SA)", "CIMA", "National Diploma Accounting"]
        },
        {
            "title": "Graphic Designer",
            "industry": "Design",
            "skills": ["Adobe Creative Suite", "Photoshop", "Illustrator", "InDesign", "Brand Design", "Print Design", "Web Design"],
            "companies": ["Design Agency", "Creative Studio", "Marketing Agency", "Print Company"],
            "education": ["BTech Graphic Design", "National Diploma Design", "BA Visual Arts"]
        },
        {
            "title": "Business Analyst",
            "industry": "Business Analysis",
            "skills": ["Business Analysis", "Requirements Gathering", "Process Mapping", "SQL", "Stakeholder Management", "Documentation"],
            "companies": ["Consulting Firm", "Business Solutions", "Systems Integration", "Process Improvement"],
            "education": ["BCom Business Science", "BSc Information Systems", "MBA"]
        },
        {
            "title": "DevOps Engineer",
            "industry": "Technology",
            "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform", "Linux", "CI/CD", "Monitoring"],
            "companies": ["Cloud Solutions", "DevOps Specialists", "Infrastructure Co", "Tech Consulting"],
            "education": ["BSc Computer Science", "BTech Information Technology", "BEng Software Engineering"]
        },
        {
            "title": "Content Writer",
            "industry": "Content",
            "skills": ["Content Writing", "SEO Writing", "Copywriting", "Social Media", "Blogging", "Research", "Editing"],
            "companies": ["Content Agency", "Digital Marketing", "Publishing House", "Media Company"],
            "education": ["BA English", "BA Journalism", "National Diploma Journalism"]
        },
        {
            "title": "Customer Service Representative",
            "industry": "Customer Service",
            "skills": ["Customer Service", "Communication", "Problem Solving", "CRM", "Call Center", "Complaint Resolution"],
            "companies": ["Call Center", "Customer Solutions", "Service Desk", "Support Center"],
            "education": ["Matric", "National Certificate Customer Service", "Diploma Business Administration"]
        }
    ]
    
    try:
        created_count = 0
        
        for i in range(100):
            # Generate random profile
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            job_profile = random.choice(job_profiles)
            location = random.choice(locations)
            
            # Generate email (fix string escaping)
            clean_first = first_name.lower().replace(' ', '')
            clean_last = last_name.lower().replace(' ', '').replace("'", "")
            email = f"{clean_first}.{clean_last}@testcv{i+1:03d}.com"
            
            # Generate experience level (1-15 years)
            years_experience = random.randint(1, 15)
            
            # Generate experience entries based on years of experience
            experience = []
            current_year = datetime.now().year
            
            if years_experience >= 2:
                # Current job
                current_company = random.choice(job_profile["companies"])
                start_date = f"{current_year - random.randint(1, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                experience.append({
                    "job_title": job_profile["title"],
                    "company": f"{current_company} {location}",
                    "start_date": start_date,
                    "end_date": None,  # Current job
                    "description": f"Working as {job_profile['title']} with expertise in {', '.join(job_profile['skills'][:3])}"
                })
            
            if years_experience >= 5:
                # Previous job
                prev_company = random.choice(job_profile["companies"])
                end_year = current_year - random.randint(1, 2)
                start_year = end_year - random.randint(2, 4)
                experience.append({
                    "job_title": f"Junior {job_profile['title']}" if random.random() > 0.5 else job_profile["title"],
                    "company": f"{prev_company} {random.choice(locations)}",
                    "start_date": f"{start_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    "end_date": f"{end_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    "description": f"Gained experience in {', '.join(random.sample(job_profile['skills'], 3))}"
                })
            
            # Education
            education = []
            degree = random.choice(job_profile["education"])
            
            # Add tertiary education
            institutions = [
                "University of the Witwatersrand", "University of Cape Town", "University of KwaZulu-Natal",
                "University of Pretoria", "Stellenbosch University", "University of Johannesburg",
                "Cape Peninsula University of Technology", "Durban University of Technology",
                "Central University of Technology", "Nelson Mandela University", "University of South Africa"
            ]
            
            grad_year = current_year - random.randint(years_experience + 1, years_experience + 5)
            education.append({
                "institution": random.choice(institutions),
                "degree": degree,
                "start_date": f"{grad_year - 3}-01-01",
                "end_date": f"{grad_year}-12-01"
            })
            
            # Sometimes add additional qualifications
            if random.random() > 0.7:
                additional_quals = [
                    "Certificate in Project Management", "Diploma in Business Administration",
                    "Certificate in Digital Marketing", "Advanced Diploma in Management",
                    "Certificate in Data Analytics", "Postgraduate Diploma"
                ]
                education.append({
                    "institution": random.choice(institutions),
                    "degree": random.choice(additional_quals),
                    "start_date": f"{grad_year + 1}-01-01",
                    "end_date": f"{grad_year + 2}-12-01"
                })
            
            # Skills with some variation
            base_skills = job_profile["skills"].copy()
            additional_skills = [
                "Communication", "Problem Solving", "Teamwork", "Leadership", "Time Management",
                "Critical Thinking", "Adaptability", "Microsoft Office", "Presentation Skills"
            ]
            
            # Add 2-4 additional skills
            skills = base_skills + random.sample(additional_skills, random.randint(2, 4))
            
            # Generate profile completeness (60-100%)
            profile_completeness = random.randint(60, 100)
            
            # Generate phone number
            phone = f"+2712{random.randint(1000000, 9999999)}"
            
            # Check if user already exists
            existing_user = await db.users.find_one({"email": email})
            if existing_user:
                # Generate new email if exists
                email = f"{clean_first}.{clean_last}.{i+1}@testcv.com"
            
            print(f"👤 Creating: {first_name} {last_name} - {job_profile['title']} ({location})")
            
            # Hash password
            hashed_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt())
            
            # Create user document
            user_doc = {
                "id": str(uuid.uuid4()),
                "email": email,
                "password_hash": hashed_password.decode('utf-8'),
                "first_name": first_name,
                "last_name": last_name,
                "role": "job_seeker",
                "is_verified": True,
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                "updated_at": datetime.utcnow(),
                "phone": phone,
                "profile": {
                    "location": location,
                    "desired_job_title": job_profile["title"],
                    "skills": skills,
                    "experience": experience,
                    "education": education,
                    "profile_completeness": profile_completeness,
                    "industry_preference": job_profile["industry"]
                },
                "job_seeker_progress": {
                    "profile_completion": profile_completeness > 70,
                    "skills_added": len(skills) > 0,
                    "experience_added": len(experience) > 0,
                    "education_added": len(education) > 0,
                    "first_application": random.random() > 0.6,
                    "total_points": profile_completeness
                }
            }
            
            # Insert user
            result = await db.users.insert_one(user_doc)
            
            if result.inserted_id:
                created_count += 1
                if created_count % 10 == 0:
                    print(f"   ✅ Progress: {created_count}/100 profiles created")
            else:
                print(f"   ❌ Failed to create {email}")
        
        print(f"\n🎉 Successfully created {created_count} diverse job seeker profiles!")
        
        # Generate summary statistics
        total_job_seekers = await db.users.count_documents({"role": "job_seeker"})
        print(f"📊 Total job seekers in database: {total_job_seekers}")
        
        # Show distribution by location
        print(f"\n📍 Location Distribution (sample):")
        location_sample = {}
        for location in locations[:10]:
            count = await db.users.count_documents({
                "role": "job_seeker", 
                "profile.location": location
            })
            if count > 0:
                location_sample[location] = count
        
        for loc, count in sorted(location_sample.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {loc}: {count} candidates")
        
        # Show job title distribution
        print(f"\n💼 Job Title Distribution (sample):")
        job_titles = [jp["title"] for jp in job_profiles]
        title_sample = {}
        for title in job_titles[:10]:
            count = await db.users.count_documents({
                "role": "job_seeker",
                "profile.desired_job_title": title
            })
            if count > 0:
                title_sample[title] = count
        
        for title, count in sorted(title_sample.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {title}: {count} candidates")
            
    except Exception as e:
        print(f"❌ Error creating job seekers: {str(e)}")
        return False
    
    finally:
        client.close()
    
    return True

async def main():
    """Main function"""
    print("🚀 Comprehensive Job Seeker Profile Creation Script")
    print("=" * 70)
    
    success = await create_100_job_seekers()
    
    if success:
        print("\n✅ Job seeker profile creation completed successfully!")
        print("🔍 CV search functionality now has comprehensive test data")
        print("\n💡 Test the CV search with various combinations:")
        print("   🎯 Positions: 'developer', 'analyst', 'manager', 'designer', 'engineer'")
        print("   📍 Locations: 'johannesburg', 'cape town', 'durban', 'pretoria', 'bloemfontein'") 
        print("   🛠️  Skills: 'python', 'javascript', 'project management', 'marketing', 'design'")
        print("   🏢 Industries: Technology, Marketing, Finance, Engineering, Design")
    else:
        print("\n❌ Profile creation failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())