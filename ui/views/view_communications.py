"""
Candidate Communications & History Workspace (Phase 4).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves WhatsApp & Email dispatch, idempotency, and audit logging.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.stat_cards import render_stat_card
from ui.components.status_badges import render_status_pill_html
from services.communication_service import get_communication_history

def render_communications_workspace(
    raw_candidates_df: pd.DataFrame = None,
    raw_applications_df: pd.DataFrame = None,
):
    """Renders the Candidate Communications Workspace."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Candidate Communications & Dispatch Center
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Outbound multi-channel messaging via WhatsApp Cloud API & Email with cryptographic idempotency logging.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    history = get_communication_history()
    total_sent = len(history)
    email_count = len([h for h in history if str(h.get("channel", "")).lower() == "email"])
    wa_count = len([h for h in history if str(h.get("channel", "")).lower() == "whatsapp"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Total Dispatched", total_sent, delta="Audited", icon="✉️")
    with c2:
        render_stat_card("Email Notices", email_count, subtitle="SendGrid / Gmail", icon="📧")
    with c3:
        render_stat_card("WhatsApp Notices", wa_count, subtitle="WhatsApp Cloud API", icon="📱")
    with c4:
        render_stat_card("2-Way Inbound Chat", "Pending", subtitle="DESIGN READY — BACKEND PENDING", icon="💬")

    st.write("")
    st.markdown("##### 📋 Verified Message Delivery History")

    if not history:
        st.info("No outbound candidate messages have been dispatched in this session.")
    else:
        for idx, h in enumerate(reversed(history[-10:])):
            cand = h.get("recipient", "Candidate")
            ch = str(h.get("channel", "email")).upper()
            m_type = h.get("message_type", "Notice")
            ts = h.get("timestamp", "Recent")
            st_val = h.get("status", "Delivered")
            
            ch_badge = f'<span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-size: 11px; font-weight: 750; padding: 2px 7px; border-radius: 8px;">{ch}</span>'

            st.markdown(
                f'''
                <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 12px 16px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 14px; font-weight: 800; color: {COLOR_TEXT_HEADING};">{cand}</span>
                            {ch_badge}
                            <span style="font-size: 12px; color: {COLOR_TEXT_MUTED};">· {m_type}</span>
                        </div>
                        <div style="font-size: 11.5px; color: {COLOR_TEXT_MUTED}; margin-top: 3px;">
                            Dispatched: {ts}
                        </div>
                    </div>
                    <div>
                        {render_status_pill_html(st_val)}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
