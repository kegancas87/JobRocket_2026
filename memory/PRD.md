# JobRocket - Product Requirements Document

> **Last Updated**: February 2026
> **Version**: 2.5.0 (Jobs Dashboard Complete)

---

## Overview

JobRocket is a B2B SaaS recruitment platform targeting recruiters, businesses, agencies, and organizations in South Africa.

---

## Architecture

- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Payments**: Payfast (sandbox) with automated subscription billing
- **Auth**: JWT with role-based access
- **AI**: OpenAI GPT-5.2 via emergentintegrations (kill switch)

---

## Subscription Tiers

| Tier | Price/Month | Users |
|------|-------------|-------|
| Starter | R6,899 | 1 |
| Growth | R10,499 | 2 |
| Pro | R19,999 | 3 |
| Enterprise | R39,999+ | 5 |

---

## What's Been Implemented

### Phase 1: Multi-Tenant Core (Dec 2025)
- [x] Multi-tenant schema (accounts, tiers, add-ons, feature gating)
- [x] Account/user management, invitations, demo data seeding

### Phase 2: P0 Features (Dec 2025)
- [x] Pricing Page, Admin Dashboard, Payfast subscription flow

### Phase 3: P1 Features (Feb 2026)
- [x] Billing Page, Bulk Job Upload (Pro+), CV Search AI Indicator
- [x] Admin Stats Caching, AI Matching Kill Switch

### Phase 6: Admin Analytics Dashboard (Feb 2026)
- [x] **Comprehensive Analytics Dashboard** (`/analytics`) - Admin only
  - 8 snapshot stat cards: Revenue, Accounts, Users, Jobs, Applications, New Accounts, Add-ons, Seats
  - Monthly Trends bar chart (6-month history)
  - Tier Distribution pie chart
  - Onboarding Completion rates (job seekers & recruiters)
  - Job Analytics: by Industry, Location, Work Type, Job Type (bar + pie charts)
  - Account Details drill-down table (company, tier, owner, MRR, usage)
  - CSV export with all sections for offline analysis
  - Refresh button with force-refresh of cached stats
  - Collapsible sections for drill-down
- [x] **Starter tier job limit**: 30 posts/month (Growth+ unlimited)

### Phase 7: Admin Account Management (Feb 2026)
- [x] **Account Management Page** (`/manage-accounts`) - Admin only
  - Account list with search, tier badges, owner email
  - Account detail panel: MRR, Users, Jobs, Credit Balance
  - **Change Tier**: Override account subscription tier (Starter/Growth/Pro/Enterprise)
  - **Grant Add-on**: Activate any of the 12 add-on features for free (1 year expiry)
  - **Revoke Add-on**: Deactivate granted add-ons
  - **Add Seats**: Grant extra user seats without payment
  - **Add Credits**: Top up account credit balance (for testing or goodwill)
  - **Audit Trail**: Full log of all admin actions per account with timestamps and reasons

### Phase 4: Job Seeker Onboarding (Feb 2026)
- [x] 7-step gamified wizard (Welcome, Location, Professional, Skills, CV Upload, Experience, Profile Boost)
- [x] Progress bar 0-100%, 3 badges, confetti, skip/resume, file uploads

### Phase 5: Recruiter Onboarding (Feb 2026)
- [x] 7-step gamified wizard with emerald/green theme
  - Step 0: Welcome ("Let's get you hiring faster")
  - Step 1: Company Basics (name, size, industry, location) - updates account doc
  - Step 2: Hiring Preferences (roles, locations, employment types, volume)
  - Step 3: Candidate Access (sourcing methods, alerts, match preferences)
  - Step 4: Activate (two CTAs: Post First Job / Browse Talent)
  - Step 5: Distribution (email, WhatsApp, social toggles)
  - Step 6: Go Live (confetti, completion)
- [x] Badges: company_live (step 1), sourcing_ready (step 3), ready_to_hire (step 6)
- [x] Post-onboarding nudges: Add team members, Explore dashboard
- [x] Skip options, save/resume, auto-redirect

### Phase 8: Automated Billing System (Feb 2026)
- [x] **PayFast Recurring Subscription Billing**
  - Monthly subscription billing via PayFast subscription API
  - Account-level billing day tracking (billing cycles start from first payment date)
  - Late payment resets billing cycle to new payment date
  
- [x] **7-Day Grace Period with Daily Retries**
  - If payment fails, account enters grace period (past_due status)
  - Daily cron job pings PayFast to check/retry payment
  - Reminder emails sent on days 7, 5, 3, 2, 1
  - Account deactivated (inactive) after 7 days
  
- [x] **Pro-Rata Calculations for Add-ons**
  - Extra seats/add-ons aligned to account billing day
  - 100% discount for pro-rata period (free until billing day)
  - AI features exempt from pro-rata (charged immediately)
  
- [x] **Payment History & Statements**
  - Full payment history with pagination
  - HTML statement download with JobRocket and customer details
  - Billing summary with monthly aggregation
  
- [x] **Read-Only Mode for Failed Seat Payments**
  - Users with inactive seats get read-only access (not blocked)
  - Main subscription failure blocks all features
  
- [x] **Frontend Billing Page Updates**
  - Subscription status banner for past_due/inactive accounts
  - Statement download component with date pickers
  - Payment history table with status badges

