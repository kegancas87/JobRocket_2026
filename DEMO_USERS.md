# 🚀 Job Rocket Demo Users & Test Accounts

## 📋 Complete Demo User Credentials

### 👤 JOB SEEKERS

#### 1. **BEGINNER USER** (0-20 Points)
- **Email:** `sarah.johnson@demo.com`  
- **Password:** `demo123`
- **Name:** Sarah Johnson
- **Location:** Cape Town, South Africa
- **Profile Status:** Basic information only
- **Skills:** Python, HTML, CSS (only 3 skills)
- **About Me:** Short description (not enough for points)
- **Gamification:** Low completion score to demonstrate gamification

#### 2. **INTERMEDIATE USER** (50-60 Points)  
- **Email:** `alex.rodriguez@demo.com`
- **Password:** `demo123`
- **Name:** Alex Rodriguez
- **Location:** Johannesburg, Gauteng
- **Profile Status:** Moderate completion
- **Skills:** JavaScript, React, Node.js, Python, Git, SQL (6 skills)
- **Work Experience:** 1 previous role at WebTech Solutions
- **About Me:** Comprehensive description (150+ characters)
- **Gamification:** Mid-level completion for testing progress

#### 3. **ADVANCED USER** (90-100 Points)
- **Email:** `michael.chen@demo.com`
- **Password:** `demo123`  
- **Name:** Michael Chen
- **Location:** Durban, KwaZulu-Natal
- **Profile Status:** Near-complete or fully complete
- **Skills:** React, Node.js, Python, TypeScript, AWS, Docker, MongoDB, PostgreSQL, GraphQL, Jest (10+ skills)
- **Work Experience:** Senior Full-Stack Developer at Digital Innovations Ltd
- **Education:** BSc Computer Science from University of Cape Town (with document)
- **Achievements:** AWS Certified Developer
- **Profile Picture:** Professional headshot
- **Intro Video:** Demo video uploaded
- **Job Applications:** 5 applications tracked
- **Email Alerts:** Enabled
- **Salary Range:** Current R60k-80k, Desired R80k-120k
- **Gamification:** Maximum points to demonstrate rocket launch celebration

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

#### 2. **DIGITAL AGENCY RECRUITER**  
- **Email:** `david.wilson@innovate.demo`
- **Password:** `demo123`
- **Name:** David Wilson
- **Company:** Innovate Digital
- **Role:** Head of Human Resources
- **Industry:** Digital Marketing & Development
- **Posted Jobs:** Product Manager, UX/UI Designer

---

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
curl -X POST "https://rocket-ats.preview.emergentagent.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "sarah.johnson@demo.com", "password": "demo123"}'

# Test advanced user profile
curl -X POST "https://rocket-ats.preview.emergentagent.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "michael.chen@demo.com", "password": "demo123"}'

# View all available jobs
curl "https://rocket-ats.preview.emergentagent.com/api/jobs"

# Check user profile progress
curl -X GET "https://rocket-ats.preview.emergentagent.com/api/auth/me" \
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

**Start testing by visiting:** https://rocket-ats.preview.emergentagent.com