"""
Sidekick AI Service — Job Seeker AI Features
Handles: Match Score, Top 10 Jobs, Auto-Apply, CV Enhancement
All wallet operations use atomic MongoDB $inc to prevent race conditions.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger("ai_service")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

# Fixed pricing in ZAR
AI_PRICING = {
    "match_score": 10.00,
    "top_matches": 50.00,
    "auto_apply": 50.00,
    "cv_enhance": 80.00,
}


def _get_chat(session_id: str, system_message: str) -> LlmChat:
    """Create a GPT-5.2 chat instance"""
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message,
    )
    chat.with_model("openai", "gpt-5.2")
    return chat


async def check_and_deduct_wallet(db, user_id: str, action: str) -> dict:
    """
    Atomically check wallet balance and deduct cost.
    Returns {"success": True, "cost": X} or {"success": False, "error": "...", "required": X, "balance": Y}
    """
    cost = AI_PRICING.get(action)
    if cost is None:
        return {"success": False, "error": f"Unknown action: {action}"}

    # Atomic: only deduct if balance >= cost
    result = await db.users.find_one_and_update(
        {"id": user_id, "wallet_balance": {"$gte": cost}},
        {
            "$inc": {"wallet_balance": -cost},
            "$set": {"updated_at": datetime.utcnow()},
        },
        return_document=True,
        projection={"_id": 0, "wallet_balance": 1},
    )

    if result is None:
        # Either user not found or insufficient balance
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "wallet_balance": 1})
        balance = user.get("wallet_balance", 0) if user else 0
        return {
            "success": False,
            "error": "Insufficient wallet balance. Please top up your wallet.",
            "required": cost,
            "balance": balance,
        }

    return {"success": True, "cost": cost, "new_balance": result.get("wallet_balance", 0)}


async def _trigger_auto_topup_if_needed(db, user_id: str, new_balance: float) -> dict:
    """
    After wallet deduction, check if auto top-up should be triggered.
    Runs async — non-blocking to the main AI flow.
    Returns the top-up result or None.
    """
    try:
        from services.payfast_wallet_service import process_auto_topup
        topup_result = await process_auto_topup(db, user_id)
        if topup_result and topup_result.get("success"):
            logger.info(f"Auto top-up triggered for {user_id}: +R{topup_result['amount']}")
        return topup_result
    except Exception as e:
        logger.error(f"Auto top-up check failed for {user_id}: {e}")
        return None


async def refund_wallet(db, user_id: str, amount: float, reason: str):
    """Refund wallet if AI call fails"""
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"wallet_balance": amount}, "$set": {"updated_at": datetime.utcnow()}},
    )
    await db.ai_usage_log.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": "refund",
        "amount": amount,
        "reason": reason,
        "created_at": datetime.utcnow(),
    })
    logger.info(f"Refunded R{amount:.2f} to user {user_id}: {reason}")


async def log_ai_usage(db, user_id: str, action: str, cost: float, metadata: dict = None):
    """Log AI usage for analytics"""
    await db.ai_usage_log.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "cost": cost,
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
    })


def _build_candidate_profile(user: dict, profile: dict = None) -> str:
    """Build a text summary of the candidate for AI prompts.
    Profile data may live in a separate collection OR directly on the user doc.
    Falls back to user doc when no separate profile exists.
    """
    # Use user doc as fallback if no separate profile
    if not profile:
        profile = user

    parts = [f"Name: {user.get('first_name', '')} {user.get('last_name', '')}"]

    if profile:
        summary = profile.get("professional_summary") or profile.get("about_me")
        if summary:
            parts.append(f"Professional Summary: {summary}")
        if profile.get("skills"):
            skills = profile["skills"]
            if isinstance(skills, list):
                parts.append(f"Skills: {', '.join(skills)}")
            else:
                parts.append(f"Skills: {skills}")
        exp = profile.get("experience") or profile.get("work_experience")
        if exp:
            if isinstance(exp, list):
                for e in exp:
                    if isinstance(e, dict):
                        title = e.get('title', '') or e.get('position', '')
                        parts.append(f"Experience: {title} at {e.get('company', '')} ({e.get('duration', '')})")
                    else:
                        parts.append(f"Experience: {e}")
            else:
                parts.append(f"Experience: {exp}")
        if profile.get("education"):
            edu = profile["education"]
            if isinstance(edu, list):
                for e in edu:
                    if isinstance(e, dict):
                        parts.append(f"Education: {e.get('degree', '')} from {e.get('institution', '')}")
                    else:
                        parts.append(f"Education: {e}")
            else:
                parts.append(f"Education: {edu}")
        if profile.get("qualifications"):
            parts.append(f"Qualifications: {profile['qualifications']}")
        if profile.get("certifications"):
            parts.append(f"Certifications: {profile['certifications']}")
        if profile.get("location"):
            parts.append(f"Location: {profile['location']}")
        desired = profile.get("desired_role") or profile.get("desired_job_title")
        if desired:
            parts.append(f"Desired Role: {desired}")
        if profile.get("desired_salary"):
            parts.append(f"Desired Salary: {profile['desired_salary']}")
        if profile.get("cv_text"):
            parts.append(f"CV Content:\n{profile['cv_text'][:3000]}")

    return "\n".join(parts)


def _build_job_summary(job: dict) -> str:
    """Build a text summary of a job posting"""
    parts = [
        f"Job Title: {job.get('title', 'N/A')}",
        f"Company: {job.get('company_name', 'N/A')}",
        f"Location: {job.get('location', 'N/A')}",
        f"Work Type: {job.get('work_type', 'N/A')}",
        f"Role Type: {job.get('role_type', 'N/A')}",
        f"Industry: {job.get('industry', 'N/A')}",
    ]
    if job.get("salary"):
        parts.append(f"Salary: {job['salary']}")
    if job.get("description"):
        parts.append(f"Description:\n{job['description'][:2000]}")
    if job.get("requirements"):
        req = job["requirements"]
        if isinstance(req, list):
            parts.append(f"Requirements:\n" + "\n".join(f"- {r}" for r in req))
        else:
            parts.append(f"Requirements: {req}")
    if job.get("qualifications"):
        parts.append(f"Qualifications: {job['qualifications']}")

    return "\n".join(parts)


# ============================================================
# FEATURE 1: JOB MATCH SCORE (R10)
# ============================================================

async def get_match_score(db, user_id: str, job_id: str) -> dict:
    """
    Generate a match score between a job seeker and a specific job.
    Checks cache first, deducts from wallet, calls GPT-5.2, stores result.
    """
    # Check cache first
    cached = await db.ai_match_scores.find_one(
        {"user_id": user_id, "job_id": job_id},
        {"_id": 0},
    )
    if cached:
        return {"success": True, "cached": True, "result": cached}

    # Deduct from wallet
    wallet = await check_and_deduct_wallet(db, user_id, "match_score")
    if not wallet["success"]:
        return wallet

    try:
        # Get user profile and job data
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        profile = await db.job_seeker_profiles.find_one({"user_id": user_id}, {"_id": 0})
        job = await db.jobs.find_one({"id": job_id}, {"_id": 0})

        if not job:
            await refund_wallet(db, user_id, wallet["cost"], "Job not found")
            return {"success": False, "error": "Job not found", "refunded": True}

        candidate_text = _build_candidate_profile(user, profile)
        job_text = _build_job_summary(job)

        # Call GPT-5.2
        chat = _get_chat(
            session_id=f"match-{user_id}-{job_id}",
            system_message="""You are an expert recruitment analyst. Analyze the match between a candidate and a job posting.
