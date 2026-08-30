"""Reusable Interview Primitives & Agenda Cards (Forest Enterprise)."""

import streamlit as st
from ui.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_BODY, COLOR_TEXT_MUTED, COLOR_PRIMARY,
    COLOR_ACCENT_BLUE, COLOR_BLUE_BG, COLOR_BLUE_BORDER
)
from ui.components.status_badges import render_status_pill_html

def render_interview_card(
    interview_id: str,
    candidate_name: str,
    role: str,
    round_type: str,
    date_str: str,
    interviewer: str,
    meeting_link: str = None,
    status: str = "Scheduled",
    key_prefix: str = "iv_card",
    idx: int = 0,
) -> bool:
    """Renders a high-density enterprise interview agenda card."""
    link_html = f'<a href="{meeting_link}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 700; font-size: 12px;">🔗 Join Meeting</a>' if meeting_link and "http" in meeting_link else '<span style="font-size: 12px; color: #94a3b8;">Google Meet Link Attached</span>'
    
    card_col1, card_col2 = st.columns([8.2, 1.8])
    with card_col1:
        html = f'''
        <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 14px; padding: 14px 18px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(22, 46, 32, 0.02);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px; font-weight: 800; color: {COLOR_TEXT_HEADING}; line-height: 1.2;">
                            {candidate_name}
                        </span>
                        <span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-size: 11px; font-weight: 750; padding: 2px 8px; border-radius: 10px;">
                            {round_type}
                        </span>
                    </div>
                    <div style="font-size: 12.5px; color: {COLOR_TEXT_MUTED}; margin-top: 4px;">
                        💼 <b>{role}</b> · 👤 Interviewer: {interviewer} · 📅 {date_str}
                    </div>
                    <div style="margin-top: 6px;">
                        {link_html}
                    </div>
                </div>
                <div>
                    {render_status_pill_html(status)}
                </div>
            </div>
        </div>
        '''
        st.html(html)

    with card_col2:
        if st.button("🔎 Details", key=f"{key_prefix}_btn_{interview_id}_{idx}", use_container_width=True):
            return True
    return False
