# JobRocket - Product Requirements Document

> **Last Updated**: June 4, 2026
> **Version**: 2.13.0 (Wallet Auto Top-Up with PayFast Tokenization)

---

## Overview

JobRocket is a B2B SaaS recruitment platform targeting recruiters, businesses, agencies, and organizations in South Africa.

---

## Architecture

- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Payments**: Payfast (LIVE) with subscription billing + card tokenization
- **Auth**: JWT with role-based access
- **AI**: OpenAI GPT-5.2 via emergentintegrations

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
- [x] **Job Match Score (R10)** — GPT-5.2 analyzes candidate vs job
- [x] **Top 10 Jobs (R50)** — Scans all active jobs, ranks by match
- [x] **Auto-Apply (R50)** — AI cover letters + application creation
- [x] **CV Enhancement (R80)** — ATS score, profile analysis, rewritten summaries
- [x] **MatchScoreBadge** — Inline reveal on job cards
- [x] **Sidekick Panel** — Floating chat sidebar with wallet top-up
- [x] **Profile data fix** — Falls back to user doc when job_seeker_profiles empty
- [x] **Caching** — Match scores cached to avoid duplicate charges
- [x] **Refund system** — Auto-refunds on AI failures

### Phase 22: Account Settings (Jun 2026)
- [x] **Change Password API** — POST /api/auth/change-password
- [x] **Settings Page** — /settings route for all roles
- [x] **Profile Settings Tab** — Added to job seeker profile
- [x] **CV Search Enhancement** — Cards show job title, company/role, salary

### Phase 23: Wallet Auto Top-Up with PayFast Tokenization (Jun 2026)
- [x] **Card Setup** — POST /api/ai/wallet/setup-card -> PayFast redirect with subscription_type=2
- [x] **Token Capture** — POST /api/payfast/wallet-itn webhook stores card token
- [x] **Auto Charge** — charge_saved_card() calls PayFast POST /subscriptions/{token}/adhoc
- [x] **Auto Top-Up Logic** — After each AI deduction, if balance < threshold -> auto charge
- [x] **Settings CRUD** — GET/POST /api/ai/wallet/auto-topup (enabled, threshold, amount)
- [x] **Card Management** — GET /api/ai/wallet/card-status, DELETE /api/ai/wallet/remove-card
- [x] **Frontend Settings UI** — Card status display, save/remove card, threshold/amount config
- [x] **Sidekick Integration** — Auto top-up badge in wallet bar, notification on auto charge

### Phase 24: Admin AI Insights Dashboard (Jun 2026)
- [x] **Comprehensive API** — GET /api/admin/ai/analytics (admin-only, verify_admin_user)
- [x] **KPI Cards** — Net Revenue, AI Actions, Wallet Top-Ups, Refunds
- [x] **Revenue by Feature** — Color-coded bars for all 4 AI features with usage counts
- [x] **Daily Revenue Trend** — 30-day bar chart of AI revenue and action counts
- [x] **Top Users Leaderboard** — Top 10 AI spenders with medal badges
- [x] **Wallet & Auto Top-Up Stats** — Balance held, avg balance, cards saved, auto-topup users, pricing
- [x] **Recent Transactions** — Expandable table with color-coded action types
- [x] **Admin-Only Access** — API returns 403 for job seekers/recruiters, frontend tab only in admin dashboard

### Phase 25: Recruiter AI Match Score for CV Search (Jun 2026)
- [x] **AI Match Endpoint** — POST /api/cv-search/ai-match (candidate_id + job_id, recruiter auth, Growth+ tier)
- [x] **GPT-5.2 Analysis** — Uses AIMatchingService for detailed candidate-job scoring
- [x] **Cached Scores** — Results stored in recruiter_match_scores collection, returned on repeat calls
- [x] **Score Retrieval** — GET /api/cv-search/ai-match-scores with candidate_id/job_id filters
- [x] **Frontend UI** — AI Match Score button on each candidate card, job selector dropdown
- [x] **Result Display** — Score badge, match label, reasoning, Skills/Experience/Location breakdown, matching/missing skills tags
- [x] **Access Control** — Recruiter-only, Growth+ tier, job must belong to recruiter's account
- [x] **Validation** — Can't enable without saved card, threshold 0-5000, amount 5-10000

---

## Key API Endpoints

### AI Sidekick
- `GET /api/ai/pricing` - Feature pricing + wallet balance
- `GET /api/ai/wallet` - Wallet balance
- `POST /api/ai/wallet/topup` - Manual top-up
- `POST /api/ai/wallet/setup-card` - Get PayFast tokenization form data
- `POST /api/payfast/wallet-itn` - PayFast ITN webhook (public)
- `GET /api/ai/wallet/card-status` - Check saved card
- `DELETE /api/ai/wallet/remove-card` - Remove saved card
- `GET /api/ai/wallet/auto-topup` - Get auto top-up settings
- `POST /api/ai/wallet/auto-topup` - Update auto top-up settings
- `POST /api/ai/match-score` - Job match score (R10)
- `POST /api/ai/top-matches` - Top 10 jobs (R50)
- `POST /api/ai/auto-apply` - Auto-apply (R50)
- `POST /api/ai/cv-enhance` - CV enhancement (R80)

### Auth
- `POST /api/auth/login` - Login (returns access_token)
- `POST /api/auth/register` - Register
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/forgot-password` - Request reset email
- `POST /api/auth/reset-password` - Reset with token

---

## Backlog / Roadmap

### P1 - Next
1. More Email Notifications (Shortlisted, Interview Scheduled, Offer Made)

### P2 - Later
1. **Refactor server.py** (>6700 lines) into modular routers
2. Stripe Integration
3. Fix legal page footer links

### P3 - Future
1. Enterprise features (RBAC, API, white-label)
2. In-App Notifications
3. ATS export, calendar integration

---

## Notes

- Payfast is in LIVE mode with production credentials
- AI features use Emergent LLM Key (EMERGENT_LLM_KEY in .env)
- init_db.py has production safety blocks
- Auto top-up uses PayFast tokenization (subscription_type=2, ad hoc charges)
