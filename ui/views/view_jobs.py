"""
Jobs Workspace, Detail Inspector, Create Job Wizard & Pipeline View (Phase 2).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves all existing job creation schemas, database insertions, and candidate linkages.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER
)
from ui.components.stat_cards import render_stat_card
from ui.components.job_cards import render_job_card
from ui.components.status_badges import render_status_pill_html, render_ats_badge_html
from services.supabase_service import create_job

def render_jobs_workspace(
    raw_jobs_df: pd.DataFrame,
    raw_candidates_df: pd.DataFrame = None,
    raw_applications_df: pd.DataFrame = None,
    can_manage_jobs: bool = True,
):
    """
    Renders the master Jobs Workspace:
    - Top Requisition KPIs
    - Subview Switcher: [💼 Jobs Directory, ⚡ Create New Job, 📊 Pipeline by Job]
    - Jobs Directory with Filters
    - Job Detail Inspector Drawer
    - Create New Job Wizard (4-step stepped process)
    - Role-Specific Job Pipeline View
    """
    if "jobs_selected_job_id" not in st.session_state:
        st.session_state["jobs_selected_job_id"] = None
    if "jobs_subview" not in st.session_state:
        st.session_state["jobs_subview"] = "💼 Jobs Directory"

    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Jobs Workspace
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Active requisitions, multi-step job creator, and role-specific candidate conversion funnels.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # 1. Telemetry Row
    # ---------------------------------------------------------
    total_jobs = len(raw_jobs_df)
    open_jobs = len(raw_jobs_df[raw_jobs_df["status"].fillna("").astype(str).str.lower().eq("open")]) if not raw_jobs_df.empty and "status" in raw_jobs_df.columns else total_jobs
    total_applicants = len(raw_applications_df) if raw_applications_df is not None and not raw_applications_df.empty else 0

    j1, j2, j3, j4 = st.columns(4)
    with j1:
        render_stat_card("Total Requisitions", total_jobs, icon="💼")
    with j2:
        render_stat_card("Open Positions", open_jobs, delta="Syndicating", icon="🟢")
    with j3:
        render_stat_card("Total Applicants", total_applicants, subtitle="Across all roles", icon="👥")
    with j4:
        render_stat_card("Target Time-to-Fill", "18 Days", subtitle="Autonomous target", icon="⚡")

    st.write("")

    # ---------------------------------------------------------
    # 2. View Switcher
    # ---------------------------------------------------------
    subview_options = ["💼 Jobs Directory", "⚡ Create New Job", "📊 Pipeline by Job"]
    subview = st.pills(
        "Jobs Mode",
        subview_options,
        default=st.session_state["jobs_subview"],
        label_visibility="collapsed",
        key="jobs_subview_pill",
    )
    st.session_state["jobs_subview"] = subview

    st.write("")

    # ---------------------------------------------------------
    # SUBVIEW A: Jobs Directory & Detail Inspector
    # ---------------------------------------------------------
    if subview == "💼 Jobs Directory":
        # Search and Filters
        f_col1, f_col2, f_col3 = st.columns([2.4, 1.3, 1.3])
        with f_col1:
            search_query = st.text_input("Search Jobs", placeholder="Search by title, department, or location...", label_visibility="collapsed", key="job_search_input")
        with f_col2:
            all_depts = ["All Departments"] + sorted(list(set(str(d) for d in raw_jobs_df["department"].dropna().unique()))) if not raw_jobs_df.empty and "department" in raw_jobs_df.columns else ["All Departments"]
            selected_dept = st.selectbox("Department", all_depts, label_visibility="collapsed", key="job_dept_sel")
        with f_col3:
            all_statuses = ["All Statuses", "Open", "Closed", "Draft"]
            selected_status = st.selectbox("Status", all_statuses, label_visibility="collapsed", key="job_status_sel")

        # Filter records
        filtered_jobs = raw_jobs_df.copy() if not raw_jobs_df.empty else pd.DataFrame()
        if not filtered_jobs.empty:
            if search_query:
                q = search_query.strip().lower()
                filtered_jobs = filtered_jobs[
                    filtered_jobs["title"].fillna("").astype(str).str.lower().str.contains(q)
                    | filtered_jobs["department"].fillna("").astype(str).str.lower().str.contains(q)
                    | filtered_jobs["location"].fillna("").astype(str).str.lower().str.contains(q)
                ]
            if selected_dept != "All Departments" and "department" in filtered_jobs.columns:
                filtered_jobs = filtered_jobs[filtered_jobs["department"].astype(str) == selected_dept]
            if selected_status != "All Statuses" and "status" in filtered_jobs.columns:
                filtered_jobs = filtered_jobs[filtered_jobs["status"].astype(str).str.lower() == selected_status.lower()]

        # Render Job Cards
        if filtered_jobs.empty:
            st.info("No requisitions match your search filters.")
        else:
            for idx, (_, row) in enumerate(filtered_jobs.iterrows()):
                j_id = str(row.get("id") or f"job_{idx}")
                j_title = str(row.get("title") or "Open Requisition")
                j_dept = str(row.get("department") or "Engineering")
                j_loc = str(row.get("location") or "Remote / Hybrid")
                j_stat = str(row.get("status") or "Open")
                
                # Count applicants for this job
                app_count = 0
                if raw_applications_df is not None and not raw_applications_df.empty and "job_id" in raw_applications_df.columns:
                    app_count = len(raw_applications_df[raw_applications_df["job_id"].astype(str) == j_id])

                is_selected = (st.session_state["jobs_selected_job_id"] == j_id)
                clicked = render_job_card(
                    job_id=j_id,
                    title=j_title,
                    department=j_dept,
                    location=j_loc,
                    status=j_stat,
                    applicant_count=app_count,
                    selected=is_selected,
                    key_prefix="ws_jobs",
                    idx=idx,
                )
                if clicked:
                    st.session_state["jobs_selected_job_id"] = j_id
                    st.rerun()

        # Job Detail Workspace (when a job is inspected)
        active_job_id = st.session_state.get("jobs_selected_job_id")
        if active_job_id and not raw_jobs_df.empty:
            match = raw_jobs_df[raw_jobs_df["id"].astype(str) == str(active_job_id)]
            if not match.empty:
                job_record = match.iloc[0].to_dict()
                st.divider()
                with st.container(border=True):
                    st.markdown(
                        f'''
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div>
                                <span style="font-size: 20px; font-weight: 800; color: #162E20;">{job_record.get("title")}</span>
                                <div style="font-size: 13px; color: #64748B;">Requisition ID: <code>{active_job_id}</code></div>
                            </div>
                            <span style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 750;">
                                {str(job_record.get("status", "OPEN")).upper()}
                            </span>
                        </div>
                        ''',
                        unsafe_allow_html=True,
                    )
                    
                    d1, d2, d3 = st.columns(3)
                    with d1:
                        st.caption(f"**Department:** {job_record.get('department', 'N/A')}")
                        st.caption(f"**Location:** {job_record.get('location', 'N/A')}")
                    with d2:
                        st.caption(f"**Salary Band:** {job_record.get('salary_range', 'Competitive / Market')}")
                        st.caption(f"**Experience:** {job_record.get('experience_level', '2-5 Years')}")
                    with d3:
                        st.caption(f"**Hiring Manager:** {job_record.get('hiring_manager', 'Talent Lead')}")
                        st.caption(f"**Target Openings:** {job_record.get('openings', 1)}")

                    st.markdown("**Job Description & Responsibilities:**")
                    st.text_area("Description", value=str(job_record.get("description") or "Standard requisition description."), height=140, disabled=True, key=f"det_desc_{active_job_id}")

                    if st.button("✖️ Close Requisition Inspector", key="close_job_det_btn"):
                        st.session_state["jobs_selected_job_id"] = None
                        st.rerun()

    # ---------------------------------------------------------
    # SUBVIEW B: Create New Job Wizard
    # ---------------------------------------------------------
    elif subview == "⚡ Create New Job":
        if not can_manage_jobs:
            st.error("🔒 You have Viewer permissions. Requisition creation requires Recruiter or Admin access.")
            return

        with st.container(border=True):
            st.markdown("### 📝 Create New Job Requisition")
            st.caption("Follow the 4-step wizard to define, structure, and publish a new job opening.")

            w_step = st.radio("Step", ["1. Requisition Basics", "2. Requirements & Skills", "3. Description & AI Polish", "4. Review & Publish"], horizontal=True, label_visibility="collapsed", key="job_wizard_step_radio")

            if w_step == "1. Requisition Basics":
                c1, c2 = st.columns(2)
                with c1:
                    new_title = st.text_input("Job Title*", placeholder="e.g. Senior Machine Learning Engineer", key="wiz_job_title")
                    new_dept = st.selectbox("Department", ["Engineering", "Product", "Data Science", "Design", "Sales", "Human Resources", "Finance", "Legal"], key="wiz_job_dept")
                with c2:
                    new_loc = st.text_input("Location*", placeholder="e.g. Bengaluru, India (Hybrid)", key="wiz_job_loc")
                    new_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Internship"], key="wiz_job_type")

            elif w_step == "2. Requirements & Skills":
                c1, c2 = st.columns(2)
                with c1:
                    new_exp = st.selectbox("Experience Level", ["Entry Level (0-2y)", "Mid Level (3-5y)", "Senior (6-9y)", "Lead / Principal (10+y)"], key="wiz_job_exp")
                    new_salary = st.text_input("Salary Range (INR / USD)", placeholder="e.g. ₹25,00,000 - ₹35,00,000", key="wiz_job_sal")
                with c2:
                    new_skills = st.text_input("Required Skills (Comma-separated)", placeholder="e.g. Python, PyTorch, LangChain, PostgreSQL", key="wiz_job_skills")
                    new_openings = st.number_input("Number of Openings", min_value=1, max_value=25, value=1, key="wiz_job_openings")

            elif w_step == "3. Description & AI Polish":
                new_desc = st.text_area("Job Description & Key Responsibilities*", height=180, placeholder="Detail the expectations, team culture, and daily deliverables for this position...", key="wiz_job_desc")

            elif w_step == "4. Review & Publish":
                t = st.session_state.get("wiz_job_title", "")
                d = st.session_state.get("wiz_job_dept", "")
                l = st.session_state.get("wiz_job_loc", "")
                desc = st.session_state.get("wiz_job_desc", "")

                if not t or not desc:
                    st.warning("⚠️ Please complete required fields (Title, Description) in previous steps before publishing.")
                else:
                    st.success(f"Ready to publish: **{t}** ({d} · {l})")
                    if st.button("🚀 Publish Requisition to Database", type="primary", use_container_width=True, key="wiz_job_submit_btn"):
                        payload = {
                            "title": t,
                            "department": d,
                            "location": l,
                            "description": desc,
                            "status": "Open",
                        }
                        create_job(payload)
                        st.toast("✅ Requisition published successfully!", icon="💼")
                        st.session_state["jobs_subview"] = "💼 Jobs Directory"
                        st.rerun()

    # ---------------------------------------------------------
    # SUBVIEW C: Role-Specific Job Pipeline View
    # ---------------------------------------------------------
    elif subview == "📊 Pipeline by Job":
        if raw_jobs_df.empty:
            st.info("No requisitions available.")
            return

        job_titles = {str(row["id"]): str(row["title"]) for _, row in raw_jobs_df.iterrows()}
        sel_job_id = st.selectbox("Select Requisition to View Pipeline", options=list(job_titles.keys()), format_func=lambda x: job_titles.get(x, x), key="pipeline_job_selector")

        if sel_job_id and raw_applications_df is not None and not raw_applications_df.empty:
            job_apps = raw_applications_df[raw_applications_df["job_id"].astype(str) == str(sel_job_id)]
            st.caption(f"Showing **{len(job_apps)} candidates** linked to this specific requisition.")
            
            if not job_apps.empty:
                for _, a_row in job_apps.iterrows():
                    c_name = str(a_row.get("candidate_name") or a_row.get("candidate_id") or "Candidate")
                    stage = str(a_row.get("application_stage") or "Shortlisted")
                    score = int(float(a_row.get("candidate_score") or a_row.get("ats_score") or 80))
                    
                    st.markdown(
                        f'''
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
                            <div style="font-size: 13.5px; font-weight: 750; color: #162E20;">{c_name}</div>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                {render_ats_badge_html(score)}
                                {render_status_pill_html(stage)}
                            </div>
                        </div>
                        ''',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No candidates currently in the pipeline for this requisition.")