Return ONLY valid JSON with this exact structure:
{
  "match_score": <number 0-100>,
  "match_rating": "<Excellent Match|Strong Match|Good Match|Fair Match|Weak Match>",
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "missing_skills": ["skill1", "skill2", ...],
  "missing_qualifications": ["qual1", "qual2", ...],
  "recommendation": "<concise recommendation paragraph>"
}
Be honest and specific. Reference actual skills and requirements from the data provided.""",
        )

        prompt = f"""Analyze this candidate's match to the job posting:

=== CANDIDATE PROFILE ===
{candidate_text}

=== JOB POSTING ===
{job_text}

Return your analysis as JSON."""

        response_text = await chat.send_message(UserMessage(text=prompt))

        # Parse JSON from response
        result = _parse_json_response(response_text)
        if not result:
            await refund_wallet(db, user_id, wallet["cost"], "Failed to parse AI response")
            return {"success": False, "error": "AI response parsing failed", "refunded": True}

        # Store result
        match_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "job_id": job_id,
            "job_title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "match_score": result.get("match_score", 0),
            "match_rating": result.get("match_rating", ""),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "missing_skills": result.get("missing_skills", []),
            "missing_qualifications": result.get("missing_qualifications", []),
            "recommendation": result.get("recommendation", ""),
            "cost_charged": wallet["cost"],
            "created_at": datetime.utcnow(),
        }
        await db.ai_match_scores.insert_one(match_record)
        del match_record["_id"]

        await log_ai_usage(db, user_id, "match_score", wallet["cost"], {"job_id": job_id})

        return {"success": True, "cached": False, "result": match_record, "new_balance": wallet["new_balance"]}

    except Exception as e:
        logger.error(f"Match score error for user {user_id}, job {job_id}: {e}")
        await refund_wallet(db, user_id, wallet["cost"], f"Error: {str(e)}")
        return {"success": False, "error": "An error occurred. Your wallet has been refunded.", "refunded": True}


# ============================================================
# FEATURE 2: TOP 10 JOBS FOR ME (R50)
# ============================================================

async def get_top_matches(db, user_id: str) -> dict:
    """Find the top 10 best matching jobs for this job seeker."""
    wallet = await check_and_deduct_wallet(db, user_id, "top_matches")
    if not wallet["success"]:
        return wallet

    try:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        profile = await db.job_seeker_profiles.find_one({"user_id": user_id}, {"_id": 0})
        candidate_text = _build_candidate_profile(user, profile)

        # Get all active jobs
        jobs = []
        async for job in db.jobs.find(
            {"is_active": {"$ne": False}},
            {"_id": 0, "id": 1, "title": 1, "company_name": 1, "location": 1, "salary": 1,
             "work_type": 1, "role_type": 1, "industry": 1, "description": 1, "requirements": 1, "qualifications": 1}
        ).limit(200):
            jobs.append(job)

        if not jobs:
            await refund_wallet(db, user_id, wallet["cost"], "No active jobs found")
            return {"success": False, "error": "No active jobs available", "refunded": True}

        # Build condensed job list for the prompt
        job_summaries = []
        for i, job in enumerate(jobs):
            summary = f"[{i}] {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')} | {job.get('location', 'N/A')} | {job.get('work_type', 'N/A')} | {job.get('salary', 'N/A')}"
            if job.get("description"):
                summary += f" | {job['description'][:200]}"
            job_summaries.append(summary)

        chat = _get_chat(
            session_id=f"top10-{user_id}-{uuid.uuid4().hex[:8]}",
            system_message="""You are an expert recruitment matching engine. Given a candidate profile and a list of jobs, identify the top 10 best matches.
