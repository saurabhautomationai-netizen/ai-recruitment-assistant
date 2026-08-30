"""Offer Letter Generator & Digital E-Signature Lifecycle Tracker.

Enables recruiters to draft, generate, and dispatch formal offer letters
with dynamic salary, bonus, equity, and start-date variables, tracking signature state.
"""

from __future__ import annotations

import streamlit as st
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


def render_offer_letter_generator(applications: List[Dict[str, Any]]) -> None:
    st.markdown("### 📝 Offer Letter Generator & E-Signature Tracker")
    st.caption("Draft customized compensation packages, preview dynamic PDF offer contracts, and track signing lifecycle.")

    if not applications:
        st.info("No candidate applications available.")
        return

    # Select Candidate for Offer
    app_options = {
        f"{a.get('candidate_name', 'Candidate')} — {a.get('job_title', 'Role')} ({a.get('stage', 'Stage')})": a
        for a in applications
    }
    selected_label = st.selectbox("Select Candidate to Extend Offer", list(app_options.keys()), key="offer_cand_select")
    selected_app = app_options[selected_label]

    tab1, tab2 = st.tabs(["📄 Draft & Generate Offer Contract", "🖋️ E-Signature Lifecycle Pipeline"])

    with tab1:
        st.markdown("#### 1. Compensation & Terms Configuration")
        c1, c2, c3 = st.columns(3)
        with c1:
            base_salary = st.text_input("Annual Base Salary", value="$140,000 / ₹28,00,000")
            joining_bonus = st.text_input("Signing / Joining Bonus", value="$15,000 / ₹3,00,000")
        with c2:
            equity_grant = st.text_input("Stock Options / RSUs", value="0.25% Equity / 2,500 RSUs (4-yr vesting)")
            start_date = st.date_input("Proposed Joining Date", value=date.today() + timedelta(days=21))
        with c3:
            offer_validity = st.date_input("Offer Acceptance Deadline", value=date.today() + timedelta(days=7))
            reporting_manager = st.text_input("Reporting Manager / Title", value="VP of Engineering")

        benefits_selected = st.multiselect(
            "Included Perks & Benefits",
            ["Comprehensive Health, Dental & Vision Insurance", "Flexible Remote / Hybrid Work Policy", "$2,500 Annual Learning & Conference Budget", "Unlimited Paid Time Off (PTO)", "Home Office Setup Reimbursement ($1,000)"],
            default=["Comprehensive Health, Dental & Vision Insurance", "Flexible Remote / Hybrid Work Policy", "Unlimited Paid Time Off (PTO)"]
        )

        cand_name = selected_app.get("candidate_name", "Jane Doe")
        job_title = selected_app.get("job_title", "Senior Software Engineer")

        offer_letter_text = f"""================================================================================
                            FORMAL OFFER OF EMPLOYMENT
================================================================================

Date: {date.today().strftime('%B %d, %Y')}

To: {cand_name}
Position: {job_title}
Reporting To: {reporting_manager}
Anticipated Start Date: {start_date.strftime('%B %d, %Y')}
Offer Expiration Date: {offer_validity.strftime('%B %d, %Y')}

Dear {cand_name},

On behalf of the leadership team, we are thrilled to extend this formal offer of
employment for the position of {job_title}. We were exceptionally impressed by your
expertise, problem-solving prowess, and culture alignment throughout our interview process.

1. COMPENSATION & INCENTIVES
   • Base Salary: {base_salary} per annum, paid in semi-monthly installments.
   • Signing Bonus: {joining_bonus}, payable on the first regular payroll cycle.
   • Equity Incentive: {equity_grant}, subject to the terms of the Company Equity Plan.

2. BENEFITS & WELLNESS
{chr(10).join(f'   • {b}' for b in benefits_selected)}

3. ACCEPTANCE & EXECUTION
This offer remains valid until {offer_validity.strftime('%B %d, %Y')}. To accept, please
electronically execute this document using the secure digital signature link provided.

Sincerely,

{reporting_manager}
VP of Engineering & Head of Talent Acquisition

--------------------------------------------------------------------------------
CANDIDATE ACCEPTANCE & DIGITAL SIGNATURE:

Signature: ___________________________    Date: _______________
Name: {cand_name}
================================================================================"""

        st.markdown("---")
        st.markdown("#### 2. Live Offer Contract Preview")
        st.code(offer_letter_text, language="text")

        b1, b2 = st.columns([1, 1])
        with b1:
            st.download_button(
                label="📥 Download Offer Letter (TXT / Contract)",
                data=offer_letter_text,
                file_name=f"Offer_Letter_{cand_name.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with b2:
            if st.button("🚀 Dispatch Offer for Digital Signature (DocuSign / E-Sign)", type="primary", use_container_width=True):
                st.success(f"🎉 Offer Letter dispatched to {selected_app.get('candidate_email', cand_name)} via secure e-signature portal!")

    with tab2:
        st.markdown("#### 📊 E-Signature Pipeline & Status Tracker")
        sample_offers = [
            {"candidate": cand_name, "role": job_title, "salary": base_salary, "status": "PENDING_SIGNATURE", "sent_date": "Today", "deadline": str(offer_validity)},
            {"candidate": "Alex Rivera", "role": "Full Stack Architect", "salary": "$160,000", "status": "SIGNED", "sent_date": "3 days ago", "deadline": "Aug 29, 2026"},
            {"candidate": "Samantha Vance", "role": "Product Designer", "salary": "$125,000", "status": "DRAFT", "sent_date": "-", "deadline": "-"},
        ]

        for off in sample_offers:
            status_color = "#10b981" if off["status"] == "SIGNED" else ("#fbbf24" if off["status"] == "PENDING_SIGNATURE" else "#94a3b8")
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255,255,255,0.08); border-left: 3px solid {status_color}; border-radius: 6px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #f8fafc; font-size: 0.95rem;">{off['candidate']}</strong> &nbsp;•&nbsp; <span style="color: #94a3b8; font-size: 0.85rem;">{off['role']}</span>
                        <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">Compensation: {off['salary']} &nbsp;|&nbsp; Deadline: {off['deadline']}</div>
                    </div>
                    <span style="background: rgba(255,255,255,0.05); color: {status_color}; border: 1px solid {status_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; font-family: monospace;">{off['status']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
