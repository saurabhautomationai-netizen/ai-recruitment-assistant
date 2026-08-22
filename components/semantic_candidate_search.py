"""Candidate semantic-search UI with transparent local fallback."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from services.semantic_search_service import rank_candidates_locally


def render_semantic_candidate_search(candidates: pd.DataFrame, jobs: pd.DataFrame) -> None:
    st.markdown('<div class="main-title">Resume semantic search</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Search candidate resume-derived fields with natural language.</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "pgvector storage and an embedding provider are migration/configuration pending. "
        "Until then, results use transparent local cosine term relevance and are labelled accordingly.",
        icon=":material/info:",
    )
    if candidates.empty:
        st.info("No candidate data is available to search.")
        return
    mode = st.segmented_control(
        "Search mode", ("Natural-language query", "Match a job description"), default="Natural-language query"
    )
    query = ""
    if mode == "Match a job description":
        if jobs.empty:
            st.info("No jobs are available.")
            return
        options = {
            str(row.get("title", "Untitled job")): str(row.get("description", ""))
            for _, row in jobs.iterrows()
        }
        selected_job = st.selectbox("Job", list(options))
        query = options[selected_job]
        st.text_area("Job description used for matching", value=query, disabled=True)
    else:
        query = st.text_input(
            "Candidate search",
            placeholder="e.g. Strong backend candidates with PostgreSQL",
        )
    if query.strip():
        results = rank_candidates_locally(query, candidates)
        if results.empty:
            st.info("No candidates matched the available stored text.")
            return
        st.caption("Similarity score: local term relevance fallback, not an embedding score.")
        for _, candidate in results.head(20).iterrows():
            with st.container(border=True):
                st.markdown(f"#### {candidate.get('full_name', 'Unknown candidate')}")
                st.metric("Similarity score", f"{candidate['relevance_score']:.1f}%")
                st.write(f"**Skills:** {candidate.get('skills', 'Not available')}")
                summary = candidate.get("resume_summary", candidate.get("summary", ""))
                if summary:
                    st.write(summary)
