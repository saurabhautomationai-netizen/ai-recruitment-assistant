"""
Bulk Data Operations Workspace (Phase 4).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves CSV/XLSX import, column mapping validator, and export.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.stat_cards import render_stat_card
from components.bulk_candidate_management import render_bulk_candidate_management

def render_bulk_data_workspace(
    candidates_df: pd.DataFrame,
    applications_df: pd.DataFrame = None,
    jobs_df: pd.DataFrame = None,
):
    """Renders the Forest Enterprise Bulk Data Operations Workspace."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Bulk Data Operations & Spreadsheet Ingestion
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Import candidate spreadsheets (.csv / .xlsx), map column schemas, validate duplicates, and batch export talent data.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        render_stat_card("Supported Formats", "CSV, XLSX", subtitle="UTF-8 ready", icon="📂")
    with b2:
        render_stat_card("Deduplication", "Active", delta="E.164 + Name", icon="🔍")
    with b3:
        render_stat_card("Schema Validation", "Auto-Mapping", subtitle="Fast match", icon="⚡")
    with b4:
        render_stat_card("Batch Audit Log", "Session-Scoped", subtitle="Local history", icon="📜")

    st.write("")
    apps = applications_df if applications_df is not None else pd.DataFrame()
    jbs = jobs_df if jobs_df is not None else pd.DataFrame()
    render_bulk_candidate_management(candidates_df, apps, jbs)
