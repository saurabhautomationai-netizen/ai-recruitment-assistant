"""
AI Recruiter Conversational Workspace (Phase 4).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves structured query routing, multi-turn context, and bookmarking.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.stat_cards import render_stat_card
from components.ai_recruiter_chat import render_ai_recruiter_chat

def render_ai_recruiter_workspace(
    candidates_df: pd.DataFrame,
    applications_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    interviews_df: pd.DataFrame,
):
    """Renders the Forest Enterprise Conversational AI Recruiter."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    AI Recruiter Intelligence Center
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Multi-turn conversational recruitment assistant answering pipeline queries, stage bottlenecks, and candidate summaries.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        render_stat_card("Recruiter Agent", "JARVIS AI", delta="Online", icon="🧠")
    with r2:
        render_stat_card("Active Context", f"{len(candidates_df)} Records", subtitle="Pipeline loaded", icon="📊")
    with r3:
        render_stat_card("Guardrails", "Enforced", subtitle="Anti-injection active", icon="🛡️")
    with r4:
        render_stat_card("Side Copilot", "Ready", subtitle="DESIGN READY — FRAMEWORK PENDING", icon="💡")

    st.write("")
    render_ai_recruiter_chat(
        candidates=candidates_df,
        applications=applications_df,
        jobs=jobs_df,
        interviews=interviews_df,
    )
