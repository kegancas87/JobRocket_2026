# JobRocket Feature Definitions

> **Reference Document** - Use this when implementing tier-gated features
> **Last Updated**: December 2025

---

## Feature ID Reference

All features use the format: `CATEGORY_FEATURE_NAME` (e.g., `ACCOUNT_MULTI_USER_ACCESS`)

---

## Account & Access

### `ACCOUNT_RECRUITER_ACCOUNT`
A registered account that allows a recruiter to access the JobRocket platform, manage jobs, view candidates, and use recruiter tools based on their subscription tier.

### `ACCOUNT_COMPANY_PROFILE`
A public-facing company profile associated with a recruiter account, used to display employer branding, job listings, and company information. Feature depth varies by subscription tier:
- **Basic**: Starter tier
- **Enhanced**: Growth tier
- **Featured**: Pro tier
- **White-label**: Enterprise tier

### `ACCOUNT_MULTI_USER_ACCESS`
Allows multiple users to access the same recruiter account and company profile. Access is shared under a single subscription and subject to seat limits.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ✅
- **Enterprise**: ✅

### `ACCOUNT_ROLE_BASED_PERMISSIONS`
Allows administrators to assign different permission levels to users (e.g., admin, recruiter, viewer). Available only in Enterprise tier.

### `ACCOUNT_INCLUDED_USERS`
The number of user seats included in the subscription by default:
- **Starter**: 1 user
- **Growth**: 2 users
- **Pro**: 3 users
- **Enterprise**: 5 users

**Extra Users**: R899/user/month (all tiers)

---

## Job Posting

### `JOB_UNLIMITED_POSTS`
Allows recruiters to create and publish an unlimited number of job listings during the subscription period.
- **All tiers**: ✅

### `JOB_DURATION_35_DAYS`
Each job listing remains active and visible on the platform for 35 days unless closed earlier by the recruiter.
- **All tiers**: ✅

### `JOB_TEMPLATES`
Predefined job posting templates that recruiters can reuse to speed up job creation and ensure consistency.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `JOB_BULK_UPLOAD`
Allows recruiters to upload multiple job listings at once via file upload or batch process.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ✅
- **Enterprise**: ✅

---

## Candidate Applications

### `CANDIDATE_APPLICANT_INBOX`
A central inbox where recruiters receive and manage candidates who apply directly to their job listings.
- **All tiers**: ✅

### `CANDIDATE_APPLICANT_FILTERING`
Allows recruiters to filter applicants using criteria such as skills, experience, location, and application status.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `CANDIDATE_STATUS_TRACKING`
Allows recruiters to move candidates through defined hiring stages (e.g., applied, shortlisted, interviewed, hired).
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `CANDIDATE_NOTES_TAGS`
Allows recruiters to add internal notes and tags to candidate profiles for internal tracking and collaboration.
- **Starter**: ➕ (Add-on)
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

---

## CV Database / Talent Pool

### `TALENT_CV_DATABASE`
Allows recruiters to browse anonymised candidate profiles within the JobRocket talent pool without seeing personal contact details.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `TALENT_PASSIVE_SEARCH`
Allows recruiters to actively search and filter candidates in the talent pool who have not applied to a specific job.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `TALENT_POOL_ALERTS`
Automated notifications sent to recruiters when new candidates matching saved criteria become available.
- **Starter**: ➕ (Add-on)
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

### `TALENT_CONTACT_ACCESS`
Allows recruiters to view full candidate profiles and contact details under a fair-use policy. Usage limits may be introduced later.
- **All tiers**: Fair-use

---

## AI & Matching

### `AI_MATCH_SCORE`
An automated relevance score calculated between a job listing and a candidate profile based on skills, experience, and role fit.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `AI_AUTO_RANKED`
Automatically sorts candidates in order of relevance based on AI match scoring.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `AI_SKILLS_MATCHING`
Matches candidate skills against job requirements to identify alignment and gaps.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

---

## Job Distribution

### `DIST_PLATFORM`
Publishes job listings within the JobRocket platform so they are visible to job seekers browsing or searching.
- **All tiers**: ✅

