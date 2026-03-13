# JobRocket API Error Codes Reference

## HTTP Status Codes Used

| Code | Name | Description |
|------|------|-------------|
| 400 | Bad Request | Invalid input, validation error, or malformed request |
| 401 | Unauthorized | Authentication required or invalid credentials |
| 402 | Payment Required | Subscription or payment issue |
| 403 | Forbidden | User doesn't have permission for this action |
| 404 | Not Found | Requested resource doesn't exist |

---

## Detailed Error Messages by Category

### Authentication Errors (401)

| Error Message | When It Occurs |
|---------------|----------------|
| `Could not validate credentials` | Invalid or expired JWT token |
| `Token has expired` | JWT token past expiration time |
| `Invalid token` | Malformed or tampered JWT token |
| `Invalid email or password` | Wrong login credentials |
| `Invalid Google token` | Google OAuth token verification failed |

---

### Authorization Errors (403)

| Error Message | When It Occurs |
|---------------|----------------|
| `Only recruiters can access this resource` | Job seeker trying to access recruiter-only features |
| `Only job seekers can apply to jobs` | Recruiter trying to apply to a job |
| `Only admins can access this resource` | Non-admin accessing admin features |
| `Only owners and admins can invite team members` | Regular member trying to invite users |
| `Only owners and admins can update team members` | Regular member trying to edit team |
| `Only owners and admins can remove team members` | Regular member trying to remove users |
| `Only owners and admins can create branches` | Regular member trying to create branch |
| `Only owners and admins can update branches` | Regular member trying to edit branch |
| `Only owners and admins can delete branches` | Regular member trying to delete branch |
| `Only owners and admins can cancel invitations` | Regular member trying to cancel invite |
| `Cannot modify account owner` | Trying to change owner's role |
| `Cannot remove account owner` | Trying to remove the account owner |
| `Cannot remove yourself` | User trying to remove their own account |
| `Feature not available in your subscription tier` | Accessing feature not included in plan |
| `Your tier does not include CV Search` | Starter tier accessing CV search |
| `Monthly contact reveal limit reached` | Exceeded CV contact reveal quota |

---

### Payment Errors (402)

| Error Message | When It Occurs |
|---------------|----------------|
| `Subscription payment required` | Account subscription expired |
| `Subscription inactive. Please reactivate` | Account deactivated due to non-payment |
| `Grace period expired. Please make a payment` | 7-day grace period ended |
| `Extra seat payment required` | Additional seat payment failed |
| `Contact reveal limit reached for this month. Upgrade your plan` | CV search quota exhausted |

---

### Validation Errors (400)

| Error Message | When It Occurs |
|---------------|----------------|
| `Missing Google credential` | Google login without token |
| `Google account has no email` | Google account missing email |
| `Email already registered` | Registration with existing email |
| `Invalid email or password` | Login validation failed |
| `You have already applied to this job` | Duplicate job application |
| `Application already withdrawn` | Withdrawing already withdrawn application |
| `Invalid step number` | Invalid onboarding step |
| `Only PDF, DOC, and DOCX files are allowed` | Wrong CV file format |
| `Only JPG, PNG, and WebP images are allowed` | Wrong image format |
| `File too large (max 10MB)` | CV/document exceeds 10MB |
| `File too large (max 5MB)` | Profile picture exceeds 5MB |
| `Unsupported file type` | Unknown file extension |
| `Invalid date format. Use YYYY-MM-DD` | Wrong date format in request |
| `Invalid tier ID` | Non-existent subscription tier |
| `Invalid add-on ID` | Non-existent add-on |
| `Add-on already active on this account` | Duplicate add-on purchase |
| `Quantity must be between 1 and 50` | Invalid seat quantity |
| `Quantity must be between 1 and 100` | Invalid bulk quantity |
| `Amount must be between R1 and R1,000,000` | Invalid credit amount |
| `Email address required` | Missing email for invitation |
| `A user with this email already exists` | Inviting existing user |
| `An invitation has already been sent to this email` | Duplicate invitation |
| `Invalid role. Must be one of: [admin, recruiter, member, viewer]` | Invalid team member role |
| `No valid fields to update` | Empty update request |
| `User not associated with an account` | User without company account |
| `Invalid report type` | Unknown report type requested |

---

### Not Found Errors (404)

| Error Message | When It Occurs |
|---------------|----------------|
| `Job not found` | Accessing non-existent or deleted job |
| `Account not found` | Invalid account ID |
| `Application not found` | Invalid application ID |
| `Company not found` | Invalid company ID |
| `Job alert not found` | Invalid job alert ID |
| `Add-on not found` | Invalid add-on ID |
| `Branch not found` | Invalid branch ID |
| `Team member not found` | Invalid team member ID |
| `Invitation not found` | Invalid invitation ID or token |
| `Candidate not found` | Invalid candidate ID in CV search |
| `Tier not found` | Invalid subscription tier |

---

## Frontend Error Handling

The frontend displays these errors as toast notifications. Common user-facing messages:

| API Error | User Message |
|-----------|--------------|
| 401 errors | "Please log in to continue" |
| 402 errors | "Subscription required" or "Upgrade your plan" |
| 403 errors | "You don't have permission to do this" |
| 404 errors | "Not found" or specific resource message |
| 400 errors | Specific validation message from API |
| Network errors | "Connection error. Please try again" |

---

## PayFast Webhook Status Codes

| Status | Description |
|--------|-------------|
| `COMPLETE` | Payment successful |
| `FAILED` | Payment failed |
| `PENDING` | Payment processing |
| `CANCELLED` | Payment cancelled by user |

---

## Subscription Status Values

| Status | Description |
|--------|-------------|
| `active` | Subscription is current and paid |
| `past_due` | Payment failed, in grace period (7 days) |
| `inactive` | Account suspended due to non-payment |
| `cancelled` | Subscription cancelled by user |

---

## Application Status Values

| Status | Description |
|--------|-------------|
| `pending` | New application, not yet reviewed |
| `reviewed` | Recruiter has viewed the application |
| `shortlisted` | Candidate shortlisted for next stage |
| `interviewed` | Interview scheduled or completed |
| `offered` | Job offer extended |
| `rejected` | Application rejected |
| `withdrawn` | Candidate withdrew application |
| `hired` | Candidate accepted and hired |
