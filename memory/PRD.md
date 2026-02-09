# JobRocket - Product Requirements Document

> **Last Updated**: February 2026
> **Version**: 2.3.0 (Both Onboarding Flows Complete)

---

## Overview

JobRocket is a B2B SaaS recruitment platform targeting recruiters, businesses, agencies, and organizations in South Africa.

---

## Architecture

- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Payments**: Payfast (sandbox)
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

---

## Backlog / Roadmap

### P2 - Next (User to reprioritize)
1. Applicant filtering & status tracking (Growth+)
2. AI match scoring & auto-ranked candidates
3. Analytics dashboard (job performance, conversion, reports)
4. Distribution features (email, WhatsApp, social)
5. Enhanced employer branding

### P3 - Future
1. Enterprise features (RBAC, API access, white-label)
2. Stripe integration
3. ATS export, calendar integration
4. Job seeker monetization
5. Quick Stats widget (bulk vs manual job performance)

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

### Onboarding
- `GET /api/onboarding/status` - Get onboarding progress
- `PUT /api/onboarding/step/{step}` - Save step data (role-aware: different fields for recruiter vs job seeker)
- `POST /api/onboarding/skip` - Skip onboarding entirely

### File Uploads
- `POST /api/uploads/cv` - Upload CV
- `POST /api/uploads/profile-picture` - Upload profile photo
- `POST /api/uploads/document` - Upload additional document

### Billing
- `GET /api/billing`, `POST /api/billing/addon`, `POST /api/billing/extra-seats`

### Jobs
- `POST /api/jobs/bulk` (Pro+), `GET /api/jobs/bulk/template`

### AI Matching
- `GET /api/ai-matching/status`, `POST /api/admin/ai-matching/toggle`

---

## Notes

- Payfast is in SANDBOX mode
- Static files at `/api/uploads/` (mounted AFTER router include)
- Onboarding: both job_seeker and recruiter redirected if onboarding_completed is falsy
- Admin role skips onboarding entirely
- Recruiter Step 1 updates account document (company info)
- Recruiter Step 4 has dual CTAs instead of Continue button
