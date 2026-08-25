"""Tiered LLM Fallback & Resilience Service for ZERO Downtime."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List

from services.sanitization_service import sanitize_text

logger = logging.getLogger("llm_resilience_service")


def _extract_json_payload(raw_response: str) -> Dict[str, Any]:
    """Robustly extract and parse JSON from LLM responses, handling markdown fencing."""
    if not raw_response:
        return {}
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_response.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned).strip()
    
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return {}


def evaluate_candidate_fit_tiered(
    job_title: str,
    job_description: str,
    required_skills: List[str],
    candidate_resume: str,
) -> Dict[str, Any]:
    """Calculate ATS match with resilient tiered fallbacks."""
    clean_title = sanitize_text(job_title)
    clean_resume = sanitize_text(candidate_resume)
    clean_skills = [sanitize_text(s) for s in required_skills if s.strip()]
    
    # Tier 3 Deterministic Local Fallback (Always Ready)
    matched_skills = []
    resume_lower = clean_resume.lower()
    for skill in clean_skills:
        if skill.lower() in resume_lower:
            matched_skills.append(skill)
            
    match_ratio = len(matched_skills) / max(len(clean_skills), 1)
    base_ats_score = int(min(max(match_ratio * 100, 35), 98))
    
    fallback_result = {
        "ats_score": base_ats_score,
        "fit_tier": "Strong Fit" if base_ats_score >= 75 else ("Moderate Fit" if base_ats_score >= 55 else "Low Fit"),
        "matched_skills": matched_skills,
        "missing_skills": [s for s in clean_skills if s not in matched_skills],
        "summary": f"Candidate demonstrates experience in {', '.join(matched_skills[:4]) or 'relevant domain competencies'}.",
        "execution_tier": "tier3_deterministic_engine",
        "model_used": "LocalRuleEngine_v2",
    }
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return fallback_result
        
    try:
        import urllib.request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = (
            f"You are an expert technical recruiter. Evaluate candidate resume for role '{clean_title}'.\n"
            f"Required Skills: {', '.join(clean_skills)}\n"
            f"Candidate Resume: {clean_resume[:1500]}\n\n"
            "Return ONLY valid JSON with keys: ats_score (number 0-100), fit_tier (string), "
            "matched_skills (array), missing_skills (array), summary (string)."
        )
        req_data = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            resp_body = json.loads(resp.read().decode("utf-8"))
            raw_text = resp_body["candidates"][0]["content"]["parts"][0]["text"]
            parsed = _extract_json_payload(raw_text)
            if parsed and "ats_score" in parsed:
                parsed["execution_tier"] = "tier2_gemini_flash"
                parsed["model_used"] = "gemini-1.5-flash"
                return parsed
    except Exception as e:
        logger.warning(f"Tier 1/2 LLM call failed or timed out: {e}. Gracefully falling back to Tier 3.")
        
    return fallback_result
