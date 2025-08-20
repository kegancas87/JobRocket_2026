#!/usr/bin/env python3
"""
Fix existing jobs and add more comprehensive job listings
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timedelta
import random

async def fix_and_expand_jobs():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'jobrocket')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔧 Fixing existing jobs and adding new job listings...")
    
    # Get companies to use their IDs and names
    companies = await db.companies.find({}).to_list(10)
    company_map = {comp["id"]: comp["name"] for comp in companies}
    
    print(f"Found {len(companies)} companies: {list(company_map.values())}")
    
    # Fix existing jobs - update them to match the Job model requirements
    print("\n📝 Fixing existing jobs...")
    existing_jobs = await db.jobs.find({}).to_list(100)
    
    for job in existing_jobs:
        # Prepare updated job data
        updated_data = {}
        
        # Add company_name if missing
        if "company_name" not in job:
            company_name = company_map.get(job.get("company_id"), "Unknown Company")
            updated_data["company_name"] = company_name
        
        # Fix salary field - convert salary_min/salary_max to single salary string
        if "salary" not in job:
            salary_min = job.get("salary_min", 250000)
            salary_max = job.get("salary_max", 450000)
            updated_data["salary"] = f"R{salary_min:,} - R{salary_max:,} per year"
        
        # Fix job_type enum values
        if job.get("job_type") == "full_time":
            updated_data["job_type"] = "Permanent"
        elif job.get("job_type") == "contract":
            updated_data["job_type"] = "Contract"
        
        # Fix work_type enum values  
        if job.get("work_type") == "hybrid":
            updated_data["work_type"] = "Hybrid"
        elif job.get("work_type") == "remote":
            updated_data["work_type"] = "Remote"
        elif job.get("work_type") == "on_site":
            updated_data["work_type"] = "Onsite"
        
        # Update the job if we have changes
        if updated_data:
            await db.jobs.update_one(
                {"id": job["id"]},
                {"$set": updated_data}
            )
            print(f"✅ Fixed job: {job.get('title', 'Unknown')} - Added {list(updated_data.keys())}")
    
    print(f"\n📊 Creating expanded job listings...")
    
    # Create many more diverse job listings
    new_jobs = []
    
    # Tech Jobs
    tech_jobs = [
        {
            "title": "Full Stack Developer",
            "description": """Join our innovative tech team as a Full Stack Developer! 

**What You'll Do:**
- Develop and maintain web applications using React, Node.js, and MongoDB
- Collaborate with designers and product managers to create user-friendly interfaces
- Write clean, maintainable, and well-documented code
- Participate in code reviews and contribute to technical discussions
- Optimize applications for maximum speed and scalability

**Requirements:**
- 3+ years of experience in full-stack development
- Proficiency in JavaScript, React, Node.js, and database technologies
- Experience with version control (Git) and agile development
- Strong problem-solving skills and attention to detail
- Bachelor's degree in Computer Science or related field preferred

**Benefits:**
- Competitive salary with performance bonuses
- Flexible working hours and remote work options
- Medical aid and retirement contributions
- Professional development opportunities""",
            "location": "Cape Town, South Africa",
            "salary": "R380,000 - R520,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Technology",
            "experience": "3-5 years",
            "qualifications": "Bachelor's degree preferred, 3+ years experience"
        },
        {
            "title": "DevOps Engineer", 
            "description": """We're seeking a skilled DevOps Engineer to streamline our development and deployment processes.

**Key Responsibilities:**
- Design and implement CI/CD pipelines using Jenkins, GitLab CI, or GitHub Actions
- Manage cloud infrastructure on AWS/Azure with Infrastructure as Code (Terraform)
- Monitor system performance and implement automated alerting
- Ensure security best practices across all environments
- Collaborate with development teams to optimize deployment strategies

**Technical Skills:**
- Experience with containerization (Docker, Kubernetes)
- Knowledge of cloud platforms (AWS, Azure, or GCP)
- Scripting languages (Python, Bash, PowerShell)
- Infrastructure as Code tools (Terraform, CloudFormation)
- Monitoring tools (Prometheus, Grafana, ELK Stack)

**What We Offer:**
- Cutting-edge technology stack
- Remote-first culture with flexible hours
- Annual learning budget for certifications
- Stock options and competitive benefits""",
            "location": "Johannesburg, South Africa",
            "salary": "R450,000 - R650,000 per year",
            "job_type": "Permanent",
            "work_type": "Remote", 
            "industry": "Technology",
            "experience": "4-7 years",
            "qualifications": "Relevant certifications preferred, 4+ years DevOps experience"
        },
        {
            "title": "Mobile App Developer (React Native)",
            "description": """Build the next generation of mobile applications with our growing product team!

