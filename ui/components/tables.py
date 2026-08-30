"""Compact Enterprise Candidate Table View."""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.status_badges import render_status_pill_html, render_ats_badge_html

def render_compact_candidate_table(
    candidates_list: list[dict],
    selected_candidate_id: str = None,
    key_prefix: str = "tbl",
) -> str | None:
    """
    Renders a compact, high-density enterprise table matching Stitch layout.
    Returns the newly selected candidate_id if an Inspect button is clicked.
    """
    if not candidates_list:
        st.markdown(
            f'''
            <div style="background: #fafaf9; border: 1px dashed {COLOR_BORDER}; border-radius: 12px; padding: 32px; text-align: center; color: {COLOR_TEXT_MUTED};">
                No matching candidates found in this view.
            </div>
            ''',
            unsafe_allow_html=True,
        )
        return None

    # Table Header Card
    hdr_html = f'''
    <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 14px; padding: 10px 16px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(22, 46, 32, 0.02);">
        <div style="display: grid; grid-template-columns: 2.2fr 1.8fr 1fr 1.2fr 1.4fr 1.2fr; gap: 12px; align-items: center; font-size: 11px; font-weight: 750; color: {COLOR_TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em;">
            <div>Candidate</div>
            <div>Applied Role</div>
            <div>Experience</div>
            <div>ATS Fit</div>
            <div>Stage / Status</div>
            <div style="text-align: right;">Action</div>
        </div>
    </div>
    '''
    st.html(hdr_html)

    clicked_id = None

    for idx, c in enumerate(candidates_list):
        c_id = c["id"]
        c_name = c["name"]
        c_role = c["role"]
        c_exp = c["exp"]
        c_score = c["score"]
        c_stage = c["stage_raw"]
        c_email = c["email"]

        is_selected = (selected_candidate_id == c_id)
        border_color = "#059669" if is_selected else COLOR_BORDER
        bg_color = "#f0fdf4" if is_selected else COLOR_SURFACE

        initials = "".join([part[0].upper() for part in c_name.split()[:2]]) if c_name else "CD"

        row_col1, row_col2 = st.columns([7.8, 1.2])

        with row_col1:
            row_html = f'''
            <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 10px 16px; margin-bottom: 6px; transition: all 0.15s ease;">
                <div style="display: grid; grid-template-columns: 2.2fr 1.8fr 1fr 1.2fr 1.4fr; gap: 12px; align-items: center; font-size: 13px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 32px; height: 32px; border-radius: 50%; background: #162E20; color: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 750; flex-shrink: 0;">
                            {initials}
                        </div>
                        <div style="overflow: hidden;">
                            <div style="font-weight: 750; color: {COLOR_TEXT_HEADING}; line-height: 1.2; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">{c_name}</div>
                            <div style="font-size: 11.5px; color: {COLOR_TEXT_MUTED}; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">{c_email}</div>
                        </div>
                    </div>
                    <div style="color: {COLOR_TEXT_BODY}; font-weight: 600;">{c_role}</div>
                    <div style="color: {COLOR_TEXT_MUTED}; font-weight: 600;">{c_exp}y exp</div>
                    <div>{render_ats_badge_html(c_score)}</div>
                    <div>{render_status_pill_html(c_stage)}</div>
                </div>
            </div>
            '''
            st.html(row_html)

        with row_col2:
            btn_label = "Active" if is_selected else "Inspect"
            if st.button(
                f"🔍 {btn_label}",
                key=f"{key_prefix}_btn_insp_{c_id}_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                clicked_id = c_id

    return clicked_id
