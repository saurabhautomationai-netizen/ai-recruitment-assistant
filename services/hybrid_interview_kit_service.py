"""Hybrid Interview Kit Service: Combining Automated AI STAR Rubrics with Manual Recruiter Questions.

Enables recruiters to:
1. Generate grounded AI STAR questions tailored to resume gaps.
2. Manually write and customize proprietary interview questions and scoring criteria.
3. Merge both into an official unified Interview Scorecard & Evaluation Kit.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.sanitization_service import sanitize_text

KITS_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "interview_kits.json")


def _load_kits_store() -> Dict[str, Any]:
    if not os.path.exists(KITS_STORE_PATH):
        os.makedirs(os.path.dirname(KITS_STORE_PATH), exist_ok=True)
        return {}
    try:
        with open(KITS_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_kits_store(data: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(KITS_STORE_PATH), exist_ok=True)
        with open(KITS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def create_manual_question(
    question_text: str,
    target_competency: str = "Technical Proficiency",
    expected_answer_signals: Optional[List[str]] = None,
    red_flags: Optional[List[str]] = None,
    max_score: int = 5,
) -> Dict[str, Any]:
    """Format a recruiter-written manual interview question with scoring rubric."""
    return {
        "id": f"q_man_{uuid.uuid4().hex[:6]}",
        "origin": "MANUAL_RECRUITER",
        "question": sanitize_text(question_text),
        "target_competency": sanitize_text(target_competency),
        "expected_answer_signals": [sanitize_text(s) for s in (expected_answer_signals or [])],
        "red_flags": [sanitize_text(f) for f in (red_flags or [])],
        "max_score": max(int(max_score), 1),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def compile_unified_interview_kit(
    job_id: str,
    job_title: str,
    candidate_id: str,
    ai_star_questions: Optional[List[Dict[str, Any]]] = None,
    manual_questions: Optional[List[Dict[str, Any]]] = None,
    interviewer_name: str = "Lead Interviewer",
) -> Dict[str, Any]:
    """Merge automated AI STAR questions and manual questions into a unified evaluation scorecard."""
    formatted_ai = []
    for q in (ai_star_questions or []):
        formatted_ai.append({
            "id": f"q_ai_{uuid.uuid4().hex[:6]}",
            "origin": "AI_GROUNDED_STAR",
            "question": sanitize_text(q.get("question", "")),
            "target_competency": sanitize_text(q.get("target_competency", "Domain Knowledge")),
            "expected_answer_signals": [sanitize_text(s) for s in q.get("expected_answer_signals", [])],
            "red_flags": [sanitize_text(f) for f in q.get("red_flags", [])],
            "max_score": 5,
        })

    all_questions = formatted_ai + (manual_questions or [])
    total_score = sum(q.get("max_score", 5) for q in all_questions)

    kit_id = f"kit_{uuid.uuid4().hex[:8]}"
    kit_payload = {
        "kit_id": kit_id,
        "job_id": str(job_id),
        "job_title": sanitize_text(job_title),
        "candidate_id": str(candidate_id),
        "interviewer_name": sanitize_text(interviewer_name),
        "total_questions": len(all_questions),
        "ai_questions_count": len(formatted_ai),
        "manual_questions_count": len(manual_questions or []),
        "max_possible_score": total_score,
        "questions": all_questions,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store = _load_kits_store()
    store[kit_id] = kit_payload
    _save_kits_store(store)
    return kit_payload


def get_interview_kit(kit_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an existing compiled interview kit."""
    store = _load_kits_store()
    return store.get(kit_id)