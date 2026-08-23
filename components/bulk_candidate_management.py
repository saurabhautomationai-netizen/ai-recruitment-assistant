"""Streamlit bulk candidate import and filtered export UI."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from services.auth_service import has_permission
from services.bulk_candidate_service import export_xlsx, import_candidates, validate_candidate_import
from services.supabase_service import get_candidates


def render_bulk_candidate_management(
    candidates: pd.DataFrame,
    applications: pd.DataFrame,
    jobs: pd.DataFrame,
) -> None:
    st.markdown('<div class="main-title">📥 Bulk Candidate Import & Export</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Upload multi-candidate CSV/XLSX spreadsheets or export filtered recruitment pipelines.</div>',
        unsafe_allow_html=True,
    )
    import_tab, export_tab = st.tabs(["📤 Bulk Import", "📥 Filtered Export"])
    with import_tab:
        with st.container(border=True):
            st.markdown("#### 📂 Upload Candidate Roster Spreadsheet")
            st.caption("Supports CSV or Excel (.xlsx) files with columns: full_name, email, phone, location, years_experience, skills.")
            uploaded = st.file_uploader("Choose CSV/XLSX file", type=("csv", "xlsx"), label_visibility="collapsed")
            if uploaded is not None:
                try:
                    frame = pd.read_csv(uploaded) if uploaded.name.casefold().endswith(".csv") else pd.read_excel(uploaded)
                except Exception as error:
                    st.error(f"The file could not be read: {error}")
                else:
                    schema_columns = set(candidates.columns) or {
                        "full_name", "email", "phone", "location",
                        "years_experience", "skills", "status",
                        "linkedin_url", "current_company", "current_role",
                    }
                    valid, invalid = validate_candidate_import(frame, candidates, schema_columns)
                    valid_col, invalid_col = st.columns(2)
                    with valid_col:
                        st.markdown(
                            f'<div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:14px; padding:14px 18px; display:flex; justify-content:space-between; align-items:center;">'
                            f'<div><div style="font-size:12px; color:#059669; font-weight:600;">VALID ROWS</div><div style="font-size:24px; font-weight:800; color:#065f46;">{len(valid)}</div></div>'
                            f'<div style="font-size:24px;">✅</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with invalid_col:
                        st.markdown(
                            f'<div style="background:#fef2f2; border:1px solid #fecaca; border-radius:14px; padding:14px 18px; display:flex; justify-content:space-between; align-items:center;">'
                            f'<div><div style="font-size:12px; color:#dc2626; font-weight:600;">INVALID ROWS</div><div style="font-size:24px; font-weight:800; color:#991b1b;">{len(invalid)}</div></div>'
                            f'<div style="font-size:24px;">⚠️</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    st.markdown("##### 📋 Valid Records Preview")
                    st.dataframe(valid, hide_index=True, width="stretch")
                    if not invalid.empty:
                        with st.expander("⚠️ View Rejected / Invalid Rows", expanded=False):
                            st.dataframe(invalid, hide_index=True, width="stretch")
                    confirmed = st.checkbox(
                        "I confirm that all valid candidate records should be imported into the active database",
                        disabled=not has_permission("candidate_write") or valid.empty,
                    )
                    if st.button(
                        "🚀 Commit Bulk Import to Database",
                        type="primary",
                        disabled=not confirmed or valid.empty or not has_permission("candidate_write"),
                    ):
                        try:
                            inserted = import_candidates(valid, schema_columns)
                        except Exception as error:
                            st.error(f"Import failed before completion: {error}")
                        else:
                            get_candidates.clear()
                            st.success(f"🎉 Successfully imported {inserted} candidate(s)! Pipeline refreshed.")
            if not has_permission("candidate_write"):
                st.caption("🔒 VIEWER access is read-only; imports are disabled.")

    with export_tab:
        with st.container(border=True):
            st.markdown("#### 🎯 Filter & Export Candidates")
            export_frame = candidates.copy()
            status_options = sorted(export_frame.get("status", pd.Series(dtype="object")).dropna().astype(str).unique())
            location_options = sorted(export_frame.get("location", pd.Series(dtype="object")).dropna().astype(str).unique())
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                status = st.selectbox("Stage Status Filter", ["All"] + status_options, key="bulk_export_status")
                minimum_experience = st.number_input("Minimum Experience (Years)", min_value=0.0, value=0.0, step=1.0)
            with c_f2:
                location = st.selectbox("Location Filter", ["All"] + location_options, key="bulk_export_location")
                minimum_score = st.number_input(
                    "Minimum Candidate Score (%)", min_value=0.0, max_value=100.0,
                    value=0.0, step=5.0,
                )
                
            if status != "All" and "status" in export_frame.columns:
                export_frame = export_frame[export_frame["status"].astype(str).eq(status)]
            if location != "All" and "location" in export_frame.columns:
                export_frame = export_frame[export_frame["location"].astype(str).eq(location)]
            if "years_experience" in export_frame.columns:
                experience = pd.to_numeric(export_frame["years_experience"], errors="coerce").fillna(0)
                export_frame = export_frame[experience >= minimum_experience]
            if not applications.empty and "candidate_id" in applications.columns:
                app_columns = [column for column in ("candidate_id", "job_id", "application_stage", "candidate_score", "ats_score") if column in applications.columns]
                latest = applications[app_columns].drop_duplicates("candidate_id")
                export_frame = export_frame.merge(latest, left_on="id", right_on="candidate_id", how="left")
                if "candidate_score" in export_frame.columns:
                    scores = pd.to_numeric(
                        export_frame["candidate_score"], errors="coerce"
                    ).fillna(0)
                    export_frame = export_frame[scores >= minimum_score]
                if not jobs.empty and {"id", "title"}.issubset(jobs.columns) and "job_id" in export_frame.columns:
                    export_frame = export_frame.merge(jobs[["id", "title"]], left_on="job_id", right_on="id", how="left", suffixes=("", "_job"))
                    selected_job = st.selectbox("Target Job Requisition", ["All"] + sorted(export_frame["title"].dropna().astype(str).unique()))
                    if selected_job != "All":
                        export_frame = export_frame[export_frame["title"].astype(str).eq(selected_job)]
            safe_export = export_frame.drop(columns=[column for column in export_frame.columns if "token" in column.casefold() or "secret" in column.casefold() or "password" in column.casefold()])
            st.info(f"📊 **{len(safe_export)}** candidate record(s) matching filter criteria.")
            st.dataframe(safe_export, hide_index=True, width="stretch")
            
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                st.download_button("📥 Download CSV Spreadsheet", safe_export.to_csv(index=False), "candidates_export.csv", "text/csv", type="primary", use_container_width=True)
            with c_d2:
                st.download_button("📊 Download Excel (.XLSX)", export_xlsx(safe_export), "candidates_export.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
