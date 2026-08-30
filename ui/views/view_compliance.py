"""
Privacy, Blind Hiring & GDPR Compliance Workspace (Phase 4).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves candidate PII masking, EEO/OFCCP tracking, and 1-click GDPR deletion purge.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.stat_cards import render_stat_card
from components.compliance_privacy import render_compliance_privacy

def render_compliance_workspace(candidates_list: list[dict]):
    """Renders the Forest Enterprise Privacy & Compliance Workspace."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Privacy & Fair Hiring Governance Center
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    EEO-1 adverse impact evaluation, candidate anonymization (blind review), and cryptographic GDPR audit trails.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        render_stat_card("EEO-1 Readiness", "100%", delta="Compliant", icon="⚖️")
    with g2:
        render_stat_card("Blind Hiring", "Active", subtitle="PII masked on review", icon="🔒")
    with g3:
        render_stat_card("GDPR Deletion SLA", "30 Days", subtitle="1-Click Purge verified", icon="🛡️")
    with g4:
        render_stat_card("Audit Ledger", "SHA-256", subtitle="Tamper-evident", icon="📜")

    st.write("")
    render_compliance_privacy(candidates=candidates_list)