**Role Overview:**
- Develop cross-platform mobile applications using React Native
- Work closely with UX/UI designers to implement pixel-perfect designs
- Integrate mobile apps with RESTful APIs and third-party services
- Optimize app performance and ensure smooth user experiences
- Participate in app store submission and deployment processes

**Requirements:**
- 2+ years of React Native development experience
- Strong JavaScript/TypeScript skills
- Experience with mobile app deployment (iOS App Store, Google Play)
- Knowledge of native mobile development (Swift/Kotlin) is a plus
- Understanding of mobile UI/UX principles

**Exciting Projects:**
- E-commerce mobile platform serving 100k+ users
- Real-time chat and messaging features
- Offline functionality and data synchronization
- Integration with payment gateways and financial services

**Perks:**
- Latest MacBook Pro and development tools
- Flexible PTO and work-life balance focus
- Team building events and company retreats""",
            "location": "Durban, South Africa", 
            "salary": "R320,000 - R480,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Technology",
            "experience": "2-4 years",
            "qualifications": "2+ years React Native experience, mobile development background"
        },
        {
            "title": "Python Backend Developer",
            "description": """Join our backend team to build scalable APIs and microservices that power millions of requests daily.

**What You'll Build:**
- RESTful APIs using FastAPI, Django, or Flask
- Microservices architecture with proper documentation
- Database design and optimization (PostgreSQL, MongoDB)
- Integration with third-party services and payment gateways
- Automated testing and deployment pipelines

**Technical Requirements:**
- 3+ years of Python development experience
- Strong knowledge of web frameworks (FastAPI, Django, Flask)
- Database design and ORM experience
- API design and RESTful service development
- Understanding of software design patterns

**Nice to Have:**
- Experience with async programming and WebSockets
- Knowledge of message queues (Redis, RabbitMQ)
- Container orchestration (Docker, Kubernetes)
- Cloud platform experience (AWS, GCP)

**Growth Opportunities:**
- Mentorship from senior engineers
- Technical conference attendance
- Open source contribution time
- Career progression to tech lead roles""",
            "location": "Remote, South Africa",
            "salary": "R360,000 - R540,000 per year", 
            "job_type": "Permanent",
            "work_type": "Remote",
            "industry": "Technology",
            "experience": "3-6 years",
            "qualifications": "3+ years Python experience, web framework knowledge"
        }
    ]
    
    # Design Jobs
    design_jobs = [
        {
            "title": "Senior UX Designer",
            "description": """Lead user experience design for our flagship products used by thousands of customers daily.

**Your Impact:**
- Conduct user research and usability testing to inform design decisions
- Create user journey maps, wireframes, and high-fidelity prototypes
- Design intuitive interfaces that solve complex user problems
- Collaborate with product managers and developers throughout the design process
- Establish and maintain design systems and style guides

**Experience & Skills:**
- 4+ years of UX design experience with a strong portfolio
- Proficiency in design tools (Figma, Sketch, Adobe Creative Suite)
- Experience with user research methodologies and usability testing
- Understanding of accessibility standards and inclusive design
- Excellent communication and presentation skills

**What Makes This Role Special:**
- Direct impact on product strategy and user satisfaction
- Work with cross-functional teams in an agile environment
- Access to user analytics and research tools
- Opportunity to mentor junior designers

**Benefits Package:**
- Competitive salary with annual reviews
- Creative workspace with latest design tools
- Professional development budget
- Flexible working arrangements""",
            "location": "Cape Town, South Africa",
            "salary": "R420,000 - R580,000 per year",
            "job_type": "Permanent", 
            "work_type": "Hybrid",
            "industry": "Design",
            "experience": "4-7 years",
            "qualifications": "4+ years UX design, strong portfolio, design tool proficiency"
        },
        {
            "title": "Product Designer",
            "description": """Shape the future of our products by designing beautiful, functional user experiences from concept to launch.

**Day-to-Day Responsibilities:**
- Partner with product managers to define feature requirements
- Create user-centered design solutions based on customer feedback
- Design and iterate on wireframes, prototypes, and visual designs
- Conduct design reviews and gather stakeholder feedback
- Ensure consistent design implementation across all platforms

**What We're Looking For:**
- 2-4 years of product design experience
- Strong visual design skills with attention to detail
- Experience designing for web and mobile platforms
- Collaborative mindset with excellent communication skills
- Portfolio showcasing end-to-end design process

