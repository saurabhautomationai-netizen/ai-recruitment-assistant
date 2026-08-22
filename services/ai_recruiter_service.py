"""Read-only structured query routing for the AI Recruiter page."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd


UNSAFE_PATTERNS = (
    r"\b(ignore|override|bypass)\b.{0,30}\b(instruction|prompt|policy|rule)s?\b",
    r"\b(system prompt|developer message|hidden instruction)s?\b",
    r"\b(drop|truncate|delete|insert|update|alter|grant|revoke)\b.{0,20}\b(table|database|row|policy|sql)\b",
    r"\b(select|with)\b.{0,80}\bfrom\b",
    r"(--|/\*|\*/|;\s*(drop|delete|update|insert|alter))",
)

STAGE_ALIASES = {
    "shortlist": "Shortlisted",
    "shortlisted": "Shortlisted",
    "interview": "Interview",
    "interviewing": "Interview",
    "selected": "Selected",
    "hired": "Selected",
    "rejected": "Rejected",
    "pending": "Pending Review",
    "pending review": "Pending Review",
}


def _text(value: Any) -> str:
    if value is None or isinstance(value, (dict, list, tuple, set)):
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def _items(value: Any) -> list[str]:
    if value is None:
        return []
    parsed = value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            parsed = re.split(r"[,;|\n]", text)
    if isinstance(parsed, dict):
        parsed = parsed.get("skills", list(parsed.values()))
    if not isinstance(parsed, (list, tuple, set)):
        parsed = [parsed]
    return [_text(item) for item in parsed if _text(item)]


def _number(value: Any) -> float | None:
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)


def _id(value: Any) -> str:
    return _text(value)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [] if frame.empty else frame.to_dict("records")


def _result(
    intent: str,
    summary: str,
    reasoning: str,
    candidates: pd.DataFrame | None = None,
    comparison: pd.DataFrame | None = None,
    confidence: str = "High",
) -> dict[str, Any]:
    return {
        "intent": intent,
        "summary": summary,
        "reasoning": reasoning,
        "candidates": _records(candidates if candidates is not None else pd.DataFrame()),
        "comparison": _records(comparison if comparison is not None else pd.DataFrame()),
        "confidence": confidence,
    }


def _build_candidate_view(
    candidates: pd.DataFrame,
    applications: pd.DataFrame,
    jobs: pd.DataFrame,
) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame()

    view = candidates.copy()
    view["candidate_id"] = view.get("id", pd.Series("", index=view.index)).map(_id)
    view["Candidate"] = view.get(
        "full_name", pd.Series("Unknown candidate", index=view.index)
    ).map(lambda value: _text(value) or "Unknown candidate")
    view["Skills"] = view.get("skills", pd.Series(None, index=view.index)).map(_items)
    view["Experience"] = pd.to_numeric(
        view.get("years_experience", pd.Series(None, index=view.index)),
        errors="coerce",
    )
    view["Candidate status"] = view.get(
        "status", pd.Series("", index=view.index)
    ).map(_text)

    if applications.empty or "candidate_id" not in applications.columns:
        view["application_id"] = ""
        view["job_id"] = ""
        view["Stage"] = view["Candidate status"]
        view["Candidate score"] = None
        view["ATS score"] = None
        view["Recommendation"] = ""
    else:
        apps = applications.copy()
        apps["candidate_id"] = apps["candidate_id"].map(_id)
        apps["application_id"] = apps.get(
            "id", pd.Series("", index=apps.index)
        ).map(_id)
        if "applied_at" in apps.columns:
            apps["_applied_at"] = pd.to_datetime(
                apps["applied_at"], errors="coerce", utc=True
            )
            apps = apps.sort_values("_applied_at", ascending=False, na_position="last")
        apps = apps.drop_duplicates("candidate_id", keep="first")
        app_columns = [
            column for column in (
                "candidate_id", "application_id", "job_id", "application_stage",
                "candidate_score", "ats_score", "recommendation",
            ) if column in apps.columns
        ]
        view = view.merge(apps[app_columns], on="candidate_id", how="left")
        view["Stage"] = view.get(
            "application_stage", pd.Series("", index=view.index)
        ).map(_text)
        view["Stage"] = view["Stage"].where(
            view["Stage"].ne(""), view["Candidate status"]
        )
        view["Candidate score"] = pd.to_numeric(
            view.get("candidate_score", pd.Series(None, index=view.index)),
            errors="coerce",
        )
        view["ATS score"] = pd.to_numeric(
            view.get("ats_score", pd.Series(None, index=view.index)),
            errors="coerce",
        )
        view["Recommendation"] = view.get(
            "recommendation", pd.Series("", index=view.index)
        ).map(_text)

    title_by_id: dict[str, str] = {}
    if not jobs.empty and {"id", "title"}.issubset(jobs.columns):
        title_by_id = {
            _id(row.get("id")): _text(row.get("title"))
            for _, row in jobs.iterrows()
            if _id(row.get("id"))
        }
    view["Job"] = view.get("job_id", pd.Series("", index=view.index)).map(
        lambda value: title_by_id.get(_id(value), "Not assigned")
    )
    return view


def _find_named(view: pd.DataFrame, name: str) -> pd.DataFrame:
    normalized = " ".join(name.casefold().split())
    if not normalized or view.empty:
        return view.iloc[0:0]
    exact = view[view["Candidate"].str.casefold() == normalized]
    if not exact.empty:
        return exact
    contains = view[
        view["Candidate"].str.casefold().str.contains(
            re.escape(normalized), regex=True, na=False
        )
    ]
    if not contains.empty:
        return contains
    # Fallback to token/first-name matching for minor spelling or single names
    words = [w for w in normalized.split() if len(w) >= 3]
    for w in words:
        word_match = view[view["Candidate"].str.casefold().str.contains(re.escape(w), regex=True, na=False)]
        if not word_match.empty:
            return word_match
    return view.iloc[0:0]


def _public_columns(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "candidate_id", "Candidate", "Job", "Stage", "Experience", "Skills",
        "Candidate score", "ATS score", "Recommendation",
    ]
    return frame[[column for column in columns if column in frame.columns]].copy()


def _unsafe(query: str) -> bool:
    return any(re.search(pattern, query, flags=re.IGNORECASE | re.DOTALL) for pattern in UNSAFE_PATTERNS)


def answer_recruiter_query(
    query: str,
    candidates: pd.DataFrame,
    applications: pd.DataFrame,
    jobs: pd.DataFrame,
    interviews: pd.DataFrame,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Route a recruiter question to an allowlisted, read-only operation."""

    raw_text = str(query).strip().strip("\"'`“”«»").strip()
    question = " ".join(raw_text.split())
    lowered = question.casefold()
    if not question:
        return _result("empty", "Please enter a recruiter question.", "No query was run.")
    if len(question) > 500:
        return _result("blocked", "That request is too long.", "Queries are limited to 500 characters for safety.", confidence="Blocked")
    if _unsafe(question):
        return _result("blocked", "I can only answer read-only recruitment questions.", "The request contained instructions or database operations outside the allowlisted recruiter tools.", confidence="Blocked")

    view = _build_candidate_view(candidates, applications, jobs)
    if view.empty:
        return _result("no_data", "No candidate data is available.", "The candidates table returned no rows.")

    compare_match = re.search(r"\bcompare\s+(.+?)\s+(?:and|with|to|vs\.?|versus)\s+(.+?)[?.]*$", question, re.I)
    if compare_match:
        names = [part.strip(" .?") for part in compare_match.groups()]
        matches = [_find_named(view, name) for name in names]
        missing = [name for name, match in zip(names, matches) if match.empty]
        if missing:
            return _result("compare", f"No unique comparison was available for: {', '.join(missing)}.", "Candidate names are resolved against the stored full_name field.", confidence="Medium")
        selected = pd.concat([match.head(1) for match in matches], ignore_index=True)
        comparison = _public_columns(selected).set_index("Candidate").transpose().reset_index(names="Attribute")
        return _result("compare", f"Comparison of {names[0]} and {names[1]}.", "The table compares their latest application, stored scores, experience, skills and recommendation.", comparison=comparison)

    why_match = re.search(r"\bwhy\s+(?:was|is)\s+(.+?)\s+(rejected|recommended)[?.]*$", question, re.I)
    if why_match:
        name, decision = why_match.groups()
        match = _find_named(view, name.strip())
        if match.empty:
            return _result("decision_reason", f"No candidate matched “{name.strip()}”.", "Candidate names are resolved against full_name.", confidence="Medium")
        row = match.iloc[0]
        recommendation = _text(row.get("Recommendation"))
        stage = _text(row.get("Stage")) or "Not available"
        if recommendation:
            summary = f"Stored recommendation for {row['Candidate']}: {recommendation}"
            reasoning = f"Latest application stage: {stage}. This explanation uses only the stored recommendation and scores; the schema has no separate decision-reason field."
        else:
            summary = f"No stored rationale is available for {row['Candidate']}."
            reasoning = f"The latest application stage is {stage}, but the existing schema contains no separate rejection/recommendation reason field."
        score = _number(row.get("Candidate score"))
        confidence = f"{score:.0f}% stored candidate score" if score is not None else "Not available"
        return _result("decision_reason", summary, reasoning, candidates=_public_columns(match.head(1)), confidence=confidence)

    ats_match = re.search(r"\bats(?:\s+score)?\s+(?:above|over|greater than|>)\s*(\d+(?:\.\d+)?)", lowered)
    if ats_match:
        threshold = float(ats_match.group(1))
        matched = view[view["ATS score"] > threshold].sort_values("ATS score", ascending=False)
        return _result("ats_threshold", f"Found {len(matched)} candidate(s) with ATS score above {threshold:g}.", "Filtered the stored applications.ats_score value; no score was generated.", candidates=_public_columns(matched))

    experience_match = re.search(r"\b(?:more than|over|above|greater than|>)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", lowered)
    if experience_match:
        threshold = float(experience_match.group(1))
        matched = view[view["Experience"] > threshold].sort_values("Experience", ascending=False)
        return _result("experience", f"Found {len(matched)} candidate(s) with more than {threshold:g} years of experience.", "Filtered candidates.years_experience using a numeric comparison.", candidates=_public_columns(matched))

    if "scheduled this week" in lowered or "interviews this week" in lowered:
        current = now or datetime.now(timezone.utc)
        start = current - timedelta(days=current.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        app_ids: set[str] = set()
        if not interviews.empty and {"application_id", "interview_date"}.issubset(interviews.columns):
            scheduled = interviews.copy()
            scheduled["_date"] = pd.to_datetime(scheduled["interview_date"], errors="coerce", utc=True)
            app_ids = set(scheduled.loc[(scheduled["_date"] >= start) & (scheduled["_date"] < end), "application_id"].map(_id))
        matched = view[view.get("application_id", pd.Series("", index=view.index)).map(_id).isin(app_ids)]
        return _result("interviews_week", f"Found {len(matched)} candidate(s) scheduled this week.", "Joined interviews.application_id to the latest applications.id and filtered the current UTC week.", candidates=_public_columns(matched))

    if "without interview" in lowered or "no interview" in lowered:
        interviewed_ids = set()
        if not interviews.empty and "application_id" in interviews.columns:
            interviewed_ids = set(interviews["application_id"].map(_id))
        application_ids = view.get("application_id", pd.Series("", index=view.index)).map(_id)
        matched = view[application_ids.ne("") & ~application_ids.isin(interviewed_ids)]
        return _result("without_interview", f"Found {len(matched)} candidate(s) with an application and no interview record.", "Compared latest applications.id with interviews.application_id.", candidates=_public_columns(matched))

    best_match = re.search(r"\b(?:best candidate|best fit|recommend(?:ed)? candidate)\s+(?:for\s+)?(.+?)[?.]*$", question, re.I)
    matching_match = re.search(r"\bcandidates?\s+matching\s+(.+?)[?.]*$", question, re.I)
    job_query = (best_match or matching_match)
    if job_query:
        requested = job_query.group(1).strip()
        job_matches = jobs.iloc[0:0]
        if not jobs.empty and "title" in jobs.columns:
            job_matches = jobs[jobs["title"].astype(str).str.casefold().str.contains(re.escape(requested.casefold()), regex=True, na=False)]
        if job_matches.empty:
            return _result("job_match", f"No job matched “{requested}”.", "Job names are resolved against jobs.title.", confidence="Medium")
        job = job_matches.iloc[0]
        matched = view[view.get("job_id", pd.Series("", index=view.index)).map(_id).eq(_id(job.get("id")))]
        matched = matched.sort_values(["Candidate score", "ATS score"], ascending=False, na_position="last")
        if best_match and not matched.empty:
            matched = matched.head(1)
            score = _number(matched.iloc[0].get("Candidate score"))
            confidence = f"{score:.0f}% stored candidate score" if score is not None else "Not available"
            summary = f"Best stored match for {job.get('title')}: {matched.iloc[0]['Candidate']}."
        else:
            confidence = "High"
            summary = f"Found {len(matched)} application(s) matching {job.get('title')}."
        return _result("job_match", summary, "Matched applications.job_id to jobs.id, then ranked by stored candidate_score and ats_score. This is not a newly generated hiring decision.", candidates=_public_columns(matched), confidence=confidence)

    stage_match = next((label for alias, label in STAGE_ALIASES.items() if re.search(rf"\b{re.escape(alias)}\b", lowered)), None)
    if stage_match:
        matched = view[view["Stage"].str.casefold().eq(stage_match.casefold())]
        return _result("stage", f"Found {len(matched)} candidate(s) in {stage_match}.", "Used the latest applications.application_stage, falling back to candidates.status only where no application stage exists.", candidates=_public_columns(matched))

    skill_match = re.search(r"\b(?:show|list|find|get)\s+(?:all\s+)?(?:the\s+)?(.+?)\s+candidates?[?.]*$", question, re.I)
    if skill_match:
        skill = skill_match.group(1).strip()
        reserved = {"all", "the", "me", "candidate"}
        if skill.casefold() not in reserved:
            matched = view[view["Skills"].map(lambda values: any(skill.casefold() in value.casefold() for value in values))]
            return _result("skill", f"Found {len(matched)} candidate(s) with {skill} in their stored skills.", "Matched the request against candidates.skills after safely parsing text, lists and JSON.", candidates=_public_columns(matched))

    return _result(
        "unsupported",
        "I couldn’t map that question to a safe recruiter query.",
        "Try a skills, experience, application-stage, ATS, interview, candidate comparison, decision-rationale, or job-match question. No database query was executed from your text.",
        confidence="Low",
    )
