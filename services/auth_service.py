"""Per-session Supabase authentication for the Streamlit dashboard."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


ROLE_PERMISSIONS = {
    "ADMIN": {"read", "candidate_write", "job_write", "interview_write", "notes_write", "communicate", "ai"},
    "RECRUITER": {"read", "candidate_write", "job_write", "interview_write", "notes_write", "communicate", "ai"},
    "VIEWER": {"read"},
}


def _new_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be configured."
        )
    return create_client(url, key)


def get_session_supabase_client() -> Client:
    """Return a client isolated to the current Streamlit user session."""

    if "supabase_client" not in st.session_state:
        st.session_state["supabase_client"] = _new_supabase_client()
    return st.session_state["supabase_client"]


def is_authenticated() -> bool:
    """Return whether this Streamlit session completed Supabase login."""

    user = st.session_state.get("auth_user")
    return isinstance(user, dict) and bool(user.get("id"))


def require_authenticated_user() -> dict:
    """Block service writes that are not tied to an authenticated session."""

    if not is_authenticated():
        raise PermissionError("Authentication is required for this action.")
    return st.session_state["auth_user"]


def get_current_role() -> str:
    """Return the normalized application role for this authenticated session."""

    user = require_authenticated_user()
    role = str(user.get("role", "RECRUITER")).strip().upper()
    return role if role in ROLE_PERMISSIONS else "VIEWER"


def has_permission(permission: str) -> bool:
    """Return whether the current role has one named application permission."""

    if not is_authenticated():
        return False
    return permission in ROLE_PERMISSIONS[get_current_role()]


def require_permission(permission: str) -> dict:
    """Enforce application authorization independently of the UI."""

    user = require_authenticated_user()
    if not has_permission(permission):
        raise PermissionError(
            f"The {get_current_role()} role is not allowed to perform this action."
        )
    return user


def _load_user_role(client: Client, user_id: str) -> str:
    """Load a migrated profile role, preserving v1.0 behavior when unavailable."""

    try:
        response = (
            client.table("recruiter_profiles")
            .select("role")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if response.data:
            role = str(response.data[0].get("role", "VIEWER")).upper()
            if role in ROLE_PERMISSIONS:
                return role
    except Exception:
        # v1.1 migration is optional until explicitly approved. Existing
        # authenticated v1.0 recruiters retain their current capabilities.
        pass
    return "RECRUITER"


def sign_in(email: str, password: str) -> dict:
    """Authenticate through Supabase and store only non-secret user metadata."""

    if not email.strip() or not password:
        raise ValueError("Email and password are required.")
    response = get_session_supabase_client().auth.sign_in_with_password(
        {"email": email.strip(), "password": password}
    )
    if response.user is None or response.session is None:
        raise PermissionError("Authentication failed.")
    user = {
        "id": str(response.user.id),
        "email": str(response.user.email or email.strip()),
        "role": _load_user_role(get_session_supabase_client(), str(response.user.id)),
    }
    st.session_state["auth_user"] = user
    return user


def sign_out() -> None:
    """End the Supabase session and remove all session-local dashboard state."""

    client = st.session_state.get("supabase_client")
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    for key in list(st.session_state):
        del st.session_state[key]
    st.cache_data.clear()


def render_login() -> None:
    """Render the only UI available to an unauthenticated visitor."""

    st.markdown('<div class="main-title">Recruiter sign in</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Sign in with your authorized Supabase '
        'recruiter account.</div>',
        unsafe_allow_html=True,
    )
    _, center, _ = st.columns([1, 1.25, 1])
    with center:
        with st.container(border=True):
            with st.form("recruiter_login"):
                email = st.text_input(
                    "Email",
                    placeholder="recruiter@example.com",
                    autocomplete="email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    autocomplete="current-password",
                )
                submitted = st.form_submit_button(
                    "Sign in",
                    type="primary",
                    icon=":material/login:",
                    width="stretch",
                )
            if submitted:
                try:
                    with st.spinner("Signing in…"):
                        sign_in(email, password)
                except Exception:
                    st.error("Sign in failed. Check your email and password.")
                else:
                    st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 8px;'>", unsafe_allow_html=True)
            with st.popover("Forgot password?", icon=":material/lock_reset:", use_container_width=True):
                st.markdown("##### Reset your password")
                st.caption("Enter your registered email address to receive a secure reset link.")
                reset_email = st.text_input(
                    "Email address",
                    placeholder="recruiter@example.com",
                    key="forgot_pwd_email_input",
                )
                if st.button(
                    "Send password reset link",
                    type="primary",
                    key="send_pwd_reset_btn",
                    use_container_width=True,
                ):
                    if not reset_email.strip():
                        st.error("Please enter your email.")
                    else:
                        try:
                            client = get_session_supabase_client()
                            client.auth.reset_password_for_email(reset_email.strip())
                            st.success(f"Reset link sent to {reset_email.strip()}! Please check your inbox.")
                        except Exception as err:
                            st.error(f"Could not send reset link: {err}")
            st.markdown("</div>", unsafe_allow_html=True)