**Tools & Technologies:**
- Figma for design and prototyping
- Miro for collaborative workshops
- Analytics tools for data-driven design decisions
- Design systems and component libraries

**Career Growth:**
- Clear career progression path to Senior Product Designer
- Regular design critiques and feedback sessions
- Conference attendance and design community involvement
- Cross-functional project leadership opportunities""",
            "location": "Johannesburg, South Africa",
            "salary": "R300,000 - R450,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid", 
            "industry": "Design",
            "experience": "2-4 years",
            "qualifications": "2-4 years product design, web/mobile experience, strong portfolio"
        }
    ]
    
    # Marketing & Business Jobs
    marketing_jobs = [
        {
            "title": "Digital Marketing Manager",
            "description": """Lead our digital marketing efforts to drive brand awareness and customer acquisition across multiple channels.

**Strategic Responsibilities:**
- Develop and execute comprehensive digital marketing strategies
- Manage multi-channel campaigns (Google Ads, Facebook, LinkedIn, Email)
- Optimize conversion funnels and improve customer acquisition costs
- Analyze campaign performance and provide actionable insights
- Collaborate with content, design, and product teams

**Key Skills Required:**
- 3+ years of digital marketing experience with proven ROI results
- Expertise in Google Analytics, Google Ads, and social media advertising
- Email marketing automation and CRM management
- A/B testing and conversion rate optimization
- Strong analytical skills with data-driven decision making

**Campaign Types You'll Manage:**
- Lead generation campaigns for B2B clients
- E-commerce conversion optimization
- Brand awareness and thought leadership content
- Retargeting and customer lifecycle campaigns

**Growth & Development:**
- Marketing budget management experience
- Team leadership and mentorship opportunities
- Access to premium marketing tools and training
- Performance-based bonuses tied to campaign success""",
            "location": "Cape Town, South Africa",
            "salary": "R350,000 - R500,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Marketing",
            "experience": "3-5 years",
            "qualifications": "3+ years digital marketing, Google Ads/Analytics certified preferred"
        },
        {
            "title": "Content Marketing Specialist", 
            "description": """Create compelling content that educates, engages, and converts our target audience across all digital touchpoints.

**Content Creation:**
- Write blog posts, whitepapers, case studies, and social media content
- Develop video scripts and work with production teams
- Create email marketing campaigns and newsletter content
- Optimize all content for SEO and search visibility
- Maintain brand voice and messaging consistency

**Content Strategy:**
- Research industry trends and competitor content strategies
- Plan content calendars aligned with product launches and campaigns
- Collaborate with subject matter experts for technical content
- Track content performance and optimize based on engagement metrics

**Required Experience:**
- 2+ years of content marketing or copywriting experience
- Excellent writing skills with portfolio of published work
- SEO knowledge and experience with content management systems
- Social media management and community engagement
- Basic design skills for creating visual content

**What You'll Love:**
- Creative freedom to experiment with new content formats
- Direct impact on brand storytelling and customer education
- Collaboration with industry thought leaders
- Professional writing and content strategy development""",
            "location": "Durban, South Africa",
            "salary": "R280,000 - R380,000 per year",
            "job_type": "Permanent", 
            "work_type": "Remote",
            "industry": "Marketing",
            "experience": "2-4 years",
            "qualifications": "2+ years content marketing, strong writing portfolio, SEO knowledge"
        }
    ]
    
    # Data & Analytics Jobs
    data_jobs = [
        {
            "title": "Senior Data Analyst",
            "description": """Transform complex data into actionable business insights that drive strategic decision-making across the organization.

**Analytics Focus Areas:**
- Customer behavior analysis and segmentation
- Product performance metrics and KPI tracking
- Marketing campaign effectiveness and attribution
- Revenue forecasting and business intelligence reporting
- A/B testing design and statistical analysis

**Technical Requirements:**
- 4+ years of data analysis experience with strong SQL skills
- Proficiency in Python or R for data manipulation and analysis
- Experience with BI tools (Tableau, Power BI, or Looker)
- Statistical analysis and hypothesis testing knowledge
- Database management and data warehouse experience

**Key Responsibilities:**
- Build automated dashboards and reporting systems
- Collaborate with stakeholders to define success metrics
- Identify trends and anomalies in business data
- Present findings to executive leadership
- Mentor junior analysts and establish best practices

