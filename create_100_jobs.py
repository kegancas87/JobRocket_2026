#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import random

# Add the current directory to Python path to import server modules
sys.path.append('/app/backend')

async def create_100_diverse_jobs():
    """Create 100 diverse job postings with various expiry dates (2 weeks to 1 month)"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/job_portal')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.job_portal
    
    print("💼 Creating 100 Diverse Job Postings...")
    print("=" * 60)
    
    # Get existing recruiter users to post jobs
    recruiters = await db.users.find({"role": "recruiter"}).to_list(None)
    if not recruiters:
        print("❌ No recruiter users found. Please create some recruiters first.")
        return False
    
    print(f"📊 Found {len(recruiters)} recruiter accounts")
    
    # Job data arrays
    job_titles = [
        # Technology
        "Senior Software Engineer", "Full Stack Developer", "Frontend Developer", "Backend Developer",
        "DevOps Engineer", "Data Scientist", "Machine Learning Engineer", "Cloud Architect",
        "Cybersecurity Analyst", "UI/UX Designer", "Product Manager", "Technical Lead",
        "Python Developer", "JavaScript Developer", "React Developer", "Node.js Developer",
        "Mobile App Developer", "Game Developer", "Database Administrator", "Network Engineer",
        
        # Business & Finance
        "Business Analyst", "Financial Analyst", "Investment Analyst", "Accountant",
        "Project Manager", "Operations Manager", "Sales Manager", "Marketing Manager",
        "Digital Marketing Specialist", "Content Marketing Manager", "SEO Specialist", "PPC Specialist",
        "HR Manager", "Recruitment Consultant", "Training Manager", "Executive Assistant",
        "Customer Success Manager", "Account Manager", "Business Development Manager", "Consultant",
        
        # Healthcare & Science
        "Software Engineer (Healthcare)", "Biomedical Engineer", "Research Analyst", "Lab Technician",
        "Clinical Data Analyst", "Health Information Manager", "Medical Device Specialist", "Pharmacist",
        
        # Education & Training
        "Training Specialist", "Curriculum Developer", "Learning Designer", "Educational Technology Specialist",
        
        # Engineering & Manufacturing
        "Mechanical Engineer", "Electrical Engineer", "Industrial Engineer", "Quality Assurance Engineer",
        "Manufacturing Engineer", "Process Engineer", "Design Engineer", "Automation Engineer",
        
        # Creative & Media
        "Graphic Designer", "Web Designer", "Video Editor", "Content Writer",
        "Social Media Manager", "Brand Manager", "Creative Director", "Photographer",
        
        # Sales & Customer Service
        "Sales Representative", "Inside Sales Representative", "Customer Service Representative",
        "Technical Support Specialist", "Sales Executive", "Regional Sales Manager",
        
        # Legal & Compliance
        "Legal Advisor", "Compliance Officer", "Contract Specialist", "Regulatory Affairs Specialist",
        
        # Operations & Logistics
        "Supply Chain Manager", "Logistics Coordinator", "Operations Analyst", "Warehouse Manager",
        "Procurement Specialist", "Inventory Manager", "Distribution Manager", "Transport Coordinator",
        
        # Additional Specialized Roles
        "Solutions Architect", "Integration Specialist", "Systems Administrator", "IT Support Specialist",
        "Scrum Master", "Agile Coach", "Change Management Specialist", "Process Improvement Analyst",
        "Risk Analyst", "Audit Manager", "Tax Specialist", "Payroll Specialist"
    ]
    
    companies = [
        # Tech Companies
        "TechSolutions SA", "Digital Innovations Cape Town", "Code Factory JHB", "App Builders PTY",
        "Cloud Systems Africa", "Data Insights Co", "Smart Tech Solutions", "Future Tech SA",
        "Innovate Digital", "Pixel Perfect Studios", "Cyber Security SA", "AI Solutions Africa",
        
        # Financial Services
        "Financial Partners SA", "Investment Solutions Cape Town", "Banking Systems JHB", "Wealth Advisors",
        "Corporate Finance Solutions", "Asset Management SA", "Financial Planning Co", "Investment Bank SA",
        
        # Consulting & Business Services
        "Business Consulting SA", "Strategy Partners", "Management Solutions", "Process Excellence",
        "Transformation Consulting", "Operations Excellence", "Business Intelligence SA", "Analytics Partners",
        
        # Healthcare & Pharma
        "HealthTech Solutions", "Medical Systems SA", "Pharma Innovations", "Healthcare Analytics",
        "Clinical Research SA", "Medical Device Co", "Health Information Systems", "Bio Solutions",
        
        # Engineering & Manufacturing
        "Engineering Solutions SA", "Manufacturing Excellence", "Industrial Systems", "Quality Dynamics",
        "Production Partners", "Automation Systems", "Design Engineering Co", "Process Solutions",
        
        # Marketing & Creative
        "Creative Agency Cape Town", "Digital Marketing SA", "Brand Builders", "Content Creators Co",
        "Social Media Solutions", "Marketing Innovations", "Creative Studios SA", "Design House",
        
        # Retail & E-commerce
        "E-commerce Solutions SA", "Retail Systems", "Online Marketplace", "Digital Retail Co",
        "Customer Experience SA", "Omnichannel Solutions", "Retail Analytics", "Commerce Platform",
        
        # Education & Training
        "Learning Solutions SA", "Training Excellence", "Education Technology", "Skills Development Co",
        "Corporate Training SA", "Knowledge Systems", "Learning Platforms", "Education Innovations",
        
        # Logistics & Supply Chain
        "Logistics Solutions SA", "Supply Chain Partners", "Distribution Excellence", "Transport Solutions",
        "Warehouse Systems", "Procurement Partners", "Inventory Solutions", "Freight Management",
        
        # Energy & Utilities
        "Energy Solutions SA", "Renewable Energy Co", "Power Systems", "Utility Management",
        "Green Energy Solutions", "Solar Innovations", "Energy Efficiency SA", "Smart Grid Solutions"
    ]
    
    locations = [
        "Johannesburg", "Cape Town", "Durban", "Pretoria", "Sandton", "Rosebank",
        "Century City", "Umhlanga", "Stellenbosch", "Port Elizabeth", "Bloemfontein",
        "East London", "Pietermaritzburg", "Nelspruit", "Polokwane", "Kimberley",
        "George", "Rustenburg", "Witbank", "Vereeniging", "Welkom", "Klerksdorp",
        "Potchefstroom", "Paarl", "Somerset West", "Bellville", "Brackenfell",
        "Randburg", "Midrand", "Centurion", "Hatfield", "Menlyn", "Brooklyn"
    ]
    
    industries = [
        "Technology", "Financial Services", "Healthcare", "Manufacturing", "Retail",
        "Consulting", "Education", "Media & Entertainment", "Real Estate", "Energy",
        "Telecommunications", "Automotive", "Aerospace", "Construction", "Agriculture",
        "Mining", "Transportation", "Hospitality", "Non-profit", "Government"
    ]
    
    job_types = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]
    work_types = ["On-site", "Remote", "Hybrid"]
    
    # Salary ranges by experience level
    salary_ranges = {
        "entry": (15000, 35000),
        "mid": (35000, 65000),
        "senior": (65000, 120000),
        "executive": (120000, 250000)
    }
    
    # Job descriptions templates
    description_templates = [
        "Join our dynamic team as a {title} and contribute to cutting-edge projects that shape the future of {industry}. We're looking for passionate professionals who thrive in collaborative environments and are eager to make a meaningful impact.",
        
        "We are seeking an experienced {title} to join our growing {industry} team. The ideal candidate will have a strong background in relevant technologies and a proven track record of delivering high-quality solutions in fast-paced environments.",
        
        "Exciting opportunity for a {title} to work with industry-leading clients and cutting-edge technology. This role offers excellent career growth opportunities and the chance to work on innovative projects that drive business success.",
        
        "Our client, a leading {industry} company, is looking for a talented {title} to join their team. This role offers competitive compensation, excellent benefits, and the opportunity to work with the latest technologies and methodologies.",
        
        "Are you a passionate {title} looking to take your career to the next level? Join our award-winning team and work on exciting projects that challenge conventional thinking and drive innovation in the {industry} sector."
    ]
    
    requirements_templates = [
        [
            "Bachelor's degree in relevant field or equivalent experience",
            "3-5 years of relevant work experience",
            "Strong analytical and problem-solving skills",
            "Excellent communication and teamwork abilities",
            "Proficiency in relevant tools and technologies"
        ],
        [
            "Proven track record in similar role",
            "Strong technical skills and industry knowledge",
            "Experience with agile methodologies",
            "Leadership and mentoring capabilities",
            "Customer-focused mindset"
        ],
        [
            "Advanced degree preferred",
            "5+ years of progressive experience",
            "Expertise in relevant technologies",
            "Strong project management skills",
            "Ability to work in fast-paced environment"
        ]
    ]
    
    created_count = 0
    current_date = datetime.utcnow()
    
    # Create expiry dates between 2 weeks and 1 month from now
    min_expiry = current_date + timedelta(weeks=2)
    max_expiry = current_date + timedelta(weeks=4)
    
    try:
        for i in range(100):
            # Select random recruiter
            recruiter = random.choice(recruiters)
            
            # Generate job data
            title = random.choice(job_titles)
            company = random.choice(companies)
            location = random.choice(locations)
            industry = random.choice(industries)
            job_type = random.choice(job_types)
            work_type = random.choice(work_types)
            
            # Determine experience level based on title
            if any(word in title.lower() for word in ["senior", "lead", "manager", "director", "architect"]):
                exp_level = "senior"
            elif any(word in title.lower() for word in ["junior", "intern", "trainee", "graduate"]):
                exp_level = "entry"
            elif any(word in title.lower() for word in ["executive", "chief", "head"]):
                exp_level = "executive"
            else:
                exp_level = "mid"
            
            # Generate salary
            salary_min, salary_max = salary_ranges[exp_level]
            salary = f"R{random.randint(salary_min, salary_max):,} - R{random.randint(salary_max, salary_max + 20000):,}"
            
            # Generate random expiry date within range
            days_to_add = random.randint(14, 30)
            expiry_date = current_date + timedelta(days=days_to_add)
            
            # Generate posting date (1-30 days ago)
            days_ago = random.randint(1, 30)
            posted_date = current_date - timedelta(days=days_ago)
            
            # Generate description and requirements
            description = random.choice(description_templates).format(
                title=title,
                industry=industry.lower()
            )
            
            requirements = random.choice(requirements_templates).copy()
            
            # Add specific requirements based on job type
            if "developer" in title.lower() or "engineer" in title.lower():
                requirements.append("Strong programming and technical skills")
                requirements.append("Experience with modern development frameworks")
            elif "manager" in title.lower():
                requirements.append("Leadership and team management experience")
                requirements.append("Strategic thinking and planning abilities")
            elif "analyst" in title.lower():
                requirements.append("Strong analytical and data interpretation skills")
                requirements.append("Proficiency in relevant analysis tools")
            
            # Create job document
            job_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "company_id": recruiter["id"],
                "company_name": recruiter.get("company_profile", {}).get("company_name", company),
                "logo_url": recruiter.get("company_profile", {}).get("company_logo_url"),
                "location": location,
                "job_type": job_type,
                "work_type": work_type,
                "industry": industry,
                "salary": salary,
                "description": description,
                "requirements": requirements,
                "posted_by": recruiter["id"],
                "posted_date": posted_date,
                "expiry_date": expiry_date,
                "is_active": True,
                "featured": random.random() < 0.1,  # 10% chance of being featured
                "created_at": posted_date,
                "updated_at": posted_date
            }
            
            # Insert job
            result = await db.jobs.insert_one(job_data)
            
            if result.inserted_id:
                created_count += 1
                
                print(f"✅ {created_count:3d}/100: {title} at {company} ({location})")
                print(f"    💰 {salary}")
                print(f"    📅 Expires: {expiry_date.strftime('%Y-%m-%d')} ({days_to_add} days from now)")
                print(f"    🏢 Posted by: {recruiter.get('email', 'Unknown recruiter')}")
                
                if created_count % 10 == 0:
                    print(f"\n📊 Progress: {created_count}/100 jobs created")
                    print("-" * 40)
            else:
                print(f"❌ Failed to create job: {title}")
        
        print(f"\n🎉 Successfully created {created_count} diverse job postings!")
        
        # Generate summary statistics
        total_jobs = await db.jobs.count_documents({"is_active": True})
        active_jobs = await db.jobs.count_documents({
            "is_active": True,
            "expiry_date": {"$gt": datetime.utcnow()}
        })
        
        print(f"📊 Database Summary:")
        print(f"   • Total jobs in database: {total_jobs}")
        print(f"   • Active (non-expired) jobs: {active_jobs}")
        print(f"   • Jobs created in this run: {created_count}")
        
        # Show expiry distribution
        print(f"\n📅 Expiry Date Distribution:")
        
        # Jobs expiring in next 2 weeks
        two_weeks = await db.jobs.count_documents({
            "is_active": True,
            "expiry_date": {
                "$gte": datetime.utcnow(),
                "$lt": datetime.utcnow() + timedelta(weeks=2)
            }
        })
        
        # Jobs expiring in 2-4 weeks
        four_weeks = await db.jobs.count_documents({
            "is_active": True,
            "expiry_date": {
                "$gte": datetime.utcnow() + timedelta(weeks=2),
                "$lt": datetime.utcnow() + timedelta(weeks=4)
            }
        })
        
        print(f"   • Expiring in next 2 weeks: {two_weeks}")
        print(f"   • Expiring in 2-4 weeks: {four_weeks}")
        
        # Show location distribution
        print(f"\n📍 Top Locations:")
        location_counts = {}
        async for job in db.jobs.find({"is_active": True}, {"location": 1}):
            loc = job.get("location", "Unknown")
            location_counts[loc] = location_counts.get(loc, 0) + 1
        
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        for loc, count in sorted_locations[:5]:
            print(f"   • {loc}: {count} jobs")
        
        # Show job type distribution
        print(f"\n💼 Job Types:")
        job_type_counts = {}
        async for job in db.jobs.find({"is_active": True}, {"job_type": 1}):
            jtype = job.get("job_type", "Unknown")
            job_type_counts[jtype] = job_type_counts.get(jtype, 0) + 1
        
        for jtype, count in sorted(job_type_counts.items()):
            print(f"   • {jtype}: {count} jobs")
            
    except Exception as e:
        print(f"❌ Error creating jobs: {str(e)}")
        return False
    
    finally:
        client.close()
    
    return True

async def main():
    """Main function"""
    print("🚀 Job Rocket - Diverse Job Creation Script")
    print("=" * 60)
    
    success = await create_100_diverse_jobs()
    
    if success:
        print("\n✅ Job creation completed successfully!")
        print("🔍 The job search functionality now has a rich dataset to work with")
        print("\n💡 Test searches with:")
        print("   🎯 Positions: 'developer', 'engineer', 'manager', 'analyst', 'designer'")
        print("   📍 Locations: 'johannesburg', 'cape town', 'durban', 'sandton'")
        print("   🏢 Industries: 'technology', 'financial services', 'healthcare'")
        print("   💰 Various salary ranges and experience levels")
        print("   📅 Different expiry dates (2 weeks to 1 month)")
    else:
        print("\n❌ Job creation failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())