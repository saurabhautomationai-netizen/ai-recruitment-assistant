import pandas as pd
import streamlit as st
from supabase import Client
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from datetime import date, time
from zoneinfo import ZoneInfo

from services.auth_service import (
    get_session_supabase_client,
    require_permission,
)


def get_supabase_client() -> Client:
    """Create and return the Supabase client."""

    return get_session_supabase_client()


def fetch_table(
    table_name: str,
    order_column: str = "created_at",
) -> pd.DataFrame:
    """
    Retrieve records from a Supabase table and return a DataFrame.
    """

    try:
        supabase = get_supabase_client()

        query = (
            supabase.table(table_name)
            .select("*")
        )

        if order_column:
            query = query.order(
                order_column,
                desc=True,
            )

        response = query.execute()
        rows = response.data or []

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows)

    except Exception as error:
        st.error(
            f"Could not load {table_name} from Supabase: {error}"
        )
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_candidates() -> pd.DataFrame:
    """Load candidate records."""

    return fetch_table("candidates")


@st.cache_data(ttl=60)
def get_applications() -> pd.DataFrame:
    """Load application records."""

    return fetch_table("applications", order_column="applied_at")


def update_application_stage(
    application_id: str,
    application_stage: str,
) -> None:
    """Update the stage of one application identified by its id."""

    require_permission("candidate_write")

    if not application_id:
        raise ValueError("An application id is required.")

    supabase = get_supabase_client()
    supabase.table("applications").update(
        {"application_stage": application_stage}
    ).eq("id", application_id).execute()


def _update_record(
    table_name: str,
    record_id: str,
    updates: dict,
    allowed_fields: set[str],
) -> None:
    """Update one authenticated record using an explicit field allowlist."""

    permission_by_table = {
        "candidates": "candidate_write",
        "jobs": "job_write",
    }
    require_permission(permission_by_table[table_name])
    if not record_id:
        raise ValueError(f"A {table_name.rstrip('s')} id is required.")
    safe_updates = {
        field: value
        for field, value in updates.items()
        if field in allowed_fields
    }
    if not safe_updates:
        raise ValueError("No supported updates were provided.")
    response = (
        get_supabase_client()
        .table(table_name)
        .update(safe_updates)
        .eq("id", record_id)
        .execute()
    )
    if not response.data:
        raise RuntimeError(
            f"The {table_name.rstrip('s')} could not be found or updated."
        )


def update_candidate(candidate_id: str, updates: dict) -> None:
    """Edit or archive a candidate without permitting deletion."""

    safe_updates = dict(updates)
    if "years_experience" in safe_updates:
        safe_updates["years_experience"] = normalize_years_experience(
            safe_updates["years_experience"]
        )

    _update_record(
        "candidates",
        candidate_id,
        safe_updates,
        {
            "full_name",
            "email",
            "phone",
            "location",
            "years_experience",
            "current_company",
            "current_role",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "status",
        },
    )


def normalize_years_experience(value) -> int | None:
    """Normalize nullable whole-year values for the integer database column."""

    if value is None:
        return None
    if not isinstance(value, (dict, list, tuple, set)):
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
    if isinstance(value, bool):
        raise ValueError("Years of experience must be a whole number.")
    text = str(value).strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValueError("Years of experience must be a whole number.") from None
    if not number.is_finite() or number != number.to_integral_value() or number < 0:
        raise ValueError("Years of experience must be a non-negative whole number.")
    return int(number)


def update_job(job_id: str, updates: dict) -> None:
    """Edit or transition a job lifecycle without permitting deletion."""

    safe_updates = dict(updates)
    if "description" in safe_updates and "job_description" not in safe_updates:
        safe_updates["job_description"] = safe_updates.pop("description")
    if "min_experience" in safe_updates and "experience_required" not in safe_updates:
        safe_updates["experience_required"] = safe_updates.pop("min_experience")

    _update_record(
        "jobs",
        job_id,
        safe_updates,
        {
            "title",
            "department",
            "location",
            "job_description",
            "required_skills",
            "experience_required",
            "salary_min",
            "salary_max",
            "employment_type",
            "status",
        },
    )