**Advanced Skills (Nice to Have):**
- Machine learning and predictive modeling
- Experience with cloud data platforms (AWS, GCP, Azure)
- ETL pipeline development and data engineering
- Advanced visualization and storytelling with data

**Impact & Growth:**
- Direct influence on product and business strategy
- Leadership opportunities in cross-functional projects
- Access to cutting-edge analytics tools and training
- Path to Senior/Principal Data Scientist roles""",
            "location": "Johannesburg, South Africa",
            "salary": "R480,000 - R680,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Data Science",
            "experience": "4-7 years", 
            "qualifications": "4+ years data analysis, SQL/Python proficiency, BI tools experience"
        },
        {
            "title": "Machine Learning Engineer",
            "description": """Build and deploy ML models that power intelligent features across our product suite, serving millions of users.

**ML Engineering:**
- Design and implement machine learning pipelines from research to production
- Deploy models using MLOps best practices and monitoring systems
- Optimize model performance and scalability for high-traffic applications
- Collaborate with data scientists to productionize research models
- Implement A/B testing frameworks for model performance evaluation

**Technical Stack:**
- Python, TensorFlow, PyTorch for model development
- Kubernetes and Docker for model deployment
- MLflow or similar for experiment tracking and model versioning
- Cloud platforms (AWS SageMaker, GCP AI Platform, Azure ML)
- Real-time and batch inference systems

**Model Applications:**
- Recommendation systems for personalized user experiences
- Natural language processing for content analysis
- Computer vision for image and video processing
- Predictive analytics for business forecasting
- Anomaly detection for security and fraud prevention

**What You'll Need:**
- 3+ years of ML engineering or similar experience
- Strong software engineering skills with production ML experience
- Experience with ML frameworks, model deployment, and monitoring
- Understanding of distributed systems and cloud infrastructure
- Advanced degree in Computer Science, Statistics, or related field preferred

**Innovation Opportunities:**
- Research and implement state-of-the-art ML techniques
- Contribute to open source ML projects and research papers
- Attend ML conferences and technical meetups
- Collaborate with top-tier data science and engineering teams""",
            "location": "Cape Town, South Africa", 
            "salary": "R550,000 - R750,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Technology",
            "experience": "3-6 years",
            "qualifications": "3+ years ML engineering, production ML experience, advanced degree preferred"
        }
    ]
    
    # Sales & Customer Success Jobs
    sales_jobs = [
        {
            "title": "Enterprise Account Manager",
            "description": """Drive revenue growth by managing and expanding relationships with our largest enterprise clients.

**Sales & Account Management:**
- Manage portfolio of enterprise accounts worth R10M+ in annual revenue
- Identify upselling and cross-selling opportunities within existing accounts
- Develop strategic account plans and quarterly business reviews
- Collaborate with technical teams on solution design and implementation
- Negotiate complex contracts and pricing agreements

**Relationship Building:**
- Serve as primary point of contact for C-level executives and decision makers
- Build trust through consultative selling and industry expertise
- Coordinate internal resources to ensure client success and satisfaction
- Present at industry conferences and client events
- Maintain deep understanding of client business objectives and challenges

**Experience Required:**
- 5+ years of B2B enterprise sales or account management experience
- Proven track record of meeting/exceeding sales targets (>R20M annually)
- Experience with complex sales cycles (6-18 months)
- Strong presentation and negotiation skills
- Industry knowledge in technology or professional services

**Success Metrics:**
- Account revenue growth and retention rates
- New contract wins within existing accounts
- Client satisfaction scores and references
- Pipeline development and forecasting accuracy

**Compensation & Benefits:**
- Competitive base salary plus uncapped commission structure
- OTE of R800K - R1.2M+ for top performers
- Equity participation and performance bonuses
- Comprehensive benefits and professional development budget""",
            "location": "Johannesburg, South Africa",
            "salary": "R450,000 - R650,000 base + commission",
            "job_type": "Permanent",
            "work_type": "Hybrid", 
            "industry": "Sales",
            "experience": "5-8 years",
            "qualifications": "5+ years enterprise sales, proven track record, industry knowledge"
        },
        {
            "title": "Customer Success Manager",
            "description": """Ensure our customers achieve their business objectives and maximize value from our platform while driving retention and expansion.

**Customer Success Strategy:**
- Develop success plans and KPIs for assigned customer portfolio
- Conduct regular health checks and business reviews with key stakeholders
- Identify at-risk accounts and implement retention strategies
- Drive product adoption and feature utilization across client organizations
- Collaborate with sales teams on expansion opportunities

