"""
JobRocket - Tier and Feature Configuration
Static configuration for subscription tiers and add-ons
"""

from .enums import TierId, FeatureId, AddonId, CompanyProfileLevel


# ============================================
# Tier Configuration
# ============================================

TIER_CONFIG = {
    TierId.STARTER: {
        "id": TierId.STARTER,
        "name": "Starter",
        "price_monthly": 6899,
        "price_annually": None,  # Future
        "currency": "ZAR",
        "included_users": 1,
        "extra_user_price": 899,
        "multi_user_access": False,
        "role_based_permissions": False,
        "company_profile_level": CompanyProfileLevel.BASIC,
        "job_post_limit": 30,  # 30 posts per month
        "features": [
            FeatureId.ACCOUNT_RECRUITER_ACCOUNT,
            FeatureId.ACCOUNT_COMPANY_PROFILE,
            FeatureId.JOB_DURATION_35_DAYS,
            FeatureId.CANDIDATE_APPLICANT_INBOX,
            FeatureId.TALENT_CONTACT_ACCESS,
            FeatureId.DIST_PLATFORM,
            FeatureId.SUPPORT_EMAIL,
        ],
        "available_addons": [
            AddonId.CANDIDATE_NOTES,
            AddonId.TALENT_ALERTS,
            AddonId.WHATSAPP_DIST,
            AddonId.SOCIAL_DIST,
            AddonId.INTERVIEW_SCHED,
        ],
        "display_order": 1,
        "is_active": True,
    },
    TierId.GROWTH: {
        "id": TierId.GROWTH,
        "name": "Growth",
        "price_monthly": 10499,
        "price_annually": None,
        "currency": "ZAR",
        "included_users": 2,
        "extra_user_price": 899,
        "multi_user_access": False,
        "role_based_permissions": False,
        "company_profile_level": CompanyProfileLevel.ENHANCED,
        "features": [
            # Account & Access
            FeatureId.ACCOUNT_RECRUITER_ACCOUNT,
            FeatureId.ACCOUNT_COMPANY_PROFILE,
            # Job Posting
            FeatureId.JOB_UNLIMITED_POSTS,
            FeatureId.JOB_DURATION_35_DAYS,
            FeatureId.JOB_TEMPLATES,
            # Candidate Applications
            FeatureId.CANDIDATE_APPLICANT_INBOX,
            FeatureId.CANDIDATE_APPLICANT_FILTERING,
            FeatureId.CANDIDATE_STATUS_TRACKING,
            FeatureId.CANDIDATE_NOTES_TAGS,
            # Talent Pool
            FeatureId.TALENT_CV_DATABASE,
            FeatureId.TALENT_PASSIVE_SEARCH,
            FeatureId.TALENT_CONTACT_ACCESS,
            # AI & Matching
            FeatureId.AI_MATCH_SCORE,
            FeatureId.AI_AUTO_RANKED,
            FeatureId.AI_SKILLS_MATCHING,
            # Distribution
            FeatureId.DIST_PLATFORM,
            FeatureId.DIST_EMAIL,
            FeatureId.DIST_WHATSAPP,
            FeatureId.DIST_SOCIAL_MEDIA,
            # Employer Branding
            FeatureId.BRAND_PROFILE_PAGE,
            # Recruiter Tools
            FeatureId.TOOLS_CANDIDATE_PIPELINE,
            FeatureId.TOOLS_EXPORT_CSV,
            # Analytics
            FeatureId.ANALYTICS_JOB_PERFORMANCE,
            # Support
            FeatureId.SUPPORT_EMAIL,
            FeatureId.SUPPORT_PRIORITY,
        ],
        "available_addons": [
            AddonId.TALENT_ALERTS,
            AddonId.MONTHLY_CAMPAIGNS,
            AddonId.FEATURED_LISTINGS,
            AddonId.EMPLOYER_VIDEO,
            AddonId.BRANDING_PACK,
            AddonId.INTERVIEW_SCHED,
            AddonId.ATS_EXPORT,
            AddonId.PRIORITY_ACCESS,
            AddonId.HOT_ALERTS,
        ],
        "display_order": 2,
        "is_active": True,
    },
    TierId.PRO: {
        "id": TierId.PRO,
        "name": "Pro",
        "price_monthly": 19999,
        "price_annually": None,
        "currency": "ZAR",
        "included_users": 3,
        "extra_user_price": 899,
        "multi_user_access": True,
        "role_based_permissions": False,
        "company_profile_level": CompanyProfileLevel.FEATURED,
        "features": [
            # Account & Access
            FeatureId.ACCOUNT_RECRUITER_ACCOUNT,
            FeatureId.ACCOUNT_COMPANY_PROFILE,
            FeatureId.ACCOUNT_MULTI_USER_ACCESS,
            # Job Posting
            FeatureId.JOB_UNLIMITED_POSTS,
            FeatureId.JOB_DURATION_35_DAYS,
            FeatureId.JOB_TEMPLATES,
            FeatureId.JOB_BULK_UPLOAD,
            # Candidate Applications
            FeatureId.CANDIDATE_APPLICANT_INBOX,
            FeatureId.CANDIDATE_APPLICANT_FILTERING,
            FeatureId.CANDIDATE_STATUS_TRACKING,
            FeatureId.CANDIDATE_NOTES_TAGS,
            # Talent Pool
            FeatureId.TALENT_CV_DATABASE,
            FeatureId.TALENT_PASSIVE_SEARCH,
            FeatureId.TALENT_POOL_ALERTS,
            FeatureId.TALENT_CONTACT_ACCESS,
            # AI & Matching
            FeatureId.AI_MATCH_SCORE,
            FeatureId.AI_AUTO_RANKED,
            FeatureId.AI_SKILLS_MATCHING,
            # Distribution
            FeatureId.DIST_PLATFORM,
            FeatureId.DIST_EMAIL,
            FeatureId.DIST_WHATSAPP,
            FeatureId.DIST_SOCIAL_MEDIA,
            FeatureId.DIST_MONTHLY_CAMPAIGNS,
            # Employer Branding
            FeatureId.BRAND_PROFILE_PAGE,
            FeatureId.BRAND_FEATURED_LISTINGS,
            FeatureId.BRAND_EMPLOYER_VIDEO,
            # Recruiter Tools
            FeatureId.TOOLS_CANDIDATE_PIPELINE,
            FeatureId.TOOLS_INTERVIEW_SCHEDULING,
            FeatureId.TOOLS_INTERNAL_COLLABORATION,
            FeatureId.TOOLS_EXPORT_CSV,
            # Analytics
            FeatureId.ANALYTICS_JOB_PERFORMANCE,
            FeatureId.ANALYTICS_CONVERSION_RATES,
            FeatureId.ANALYTICS_MONTHLY_REPORTS,
            # Integrations
            FeatureId.INTEGRATION_ATS_EXPORT,
            # Support
            FeatureId.SUPPORT_EMAIL,
            FeatureId.SUPPORT_PRIORITY,
            # Job Seeker Interaction
            FeatureId.SEEKER_PRIORITY_ACCESS,
            FeatureId.SEEKER_HOT_ALERTS,
        ],
        "available_addons": [
            AddonId.BRANDING_PACK,
        ],
        "display_order": 3,
        "is_active": True,
    },
    TierId.ENTERPRISE: {
        "id": TierId.ENTERPRISE,
        "name": "Enterprise",
        "price_monthly": 39999,  # Starting price, custom quotes
        "price_annually": None,
        "currency": "ZAR",
        "included_users": 5,
        "extra_user_price": 899,
        "multi_user_access": True,
        "role_based_permissions": True,
        "company_profile_level": CompanyProfileLevel.WHITE_LABEL,
        "features": [
            # All features included
            FeatureId.ACCOUNT_RECRUITER_ACCOUNT,
            FeatureId.ACCOUNT_COMPANY_PROFILE,
            FeatureId.ACCOUNT_MULTI_USER_ACCESS,
            FeatureId.ACCOUNT_ROLE_BASED_PERMISSIONS,
            FeatureId.JOB_UNLIMITED_POSTS,
            FeatureId.JOB_DURATION_35_DAYS,
            FeatureId.JOB_TEMPLATES,
            FeatureId.JOB_BULK_UPLOAD,
            FeatureId.CANDIDATE_APPLICANT_INBOX,
            FeatureId.CANDIDATE_APPLICANT_FILTERING,
            FeatureId.CANDIDATE_STATUS_TRACKING,
            FeatureId.CANDIDATE_NOTES_TAGS,
            FeatureId.TALENT_CV_DATABASE,
            FeatureId.TALENT_PASSIVE_SEARCH,
            FeatureId.TALENT_POOL_ALERTS,
            FeatureId.TALENT_CONTACT_ACCESS,
            FeatureId.AI_MATCH_SCORE,
            FeatureId.AI_AUTO_RANKED,
            FeatureId.AI_SKILLS_MATCHING,
            FeatureId.DIST_PLATFORM,
            FeatureId.DIST_EMAIL,
            FeatureId.DIST_WHATSAPP,
            FeatureId.DIST_SOCIAL_MEDIA,
            FeatureId.DIST_MONTHLY_CAMPAIGNS,
            FeatureId.BRAND_PROFILE_PAGE,
            FeatureId.BRAND_FEATURED_LISTINGS,
            FeatureId.BRAND_EMPLOYER_VIDEO,
            FeatureId.BRAND_BRANDING_PACK,
            FeatureId.BRAND_CUSTOM_STYLING,
            FeatureId.TOOLS_CANDIDATE_PIPELINE,
            FeatureId.TOOLS_INTERVIEW_SCHEDULING,
            FeatureId.TOOLS_INTERNAL_COLLABORATION,
            FeatureId.TOOLS_EXPORT_CSV,
            FeatureId.ANALYTICS_JOB_PERFORMANCE,
            FeatureId.ANALYTICS_CONVERSION_RATES,
            FeatureId.ANALYTICS_MONTHLY_REPORTS,
            FeatureId.INTEGRATION_ATS_EXPORT,
            FeatureId.INTEGRATION_API_ACCESS,
            FeatureId.SUPPORT_EMAIL,
            FeatureId.SUPPORT_PRIORITY,
            FeatureId.SUPPORT_DEDICATED_MANAGER,
            FeatureId.SUPPORT_SLA,
            FeatureId.SEEKER_PRIORITY_ACCESS,
            FeatureId.SEEKER_HOT_ALERTS,
        ],
        "available_addons": [],  # All features included
        "display_order": 4,
        "is_active": True,
    },
}