def create_job(job_data: dict) -> dict:
    """Insert a new job requisition into Supabase."""

    require_permission("job_write")
    raw_data = dict(job_data)
    if "description" in raw_data and "job_description" not in raw_data:
        raw_data["job_description"] = raw_data.pop("description")
    if "min_experience" in raw_data and "experience_required" not in raw_data:
        raw_data["experience_required"] = raw_data.pop("min_experience")

    allowed_fields = {
        "title",
        "department",
        "location",
        "job_description",
        "required_skills",
        "experience_required",
        "salary_min",
        "salary_max",
        "employment_type",
        "status",
    }
    safe_data = {
        field: value
        for field, value in raw_data.items()
        if field in allowed_fields and value is not None
    }
    if not safe_data.get("title", "").strip():
        raise ValueError("Job title is required.")
    
    safe_data.setdefault("status", "Open")
    client = get_supabase_client()
    response = client.table("jobs").insert(safe_data).execute()
    if not response.data:
        raise RuntimeError("Could not create the job.")
    new_job = response.data[0]
    try:
        from services.recruiter_partition_service import assign_job_to_recruiter, get_current_recruiter_email
        cur_email = get_current_recruiter_email()
        if cur_email and "id" in new_job:
            assign_job_to_recruiter(str(new_job["id"]), cur_email)
    except Exception:
        pass
    return new_job


@st.cache_data(ttl=60)
def get_interviews() -> pd.DataFrame:
    """Load scheduled interview records."""

    return fetch_table("interviews", order_column="interview_date")


INTERVIEW_LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")


def normalize_interview_datetime(value) -> str:
    """Return one canonical UTC ISO value for the timestamptz column."""

    timestamp = pd.Timestamp(value)
    if pd.isna(timestamp):
        raise ValueError("Interview date and time are required.")
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(INTERVIEW_LOCAL_TIMEZONE)
    return timestamp.tz_convert("UTC").isoformat(timespec="seconds")


def parse_interview_datetime_series(values: pd.Series) -> pd.Series:
    """Parse mixed Supabase ISO timestamps and display them in recruiter time."""

    return pd.to_datetime(
        values,
        errors="coerce",
        format="mixed",
        utc=True,
    ).dt.tz_convert(INTERVIEW_LOCAL_TIMEZONE)


def build_interview_reschedule_updates(
    *,
    current_interview_date,
    revised_date: date | None = None,
    revised_time: time | None = None,
    interviewer: str | None = None,
    feedback=None,
    meeting_location: str | None = None,
) -> dict:
    """Build a partial reschedule payload without discarding metadata."""

    updates: dict = {}
    if revised_date is not None or revised_time is not None:
        current = pd.to_datetime(
            current_interview_date,
            errors="coerce",
            format="mixed",
            utc=True,
        )
        if pd.isna(current):
            raise ValueError("The existing interview date and time are invalid.")
        current_local = current.tz_convert(INTERVIEW_LOCAL_TIMEZONE)
        target_date = revised_date or current_local.date()
        target_time = revised_time or current_local.time().replace(tzinfo=None)
        updates["interview_date"] = normalize_interview_datetime(
            datetime.combine(target_date, target_time)
        )
    if interviewer is not None:
        updates["interviewer"] = interviewer.strip()
    if meeting_location is not None:
        metadata = dict(feedback) if isinstance(feedback, dict) else {
            "feedback": feedback or ""
        }
        location_key = next(
            (
                key
                for key in ("meeting_link", "meeting_location", "location")
                if key in metadata
            ),
            "location",
        )
        metadata[location_key] = meeting_location.strip()
        updates["feedback"] = metadata
    return updates


