"""Public Careers Portal & Inbound Candidate Application Form.

Allows external candidates to view active job openings, filter by department/location,
and submit inbound applications with resume uploads, auto-creating candidate records.
"""

from __future__ import annotations

import streamlit as st
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def render_public_careers_portal(jobs: List[Dict[str, Any]], on_apply_callback: Optional[callable] = None) -> None:
    st.markdown("### 🌐 Public Careers Portal & Inbound Application Form")
    st.caption("External candidate portal — view live openings, explore requirements, and submit direct applications.")

    active_jobs = [j for j in jobs if j.get("status", "Active") in ("Active", "Open", "PUBLISHED")]
    if not active_jobs:
        active_jobs = jobs  # Fallback to display all jobs if status filter is permissive

    if not active_jobs:
        st.info("No public job openings are currently published. Check back soon!")
        return

    # Filter Bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search openings by title, skill, or keyword", placeholder="e.g. Full Stack Engineer, Python, Design...")
    with col2:
        depts = sorted(list({j.get("department", "Engineering") for j in active_jobs if j.get("department")}))
        dept_filter = st.selectbox("Department", ["All Departments"] + depts)
    with col3:
        locs = sorted(list({j.get("location", "Remote") for j in active_jobs if j.get("location")}))
        loc_filter = st.selectbox("Location", ["All Locations"] + locs)

    # Filter logic
    filtered = active_jobs
    if search_query:
        q = search_query.lower()
        filtered = [
            j for j in filtered
            if q in j.get("title", "").lower() or q in j.get("description", "").lower() or q in str(j.get("requirements", "")).lower()
        ]
    if dept_filter != "All Departments":
        filtered = [j for j in filtered if j.get("department") == dept_filter]
    if loc_filter != "All Locations":
        filtered = [j for j in filtered if j.get("location") == loc_filter]

    st.markdown(f"**Showing {len(filtered)} active position(s)**")
    st.markdown("---")

    # Display Jobs in Bento Cards
    for job in filtered:
        job_id = job.get("id")
        title = job.get("title", "Open Role")
        dept = job.get("department", "Engineering")
        loc = job.get("location", "Remote")
        job_type = job.get("type", "Full-Time")
        desc = job.get("description", "Join our fast-growing team to build high-impact autonomous solutions.")

        with st.container():
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 18px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #f8fafc; font-size: 1.15rem;">{title}</h4>
                        <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">{job_type}</span>
                    </div>
                    <p style="margin: 6px 0 12px; color: #94a3b8; font-size: 0.85rem;">🏢 {dept} &nbsp;•&nbsp; 📍 {loc}</p>
                    <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5;">{desc[:250]}...</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"📝 View Details & Apply for {title}", expanded=False):
                st.markdown("#### Role Description & Requirements")
                st.write(desc)
                if job.get("requirements"):
                    st.markdown("**Requirements:**")
                    st.write(job.get("requirements"))

                st.markdown("---")
                st.markdown("#### Candidate Application Form")

                with st.form(key=f"apply_form_{job_id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        full_name = st.text_input("Full Name *", placeholder="Jane Doe")
                        email = st.text_input("Email Address *", placeholder="jane.doe@example.com")
                        phone = st.text_input("Phone Number *", placeholder="+1 (555) 019-2834")
                    with c2:
                        linkedin = st.text_input("LinkedIn / Portfolio URL", placeholder="https://linkedin.com/in/janedoe")
                        years_exp = st.number_input("Years of Relevant Experience", min_value=0, max_value=40, value=3)
                        expected_salary = st.text_input("Expected Annual Compensation", placeholder="$120,000 / ₹25 LPA")

                    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"], key=f"resume_{job_id}")
                    cover_note = st.text_area("Cover Note / Why You're a Great Fit", placeholder="Briefly describe your relevant background and interest...")

                    submitted = st.form_submit_button("🚀 Submit Inbound Application", use_container_width=True)

                    if submitted:
                        if not full_name.strip() or not email.strip():
                            st.error("Please provide your full name and email address.")
                        else:
                            candidate_payload = {
                                "name": full_name.strip(),
                                "email": email.strip(),
                                "phone": phone.strip(),
                                "linkedin": linkedin.strip(),
                                "years_experience": years_exp,
                                "expected_salary": expected_salary.strip(),
                                "cover_note": cover_note.strip(),
                                "job_id": job_id,
                                "job_title": title,
                                "applied_at": datetime.now(timezone.utc).isoformat(),
                                "has_resume": resume_file is not None,
                            }
                            if on_apply_callback:
                                on_apply_callback(candidate_payload)

                            st.success(f"🎉 Application successfully received for {title}! Our recruiting team will review your profile shortly.")