### `DIST_EMAIL`
Distributes job listings to job seekers via email notifications based on relevance and preferences.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `DIST_WHATSAPP`
Distributes job listings to job seekers through WhatsApp channels or broadcasts.
- **Starter**: ➕ (Add-on)
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `DIST_SOCIAL_MEDIA`
Publishes or promotes job listings across JobRocket-managed social media channels.
- **Starter**: ➕ (Add-on)
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `DIST_MONTHLY_CAMPAIGNS`
A recurring promotion service that actively distributes a recruiter's open roles across JobRocket channels throughout the month.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

---

## Employer Branding

### `BRAND_PROFILE_PAGE`
A branded employer page displaying company details, branding assets, and job listings.
- **Starter**: Basic
- **Growth**: Enhanced
- **Pro**: Featured
- **Enterprise**: White-label

### `BRAND_FEATURED_LISTINGS`
Highlights selected job listings for increased visibility within the platform.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

### `BRAND_EMPLOYER_VIDEO`
Allows recruiters to embed or upload a company or employer branding video on their profile or job listings.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

### `BRAND_BRANDING_PACK`
A bundled branding enhancement that may include profile optimisation, featured placements, and promotional exposure.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ➕ (Add-on)
- **Enterprise**: ✅

### `BRAND_CUSTOM_STYLING`
Allows enterprise recruiters to visually customise job listings (layout, styling, branding elements) beyond standard templates.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ❌
- **Enterprise**: ✅

---

## Recruiter Tools

### `TOOLS_CANDIDATE_PIPELINE`
A visual workflow tool that allows recruiters to manage candidates across hiring stages.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `TOOLS_INTERVIEW_SCHEDULING`
Allows recruiters to schedule interviews with candidates and manage interview-related communications.
- **Starter**: ➕ (Add-on)
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

### `TOOLS_INTERNAL_COLLABORATION`
Allows multiple users within the same recruiter account to collaborate on candidates, notes, and hiring workflows.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ✅
- **Enterprise**: ✅

### `TOOLS_EXPORT_CSV`
Allows recruiters to export candidate data to CSV format for use in external systems.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

---

## Analytics & Reporting

### `ANALYTICS_JOB_PERFORMANCE`
Provides analytics on job listing performance, such as views, applications, and engagement.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `ANALYTICS_CONVERSION_RATES`
Tracks candidate movement through hiring stages and calculates conversion metrics.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ✅
- **Enterprise**: ✅

### `ANALYTICS_MONTHLY_REPORTS`
Automated reports summarising hiring activity, performance, and outcomes over a monthly period.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ✅
- **Enterprise**: ✅

---

## Integrations

### `INTEGRATION_ATS_EXPORT`
Allows candidate data to be exported or synced with external Applicant Tracking Systems.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

### `INTEGRATION_API_ACCESS`
Provides programmatic access to JobRocket data and functionality via an API.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ❌
- **Enterprise**: ✅

---

## Support & SLA

### `SUPPORT_EMAIL`
Standard customer support provided via email.
- **All tiers**: ✅

### `SUPPORT_PRIORITY`
Faster response times and higher support priority compared to standard support.
- **Starter**: ❌
- **Growth**: ✅
- **Pro**: ✅
- **Enterprise**: ✅

### `SUPPORT_DEDICATED_MANAGER`
An assigned support contact responsible for account success and escalation handling.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ❌
- **Enterprise**: ✅

### `SUPPORT_SLA`
A formal service level agreement defining uptime, response times, and support commitments.
- **Starter**: ❌
- **Growth**: ❌
- **Pro**: ❌
- **Enterprise**: ✅

---

## Job Seeker Interaction

### `SEEKER_PRIORITY_ACCESS`
Allows recruiters to receive early or prioritised access to high-intent or featured job seekers.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

### `SEEKER_HOT_ALERTS`
Notifications sent to recruiters when high-quality or high-demand candidates become available.
- **Starter**: ❌
- **Growth**: ➕ (Add-on)
- **Pro**: ✅
- **Enterprise**: ✅

---

## Implementation Notes

1. All features are **tier-gated** - check account tier before allowing access
2. Features may be **subject to fair-use** policies
3. Designed to support **future usage-based monetisation**
4. Implement with **feature flags** where possible
5. Add-ons (➕) can be purchased to unlock features at lower tiers