### Phase 9: Jobs Dashboard (Feb 2026)
- [x] **Recruiter Jobs Dashboard** (`/jobs-dashboard`)
  - Quick stats bar: Active Jobs, Applications This Month, Interviews, Expired Jobs
  - Job cards showing:
    - Job title, location, salary, job type, posted date
    - Days until expiry with color-coded status
    - Application statistics (total, pending, shortlisted, interviewed, offered)
    - "Has Notes" badge when recruiter notes exist
    - "Expiring Soon" badge for jobs expiring in <7 days
  - **Filtering & Sorting**:
    - Search by job title/location
    - Sort: Newest First, Expiring Soon, Most Applications, Posted Date
    - Toggle to show/hide expired jobs (hidden by default)
  - **Job Actions**:
    - View Applicants - opens pipeline modal
    - Add/Edit Notes - saves recruiter notes per job
    - Reactivate Expired Job - extends expiry date by configurable days
    - Edit Job - redirects to job editing
  - **Applicants Pipeline Modal**:
    - Status filter tabs (All, Pending, Reviewed, Shortlisted, Interviewed, Offered, Rejected)
    - Applicant cards with avatar, name, email, location, skills, cover letter preview
    - Quick status actions (Mark Reviewed, Shortlist, Schedule Interview, Make Offer, Reject)
    - View Profile button opens full applicant profile modal
    - Resume/CV download link

### Phase 10: Email Notifications (Feb 2026)
- [x] **Email Service Setup**
  - SMTP integration with `mail.jobrocket.co.za:465`
  - HTML email templates with Job Rocket branding
  - Support for multiple email types (job alerts, applications, notifications)
  
- [x] **Application Email Notifications**
  - **To Job Seeker (on apply)**: Confirmation email with job details and next steps
  - **To Recruiter (on apply)**: New application notification with link to Jobs Dashboard
  - **To Job Seeker (on rejection)**: Encouraging rejection email with CTA to browse more jobs
  
- [x] **Job Alert Notifications** (previously implemented)
  - Email notifications when new jobs match saved alerts

---

## Backlog / Roadmap

### P1 - Next
1. **Recruiter Reporting Feature** - CV search usage stats reporting
2. **Job Application Notifications** - Email recruiters when job seekers apply

### P2 - Later
1. AI match scoring & auto-ranked candidates
2. Distribution features (email, WhatsApp, social)
3. Enhanced employer branding
4. Talent Pool Alerts - save searches and get alerts for new matching candidates

### P3 - Future
1. Enterprise features (RBAC, API access, white-label)
2. Stripe integration
3. ATS export, calendar integration
4. Job seeker monetization
5. Quick Stats widget (bulk vs manual job performance)
6. In-app real-time notifications

---

## Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@jobrocket.co.za | admin123 |
| Recruiter (Starter) | hr@techcorp.co.za | demo123 |
| Recruiter (Growth) | talent@innovatedigital.co.za | demo123 |
| Recruiter (Pro) | careers@fintechsa.co.za | demo123 |
| Recruiter (Enterprise) | admin@globalrecruit.co.za | demo123 |
| Job Seeker | thabo.mthembu@gmail.com | demo123 |
| Job Seeker | nomsa.dlamini@gmail.com | demo123 |
| Job Seeker | pieter.vandermerwe@gmail.com | demo123 |

---

## Key API Endpoints

### Jobs Dashboard (NEW)
- `GET /api/jobs/dashboard` - Get jobs with stats, activity indicators, filtering/sorting
- `PUT /api/jobs/{job_id}/notes` - Add/update recruiter notes for a job
- `PUT /api/jobs/{job_id}/reactivate` - Reactivate an expired job with new expiry date
- `GET /api/jobs/{job_id}/applicants` - Get applicants for a job with status filter

### Onboarding
- `GET /api/onboarding/status` - Get onboarding progress
- `PUT /api/onboarding/step/{step}` - Save step data (role-aware: different fields for recruiter vs job seeker)
- `POST /api/onboarding/skip` - Skip onboarding entirely

### File Uploads
- `POST /api/uploads/cv` - Upload CV
- `POST /api/uploads/profile-picture` - Upload profile photo
- `POST /api/uploads/document` - Upload additional document

### Billing & Payments
- `GET /api/billing` - Get billing summary
- `GET /api/billing/history` - Get payment history (paginated)
- `GET /api/billing/statement` - Generate HTML/JSON statement for date range
- `GET /api/billing/summary` - Get monthly billing summary
- `GET /api/billing/account-info` - Get billing account details with billing_day
- `POST /api/billing/addon` - Purchase add-on
- `POST /api/billing/extra-seats` - Purchase extra user seats (pro-rata)
- `GET /api/subscription/status` - Check subscription status (active/past_due/inactive)
- `POST /api/subscription/reactivate` - Reactivate suspended subscription
- `POST /api/payments/subscription` - Initiate PayFast subscription
- `POST /api/payments/webhook` - PayFast ITN webhook handler
- `GET /api/seat/status` - Check extra seat user status

### Jobs
- `POST /api/jobs/bulk` (Pro+), `GET /api/jobs/bulk/template`

### AI Matching
- `GET /api/ai-matching/status`, `POST /api/admin/ai-matching/toggle`

---

## Billing Scheduler (Cron Job)

The billing scheduler runs daily tasks:
```bash
cd /app/backend && python -m tasks.billing_scheduler
```

Tasks performed:
1. Check past-due accounts and ping PayFast for payment status
2. Check accounts approaching billing date
3. Check extra seats with payment issues
4. Check addon subscriptions
5. Generate daily billing summary (stored in billing_summaries collection)

---

## Notes

- Payfast is in SANDBOX mode
- Static files at `/api/uploads/` (mounted AFTER router include)
- Onboarding: both job_seeker and recruiter redirected if onboarding_completed is falsy
- Admin role skips onboarding entirely
- Recruiter Step 1 updates account document (company info)
- Recruiter Step 4 has dual CTAs instead of Continue button
