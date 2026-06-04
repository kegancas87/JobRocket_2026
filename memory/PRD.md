# JobRocket - Product Requirements Document

> **Last Updated**: June 2026
> **Version**: 2.12.0 (AI Sidekick + Change Password + CV Search Enhancement)

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

### Phase 1-5: Core Platform (Dec 2025 - Feb 2026)
- [x] Multi-tenant schema, accounts, tiers, add-ons, feature gating
- [x] Pricing Page, Admin Dashboard, Payfast subscription flow
- [x] Billing Page, Bulk Job Upload, CV Search AI Indicator
- [x] Job Seeker & Recruiter 7-step gamified onboarding wizards
- [x] Admin Stats Caching, AI Matching Kill Switch

### Phase 6-7: Admin Tools (Feb 2026)
- [x] Comprehensive Analytics Dashboard (8 stat cards, charts, CSV export)
- [x] Account Management (Change Tier, Grant/Revoke Add-ons, Audit Trail)

### Phase 8-9: Billing & Jobs (Feb 2026)
- [x] PayFast Recurring Subscription with 7-day grace period
- [x] Recruiter Jobs Dashboard with applicants pipeline

### Phase 10-12: Communications & Reports (Feb 2026)
- [x] Email Notifications (applications, rejections, job alerts)
- [x] 3 MVP Reports (Time-to-Fill, Pipeline Conversion, Recruiter Workload)

### Phase 13-16: Profile & Sharing (Feb-Mar 2026)
- [x] Job Seeker Profile (picture, video, documents, edit/delete entries)
- [x] Custom Branding (favicon, title, meta)
- [x] Document Management System (CV + 4 additional docs)
- [x] Shareable Job Details Page at /jobs/{jobId}

### Phase 17-19: Growth Features (Apr 2026)
- [x] Guest Job Browsing at /browse-jobs
- [x] Free Tier & Package Purchase Flow
- [x] Billing Cycle Enforcement (grace period, suspended UI)
- [x] PayFast Signature Fix (insertion order, URL encoding)

### Phase 20: Security & SEO (Apr 2026)
- [x] Forgot Password Flow (email-based reset, 1-hour expiry)
- [x] SEO Optimization (meta tags, sitemap, robots.txt, JSON-LD)
- [x] Production DB Wipe Safety blocks on init_db.py
- [x] Google Analytics integration

### Phase 21: AI Sidekick for Job Seekers (Jun 2026)
- [x] **Wallet System** — `wallet_balance` field on users, atomic $inc deductions
- [x] **Job Match Score (R10)** — GPT-5.2 analyzes candidate vs job, returns score/strengths/weaknesses
- [x] **Top 10 Jobs (R50)** — Scans all active jobs, ranks by match percentage
- [x] **Auto-Apply (R50)** — Generates AI cover letters and creates applications
- [x] **CV Enhancement (R80)** — ATS score, profile analysis, rewritten summaries
- [x] **MatchScoreBadge** — Inline reveal button on job cards
- [x] **Sidekick Panel** — Floating chat sidebar with wallet top-up
- [x] **Profile data integration** — Falls back to user doc when job_seeker_profiles empty
- [x] **Caching** — Match scores cached to avoid duplicate charges
- [x] **Refund system** — Auto-refunds wallet on AI failures

### Phase 22: Change Password & CV Search Enhancement (Jun 2026)
- [x] **Change Password API** — POST /api/auth/change-password (validates current pw, min 6 chars, different)
- [x] **Settings Page** — /settings route accessible for all roles
- [x] **Profile Settings Tab** — Added to job seeker profile tabs
- [x] **Navigation Integration** — Settings link in dropdown for job seekers and recruiters
- [x] **CV Search Enhancement** — Candidate cards now show desired_job_title, current company/role, salary range

---

## Backlog / Roadmap

### P1 - Next
1. AI Match Score for CV Search (Recruiter Sidekick)
2. More Email Notifications (Shortlisted, Interview Scheduled, Offer Made)
3. Fix and Re-enable Onboarding Flow

### P2 - Later
1. **Refactor server.py** (>6200 lines) into modular routers
2. Admin AI Insights Dashboard (view AI usage, revenue, refunds)
3. Stripe Integration
4. Distribution features (email, WhatsApp, social)
5. Fix legal page footer links

### P3 - Future
1. Enterprise features (RBAC, API access, white-label)
2. In-App Notifications
3. ATS export, calendar integration
4. Talent Pool Alerts

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

### AI Sidekick (NEW)
- `GET /api/ai/pricing` - Get feature pricing and wallet balance
- `GET /api/ai/wallet` - Get wallet balance
- `POST /api/ai/wallet/topup` - Top up wallet (amount: 1-10000)
- `POST /api/ai/match-score` - Match score for candidate vs job (R10)
- `GET /api/ai/match-scores` - Get all cached match scores
- `POST /api/ai/top-matches` - Find top 10 matching jobs (R50)
- `POST /api/ai/auto-apply` - Auto-apply with AI cover letters (R50)
- `POST /api/ai/cv-enhance` - CV and profile enhancement (R80)
- `GET /api/ai/dashboard` - AI usage dashboard for job seekers

### Auth
- `POST /api/auth/login` - Login (returns access_token)
- `POST /api/auth/register` - Register
- `POST /api/auth/change-password` - Change password (requires current + new)
- `POST /api/auth/forgot-password` - Request reset email
- `POST /api/auth/reset-password` - Reset with token

### CV Search
- `GET /api/cv-search` - Search candidates (Growth+ tier)
- `POST /api/cv-search/reveal/{id}` - Reveal contact info

---

## Notes

- Payfast is in LIVE mode with production credentials
- Onboarding: Currently DISABLED - users go straight to dashboard
- Admin role skips onboarding entirely
- AI features use Emergent LLM Key (EMERGENT_LLM_KEY in .env)
- init_db.py has production safety blocks
