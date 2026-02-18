# 🚀 Job Rocket Demo Users & Test Accounts

## 📋 Complete Demo User Credentials

### 👑 ADMIN USER

#### **ADMIN ACCOUNT**
- **Email:** `admin@jobrocket.com`  
- **Password:** `admin123`
- **Name:** Admin User
- **Role:** Platform Administrator
- **Access:** Full admin dashboard, discount code management, usage statistics

---

### 👤 JOB SEEKERS

#### 1. **BEGINNER USER** (25 Points)
- **Email:** `sarah.beginner@demo.com`  
- **Password:** `demo123`
- **Name:** Sarah Johnson
- **Location:** Cape Town, South Africa
- **Profile Status:** Basic information, recent graduate
- **Skills:** HTML, CSS, JavaScript (3 skills)
- **Education:** Bachelor of Computer Science from UCT
- **Experience:** Recent graduate, no work history
- **Gamification:** Low completion score (25 points)

#### 2. **INTERMEDIATE USER** (65 Points)  
- **Email:** `alex.intermediate@demo.com`
- **Password:** `demo123`
- **Name:** Alex Rodriguez
- **Location:** Johannesburg, South Africa
- **Profile Status:** Mid-level developer profile
- **Skills:** React, Node.js, Python, MongoDB, Express, JavaScript, TypeScript (7 skills)
- **Education:** Bachelor of Science in IT from Wits University
- **Experience:** 2 years at StartupCo as Junior Developer
- **Achievements:** Employee of the Month, Hackathon Winner
- **Gamification:** Intermediate completion (65 points)

#### 3. **SENIOR USER** (100 Points)
- **Email:** `mike.senior@demo.com`
- **Password:** `demo123`
- **Name:** Mike Thompson
- **Location:** Durban, South Africa
- **Profile Status:** Complete senior developer profile
- **Skills:** React, Python, Django, AWS, Docker, Kubernetes, PostgreSQL, Redux, TypeScript, GraphQL (10+ skills)
- **Education:** Bachelor of Engineering from Stellenbosch University
- **Experience:** 5+ years across TechCorp and DevStudio
- **Achievements:** AWS Certified, Scrum Master Certified, Tech Lead of the Year
- **Gamification:** Complete profile (100 points)

---

### 👔 RECRUITERS

#### 1. **TECHCORP RECRUITER**
- **Email:** `lisa.martinez@techcorp.demo`
- **Password:** `demo123`
- **Name:** Lisa Martinez  
- **Company:** TechCorp Solutions
- **Role:** Senior Talent Acquisition Specialist
- **Industry:** Technology Consulting
- **Posted Jobs:** Senior React Developer, Junior Frontend Developer
- **Profile Status:** Complete company profile (100 points)

#### 2. **DIGITAL AGENCY RECRUITER**  
- **Email:** `david.wilson@innovate.demo`
- **Password:** `demo123`
- **Name:** David Wilson
- **Company:** Innovate Digital Agency
- **Role:** Head of Human Resources
- **Industry:** Digital Marketing & Development
- **Posted Jobs:** UX/UI Designer, Product Manager
- **Profile Status:** Complete company profile (100 points)

#### 3. **DATA ANALYTICS RECRUITER**
- **Email:** `emma.davis@dataflow.demo`
- **Password:** `demo123`
- **Name:** Emma Davis
- **Company:** DataFlow Analytics
- **Role:** Talent Acquisition Manager
- **Industry:** Data Science & Analytics
- **Posted Jobs:** Data Scientist
- **Profile Status:** Complete company profile (100 points)

---

## 🏢 DEMO COMPANIES

### 1. **TechCorp Solutions**
- **Industry:** Technology Consulting
- **Size:** 50-200 employees
- **Location:** Cape Town, South Africa
- **Description:** Leading technology consulting firm specializing in digital transformation
- **Jobs Posted:** Senior React Developer, Junior Frontend Developer

### 2. **Innovate Digital Agency**
- **Industry:** Digital Marketing & Development
- **Size:** 10-50 employees
- **Location:** Johannesburg, South Africa
- **Description:** Creative digital agency focused on cutting-edge web development
- **Jobs Posted:** UX/UI Designer, Product Manager

