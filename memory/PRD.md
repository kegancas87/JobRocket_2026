# JobRocket - Product Requirements Document

> **Last Updated**: December 2025
> **Version**: 2.0.0 (Multi-tenant SaaS Architecture)

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

## Architecture (v2.0.0)

### Multi-Tenant Model

```
Account (Tenant)
├── Owner User (account_role: owner)
├── Team Members (account_role: admin/recruiter/viewer)
├── Subscription (tier_id: starter/growth/pro/enterprise)
├── Add-ons (purchased features)
├── Jobs (posted by team members)
└── Applications (received from job seekers)
```

### Tech Stack

- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Payments**: Payfast (primary), Stripe (future)
- **Auth**: JWT with role-based access

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

### Phase 1: Multi-Tenant Core ✅ (December 2025)

- [x] New database schema for accounts, tiers, add-ons
- [x] Account auto-creation on recruiter signup
- [x] Tier configuration with 4 subscription levels
- [x] 12 purchasable add-ons defined
- [x] Feature access service for tier-gating
- [x] Account service for user management
- [x] Updated auth flow with account context
- [x] User invitation system
- [x] Demo data seeding script
- [x] API endpoints:
  - `/api/tiers` - List subscription tiers
  - `/api/account` - Get/update account
  - `/api/account/users` - List account users
  - `/api/account/invite` - Invite team member
  - `/api/addons` - Available add-ons
  - All job CRUD endpoints
  - All application endpoints

### Phase 2: Frontend & Payments ✅ (December 2025)

- [x] **Pricing Page** - New 4-tier pricing with feature comparison
  - Displays all tiers with prices, user counts, features
  - Most Popular badge for Pro tier
  - Subscribe buttons initiate Payfast payment
  - Feature comparison table
  - Public access (no login required)
  
- [x] **Admin Account Dashboard** - Admin-only view of all accounts
  - Stats: Total Accounts, Users, Jobs, Monthly Revenue
  - Tier distribution cards
  - Accounts list with filtering and search
  - Access restricted to admin users only
  
- [x] **Payment Result Pages** - Success and Cancel pages
  - Payment success page with confirmation
  - Payment cancel page with retry option
  - Public access (no login required for redirect from Payfast)
  
- [x] **Payfast Integration** - Complete subscription payment flow
  - Generates payment with correct tier amount
  - Signature generation for security
  - Return/Cancel URLs use BASE_URL from environment
  - Webhook endpoint for payment notifications

### Reference Documents Created

- `/app/memory/FEATURES.md` - Complete feature definitions
- `/app/memory/TIERS.md` - Tier configuration reference
- `/app/backend/models/` - New model architecture
- `/app/backend/services/` - Business logic services

---

## Backlog / Roadmap

### P1 - High Priority (Next)

3. **Feature Implementation**
   - Bulk job upload (Pro+)
   - Applicant filtering (Growth+)
   - Applicant status tracking (Growth+)
   - CV database/talent pool (Growth+)
   - Export candidates CSV (Growth+)

4. **AI Features**
   - AI match scoring (Growth+)
   - Auto-ranked candidates (Growth+)
   - Skills matching (Growth+)

### P2 - Medium Priority

5. **Analytics**
   - Job performance metrics (Growth+)
   - Applicant conversion rates (Pro+)
   - Monthly hiring reports (Pro+)

6. **Distribution**
   - Email distribution (Growth+)
   - WhatsApp distribution (add-on)
   - Social media distribution (add-on)

7. **Employer Branding**
   - Enhanced company profiles by tier
   - Featured job listings
   - Employer video support

### P3 - Future

8. **Enterprise Features**
   - Role-based permissions
   - API access
   - Custom listing styling
   - White-label branding

9. **Integrations**
   - ATS export
   - Stripe payments
   - Calendar integration

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
- `POST /api/auth/register` - Register user (auto-creates account for recruiters)
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
- `GET /api/public/jobs/{id}` - Public job detail

### Applications
- `POST /api/applications` - Apply to job (job seekers)
- `GET /api/applications` - Get applications
- `GET /api/jobs/{id}/applications` - Get job applications
- `PUT /api/applications/{id}/status` - Update status (requires feature)

### Payments
- `POST /api/payments/subscription` - Initiate subscription payment
- `POST /api/payments/webhook` - Payfast webhook

---

## Notes

- MongoDB is used (not MySQL) - compatible with Render hosting
- Payfast is in sandbox mode - switch to production for live payments
- Feature gating is implemented at API level - frontend should also hide unavailable features
- All demo accounts have active subscriptions for testing
