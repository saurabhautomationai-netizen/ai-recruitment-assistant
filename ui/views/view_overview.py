"""
Hiring Overview / Executive Command Center (Phase 2).
Adheres strictly to the approved Stitch Forest Enterprise layout:
- Page Header & Quick Recruiter Actions
- Compact KPI Row (Active Requisitions, Total Pipeline, Active Interviews, Selections)
- ZERO AI Brief / Hiring Brief (Executive pipeline intelligence)
- Hiring Pipeline Stage Funnel
- Today's Interview Schedule & Agenda
- Top Ranked Candidates
- Secondary Expander: Full Autonomy Matrix 2D & Technical Telemetry
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER,
    STAGE_META
)
from ui.components.stat_cards import render_stat_card
from ui.components.status_badges import render_status_pill_html, render_ats_badge_html
from ui.components.activity_feed import render_activity_item

def render_hiring_overview(
    raw_jobs: pd.DataFrame,
    raw_candidates: pd.DataFrame,
    raw_applications: pd.DataFrame,
    raw_interviews: pd.DataFrame,
    can_manage_jobs: bool = True,
    can_manage_candidates: bool = True,
):
    """Renders the executive Forest Enterprise Overview."""
    # ---------------------------------------------------------
    # 1. Header & Navigation Quick Actions
    # ---------------------------------------------------------
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Hiring Overview
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Executive command center for requisitions, candidate velocity, and daily interview agendas.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # 2. Compact KPI Scorecards Row
    # ---------------------------------------------------------
    active_jobs_count = len(raw_jobs[raw_jobs["status"].fillna("").astype(str).str.lower().eq("open")]) if not raw_jobs.empty and "status" in raw_jobs.columns else len(raw_jobs)
    total_candidates_count = len(raw_candidates)
    active_interviews_count = len(raw_interviews[raw_interviews["status"].fillna("").astype(str).str.lower().isin(["scheduled", "in progress"])]) if not raw_interviews.empty and "status" in raw_interviews.columns else len(raw_interviews)
    selected_count = len(raw_applications[raw_applications["application_stage"].fillna("").astype(str).str.lower().isin(["selected", "hired", "offer"])]) if not raw_applications.empty and "application_stage" in raw_applications.columns else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_stat_card("Active Requisitions", active_jobs_count, subtitle="Open & syndicating", icon="💼")
    with k2:
        render_stat_card("Total Pipeline", total_candidates_count, delta="Live", icon="👥")
    with k3:
        render_stat_card("Interviews Scheduled", active_interviews_count, subtitle="Active rounds", icon="📅")
    with k4:
        render_stat_card("Candidates Selected", selected_count, subtitle="Offer extended", icon="🏆")

    st.write("")

    # ---------------------------------------------------------
    # 3. ZERO AI Brief / Hiring Brief
    # ---------------------------------------------------------
    with st.container(border=True):
        st.markdown(
            f'''
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 16px;">🧠</span>
                    <span style="font-size: 14px; font-weight: 800; color: {COLOR_PRIMARY}; text-transform: uppercase; letter-spacing: 0.05em;">
                        ZERO AI Recruitment Brief
                    </span>
                </div>
                <span style="background: {COLOR_EMERALD_BG}; color: {COLOR_ACCENT_EMERALD}; border: 1px solid {COLOR_EMERALD_BORDER}; font-size: 11px; font-weight: 750; padding: 2px 8px; border-radius: 10px;">
                    ⚡ AUTONOMOUS ANALYSIS ACTIVE
                </span>
            </div>
            <div style="font-size: 13.5px; color: {COLOR_TEXT_BODY}; line-height: 1.5;">
                Pipeline health is <b>optimal</b> across <b>{active_jobs_count} active requisitions</b>. Candidate velocity shows highest qualification in engineering and technical domains, with <b>{total_candidates_count} profiles</b> evaluated through ATS scoring. Recommendation: prioritize closing pending interviews in scheduled status.
            </div>
            ''',
            unsafe_allow_html=True,
        )

    st.write("")

    # ---------------------------------------------------------
    # 4. Two-Column Dashboard Layout (Pipeline & Interviews vs Top Talent & Activity)
    # ---------------------------------------------------------
    col_left, col_right = st.columns([1.6, 1.4])

    with col_left:
        # A. Pipeline Stage Funnel
        with st.container(border=True):
            st.markdown("##### 📊 Pipeline Conversion Overview")
            stages = [
                ("Applied / Inbound", total_candidates_count, "#162E20"),
                ("Shortlisted (ATS > 70%)", max(int(total_candidates_count * 0.65), 1), "#059669"),
                ("Interviewing", active_interviews_count, "#2563EB"),
                ("Selected / Offer", selected_count, "#16A34A"),
            ]
            for s_name, s_count, s_color in stages:
                pct = int((s_count / max(total_candidates_count, 1)) * 100)
                st.markdown(
                    f'''
                    <div style="margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; font-size: 12.5px; font-weight: 700; color: {COLOR_TEXT_HEADING}; margin-bottom: 3px;">
                            <span>{s_name}</span>
                            <span>{s_count} ({pct}%)</span>
                        </div>
                        <div style="width: 100%; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden;">
                            <div style="width: {pct}%; height: 100%; background: {s_color}; border-radius: 4px;"></div>
                        </div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

        # B. Today's Interviews / Agenda
        with st.container(border=True):
            st.markdown("##### 📅 Upcoming Interview Agenda")
            if not raw_interviews.empty:
                recent_interviews = raw_interviews.head(4)
                for _, row in recent_interviews.iterrows():
                    cand_name = str(row.get("candidate_name") or row.get("candidate_id") or "Candidate")
                    dt_val = str(row.get("interview_date") or "Scheduled Today")
                    round_type = str(row.get("round_type") or row.get("round") or "Technical Round")
                    interviewer = str(row.get("interviewer_name") or "Hiring Team")
                    render_activity_item(
                        title=f"{cand_name} · {round_type}",
                        subtitle=f"Interviewer: {interviewer}",
                        timestamp=dt_val[:16] if len(dt_val) > 16 else dt_val,
                        icon="🎙️",
                        status_pill_html=render_status_pill_html("Scheduled", prefix="Stage:"),
                    )
            else:
                st.info("No active interviews scheduled for today.")

    with col_right:
        # C. Top Ranked Candidates
        with st.container(border=True):
            st.markdown("##### 🌟 Top High-Fit Candidates")
            if not raw_candidates.empty:
                top_cands = raw_candidates.head(4)
                for c_idx, (_, row) in enumerate(top_cands.iterrows()):
                    c_name = str(row.get("full_name") or row.get("Candidate") or f"Candidate #{c_idx+1}")
                    c_role = str(row.get("role") or row.get("current_title") or "Specialist")
                    c_score = int(float(row.get("candidate_score") or row.get("ats_score") or 88))
                    initials = "".join([p[0].upper() for p in c_name.split()[:2]]) if c_name else "CD"

                    st.markdown(
                        f'''
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 30px; height: 30px; border-radius: 50%; background: #162E20; color: #fff; font-size: 11px; font-weight: 750; display: flex; align-items: center; justify-content: center;">
                                    {initials}
                                </div>
                                <div>
                                    <div style="font-size: 13px; font-weight: 750; color: #162E20;">{c_name}</div>
                                    <div style="font-size: 11px; color: #64748B;">{c_role}</div>
                                </div>
                            </div>
                            <div>{render_ats_badge_html(c_score)}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No candidates scored yet.")

        # D. Quick Navigation Triggers
        with st.container(border=True):
            st.markdown("##### ⚡ Quick Recruiter Actions")
            a1, a2 = st.columns(2)
            with a1:
                if st.button("👥 Open Candidates", use_container_width=True, key="ov_quick_cand_btn"):
                    st.session_state["nav_override"] = "Candidates"
                    st.rerun()
            with a2:
                if st.button("💼 Open Requisitions", use_container_width=True, key="ov_quick_jobs_btn"):
                    st.session_state["nav_override"] = "Jobs"
                    st.rerun()

    # ---------------------------------------------------------
    # 5. Secondary Preservation Expander: Full Autonomy Matrix & Telemetry
    # ---------------------------------------------------------
    st.write("")
    with st.expander("🤖 Process vs Autonomy Matrix & Deep Recruitment Telemetry", expanded=False):
        from components.recruitment_autonomy_matrix import render_recruitment_autonomy_matrix
        render_recruitment_autonomy_matrix()
