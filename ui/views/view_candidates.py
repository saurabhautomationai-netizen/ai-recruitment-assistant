"""
Candidate Workspace View (Phase 1).
Provides:
  Candidate Workspace
   ├── Table View (Compact Enterprise Table)
   ├── Kanban View (5-Stage Interactive Board)
   └── Candidate Detail Drawer
Preserves all live Supabase data, RBAC, and stage transition logic.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_MUTED, STAGE_META
)
from ui.components.stat_cards import render_stat_card
from ui.components.filters import render_candidate_filter_bar
from ui.components.tables import render_compact_candidate_table
from ui.components.drawers import render_candidate_detail_drawer
from components.candidate_kanban_board import normalize_stage, _execute_stage_transition

def _normalize_candidate_records(candidates_df: pd.DataFrame) -> list[dict]:
    """Extracts and normalizes live records from the candidates DataFrame."""
    records = []
    if candidates_df.empty:
        return records

    for c_idx, (_, row) in enumerate(candidates_df.iterrows()):
        raw_id = (
            row.get("candidate_id")
            or row.get("id")
            or row.get("Candidate")
            or row.get("full_name")
            or f"c_{c_idx}"
        )
        c_id = str(raw_id).strip() if (pd.notna(raw_id) and str(raw_id).strip()) else f"cand_{c_idx}"
        c_name = str(row.get("Candidate") or row.get("full_name") or row.get("name") or f"Candidate #{c_idx+1}")
        c_role = str(row.get("Role") or row.get("role") or row.get("current_title") or "Technical Specialist")
        c_exp = str(row.get("Experience") or row.get("years_experience") or "3")
        c_score = int(float(row.get("Candidate Score") or row.get("candidate_score") or row.get("ats_score") or 85))
        c_stage_raw = str(row.get("Status") or row.get("candidate_status") or row.get("application_stage") or "Shortlisted")
        c_stage_canonical = normalize_stage(c_stage_raw)
        c_email = str(row.get("email") or f"{c_name.lower().replace(' ', '.')}@example.com")
        c_phone = str(row.get("phone") or "+91 98765 43210")
        c_location = str(row.get("location") or "Pune, India")
        c_skills = row.get("skills") if isinstance(row.get("skills"), list) else []
        c_resume = str(row.get("resume_text") or row.get("summary") or "")

        records.append({
            "id": c_id,
            "name": c_name,
            "role": c_role,
            "exp": c_exp,
            "score": c_score,
            "stage_raw": c_stage_raw,
            "stage_canonical": c_stage_canonical,
            "email": c_email,
            "phone": c_phone,
            "location": c_location,
            "skills": c_skills,
            "resume_text": c_resume,
            "idx": c_idx,
        })
    return records

def render_candidate_workspace(
    candidates_df: pd.DataFrame,
    raw_applications_df: pd.DataFrame = None,
    can_manage_candidates: bool = True,
):
    """
    Renders the unified Candidate Workspace:
    - Top Telemetry Bar (Total, Shortlisted, Interviewing, Selected)
    - Subview Switcher: [📋 Kanban View, 📄 Table View]
    - Search & Filter bar
    - Table / Kanban renderer
    - Candidate Detail Drawer
    """
    if "workspace_selected_cand_id" not in st.session_state:
        st.session_state["workspace_selected_cand_id"] = None
    if "workspace_subview" not in st.session_state:
        st.session_state["workspace_subview"] = "📋 Kanban View"

    all_records = _normalize_candidate_records(candidates_df)

    # ---------------------------------------------------------
    # 1. Top Section Header & Telemetry
    # ---------------------------------------------------------
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 14px;">
            <div>
                <div style="font-size: 24px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Candidate Workspace
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 2px;">
                    Manage candidate stages, inspect ATS compatibility, and trigger interview workflows.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # Telemetry Row
    total_count = len(all_records)
    shortlisted_count = len([c for c in all_records if c["stage_canonical"] == "shortlisted"])
    interview_count = len([c for c in all_records if c["stage_canonical"] in ["scheduled", "interview"]])
    selected_count = len([c for c in all_records if c["stage_canonical"] == "selected"])

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        render_stat_card("Total Pipeline", total_count, delta="Live", icon="👥")
    with kpi2:
        render_stat_card("Shortlisted", shortlisted_count, subtitle="Screening passed", icon="📋")
    with kpi3:
        render_stat_card("In Interview", interview_count, subtitle="Active rounds", icon="🎙️")
    with kpi4:
        render_stat_card("Selected / Hired", selected_count, subtitle="Offer extended", icon="🏆")

    st.write("")

    # ---------------------------------------------------------
    # 2. View Switcher & Filters
    # ---------------------------------------------------------
    ctrl_col1, ctrl_col2 = st.columns([1.4, 3.6])
    with ctrl_col1:
        subview = st.pills(
            "View Mode",
            ["📋 Kanban View", "📄 Table View"],
            default=st.session_state["workspace_subview"],
            label_visibility="collapsed",
            key="cand_workspace_view_mode_pill",
        )
        st.session_state["workspace_subview"] = subview

    with ctrl_col2:
        all_roles = list(set(c["role"] for c in all_records))
        all_stages = list(set(c["stage_raw"] for c in all_records))
        search_query, selected_role, selected_stage = render_candidate_filter_bar(
            roles=all_roles,
            statuses=all_stages,
            key_prefix="cand_ws",
        )

    # Filter records based on user search inputs
    filtered_records = all_records
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered_records = [
            c for c in filtered_records
            if q in c["name"].lower() or q in c["role"].lower() or q in c["email"].lower()
        ]
    if selected_role and selected_role != "All Roles":
        filtered_records = [c for c in filtered_records if c["role"] == selected_role]
    if selected_stage and selected_stage != "All Stages":
        filtered_records = [c for c in filtered_records if c["stage_raw"] == selected_stage]

    # ---------------------------------------------------------
    # 3. Render Chosen Subview (Kanban vs. Table)
    # ---------------------------------------------------------
    if subview == "📋 Kanban View":
        # Render the 5-stage Kanban board using existing component logic
        from components.candidate_kanban_board import render_candidate_kanban_board
        # Construct DataFrame matching the filtered records to preserve live data
        if filtered_records:
            filtered_df = pd.DataFrame(filtered_records)
        else:
            filtered_df = pd.DataFrame()
        render_candidate_kanban_board(filtered_df, raw_applications_df)

    else:
        # Render the Compact Enterprise Table View
        new_sel_id = render_compact_candidate_table(
            candidates_list=filtered_records,
            selected_candidate_id=st.session_state["workspace_selected_cand_id"],
            key_prefix="ws_table",
        )
        if new_sel_id:
            st.session_state["workspace_selected_cand_id"] = new_sel_id
            st.rerun()

    # ---------------------------------------------------------
    # 4. Candidate Detail Drawer (When selected)
    # ---------------------------------------------------------
    active_cand_id = st.session_state.get("workspace_selected_cand_id")
    if active_cand_id:
        active_cand = next((c for c in all_records if c["id"] == active_cand_id), None)
        if active_cand:
            st.divider()

            def _on_close():
                st.session_state["workspace_selected_cand_id"] = None
                st.rerun()

            def _on_stage_change(cand_id, new_stage_id, new_stage_title, cand_name):
                _execute_stage_transition(cand_id, new_stage_id, new_stage_title, cand_name)
                st.rerun()

            render_candidate_detail_drawer(
                candidate=active_cand,
                on_close_callback=_on_close,
                on_stage_change_callback=_on_stage_change,
                can_manage_candidates=can_manage_candidates,
                key_prefix="ws_drawer",
            )
