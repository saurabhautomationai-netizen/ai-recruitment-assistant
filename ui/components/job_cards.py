"""Reusable Job Cards & Requisition Primitives (Forest Enterprise)."""

import streamlit as st
from ui.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_BODY, COLOR_TEXT_MUTED, COLOR_PRIMARY,
    COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER
)

def render_job_card(
    job_id: str,
    title: str,
    department: str,
    location: str,
    status: str,
    applicant_count: int,
    openings: int = 1,
    selected: bool = False,
    key_prefix: str = "job_card",
    idx: int = 0,
) -> bool:
    """
    Renders an elevated requisition card with status, applicant count, and selection button.
    Returns True if Inspect was clicked.
    """
    is_open = str(status).strip().lower() in ["open", "active"]
    status_bg = "#ecfdf5" if is_open else "#f1f5f9"
    status_color = "#047857" if is_open else "#64748b"
    status_border = "#a7f3d0" if is_open else "#cbd5e1"
    border_color = "#059669" if selected else COLOR_BORDER
    bg_color = "#f0fdf4" if selected else COLOR_SURFACE

    card_col1, card_col2 = st.columns([8.2, 1.8])

    with card_col1:
        card_html = f'''
        <div style="background: {bg_color}; border: 1.5px solid {border_color}; border-radius: 14px; padding: 14px 18px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(22, 46, 32, 0.02);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px; font-weight: 800; color: {COLOR_TEXT_HEADING}; line-height: 1.2;">
                            {title}
                        </span>
                        <span style="background: {status_bg}; color: {status_color}; border: 1px solid {status_border}; font-size: 11px; font-weight: 750; padding: 2px 8px; border-radius: 10px;">
                            {status.upper()}
                        </span>
                    </div>
                    <div style="font-size: 12.5px; color: {COLOR_TEXT_MUTED}; margin-top: 4px;">
                        🏢 <b>{department}</b> · 📍 {location} · 🎯 {openings} Vacancy
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="background: #f8fafc; border: 1px solid #e2e8f0; color: {COLOR_TEXT_HEADING}; font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 8px;">
                        👥 {applicant_count} Candidates
                    </span>
                </div>
            </div>
        </div>
        '''
        st.html(card_html)

    with card_col2:
        btn_label = "Viewing" if selected else "Inspect"
        if st.button(
            f"🔎 {btn_label}",
            key=f"{key_prefix}_btn_{job_id}_{idx}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            return True
    return False