### 3. **DataFlow Analytics**
- **Industry:** Data Science & Analytics
- **Size:** 20-100 employees
- **Location:** Durban, South Africa
- **Description:** Data science company helping businesses make data-driven decisions
- **Jobs Posted:** Data Scientist

---

## 💼 SAMPLE JOBS CREATED

### **Active Job Listings:**
1. **Senior React Developer** - TechCorp Solutions (R450k-R650k)
2. **UX/UI Designer** - Innovate Digital Agency (R300k-R450k)
3. **Data Scientist** - DataFlow Analytics (R400k-R600k)
4. **Junior Frontend Developer** - TechCorp Solutions (R250k-R350k)
5. **Product Manager** - Innovate Digital Agency (R500k-R700k)

### **Job Features:**
- All jobs have detailed descriptions and requirements
- Mix of experience levels (entry, mid, senior)
- Different work types (hybrid, on-site, remote)
- Realistic South African salary ranges
- Sample applications from job seekers

---

## 🏷️ DEMO DISCOUNT CODES

### **Active Codes:**
1. **WELCOME20** - 20% off (min R1000 purchase, max R1000 discount)
2. **NEWUSER15** - 15% off (min R500 purchase)
3. **SAVE500** - R500 fixed discount (min R2000 purchase)

### **Test Codes:**
4. **EXPIRED10** - 10% off (EXPIRED - for testing validation)

---

## 📝 SAMPLE APPLICATION DATA

### **Job Applications Created:**
- Mike Thompson applied for Senior React Developer (reviewed)
- Alex Rodriguez applied for Senior React Developer (pending)
- Sarah Johnson applied for Junior Frontend Developer (pending)
- Alex Rodriguez applied for Junior Frontend Developer (shortlisted)
- Mike Thompson applied for Data Scientist (interviewed)

### **Application Features:**
- Different application statuses for testing
- Cover letters and applicant snapshots
- Application date tracking
- Recruiter application management

---

## 🧪 TESTING SCENARIOS

### **Job Seeker Testing:**
1. **Profile Completion:** Test gamification with Sarah (25 points), Alex (65 points), Mike (100 points)
2. **Job Applications:** Apply to jobs and track application status
3. **Profile Updates:** Update skills, experience, and see progress changes

### **Recruiter Testing:**
1. **Job Posting:** Create new jobs and manage existing ones
2. **Application Management:** Review applications, update statuses
3. **Package Purchase:** Test discount codes and payment flow
4. **Company Management:** Update company profiles and team structure

### **Admin Testing:**
1. **Discount Management:** Create, edit, deactivate discount codes
2. **Usage Analytics:** View discount code usage statistics
3. **Platform Overview:** Monitor overall platform activity

### **Payment Testing:**
1. **Discount Validation:** Test all discount codes including expired ones
2. **Payment Flow:** Complete Payfast sandbox payments
3. **Package Activation:** Verify automatic package activation after payment

---

## 💳 PAYMENT TESTING

### **Payfast Integration:**
- **Mode:** Sandbox (safe for testing)
- **Merchant ID:** 14208372
- **Test Environment:** https://sandbox.payfast.co.za
- **Package Types:** Two Listings (R2800), Five Listings (R4150), Unlimited (R3899/month)

### **Discount Testing:**
- Apply codes during checkout
- Verify price calculations
- Test validation for expired/invalid codes
- Check usage limits and restrictions

---

## 🔧 TECHNICAL NOTES

### **Database Collections:**
- **users:** All user accounts (job seekers, recruiters, admin)
- **companies:** Company profiles and information
- **jobs:** Job listings with full details
- **job_applications:** Application tracking and management
- **discount_codes:** Promotional codes and usage tracking
- **packages:** Available job listing packages
- **payments:** Payment processing and history

### **Authentication:**
- JWT-based authentication
- Role-based access control
- Session management and security

### **Features Implemented:**
- ✅ User registration and login
- ✅ Profile completion gamification
- ✅ Job posting and management
- ✅ Application tracking system
- ✅ Discount codes system
- ✅ Payment processing (Payfast)
- ✅ Admin dashboard
- ✅ Package management

---

**🚀 Ready to test the complete Job Rocket platform with realistic demo data!**

### 🔧 ADMINISTRATORS