**Daily Responsibilities:**
- Monitor customer usage data and engagement metrics
- Provide training and onboarding support for new users
- Resolve escalated customer issues and coordinate with technical teams
- Create success stories and case studies showcasing customer wins
- Maintain accurate records in CRM and provide regular reporting

**Skills & Experience:**
- 2-4 years in customer success, account management, or consulting
- Strong analytical skills with ability to interpret customer data
- Excellent communication and presentation abilities
- Experience with SaaS platforms and technology solutions
- Project management and cross-functional collaboration skills

**Customer Portfolio:**
- 50-80 mid-market accounts with ARR of R500K - R2M each
- Mix of industries including tech, finance, healthcare, and retail
- Focus on driving net revenue retention >110%
- Expansion opportunities through new products and user growth

**Growth & Development:**
- Clear path to Senior CSM and team leadership roles
- Customer success certification and training programs
- Direct impact on company growth and customer satisfaction
- Collaboration with product teams on feature development""",
            "location": "Cape Town, South Africa",
            "salary": "R320,000 - R450,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Customer Success", 
            "experience": "2-4 years",
            "qualifications": "2-4 years customer success/account management, SaaS experience preferred"
        }
    ]
    
    # Operations & HR Jobs  
    operations_jobs = [
        {
            "title": "Operations Manager",
            "description": """Streamline business processes and drive operational excellence across all departments to support rapid company growth.

**Operational Leadership:**
- Design and implement scalable business processes and workflows
- Manage cross-functional projects and process improvement initiatives  
- Develop KPIs and reporting systems to track operational performance
- Coordinate between departments to ensure smooth daily operations
- Lead digital transformation and automation projects

**Process Optimization:**
- Analyze current workflows and identify inefficiencies or bottlenecks
- Implement lean methodologies and continuous improvement practices
- Standardize procedures across teams and document best practices
- Evaluate and implement new tools and technologies
- Train teams on new processes and ensure adoption

**Required Background:**
- 4+ years of operations management or business process improvement experience
- Strong analytical and problem-solving skills with data-driven approach
- Project management experience with complex, multi-stakeholder initiatives
- Change management and team leadership capabilities
- Bachelor's degree in Business, Operations, or related field

**Key Focus Areas:**
- Customer onboarding and lifecycle management processes
- Sales operations and CRM optimization
- Financial reporting and budget management support
- Vendor management and procurement processes
- Quality assurance and compliance management

**Leadership Opportunities:**
- Build and lead operations team as company scales
- Represent operations in strategic planning and executive meetings
- Drive culture of operational excellence and continuous improvement
- Mentor other managers and contribute to leadership development""",
            "location": "Durban, South Africa", 
            "salary": "R420,000 - R580,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Operations",
            "experience": "4-7 years",
            "qualifications": "4+ years operations management, process improvement, project management"
        },
        {
            "title": "HR Business Partner",
            "description": """Partner with business leaders to align HR strategies with company objectives while fostering a positive employee experience.

**Strategic HR Partnership:**
- Work closely with department heads on workforce planning and organizational design
- Provide guidance on performance management, employee development, and succession planning
- Lead talent acquisition strategies and hiring process optimization
- Design compensation and benefits programs aligned with market standards
- Drive employee engagement initiatives and culture development

**Employee Relations:**
- Serve as primary HR contact for assigned business units (150-200 employees)
- Handle complex employee relations issues and conflict resolution
- Conduct investigations and ensure compliance with labor laws
- Provide coaching to managers on HR policies and best practices
- Support disciplinary processes and termination procedures when necessary

**Talent Development:**
- Partner with L&D teams to identify skills gaps and training needs
- Create career development paths and internal mobility programs
- Facilitate performance review processes and calibration sessions
- Support leadership development and high-potential employee programs
- Design retention strategies for critical roles and top performers

**Experience & Qualifications:**
- 3+ years of HR business partner or generalist experience
- Strong knowledge of South African labor law and HR compliance
- Experience with HRIS systems and people analytics
- Excellent interpersonal and communication skills
- Bachelor's degree in HR, Psychology, or related field; SHRM certification preferred

**Impact & Growth:**
- Direct influence on company culture and employee satisfaction
- Partnership with senior leadership on strategic workforce decisions
- Opportunity to build HR programs from the ground up
- Professional development through HR conferences and certification programs""",
            "location": "Johannesburg, South Africa",
            "salary": "R380,000 - R520,000 per year", 
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Human Resources",
            "experience": "3-6 years",
            "qualifications": "3+ years HR business partner experience, SA labor law knowledge"
        }
    ]
    
    # Finance Jobs
    finance_jobs = [
        {
            "title": "Senior Financial Analyst",
            "description": """Drive financial planning and analysis to support strategic decision-making and business growth initiatives.

