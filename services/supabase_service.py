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
def get_jobs() -> pd.DataFrame:
    """Load job records."""

    return fetch_table("jobs")