#### 1. **SYSTEM ADMIN**
- **Email:** `admin@jobrocket.demo`
- **Password:** `admin123`
- **Name:** John Administrator
- **Role:** Platform Administrator
- **Permissions:** Full system access, user management, analytics

---

## 🏢 Demo Companies & Jobs

### **TechCorp Solutions**
- **Industry:** Technology Consulting
- **Size:** 201-500 employees
- **Location:** Johannesburg, Gauteng
- **Jobs Posted:** 
  - Senior React Developer (R60k-90k, Remote, Featured)
  - Junior Frontend Developer (R25k-35k, Hybrid)

### **Innovate Digital**
- **Industry:** Digital Marketing
- **Size:** 51-200 employees  
- **Location:** Cape Town, Western Cape
- **Jobs Posted:**
  - Product Manager (R45k-70k, Hybrid)
  - UX/UI Designer (R40k-60k, Remote)

### **FinTech Solutions SA**
- **Industry:** Financial Technology
- **Size:** 101-200 employees
- **Location:** Sandton, Gauteng
- **Jobs Posted:**
  - DevOps Engineer (R70k-100k, Remote, Featured)

---

## 🎮 Gamification Testing Scenarios

### **Scenario 1: New User Onboarding**
1. Login as Sarah Johnson (`sarah.johnson@demo.com`)
2. See 0 points, empty grey trophy
3. Complete profile sections to earn points
4. Watch progress circle fill and points increase

### **Scenario 2: Mid-Progress User**
1. Login as Alex Rodriguez (`alex.rodriguez@demo.com`) 
2. See ~60 points, partially filled progress circle
3. Complete remaining sections to reach 100 points
4. Trigger trophy completion animation

### **Scenario 3: Complete Profile Showcase**
1. Login as Michael Chen (`michael.chen@demo.com`)
2. See 100 points, gold trophy
3. Experience rocket launch celebration
4. Access to all premium features

### **Scenario 4: Job Application Tracking**
1. Login as any job seeker
2. Apply to jobs using "Quick Apply" button
3. Watch job application counter increase
4. Earn points after 5 applications

### **Scenario 5: Recruiter Dashboard**
1. Login as Lisa Martinez (`lisa.martinez@techcorp.demo`)
2. View company job postings
3. Access candidate search and ATS features
4. Manage recruitment pipeline

---

## 🧪 Testing Features

### **Authentication Flow**
- Registration with email validation
- Login with JWT token
- Password reset functionality
- Role-based access control

### **Profile Gamification**
- **Profile Picture Upload:** +5 points
- **About Me (50+ chars):** +10 points  
- **Work Experience:** +10 points
- **5+ Skills:** +20 points
- **Education + Document:** +10 points
- **Achievements:** +10 points
- **Intro Video:** +20 points
- **5 Job Applications:** +10 points
- **Email Alerts Setup:** +5 points
- **Total:** 100 points

### **Visual Celebrations**
- Grey trophy → Gold trophy transformation
- Circular progress indicator
- Rocket launch animation at 100 points
- Point badges and progress notifications
- Achievement unlocks and milestones

### **Job Board Features**
- Advanced search and filtering
- Company profiles and job details  
- One-click job applications
- Save/favorite jobs functionality
- Remote/hybrid job indicators

---

## 🎯 Quick Test Commands

```bash
# Test beginner user login
curl -X POST "https://seeker-profile-v2.preview.emergentagent.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "sarah.johnson@demo.com", "password": "demo123"}'

# Test advanced user profile
curl -X POST "https://seeker-profile-v2.preview.emergentagent.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "michael.chen@demo.com", "password": "demo123"}'

# View all available jobs
curl "https://seeker-profile-v2.preview.emergentagent.com/api/jobs"

# Check user profile progress
curl -X GET "https://seeker-profile-v2.preview.emergentagent.com/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🚀 Ready for Testing!

All demo users are set up with realistic data to showcase:
- ✅ Complete authentication system
- ✅ Gamified profile completion  
- ✅ Progressive point system
- ✅ Trophy and rocket animations
- ✅ Job search and application
- ✅ Role-based access control
- ✅ Professional UI/UX design

**Start testing by visiting:** https://seeker-profile-v2.preview.emergentagent.com