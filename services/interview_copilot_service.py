"""Evidence-grounded, session-safe interview assistance."""

from __future__ import annotations

import re
from typing import Any


FOCUS_AREAS = ("Technical", "Experience", "Behavioural", "Role Fit")


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return "; ".join(f"{key}: {_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return ", ".join(filter(None, (_text(item) for item in value)))
    return str(value).strip()


def build_interview_preparation(
    candidate: dict[str, Any],
    application: dict[str, Any],
    job: dict[str, Any],
    notes: list[dict[str, Any]],
    interviews: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a factual preparation brief from stored recruitment evidence."""

    skills = _text(candidate.get("skills"))
    required = _text(job.get("required_skills"))
    candidate_tokens = {token.casefold() for token in re.findall(r"[\w+#.-]+", skills)}
    required_items = [item.strip() for item in re.split(r"[,;|]", required) if item.strip()]
    matched = [item for item in required_items if item.casefold() in candidate_tokens]
    missing = [item for item in required_items if item.casefold() not in candidate_tokens]
    previous_feedback = []
    for item in interviews:
        feedback = item.get("feedback")
        if isinstance(feedback, dict):
            feedback = feedback.get("feedback") or feedback.get("notes")
        if _text(feedback):
            previous_feedback.append(_text(feedback))
    return {
        "candidate_summary": _text(candidate.get("resume_summary"))
        or _text(candidate.get("summary"))
        or f"{_text(candidate.get('full_name')) or 'Candidate'} has "
           f"{_text(candidate.get('years_experience')) or 'unspecified'} years of stored experience.",
        "job_requirements": required or _text(job.get("description")) or "Not available",
        "strong_areas": matched or ([skills] if skills else []),
        "concerns": missing,
        "focus_areas": missing or required_items or ["Validate role-specific experience"],
        "candidate_score": application.get("candidate_score"),
        "ats_score": application.get("ats_score"),
        "recommendation": _text(application.get("recommendation")),
        "stored_questions": application.get("interview_questions") or [],
        "recruiter_notes": [_text(note.get("note")) for note in notes if _text(note.get("note"))],
        "previous_feedback": previous_feedback,
    }


def suggest_follow_up(focus_area: str, response: str, preparation: dict[str, Any]) -> str:
    """Suggest a neutral follow-up without making a hiring decision."""

    response = " ".join(response.strip().split())
    if not response:
        return "Ask the candidate to describe a specific example before requesting more detail."
    snippets = {
        "Technical": "What trade-offs did you consider, and how did you validate the result?",
        "Experience": "What was your personal contribution, and what measurable outcome followed?",
        "Behavioural": "What did you do next, and what would you change in a similar situation?",
        "Role Fit": "How would that experience help you deliver the responsibilities of this role?",
    }
    focus = focus_area if focus_area in FOCUS_AREAS else "Role Fit"
    concern = next(iter(preparation.get("concerns", [])), "")
    suffix = f" Also clarify their experience with {concern}." if concern else ""
    return snippets[focus] + suffix


def evaluate_interview(entries: list[dict[str, str]]) -> dict[str, Any]:
    """Summarize recruiter-entered evidence without recommending a hire."""

    completed = [entry for entry in entries if entry.get("response", "").strip()]
    strengths = [
        entry["response"].strip()
        for entry in completed
        if any(word in entry["response"].casefold() for word in ("led", "improved", "built", "delivered", "reduced"))
    ]
    concerns = [
        entry["response"].strip()
        for entry in completed
        if any(word in entry["response"].casefold() for word in ("unsure", "limited", "not used", "no experience"))
    ]
    uncovered = [area for area in FOCUS_AREAS if area not in {entry.get("area") for entry in completed}]
    next_step = (
        "Recruiter review is required; cover the remaining areas before deciding: "
        + ", ".join(uncovered)
        if uncovered
        else "Recruiter review is required. Compare the evidence with the role criteria before choosing a next step."
    )
    return {
        "strengths": strengths,
        "concerns": concerns,
        "evidence": [f"{entry.get('area')}: {entry.get('response', '').strip()}" for entry in completed],
        "recommended_next_step": next_step,
    }
