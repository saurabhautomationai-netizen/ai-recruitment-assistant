"""Reusable Offer Cards & E-Sign Status Indicators (Forest Enterprise)."""

import streamlit as st
from ui.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.status_badges import render_status_pill_html

def render_offer_summary_card(
    candidate_name: str,
    role: str,
    ctc_display: str,
    start_date: str,
    status: str = "Extended",
    key_prefix: str = "off_card",
    idx: int = 0,
) -> bool:
    """Renders a high-density enterprise offer card."""
    card_col1, card_col2 = st.columns([8.2, 1.8])
    with card_col1:
        html = f'''
        <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 14px; padding: 14px 18px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="font-size: 16px; font-weight: 800; color: {COLOR_TEXT_HEADING}; line-height: 1.2;">
                        {candidate_name}
                    </div>
                    <div style="font-size: 12.5px; color: {COLOR_TEXT_MUTED}; margin-top: 4px;">
                        💼 <b>{role}</b> · 💰 Annual CTC: <b>{ctc_display}</b> · 📅 Proposed Start: {start_date}
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
        if st.button("📄 Preview", key=f"{key_prefix}_btn_{idx}", use_container_width=True):
            return True
    return False
