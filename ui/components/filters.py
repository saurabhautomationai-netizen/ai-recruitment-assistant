"""Standardized Candidate Workspace Filter Bar."""

import streamlit as st

def render_candidate_filter_bar(
    roles: list[str],
    statuses: list[str],
    key_prefix: str = "cand_filter",
) -> tuple[str, str, str]:
    """Renders the top filter row: Search text, Role filter, Status filter."""
    col1, col2, col3 = st.columns([2.2, 1.2, 1.2])

    with col1:
        search_query = st.text_input(
            "Search Candidates",
            placeholder="Search by name, role, email, or skills...",
            label_visibility="collapsed",
            key=f"{key_prefix}_search_input",
        )

    with col2:
        role_options = ["All Roles"] + sorted([r for r in roles if r and str(r).strip() != ""])
        selected_role = st.selectbox(
            "Filter by Role",
            options=role_options,
            index=0,
            label_visibility="collapsed",
            key=f"{key_prefix}_role_sel",
        )

    with col3:
        status_options = ["All Stages"] + sorted([s for s in statuses if s and str(s).strip() != ""])
        selected_status = st.selectbox(
            "Filter by Stage",
            options=status_options,
            index=0,
            label_visibility="collapsed",
            key=f"{key_prefix}_status_sel",
        )

    return search_query, selected_role, selected_status
