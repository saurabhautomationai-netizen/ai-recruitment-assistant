"""Streamlit UI for evidence-grounded interview assistance."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from services.interview_copilot_service import (
    FOCUS_AREAS,
    build_interview_preparation,
    evaluate_interview,
    suggest_follow_up,
)


def _records_for(frame: pd.DataFrame, column: str, value: str) -> list[dict]:
    if frame.empty or column not in frame.columns:
        return []
    return frame[frame[column].astype(str).eq(value)].to_dict("records")


def render_interview_copilot(
    candidates: pd.DataFrame,
    applications: pd.DataFrame,
    jobs: pd.DataFrame,
    notes: pd.DataFrame,
    interviews: pd.DataFrame,
) -> None:
    st.markdown('<div class="main-title">AI Interview Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Evidence-grounded assistance during an interview. '
        'The recruiter remains responsible for every hiring decision.</div>',
        unsafe_allow_html=True,
    )
    st.warning(
        "Do not enter protected or sensitive attributes. Notes remain in this browser "
        "session and are not written to Supabase.",
        icon=":material/security:",
    )
    if candidates.empty or applications.empty:
        st.info("Candidate and application data are required to start the copilot.")
        return
    names = {
        str(row.get("id", "")): str(row.get("full_name", "Unknown candidate"))
        for _, row in candidates.iterrows()
    }
    options = {}
    for _, application in applications.iterrows():
        candidate_id = str(application.get("candidate_id", ""))
        label = f"{names.get(candidate_id, 'Unknown candidate')} — {application.get('application_stage', 'Unknown stage')}"
        options[label] = str(application.get("id", ""))
    selected_label = st.selectbox("Select interview application", list(options))
    application_id = options[selected_label]
    application = applications[applications["id"].astype(str).eq(application_id)].iloc[0].to_dict()
    candidate_rows = candidates[candidates["id"].astype(str).eq(str(application.get("candidate_id", "")))]
    candidate = candidate_rows.iloc[0].to_dict() if not candidate_rows.empty else {}
    job_rows = jobs[jobs["id"].astype(str).eq(str(application.get("job_id", "")))] if not jobs.empty and "id" in jobs.columns else pd.DataFrame()
    job = job_rows.iloc[0].to_dict() if not job_rows.empty else {}
    preparation = build_interview_preparation(
        candidate,
        application,
        job,
        _records_for(notes, "application_id", application_id),
        _records_for(interviews, "application_id", application_id),
    )

    st.subheader("Interview preparation")
    summary_col, requirements_col = st.columns(2)
    with summary_col.container(border=True, height="stretch"):
        st.markdown("#### Candidate summary")
        st.write(preparation["candidate_summary"])
        st.caption(
            f"Candidate score: {preparation['candidate_score'] or 'N/A'} · "
            f"ATS score: {preparation['ats_score'] or 'N/A'}"
        )
    with requirements_col.container(border=True, height="stretch"):
        st.markdown("#### Job requirements")
        st.write(preparation["job_requirements"])
        if preparation["recommendation"]:
            st.caption(f"Stored AI recommendation: {preparation['recommendation']}")
    detail_cols = st.columns(3)
    for column, title, items in zip(
        detail_cols,
        ("Strong areas", "Concerns to validate", "Recommended focus"),
        (preparation["strong_areas"], preparation["concerns"], preparation["focus_areas"]),
    ):
        with column.container(border=True, height="stretch"):
            st.markdown(f"#### {title}")
            if items:
                for item in items:
                    st.write(f"- {item}")
            else:
                st.caption("No stored evidence available.")

    entry_key = f"copilot_entries_{application_id}"
    entries = st.session_state.setdefault(entry_key, [])
    covered = {entry.get("area") for entry in entries if entry.get("response", "").strip()}
    st.subheader("Interview progress")
    progress_cols = st.columns(4)
    for column, area in zip(progress_cols, FOCUS_AREAS):
        column.metric(area, "Covered" if area in covered else "Pending")

    with st.form(f"copilot_response_{application_id}"):
        focus_area = st.segmented_control(
            "Focus area", FOCUS_AREAS, default="Technical", key=f"copilot_focus_{application_id}"
        )
        recruiter_prompt = st.text_input("Question or topic", placeholder="What did you ask?")
        candidate_response = st.text_area(
            "Recruiter notes or candidate response",
            placeholder="Capture job-relevant evidence only.",
            height=140,
        )
        add_response = st.form_submit_button("Add evidence and suggest follow-up", type="primary")
    if add_response:
        if not candidate_response.strip():
            st.error("Enter a response or recruiter note first.")
        else:
            entry = {
                "area": focus_area or "Technical",
                "question": recruiter_prompt.strip(),
                "response": candidate_response.strip(),
            }
            entry["suggestion"] = suggest_follow_up(entry["area"], entry["response"], preparation)
            entries.append(entry)
            st.rerun()

    for index, entry in enumerate(entries):
        with st.container(border=True):
            st.markdown(f"**{entry['area']}** — {entry.get('question') or 'Recruiter note'}")
            st.write(entry["response"])
            st.info(entry["suggestion"], icon=":material/psychology:")
            if st.button("Remove", key=f"remove_copilot_entry_{application_id}_{index}"):
                entries.pop(index)
                st.rerun()

    if st.button(
        "Summarize interview evidence",
        icon=":material/summarize:",
        disabled=not entries,
    ):
        st.session_state[f"copilot_evaluation_{application_id}"] = evaluate_interview(entries)
    evaluation = st.session_state.get(f"copilot_evaluation_{application_id}")
    if evaluation:
        st.subheader("Evaluation assistant")
        st.caption("Assistance only — this is not an automated hiring decision.")
        for label, key in (("Strengths", "strengths"), ("Concerns", "concerns"), ("Evidence", "evidence")):
            with st.expander(label, expanded=label == "Evidence"):
                if evaluation[key]:
                    for item in evaluation[key]:
                        st.write(f"- {item}")
                else:
                    st.caption("No explicit evidence identified.")
        st.info(evaluation["recommended_next_step"], icon=":material/person_check:")
