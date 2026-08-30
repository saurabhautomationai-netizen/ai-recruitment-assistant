"""
AI Interview Copilot View (Phase 3).
Adheres strictly to the approved Stitch split-pane design.
Preserves all existing STAR framework rubrics, question generation, and evidence analysis.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from components.interview_copilot import render_interview_copilot

def render_interview_copilot_workspace(
    candidates_df: pd.DataFrame,
    applications_df: pd.DataFrame,
    jobs_df: pd.DataFrame,
    notes_df: pd.DataFrame,
    interviews_df: pd.DataFrame,
):
    """Wraps the evidence-grounded AI Interview Copilot in the Forest Enterprise workspace."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    AI Interview Copilot
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Evidence-grounded STAR technical rubrics, competency probes, and candidate gap analysis.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    render_interview_copilot(
        candidates=candidates_df,
        applications=applications_df,
        jobs=jobs_df,
        notes=notes_df,
        interviews=interviews_df,
    )