Return ONLY valid JSON:
{
  "top_matches": [
    {
      "job_index": <number>,
      "match_percentage": <number 0-100>,
      "confidence_score": <number 0-100>,
      "why_matched": "<brief explanation>",
      "missing_requirements": ["req1", "req2"]
    }
  ]
}
Rank by match_percentage descending. Be specific about why each job matches.""",
        )

        prompt = f"""Find the top 10 best matching jobs for this candidate:

=== CANDIDATE ===
{candidate_text}

=== AVAILABLE JOBS ===
{chr(10).join(job_summaries)}

Return top 10 matches as JSON."""

        response_text = await chat.send_message(UserMessage(text=prompt))

        result = _parse_json_response(response_text)
        if not result or "top_matches" not in result:
            await refund_wallet(db, user_id, wallet["cost"], "Failed to parse AI response")
            return {"success": False, "error": "AI response parsing failed", "refunded": True}

        # Enrich with full job data
        enriched_matches = []
        for match in result["top_matches"][:10]:
            idx = match.get("job_index", -1)
            if 0 <= idx < len(jobs):
                job = jobs[idx]
                enriched_matches.append({
                    "job_id": job["id"],
                    "job_title": job.get("title", ""),
                    "company_name": job.get("company_name", ""),
                    "location": job.get("location", ""),
                    "salary": job.get("salary", ""),
                    "work_type": job.get("work_type", ""),
                    "match_percentage": match.get("match_percentage", 0),
                    "confidence_score": match.get("confidence_score", 0),
                    "why_matched": match.get("why_matched", ""),
                    "missing_requirements": match.get("missing_requirements", []),
                })

        # Store search result
        search_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "matches": enriched_matches,
            "cost_charged": wallet["cost"],
            "created_at": datetime.utcnow(),
        }
        await db.ai_top_searches.insert_one(search_record)
        del search_record["_id"]

        await log_ai_usage(db, user_id, "top_matches", wallet["cost"])

        return {"success": True, "result": search_record, "new_balance": wallet["new_balance"]}

    except Exception as e:
        logger.error(f"Top matches error for user {user_id}: {e}")
        await refund_wallet(db, user_id, wallet["cost"], f"Error: {str(e)}")
        return {"success": False, "error": "An error occurred. Your wallet has been refunded.", "refunded": True}


# ============================================================
# FEATURE 3: AUTO-APPLY TO TOP JOBS (R50)
# ============================================================

async def auto_apply_jobs(db, user_id: str, job_ids: list, min_match_score: int = 70) -> dict:
    """Auto-apply to selected jobs with AI-generated cover letters."""
    wallet = await check_and_deduct_wallet(db, user_id, "auto_apply")
    if not wallet["success"]:
        return wallet

    try:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        profile = await db.job_seeker_profiles.find_one({"user_id": user_id}, {"_id": 0})
        candidate_text = _build_candidate_profile(user, profile)

        results = []
        for job_id in job_ids[:10]:
            # Check if already applied
            existing = await db.job_applications.find_one({"applicant_id": user_id, "job_id": job_id})
            if existing:
                results.append({"job_id": job_id, "status": "already_applied", "message": "Already applied to this job"})
                continue

            job = await db.jobs.find_one({"id": job_id, "is_active": {"$ne": False}}, {"_id": 0})
            if not job:
                results.append({"job_id": job_id, "status": "skipped", "message": "Job not found or inactive"})
                continue

            job_text = _build_job_summary(job)

            # Generate cover letter
            chat = _get_chat(
                session_id=f"cover-{user_id}-{job_id}",
                system_message="""You are an expert career coach. Write a personalized, compelling cover letter for this candidate applying to this job.
