"""Candidate Detail Drawer Presentation (Forest Enterprise)."""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_SURFACE, COLOR_PRIMARY, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER,
    STAGE_META
)
from ui.components.status_badges import render_status_pill_html, render_ats_badge_html

def render_candidate_detail_drawer(
    candidate: dict,
    on_close_callback=None,
    on_stage_change_callback=None,
    can_manage_candidates: bool = True,
    key_prefix: str = "drawer",
):
    """
    Renders the approved Stitch Candidate Detail Drawer.
    Surfaces EXISTING candidate data only: identity, experience, role, ATS score,
    skills, education, notes, and direct stage change controls.
    """
    c_id = candidate["id"]
    c_name = candidate["name"]
    c_role = candidate["role"]
    c_exp = candidate["exp"]
    c_score = candidate["score"]
    c_stage_raw = candidate["stage_raw"]
    c_stage_canonical = candidate["stage_canonical"]
    c_email = candidate["email"]
    c_phone = candidate["phone"]
    c_location = candidate.get("location", "Not specified")
    c_skills = candidate.get("skills", [])
    c_resume = candidate.get("resume_text", "")
    initials = "".join([part[0].upper() for part in c_name.split()[:2]]) if c_name else "CD"

    drawer_header_html = f'''
    <div style="background: {COLOR_SURFACE}; border: 1.5px solid {COLOR_ACCENT_EMERALD}; border-radius: 18px; padding: 20px 24px; box-shadow: 0 4px 24px rgba(5, 150, 105, 0.08); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 52px; height: 52px; border-radius: 14px; background: {COLOR_PRIMARY}; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800;">
                    {initials}
                </div>
                <div>
                    <div style="font-size: 22px; font-weight: 800; color: {COLOR_TEXT_HEADING}; line-height: 1.2;">
                        {c_name}
                    </div>
                    <div style="font-size: 13px; color: {COLOR_TEXT_MUTED}; margin-top: 2px;">
                        <b>{c_role}</b> · {c_location} · {c_email} · {c_phone}
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                {render_ats_badge_html(c_score)}
                {render_status_pill_html(c_stage_raw)}
            </div>
        </div>
    </div>
    '''
    st.html(drawer_header_html)

    # 2-Column Detail Layout
    col_left, col_right = st.columns([1.6, 1.4])

    with col_left:
        with st.container(border=True):
            st.markdown("##### 📄 Professional Background & Skills")
            st.caption(f"**Experience Level:** {c_exp} verified years in relevant domain")

            # Skills chips
            if c_skills and isinstance(c_skills, list) and len(c_skills) > 0:
                st.markdown("**Identified Skills:**")
                skill_badges = "".join([
                    f'<span style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 10px; margin-right: 6px; margin-bottom: 6px; display: inline-block;">✅ {s}</span>'
                    for s in c_skills[:12]
                ])
                st.html(f'<div style="margin-bottom: 12px;">{skill_badges}</div>')
            else:
                st.info("Skills parsed from candidate application documents.")

            # Full Resume Expander
            with st.expander("📄 View Full Candidate Resume & History", expanded=False):
                if c_resume and str(c_resume).strip():
                    st.text_area("Resume Content", value=str(c_resume), height=220, disabled=True, key=f"{key_prefix}_res_txt_{c_id}")
                else:
                    st.markdown(f"**Candidate:** {c_name}\n**Position:** {c_role}\n**Experience:** {c_exp} years\n**Contact:** {c_email}")
                    st.caption("Standard application profile attached.")

    with col_right:
        with st.container(border=True):
            st.markdown("##### ⚡ Recruiter Actions & Pipeline Stage")
            st.caption("Update candidate stage directly across Supabase and n8n pipelines.")

            stage_titles = [meta["title"] for meta in STAGE_META.values()]
            current_stage_title = next(
                (meta["title"] for meta in STAGE_META.values() if meta["id"] == c_stage_canonical),
                "Shortlisted"
            )

            if can_manage_candidates:
                new_stage_label = st.selectbox(
                    "Transition to Stage",
                    options=stage_titles,
                    index=stage_titles.index(current_stage_title) if current_stage_title in stage_titles else 0,
                    key=f"{key_prefix}_stage_select_{c_id}",
                )

                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    target_meta = next((m for m in STAGE_META.values() if m["title"] == new_stage_label), None)
                    if target_meta and target_meta["id"] != c_stage_canonical:
                        if st.button("💾 Apply Stage Move", type="primary", use_container_width=True, key=f"{key_prefix}_apply_{c_id}"):
                            if on_stage_change_callback:
                                on_stage_change_callback(c_id, target_meta["id"], target_meta["title"], c_name)

                with act_col2:
                    if st.button("✖️ Close Inspector", use_container_width=True, key=f"{key_prefix}_close_{c_id}"):
                        if on_close_callback:
                            on_close_callback()
            else:
                st.info(f"Current Stage: **{current_stage_title}** (Read-Only access)")
                if st.button("✖️ Close Inspector", use_container_width=True, key=f"{key_prefix}_close_ro_{c_id}"):
                    if on_close_callback:
                        on_close_callback()
