import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def get_supabase_client() -> Client:
    """Create and return the Supabase client."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError(
            "SUPABASE_URL is missing from the .env file."
        )

    if not supabase_key:
        raise ValueError(
            "SUPABASE_KEY is missing from the .env file."
        )

    return create_client(
        supabase_url,
        supabase_key,
    )


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

    if not application_id:
        raise ValueError("An application id is required.")

    supabase = get_supabase_client()
    supabase.table("applications").update(
        {"application_stage": application_stage}
    ).eq("id", application_id).execute()


@st.cache_data(ttl=60)
def get_interviews() -> pd.DataFrame:
    """Load scheduled interview records."""

    return fetch_table("interviews", order_column="interview_date")


def create_interview(
    application_id: str,
    interview_date: str,
    interviewer: str,
    feedback: dict,
) -> None:
    """Insert one interview unless the application slot already exists."""

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

    if not interview_id:
        raise ValueError("An interview id is required.")

    allowed_fields = {"status", "feedback", "rating"}
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

    response = (
        get_supabase_client()
        .table("interviews")
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
