"""
JobRocket - AI Matching Service
Provides AI-powered candidate-job matching with fallback to keyword matching
Includes kill switch to disable AI and revert to keyword matching
"""

import os
import re
import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration - can be toggled via environment variable or database setting
AI_MATCHING_ENABLED = os.environ.get('AI_MATCHING_ENABLED', 'true').lower() == 'true'


class AIMatchingService:
    """
    AI-powered matching service with keyword fallback.
    Can be disabled via environment variable AI_MATCHING_ENABLED=false
    """
    
    def __init__(self, db=None):
        self.db = db
        self._ai_enabled = AI_MATCHING_ENABLED
        self._llm_chat = None
        self._api_key = os.environ.get('EMERGENT_LLM_KEY')
    
    @property
    def is_ai_enabled(self) -> bool:
        """Check if AI matching is currently enabled"""
        return self._ai_enabled and self._api_key is not None
    
    def enable_ai(self):
        """Enable AI matching"""
        self._ai_enabled = True
        logger.info("AI matching enabled")
    
    def disable_ai(self):
        """Disable AI matching (kill switch)"""
        self._ai_enabled = False
        logger.warning("AI matching disabled - falling back to keyword matching")
    
    async def get_match_score(
        self,
        job: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get match score between a job and candidate.
        Uses AI if enabled, otherwise falls back to keyword matching.
        
        Returns:
            {
                "score": int (0-100),
                "reasoning": str,
                "method": "ai" | "keyword",
                "breakdown": {...}
            }
        """
        if self.is_ai_enabled:
            try:
                return await self._ai_match(job, candidate)
            except Exception as e:
                logger.error(f"AI matching failed, falling back to keyword: {e}")
                return self._keyword_match(job, candidate)
        else:
            return self._keyword_match(job, candidate)
    
    async def _ai_match(
        self,
        job: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI-powered matching using LLM"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Initialize chat if not already done
        if not self._llm_chat:
            self._llm_chat = LlmChat(
                api_key=self._api_key,
                session_id=f"match-{datetime.utcnow().timestamp()}",
                system_message="""You are an expert recruitment AI assistant. 
Your task is to analyze job requirements and candidate profiles to determine match quality.
You must respond ONLY with valid JSON in this exact format:
{
    "score": <number 0-100>,
    "reasoning": "<brief explanation>",
    "skills_match": <number 0-100>,
    "experience_match": <number 0-100>,
    "location_match": <number 0-100>,
    "top_matching_skills": ["skill1", "skill2", "skill3"],
    "missing_skills": ["skill1", "skill2"]
}"""
            ).with_model("openai", "gpt-5.2")
        
        # Build the prompt
        job_text = f"""
JOB DETAILS:
- Title: {job.get('title', 'Unknown')}
- Company: {job.get('company_name', 'Unknown')}
- Location: {job.get('location', 'Unknown')}
- Description: {job.get('description', '')}
- Required Experience: {job.get('experience', 'Not specified')}
- Qualifications: {job.get('qualifications', 'Not specified')}
- Industry: {job.get('industry', 'Not specified')}
- Work Type: {job.get('work_type', 'Not specified')}
"""
        
        candidate_text = f"""
CANDIDATE PROFILE:
- Name: {candidate.get('first_name', '')} {candidate.get('last_name', '')}
- Location: {candidate.get('location', 'Unknown')}
- About: {candidate.get('about_me', '')}
- Skills: {', '.join(candidate.get('skills', []))}
- Experience Level: {self._estimate_experience_level(candidate)}
"""
        
        prompt = f"""Analyze the match between this job and candidate:

{job_text}

{candidate_text}

Provide a match score and analysis as JSON only."""

        user_message = UserMessage(text=prompt)
        
        try:
            response = await self._llm_chat.send_message(user_message)
            
            # Parse JSON response
            import json
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "score": min(100, max(0, int(result.get("score", 50)))),
                    "reasoning": result.get("reasoning", "AI analysis complete"),
                    "method": "ai",
                    "breakdown": {
                        "skills_match": result.get("skills_match", 50),
                        "experience_match": result.get("experience_match", 50),
                        "location_match": result.get("location_match", 50),
                        "top_matching_skills": result.get("top_matching_skills", []),
                        "missing_skills": result.get("missing_skills", [])
                    }
                }
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            raise
        
        # Fallback if parsing fails
        return self._keyword_match(job, candidate)
    
    def _keyword_match(
        self,
        job: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Keyword-based matching algorithm"""
        
        # Extract job requirements
        job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('qualifications', '')}".lower()
        job_location = job.get('location', '').lower()
        
        # Extract candidate info
        candidate_skills = [s.lower() for s in candidate.get('skills', [])]
        candidate_location = candidate.get('location', '').lower()
        candidate_about = candidate.get('about_me', '').lower()
        
        # Skills matching
        skills_score = 0
        matching_skills = []
        missing_skills = []
        
        # Common skills to look for
        common_skills = [
            'python', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 'aws',
            'docker', 'kubernetes', 'git', 'java', 'c++', 'c#', '.net', 'php',
            'ruby', 'go', 'rust', 'typescript', 'html', 'css', 'sass', 'vue',
            'angular', 'django', 'flask', 'fastapi', 'spring', 'express',
            'postgresql', 'mysql', 'redis', 'elasticsearch', 'graphql',
            'machine learning', 'data science', 'ai', 'deep learning',
            'figma', 'photoshop', 'illustrator', 'sketch', 'xd',
            'marketing', 'seo', 'analytics', 'social media', 'content',
            'excel', 'powerbi', 'tableau', 'power bi', 'salesforce',
            'project management', 'agile', 'scrum', 'jira', 'leadership'
        ]
        
        # Check which skills from job description the candidate has
        for skill in common_skills:
            if skill in job_text:
                if skill in candidate_skills or skill in candidate_about:
                    matching_skills.append(skill)
                    skills_score += 20
                else:
                    missing_skills.append(skill)
        
        # Also check candidate's listed skills against job
        for skill in candidate_skills:
            if skill in job_text and skill not in matching_skills:
                matching_skills.append(skill)
                skills_score += 15
        
        skills_score = min(100, skills_score)
        
        # Location matching
        location_score = 0
        if job.get('work_type', '').lower() == 'remote':
            location_score = 100
        elif job_location and candidate_location:
            # Check for city/province match
            if any(loc in candidate_location for loc in job_location.split(',')):
                location_score = 100
            elif any(loc in job_location for loc in candidate_location.split(',')):
                location_score = 100
            else:
                # Partial match (same country)
                sa_indicators = ['south africa', 'gauteng', 'western cape', 'kwazulu', 'johannesburg', 'cape town', 'pretoria', 'durban']
                if any(ind in job_location for ind in sa_indicators) and any(ind in candidate_location for ind in sa_indicators):
                    location_score = 60
        
        # Experience level estimation
        experience_score = 50  # Default middle score
        exp_level = self._estimate_experience_level(candidate)
        job_exp = job.get('experience', '').lower()
        
        if 'senior' in job_exp or '5+' in job_exp or '7+' in job_exp:
            if exp_level in ['senior', 'lead']:
                experience_score = 100
            elif exp_level == 'mid':
                experience_score = 60
            else:
                experience_score = 30
        elif 'mid' in job_exp or '3+' in job_exp or '2-5' in job_exp:
            if exp_level in ['mid', 'senior']:
                experience_score = 100
            elif exp_level == 'junior':
                experience_score = 70
            else:
                experience_score = 40
        elif 'junior' in job_exp or 'entry' in job_exp or '0-2' in job_exp or '1-2' in job_exp:
            if exp_level in ['entry', 'junior']:
                experience_score = 100
            elif exp_level == 'mid':
                experience_score = 80
            else:
                experience_score = 60
        
        # Calculate overall score
        overall_score = int(
            (skills_score * 0.5) +
            (experience_score * 0.3) +
            (location_score * 0.2)
        )
        
        # Generate reasoning
        reasoning_parts = []
        if matching_skills:
            reasoning_parts.append(f"Strong skill matches: {', '.join(matching_skills[:5])}")
        if location_score >= 80:
            reasoning_parts.append("Location is a good fit")
        elif location_score >= 50:
            reasoning_parts.append("Location may require relocation")
        if experience_score >= 80:
            reasoning_parts.append("Experience level matches requirements")
        
        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Basic profile match"
        
        return {
            "score": overall_score,
            "reasoning": reasoning,
            "method": "keyword",
            "breakdown": {
                "skills_match": skills_score,
                "experience_match": experience_score,
                "location_match": location_score,
                "top_matching_skills": matching_skills[:5],
                "missing_skills": missing_skills[:5]
            }
        }
    
    def _estimate_experience_level(self, candidate: Dict[str, Any]) -> str:
        """Estimate candidate's experience level from profile"""
        work_exp = candidate.get('work_experience', [])
        
        if not work_exp:
            about = candidate.get('about_me', '').lower()
            if 'senior' in about or 'lead' in about or '10+ years' in about:
                return 'senior'
            elif 'junior' in about or 'entry' in about or 'graduate' in about:
                return 'entry'
            return 'mid'
        
        # Calculate total years from work experience
        total_months = 0
        for exp in work_exp:
            try:
                start = exp.get('start_date')
                end = exp.get('end_date') or datetime.utcnow()
                if isinstance(start, str):
                    start = datetime.fromisoformat(start.replace('Z', '+00:00'))
                if isinstance(end, str):
                    end = datetime.fromisoformat(end.replace('Z', '+00:00'))
                months = (end - start).days / 30
                total_months += months
            except:
                continue
        
        years = total_months / 12
        
        if years >= 8:
            return 'lead'
        elif years >= 5:
            return 'senior'
        elif years >= 2:
            return 'mid'
        elif years >= 0.5:
            return 'junior'
        return 'entry'
    
    async def batch_match(
        self,
        job: Dict[str, Any],
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match multiple candidates against a single job.
        Returns sorted list with best matches first.
        """
        results = []
        for candidate in candidates:
            match = await self.get_match_score(job, candidate)
            results.append({
                "candidate_id": candidate.get('id'),
                "candidate_name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}",
                **match
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results


# Singleton instance
_ai_matching_service: Optional[AIMatchingService] = None


def get_ai_matching_service(db=None) -> AIMatchingService:
    """Get or create the AI matching service singleton"""
    global _ai_matching_service
    if _ai_matching_service is None:
        _ai_matching_service = AIMatchingService(db)
    return _ai_matching_service


def set_ai_matching_enabled(enabled: bool):
    """Global kill switch for AI matching"""
    service = get_ai_matching_service()
    if enabled:
        service.enable_ai()
    else:
        service.disable_ai()
