# JobRocket - Product Requirements Document

> **Last Updated**: February 2026
> **Version**: 2.1.0 (P1 Features Complete)

---

## Overview

JobRocket is a B2B SaaS recruitment platform targeting recruiters, businesses, agencies, and organizations in South Africa. The platform enables employers to post jobs, manage candidates, and access a talent pool of job seekers.

### Key User Personas

1. **Recruiters/Businesses** (Paying Customers)
   - Post unlimited jobs
   - Manage applicants
   - Access CV database
   - Use AI matching features
   - Collaborate with team members

2. **Job Seekers** (Free Users)
   - Create profiles
   - Search and apply for jobs
   - Get discovered by recruiters

3. **Platform Admins**
   - Manage users and accounts
   - Create discount codes
   - View analytics

---

## Architecture (v2.1.0)

### Multi-Tenant Model

```
Account (Tenant)
- Owner User (account_role: owner)
- Team Members (account_role: admin/recruiter/viewer)
- Subscription (tier_id: starter/growth/pro/enterprise)
- Add-ons (purchased features)
- Jobs (posted by team members)
- Applications (received from job seekers)
```

### Tech Stack

- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Payments**: Payfast (primary), Stripe (future)
- **Auth**: JWT with role-based access
- **AI**: OpenAI GPT-5.2 via emergentintegrations (with kill switch)

### Key Collections

| Collection | Purpose |
|------------|---------|
| `users` | All users (job seekers, recruiters, admins) |
| `accounts` | Tenant/billing entities for recruiters |
| `account_addons` | Purchased add-ons per account |
| `tiers` | Subscription tier definitions |
| `addons` | Add-on product definitions |
| `jobs` | Job listings |
| `job_applications` | Applications from job seekers |
| `payments` | Payment records |
| `team_invitations` | Pending team invitations |
| `discount_codes` | Promotional codes |

---

## Subscription Tiers

| Tier | Price/Month | Users | Key Features |
|------|-------------|-------|--------------|
| **Starter** | R6,899 | 1 | Unlimited jobs, basic profile |
| **Growth** | R10,499 | 2 | + AI matching, CV database, filtering |
| **Pro** | R19,999 | 3 | + Bulk upload, analytics, collaboration |
| **Enterprise** | R39,999+ | 5 | + API access, white-label, RBAC |

**Extra Users**: R899/user/month (all tiers)

---

## What's Been Implemented

### Phase 1: Multi-Tenant Core (December 2025)

- [x] New database schema for accounts, tiers, add-ons
- [x] Account auto-creation on recruiter signup
- [x] Tier configuration with 4 subscription levels
- [x] 12 purchasable add-ons defined
- [x] Feature access service for tier-gating
- [x] Account service for user management
- [x] Updated auth flow with account context
- [x] User invitation system
- [x] Demo data seeding script

### Phase 2: P0 - Frontend & Payments (December 2025)

- [x] **Pricing Page** - 4-tier pricing with feature comparison
- [x] **Admin Account Dashboard** - Stats, tier distribution, account list
- [x] **Payment Result Pages** - Success and Cancel pages
- [x] **Payfast Integration** - Subscription payment flow (sandbox)

### Phase 3: P1 Features (February 2026)

- [x] **Billing Page** (`/billing`) - Full customer billing management
  - Overview tab: Current plan, monthly charges, user seats
  - Add-ons tab: View active add-ons, purchase new ones
  - Users tab: View/purchase/cancel extra user seats
  - History tab: Payment history with status badges
  - Payfast redirect for add-on and seat purchases

- [x] **Bulk Job Upload** (`/bulk-upload`) - Pro+ tier feature
  - Drag & drop file upload for CSV and Excel (.xlsx)
  - Template download (CSV and Excel formats)
  - Upload results with success/failure counts and error details
  - Feature-gated: Navigation link hidden for non-Pro tiers
  - API returns 403 for unauthorized tier access

- [x] **CV Search AI Indicator** - Shows matching method on CV Search page
  - Purple badge when AI matching is active
  - Gray badge when using keyword matching
  - Non-admin API endpoint for recruiter access

- [x] **Admin Stats Caching** - Cached analytics for admin dashboard
  - Refreshes every 12 hours (6am/6pm SAST)
  - Includes revenue, user counts, tier distribution