def create_interview(
    application_id: str,
    interview_date: str,
    interviewer: str,
    feedback: dict,
) -> None:
    """Insert one interview unless the application slot already exists."""

    require_permission("interview_write")

    if not application_id:
        raise ValueError("An application id is required.")

    supabase = get_supabase_client()
    duplicate_response = (
        supabase.table("interviews")
        .select("id")
        .eq("application_id", application_id)
        .eq("interview_date", interview_date)
        .limit(1)
        .execute()
    )

    if duplicate_response.data:
        raise ValueError(
            "An interview is already scheduled for this date and time."
        )

    supabase.table("interviews").insert(
        {
            "application_id": application_id,
            "interview_date": interview_date,
            "interviewer": interviewer,
            "feedback": feedback,
            "status": "Scheduled",
        }
    ).execute()


def update_interview(
    interview_id: str,
    updates: dict,
) -> None:
    """Update allowed fields on one interview identified by its id."""

    require_permission("interview_write")

    if not interview_id:
        raise ValueError("An interview id is required.")

    allowed_fields = {
        "status",
        "feedback",
        "rating",
        "interview_date",
        "interviewer",
    }
    safe_updates = {
        field: value
        for field, value in updates.items()
        if field in allowed_fields
    }

    if not safe_updates:
        raise ValueError("No interview updates were provided.")

    if "status" in safe_updates and safe_updates["status"] not in {
        "Scheduled",
        "Completed",
        "Cancelled",
    }:
        raise ValueError("The interview status is invalid.")

    if "rating" in safe_updates:
        rating = safe_updates["rating"]

        if (
            isinstance(rating, bool)
            or not isinstance(rating, int)
            or rating < 1
            or rating > 5
        ):
            raise ValueError("Rating must be between 1 and 5.")

    if "interview_date" in safe_updates:
        safe_updates["interview_date"] = normalize_interview_datetime(
            safe_updates["interview_date"]
        )

    client = get_supabase_client()
    current_response = (
        client.table("interviews")
        .select("interview_date,interviewer,status,feedback,rating")
        .eq("id", interview_id)
        .limit(1)
        .execute()
    )
    if not current_response.data:
        raise RuntimeError("The interview could not be found or updated.")

    current = current_response.data[0]
    feedback = current.get("feedback")
    if not isinstance(feedback, dict):
        feedback = {"feedback": feedback or ""}
    else:
        feedback = dict(feedback)
    history = feedback.get("_history", [])
    if not isinstance(history, list):
        history = []
    changed_fields = {
        field: {"from": current.get(field), "to": value}
        for field, value in safe_updates.items()
        if field != "feedback" and current.get(field) != value
    }
    if changed_fields:
        history.append(
            {
                "changed_at": datetime.now(timezone.utc).isoformat(),
                "changes": changed_fields,
            }
        )
        history = history[-50:]
    if "feedback" in safe_updates:
        incoming_feedback = safe_updates["feedback"]
        if isinstance(incoming_feedback, dict):
            incoming_feedback = dict(incoming_feedback)
            incoming_feedback["_history"] = history
            safe_updates["feedback"] = incoming_feedback
        else:
            feedback["feedback"] = incoming_feedback
            safe_updates["feedback"] = feedback
    elif changed_fields:
        feedback["_history"] = history
        safe_updates["feedback"] = feedback

    response = (
        client.table("interviews")
        .update(safe_updates)
        .eq("id", interview_id)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "The interview could not be found or updated."
        )


@st.cache_data(ttl=60)
def get_recruiter_notes() -> pd.DataFrame:
    """Load recruiter notes newest first."""

    return fetch_table("recruiter_notes", order_column="created_at")


def create_recruiter_note(
    application_id: str,
    note: str,
    recruiter_name: str,
) -> None:
    """Persist a recruiter note for one application."""

    require_permission("notes_write")

    if not application_id:
        raise ValueError("An application id is required.")

    if not note.strip():
        raise ValueError("Note text is required.")

    if not recruiter_name.strip():
        raise ValueError("Recruiter name is required.")

    response = (
        get_supabase_client()
        .table("recruiter_notes")
        .insert(
            {
                "application_id": application_id,
                "note": note.strip(),
                "recruiter_name": recruiter_name.strip(),
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("The recruiter note could not be saved.")


@st.cache_data(ttl=60)
def get_jobs() -> pd.DataFrame:
    """Load job records."""

    return fetch_table("jobs")