# ============================================
# Add-on Configuration
# ============================================

ADDON_CONFIG = {
    AddonId.CANDIDATE_NOTES: {
        "id": AddonId.CANDIDATE_NOTES,
        "name": "Candidate Notes & Tags",
        "description": "Add internal notes and tags to candidate profiles for tracking and collaboration.",
        "feature_id": FeatureId.CANDIDATE_NOTES_TAGS,
        "price_monthly": 499,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.STARTER],
        "is_active": True,
    },
    AddonId.TALENT_ALERTS: {
        "id": AddonId.TALENT_ALERTS,
        "name": "Talent Pool Alerts",
        "description": "Get notified when new candidates matching your criteria become available.",
        "feature_id": FeatureId.TALENT_POOL_ALERTS,
        "price_monthly": 699,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.STARTER, TierId.GROWTH],
        "is_active": True,
    },
    AddonId.WHATSAPP_DIST: {
        "id": AddonId.WHATSAPP_DIST,
        "name": "WhatsApp Distribution",
        "description": "Distribute job listings through WhatsApp channels.",
        "feature_id": FeatureId.DIST_WHATSAPP,
        "price_monthly": 899,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.STARTER],
        "is_active": True,
    },
    AddonId.SOCIAL_DIST: {
        "id": AddonId.SOCIAL_DIST,
        "name": "Social Media Distribution",
        "description": "Publish jobs across JobRocket social media channels.",
        "feature_id": FeatureId.DIST_SOCIAL_MEDIA,
        "price_monthly": 899,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.STARTER],
        "is_active": True,
    },
    AddonId.MONTHLY_CAMPAIGNS: {
        "id": AddonId.MONTHLY_CAMPAIGNS,
        "name": "Monthly Job Campaigns",
        "description": "Active promotion of your open roles throughout the month.",
        "feature_id": FeatureId.DIST_MONTHLY_CAMPAIGNS,
        "price_monthly": 1499,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.GROWTH],
        "is_active": True,
    },
    AddonId.FEATURED_LISTINGS: {
        "id": AddonId.FEATURED_LISTINGS,
        "name": "Featured Job Listings",
        "description": "Highlight your jobs for increased visibility.",
        "feature_id": FeatureId.BRAND_FEATURED_LISTINGS,
        "price_monthly": 999,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.GROWTH],
        "is_active": True,
    },
    AddonId.EMPLOYER_VIDEO: {
        "id": AddonId.EMPLOYER_VIDEO,
        "name": "Employer Video",
        "description": "Embed company branding videos on your profile and listings.",
        "feature_id": FeatureId.BRAND_EMPLOYER_VIDEO,
        "price_monthly": 799,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.GROWTH],
        "is_active": True,
    },
    AddonId.BRANDING_PACK: {
        "id": AddonId.BRANDING_PACK,
        "name": "Employer Branding Pack",
        "description": "Complete branding enhancement with profile optimization and featured placements.",
        "feature_id": FeatureId.BRAND_BRANDING_PACK,
        "price_monthly": None,
        "price_once": 2499,
        "is_recurring": False,
        "available_tiers": [TierId.GROWTH, TierId.PRO],
        "is_active": True,
    },
    AddonId.INTERVIEW_SCHED: {
        "id": AddonId.INTERVIEW_SCHED,
        "name": "Interview Scheduling",
        "description": "Schedule interviews with candidates and manage communications.",
        "feature_id": FeatureId.TOOLS_INTERVIEW_SCHEDULING,
        "price_monthly": 599,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.STARTER, TierId.GROWTH],
        "is_active": True,
    },
    AddonId.ATS_EXPORT: {
        "id": AddonId.ATS_EXPORT,
        "name": "ATS Export",
        "description": "Export candidate data to external Applicant Tracking Systems.",
        "feature_id": FeatureId.INTEGRATION_ATS_EXPORT,
        "price_monthly": 1299,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.GROWTH],
        "is_active": True,
    },
    AddonId.PRIORITY_ACCESS: {
        "id": AddonId.PRIORITY_ACCESS,
        "name": "Priority Candidate Access",
        "description": "Get early access to high-intent job seekers.",
        "feature_id": FeatureId.SEEKER_PRIORITY_ACCESS,
        "price_monthly": 999,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.GROWTH],
        "is_active": True,
    },
    AddonId.HOT_ALERTS: {
        "id": AddonId.HOT_ALERTS,
        "name": "Hot Candidate Alerts",
        "description": "Get notified when high-quality candidates become available.",
        "feature_id": FeatureId.SEEKER_HOT_ALERTS,
        "price_monthly": 799,
        "price_once": None,
        "is_recurring": True,
        "available_tiers": [TierId.GROWTH],
        "is_active": True,
    },
}


def get_tier_config(tier_id: TierId) -> dict:
    """Get configuration for a specific tier"""
    return TIER_CONFIG.get(tier_id, TIER_CONFIG[TierId.STARTER])


def get_addon_config(addon_id: AddonId) -> dict:
    """Get configuration for a specific add-on"""
    return ADDON_CONFIG.get(addon_id)


def get_all_tiers() -> list:
    """Get all tier configurations sorted by display order"""
    return sorted(TIER_CONFIG.values(), key=lambda x: x["display_order"])


def get_available_addons_for_tier(tier_id: TierId) -> list:
    """Get all add-ons available for purchase at a specific tier"""
    tier = get_tier_config(tier_id)
    addon_ids = tier.get("available_addons", [])
    return [ADDON_CONFIG[aid] for aid in addon_ids if aid in ADDON_CONFIG]


def tier_has_feature(tier_id: TierId, feature_id: FeatureId) -> bool:
    """Check if a tier includes a specific feature"""
    tier = get_tier_config(tier_id)
    return feature_id in tier.get("features", [])