- [x] **AI Matching Kill Switch** - Admin can toggle AI on/off
  - POST /api/admin/ai-matching/toggle endpoint
  - Falls back to keyword matching when disabled
  - Status visible to all recruiters on CV Search page

---

## Backlog / Roadmap

### P2 - Medium Priority (User to reprioritize)

1. **Feature Implementation**
   - Applicant filtering (Growth+)
   - Applicant status tracking (Growth+)
   - CV database/talent pool (Growth+)
   - Export candidates CSV (Growth+)

2. **AI Features**
   - AI match scoring (Growth+)
   - Auto-ranked candidates (Growth+)
   - Skills matching (Growth+)

3. **Analytics**
   - Job performance metrics (Growth+)
   - Applicant conversion rates (Pro+)
   - Monthly hiring reports (Pro+)

4. **Distribution**
   - Email distribution (Growth+)
   - WhatsApp distribution (add-on)
   - Social media distribution (add-on)

5. **Employer Branding**
   - Enhanced company profiles by tier
   - Featured job listings
   - Employer video support

### P3 - Future

6. **Enterprise Features**
   - Role-based permissions
   - API access
   - Custom listing styling
   - White-label branding

7. **Integrations**
   - ATS export
   - Stripe payments
   - Calendar integration

8. **Job Seeker Monetization**
   - Paid features for job seekers (user requested later)

---

## Test Credentials

### Admin
- Email: `admin@jobrocket.co.za`
- Password: `admin123`

### Recruiters (by tier)
| Tier | Email | Password |
|------|-------|----------|
| Starter | `hr@techcorp.co.za` | `demo123` |
| Growth | `talent@innovatedigital.co.za` | `demo123` |
| Pro | `careers@fintechsa.co.za` | `demo123` |
| Enterprise | `admin@globalrecruit.co.za` | `demo123` |

### Job Seekers
- `thabo.mthembu@gmail.com` / `demo123`
- `nomsa.dlamini@gmail.com` / `demo123`
- `pieter.vandermerwe@gmail.com` / `demo123`

---

## API Reference

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user with account details

### Account Management
- `GET /api/account` - Get account details with features
- `PUT /api/account` - Update account/company info
- `GET /api/account/users` - List team members
- `POST /api/account/invite` - Invite team member
- `DELETE /api/account/users/{id}` - Remove team member

### Tiers & Add-ons
- `GET /api/tiers` - List all tiers
- `GET /api/tiers/{id}` - Get tier details
- `GET /api/addons` - Available add-ons for current account

### Jobs
- `POST /api/jobs` - Create job
- `GET /api/jobs` - Get account's jobs
- `PUT /api/jobs/{id}` - Update job
- `DELETE /api/jobs/{id}` - Delete job
- `GET /api/public/jobs` - Public job listings
- `POST /api/jobs/bulk` - Bulk upload jobs (Pro+)
- `GET /api/jobs/bulk/template` - Download bulk upload template

### Applications
- `POST /api/applications` - Apply to job
- `GET /api/applications` - Get applications
- `GET /api/jobs/{id}/applications` - Get job applications
- `PUT /api/applications/{id}/status` - Update status

### Billing
- `GET /api/billing` - Billing summary for account
- `GET /api/billing/history` - Payment history
- `POST /api/billing/addon` - Purchase add-on
- `DELETE /api/billing/addon/{id}` - Cancel add-on
- `POST /api/billing/extra-seats` - Purchase extra seats
- `GET /api/billing/extra-seats` - List extra seats
- `DELETE /api/billing/extra-seats/{id}` - Cancel seat

### AI Matching
- `GET /api/ai-matching/status` - Get AI matching status (any user)
- `GET /api/admin/ai-matching/status` - Get AI matching status (admin)
- `POST /api/admin/ai-matching/toggle` - Toggle AI on/off (admin)
- `POST /api/cv-search/match` - Match candidates to job
- `GET /api/cv-search` - Search candidates

### Admin
- `GET /api/admin/stats` - Cached system-wide statistics

### Payments
- `POST /api/payments/subscription` - Initiate subscription payment
- `POST /api/payments/webhook` - Payfast webhook

---

## Notes

- MongoDB is used (not MySQL)
- Payfast is in sandbox mode
- Feature gating at API level + UI level (nav links hidden)
- AI matching has kill switch (env var + admin endpoint)
- Billing uses recurring monthly payments via Payfast
- User seat policy: cancelled seats stay active until billing period ends