**Financial Analysis & Reporting:**
- Prepare monthly, quarterly, and annual financial reports for executive leadership
- Conduct variance analysis and provide insights on budget vs. actual performance
- Build financial models for business planning, forecasting, and scenario analysis
- Support M&A due diligence and integration planning
- Analyze profitability by product, customer segment, and geographic region

**Strategic Planning Support:**
- Lead annual budgeting process and quarterly forecast updates
- Partner with department heads on resource planning and investment decisions
- Evaluate new business opportunities and pricing strategies
- Conduct competitive analysis and market research to inform strategy
- Present financial recommendations to executive team and board of directors

**Technical Skills Required:**
- 4+ years of financial analysis experience, preferably in high-growth companies
- Advanced Excel and financial modeling skills
- Experience with ERP systems (SAP, NetSuite) and BI tools (Tableau, Power BI)
- Strong understanding of accounting principles and financial statements
- CPA, CA(SA), or advanced finance degree preferred

**Key Projects:**
- Revenue recognition analysis for new product launches
- Unit economics modeling for subscription business
- ROI analysis for marketing and sales investments
- Cash flow forecasting and working capital management
- International expansion financial planning

**Career Development:**
- Path to Finance Manager and Controller roles
- Exposure to all aspects of finance and executive decision-making
- Professional development support for CPA/CA certification
- Cross-functional projects with sales, marketing, and operations teams""",
            "location": "Cape Town, South Africa",
            "salary": "R450,000 - R620,000 per year",
            "job_type": "Permanent",
            "work_type": "Hybrid",
            "industry": "Finance",
            "experience": "4-7 years",
            "qualifications": "4+ years financial analysis, advanced Excel, CPA/CA preferred"
        }
    ]
    
    # Combine all job categories
    all_new_jobs = tech_jobs + design_jobs + marketing_jobs + data_jobs + sales_jobs + operations_jobs + finance_jobs
    
    # Assign jobs to companies and add required fields
    for i, job_template in enumerate(all_new_jobs):
        # Cycle through companies
        company_id = companies[i % len(companies)]["id"]
        company_name = companies[i % len(companies)]["name"]
        
        # Get a recruiter from this company
        recruiters = await db.users.find({"company_id": company_id, "role": "recruiter"}).to_list(10)
        posted_by = recruiters[0]["id"] if recruiters else companies[0]["id"]  # Fallback to first company
        
        # Create job with all required fields
        job_id = str(uuid.uuid4())
        posted_date = datetime.utcnow() - timedelta(days=random.randint(1, 25))
        expiry_date = posted_date + timedelta(days=35)
        
        job = {
            "id": job_id,
            "company_id": company_id,
            "company_name": company_name,
            "posted_by": posted_by,
            "posted_date": posted_date,
            "expiry_date": expiry_date,
            "is_active": True,
            "featured": random.choice([True, False, False, False]),  # 25% chance of featured
            "external_application_link": None,  # Use easy apply
            "application_email": None,
            "closing_date": None,
            **job_template
        }
        
        new_jobs.append(job)
        print(f"✅ Created: {job_template['title']} at {company_name}")
    
    # Insert all new jobs
    if new_jobs:
        await db.jobs.insert_many(new_jobs)
        print(f"\n🎉 Successfully created {len(new_jobs)} new job listings!")
    
    # Verify final job count
    total_jobs = await db.jobs.count_documents({})
    active_jobs = await db.jobs.count_documents({"is_active": True})
    featured_jobs = await db.jobs.count_documents({"featured": True})
    
    print(f"\n📊 Final Statistics:")
    print(f"   • Total jobs: {total_jobs}")
    print(f"   • Active jobs: {active_jobs}")
    print(f"   • Featured jobs: {featured_jobs}")
    print(f"   • Companies with jobs: {len(companies)}")
    
    # Show job distribution by industry
    print(f"\n📋 Jobs by Industry:")
    pipeline = [
        {"$group": {"_id": "$industry", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    job_stats = await db.jobs.aggregate(pipeline).to_list(20)
    for stat in job_stats:
        print(f"   • {stat['_id']}: {stat['count']} jobs")
    
    print(f"\n🚀 Job listings are now ready! The platform should show all active jobs.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_and_expand_jobs())