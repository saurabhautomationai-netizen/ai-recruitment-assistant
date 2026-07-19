"""Shared database connections for the recruitment dashboard."""

import os

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


@st.cache_resource
def get_supabase_client() -> Client:
    """Create one reusable Supabase client from local environment settings."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in the .env file."
        )

    return create_client(supabase_url, supabase_key)