The cover letter should:
- Be professional but not generic
- Highlight specific matching skills and experience
- Address the job requirements directly
- Be concise (200-300 words)
- Make the candidate stand out

Return ONLY valid JSON:
{
  "cover_letter": "<the full cover letter text>",
  "key_selling_points": ["point1", "point2", "point3"]
}""",
            )

            prompt = f"""Write a cover letter for this application:

=== CANDIDATE ===
{candidate_text}

=== JOB ===
{job_text}

Return as JSON."""

            response_text = await chat.send_message(UserMessage(text=prompt))

            cover_data = _parse_json_response(response_text)
            cover_letter = cover_data.get("cover_letter", "") if cover_data else ""

            # Create the application
            application = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "applicant_id": user_id,
                "cover_letter": cover_letter,
                "status": "submitted",
                "source": "ai_auto_apply",
                "ai_generated": True,
                "applied_date": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await db.job_applications.insert_one(application)

            results.append({
                "job_id": job_id,
                "application_id": application["id"],
                "job_title": job.get("title", ""),
                "company_name": job.get("company_name", ""),
                "status": "applied",
                "cover_letter_preview": cover_letter[:150] + "..." if len(cover_letter) > 150 else cover_letter,
            })

        # Store auto-apply record
        apply_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "applications": results,
            "cost_charged": wallet["cost"],
            "created_at": datetime.utcnow(),
        }
        await db.ai_auto_applies.insert_one(apply_record)

        await log_ai_usage(db, user_id, "auto_apply", wallet["cost"], {"job_count": len(job_ids)})

        applied_count = sum(1 for r in results if r["status"] == "applied")
        return {
            "success": True,
            "result": {
                "applied_count": applied_count,
                "total_requested": len(job_ids),
                "applications": results,
            },
            "new_balance": wallet["new_balance"],
        }

    except Exception as e:
        logger.error(f"Auto-apply error for user {user_id}: {e}")
        await refund_wallet(db, user_id, wallet["cost"], f"Error: {str(e)}")
        return {"success": False, "error": "An error occurred. Your wallet has been refunded.", "refunded": True}


# ============================================================
# FEATURE 4: CV & PROFILE ENHANCEMENT (R80)
# ============================================================

async def enhance_cv_profile(db, user_id: str) -> dict:
    """Analyze and enhance the job seeker's CV and profile."""
    wallet = await check_and_deduct_wallet(db, user_id, "cv_enhance")
    if not wallet["success"]:
        return wallet

    try:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        profile = await db.job_seeker_profiles.find_one({"user_id": user_id}, {"_id": 0})
        candidate_text = _build_candidate_profile(user, profile)

        chat = _get_chat(
            session_id=f"cv-enhance-{user_id}-{uuid.uuid4().hex[:8]}",
            system_message="""You are an expert career coach and CV specialist. Analyze the candidate's profile and CV, then provide detailed enhancement recommendations.

Return ONLY valid JSON:
{
  "overall_score": <number 0-100>,
  "ats_score": <number 0-100>,
  "profile_completion_score": <number 0-100>,
  "improved_professional_summary": "<rewritten professional summary>",
  "suggested_skills": ["skill1", "skill2", ...],
  "suggested_keywords": ["keyword1", "keyword2", ...],
  "missing_information": ["info1", "info2", ...],
  "rewritten_achievements": ["achievement1", "achievement2", ...],
  "improved_experience_descriptions": [
    {"original_role": "<role>", "improved_description": "<better description>"}
  ],
  "improved_skills_section": "<rewritten skills section>",
  "improved_profile_summary": "<enhanced profile summary>",
  "general_recommendations": ["rec1", "rec2", ...]
}
Be specific, actionable, and reference actual content from their profile.""",
        )

        prompt = f"""Analyze and enhance this candidate's CV and profile:

=== CURRENT PROFILE ===
{candidate_text}

Provide comprehensive enhancement recommendations as JSON."""

        response_text = await chat.send_message(UserMessage(text=prompt))

        result = _parse_json_response(response_text)
        if not result:
            await refund_wallet(db, user_id, wallet["cost"], "Failed to parse AI response")
            return {"success": False, "error": "AI response parsing failed", "refunded": True}

        # Store enhancement record
        enhance_record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "result": result,
            "cost_charged": wallet["cost"],
            "created_at": datetime.utcnow(),
        }
        await db.ai_cv_enhancements.insert_one(enhance_record)
        del enhance_record["_id"]

        await log_ai_usage(db, user_id, "cv_enhance", wallet["cost"])

        return {"success": True, "result": enhance_record, "new_balance": wallet["new_balance"]}

    except Exception as e:
        logger.error(f"CV enhance error for user {user_id}: {e}")
        await refund_wallet(db, user_id, wallet["cost"], f"Error: {str(e)}")
        return {"success": False, "error": "An error occurred. Your wallet has been refunded.", "refunded": True}


def _parse_json_response(text: str) -> dict:
    """Extract and parse JSON from an LLM response"""
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    import re
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*\}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue

    logger.error(f"Failed to parse JSON from response: {text[:200]}")
    return None
