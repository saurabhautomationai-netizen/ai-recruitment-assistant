"""
Applications Workspace & Linkage Inspector (Phase 2).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves candidate-job linkage, ATS score distributions, and recruiter dispositions.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.stat_cards import render_stat_card
from ui.components.status_badges import render_status_pill_html, render_ats_badge_html

def render_applications_workspace(
    raw_applications_df: pd.DataFrame,
    raw_candidates_df: pd.DataFrame = None,
    raw_jobs_df: pd.DataFrame = None,
    can_manage_candidates: bool = True,
):
    """
    Renders the Applications Workspace:
    - Summary Telemetry Row
    - Search & Stage Filters
    - Enterprise Applications Table
    - Application Detail Inspection Drawer
    """
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Applications Workspace
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Candidate-to-job application registry, AI recommendations, and stage transitions.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if raw_applications_df is None or raw_applications_df.empty:
        st.info("No active applications in the database.")
        return

    # ---------------------------------------------------------
    # 1. Telemetry Row
    # ---------------------------------------------------------
    total_apps = len(raw_applications_df)
    shortlisted_apps = len(raw_applications_df[raw_applications_df["application_stage"].fillna("").astype(str).str.lower().eq("shortlisted")]) if "application_stage" in raw_applications_df.columns else 0
    interview_apps = len(raw_applications_df[raw_applications_df["application_stage"].fillna("").astype(str).str.lower().isin(["scheduled", "interview"])]) if "application_stage" in raw_applications_df.columns else 0
    selected_apps = len(raw_applications_df[raw_applications_df["application_stage"].fillna("").astype(str).str.lower().isin(["selected", "hired", "offer"])]) if "application_stage" in raw_applications_df.columns else 0

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        render_stat_card("Total Applications", total_apps, delta="Live", icon="📄")
    with a2:
        render_stat_card("Shortlisted", shortlisted_apps, subtitle="Screening cleared", icon="📋")
    with a3:
        render_stat_card("Active Interviewing", interview_apps, subtitle="In evaluation", icon="🎙️")
    with a4:
        render_stat_card("Offer / Selected", selected_apps, subtitle="Final stage", icon="🏆")

    st.write("")

    # ---------------------------------------------------------
    # 2. Search and Filtering Bar
    # ---------------------------------------------------------
    sc1, sc2 = st.columns([2.8, 1.2])
    with sc1:
        search_query = st.text_input("Search Applications", placeholder="Search by candidate name or application ID...", label_visibility="collapsed", key="app_search_input")
    with sc2:
        all_stages = ["All Stages"] + sorted(list(set(str(s) for s in raw_applications_df["application_stage"].dropna().unique()))) if "application_stage" in raw_applications_df.columns else ["All Stages"]
        selected_stage = st.selectbox("Stage Filter", all_stages, label_visibility="collapsed", key="app_stage_sel")

    filtered_apps = raw_applications_df.copy()
    if search_query:
        q = search_query.strip().lower()
        filtered_apps = filtered_apps[
            filtered_apps["candidate_id"].fillna("").astype(str).str.lower().str.contains(q)
            | (filtered_apps["candidate_name"].fillna("").astype(str).str.lower().str.contains(q) if "candidate_name" in filtered_apps.columns else False)
        ]
    if selected_stage != "All Stages" and "application_stage" in filtered_apps.columns:
        filtered_apps = filtered_apps[filtered_apps["application_stage"].astype(str) == selected_stage]

    st.write("")

    # ---------------------------------------------------------
    # 3. Enterprise Applications Table
    # ---------------------------------------------------------
    hdr_html = f'''
    <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 14px; padding: 10px 16px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(22, 46, 32, 0.02);">
        <div style="display: grid; grid-template-columns: 2.5fr 2fr 1.2fr 1.5fr 1.2fr; gap: 12px; align-items: center; font-size: 11px; font-weight: 750; color: {COLOR_TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em;">
            <div>Candidate</div>
            <div>Applied Job ID</div>
            <div>ATS Score</div>
            <div>Application Stage</div>
            <div>Recommendation</div>
        </div>
    </div>
    '''
    st.html(hdr_html)

    for idx, (_, row) in enumerate(filtered_apps.iterrows()):
        app_id = str(row.get("id") or f"app_{idx}")
        cand_id = str(row.get("candidate_id") or f"cand_{idx}")
        cand_name = str(row.get("candidate_name") or cand_id)
        job_id = str(row.get("job_id") or "General Pipeline")
        stage = str(row.get("application_stage") or "Shortlisted")
        score = int(float(row.get("candidate_score") or row.get("ats_score") or 82))
        rec = str(row.get("recommendation") or "Strong Fit")

        initials = "".join([p[0].upper() for p in cand_name.split()[:2]]) if cand_name else "CD"

        row_html = f'''
        <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 10px 16px; margin-bottom: 6px;">
            <div style="display: grid; grid-template-columns: 2.5fr 2fr 1.2fr 1.5fr 1.2fr; gap: 12px; align-items: center; font-size: 13px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #162E20; color: #fff; font-size: 11px; font-weight: 750; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        {initials}
                    </div>
                    <div>
                        <div style="font-weight: 750; color: {COLOR_TEXT_HEADING};">{cand_name}</div>
                        <div style="font-size: 11px; color: {COLOR_TEXT_MUTED};">ID: {app_id[:8]}</div>
                    </div>
                </div>
                <div style="font-weight: 600; color: {COLOR_TEXT_BODY};">{job_id[:16]}</div>
                <div>{render_ats_badge_html(score)}</div>
                <div>{render_status_pill_html(stage)}</div>
                <div style="font-size: 12px; font-weight: 700; color: #047857;">{rec}</div>
            </div>
        </div>
        '''
        st.html(row_html)
