# JobRocket - Product Requirements Document

> **Last Updated**: February 2026
> **Version**: 2.2.0 (Job Seeker Onboarding Complete)

---

## Overview

JobRocket is a B2B SaaS recruitment platform targeting recruiters, businesses, agencies, and organizations in South Africa. The platform enables employers to post jobs, manage candidates, and access a talent pool of job seekers.

### Key User Personas

1. **Recruiters/Businesses** (Paying Customers)
2. **Job Seekers** (Free Users)
3. **Platform Admins**

---

## Architecture (v2.2.0)

### Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Payments**: Payfast (sandbox)
- **Auth**: JWT with role-based access
- **AI**: OpenAI GPT-5.2 via emergentintegrations (with kill switch)

---

## Subscription Tiers

| Tier | Price/Month | Users | Key Features |
|------|-------------|-------|--------------|
| Starter | R6,899 | 1 | Unlimited jobs, basic profile |
| Growth | R10,499 | 2 | + AI matching, CV database, filtering |
| Pro | R19,999 | 3 | + Bulk upload, analytics, collaboration |
| Enterprise | R39,999+ | 5 | + API access, white-label, RBAC |

---

## What's Been Implemented

### Phase 1: Multi-Tenant Core (Dec 2025)
- [x] Multi-tenant database schema (accounts, tiers, add-ons)
- [x] Feature access service for tier-gating
- [x] Account/user management, invitations
- [x] Demo data seeding

### Phase 2: P0 Features (Dec 2025)
- [x] Pricing Page with 4 tiers
- [x] Admin Account Dashboard
- [x] Payfast subscription flow (sandbox)
- [x] Payment success/cancel pages

### Phase 3: P1 Features (Feb 2026)
- [x] Billing Page (`/billing`) - subscription, add-ons, seats management
- [x] Bulk Job Upload (`/bulk-upload`) - CSV/Excel, Pro+ gated
- [x] CV Search AI Indicator - shows AI/keyword matching status
- [x] Admin Stats Caching - 12-hour refresh
- [x] AI Matching Kill Switch

### Phase 4: Job Seeker Onboarding (Feb 2026)
- [x] **Gamified 7-Step Onboarding Wizard** (`/onboarding`)
  - Step 0: Welcome Screen with user's name
  - Step 1: Location (15%)
  - Step 2: Professional Snapshot - job title, experience, industry, employment type (35%)
  - Step 3: Skills & Strengths - autocomplete skills, seniority, strengths (55%)
  - Step 4: CV Upload - file upload, LinkedIn URL, salary range (75%)
  - Step 5: Experience & Availability - work history, availability (90%)
  - Step 6: Profile Boost - photo, intro, open to opportunities, documents (100%)
- [x] **Gamification**: Progress bar, step indicators, 3 badges (profile_started, almost_there, profile_complete), confetti on completion
- [x] **Skip options**: Skip individual steps or entire onboarding
- [x] **Save & resume**: Progress saved to DB, resumable on re-login
- [x] **Auto-redirect**: Job seekers without completed onboarding redirected to wizard
- [x] **File uploads**: CV (PDF/DOC), profile picture (JPG/PNG), additional documents (up to 10)
- [x] **Role isolation**: Only job_seeker role sees onboarding; recruiters/admins unaffected

---

## Backlog / Roadmap

### P2 - Next (User to reprioritize)
1. **Recruiter Onboarding Flow** (gamified, similar to job seeker)
2. Applicant filtering & status tracking (Growth+)
3. AI match scoring & auto-ranked candidates
4. Analytics dashboard
5. Distribution features (email, WhatsApp, social)
6. Enhanced employer branding

### P3 - Future
1. Enterprise features (RBAC, API access, white-label)
2. Stripe integration
3. ATS export, calendar integration
4. Job seeker monetization
5. **Quick Stats widget** - show recruiter dashboard comparison of bulk-uploaded vs manually posted job performance

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

### Onboarding (New)
- `GET /api/onboarding/status` - Get onboarding progress
- `PUT /api/onboarding/step/{step}` - Save step data
- `POST /api/onboarding/skip` - Skip onboarding entirely

### File Uploads (New)
- `POST /api/uploads/cv` - Upload CV (PDF/DOC/DOCX)
- `POST /api/uploads/profile-picture` - Upload profile photo (JPG/PNG/WebP)
- `POST /api/uploads/document` - Upload additional document

### Authentication
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`

### Billing
- `GET /api/billing`, `GET /api/billing/history`
- `POST /api/billing/addon`, `DELETE /api/billing/addon/{id}`
- `POST /api/billing/extra-seats`, `DELETE /api/billing/extra-seats/{id}`

### Jobs
- `POST /api/jobs/bulk` (Pro+), `GET /api/jobs/bulk/template`

### AI Matching
- `GET /api/ai-matching/status`, `POST /api/admin/ai-matching/toggle`

---

## Notes

- Payfast is in SANDBOX mode
- Static files served at `/api/uploads/` (must be mounted AFTER router include)
- Onboarding `onboarding_completed` defaults to null for existing MongoDB users (triggers onboarding)
- AI matching has kill switch via env var + admin endpoint
