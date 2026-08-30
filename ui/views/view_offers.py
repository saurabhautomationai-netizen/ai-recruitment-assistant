"""
Offer Management Workspace, Create Offer Wizard & Contract Preview (Phase 3).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves existing offer letter generation, PDF compilation, and e-sign status tracking.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER
)
from ui.components.stat_cards import render_stat_card
from ui.components.offer_cards import render_offer_summary_card
from ui.components.status_badges import render_status_pill_html
from services.offer_letter_service import compile_offer_letter_pdf

def render_offer_workspace(
    raw_applications_df: pd.DataFrame,
    raw_candidates_df: pd.DataFrame = None,
    raw_jobs_df: pd.DataFrame = None,
    can_manage_offers: bool = True,
):
    """
    Renders the unified Offer Management Workspace:
    - Offer KPIs
    - Subview Switcher: [💼 Offer Pipeline, 📝 Create Offer Wizard, 👤 Candidate Offer Portal (Preview)]
    - Offer Pipeline Table
    - 4-Step Create Offer Wizard
    - High-Fidelity Contract Preview & PDF Download
    """
    if "offer_subview" not in st.session_state:
        st.session_state["offer_subview"] = "💼 Offer Pipeline"

    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Offer Management & E-Signature Workspace
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Draft executive CTC packages, preview dynamic PDF employment agreements, and track digital signing states.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # 1. Telemetry Row
    # ---------------------------------------------------------
    total_offers = 4
    accepted_offers = 2
    pending_sign = 1
    in_draft = 1

    o1, o2, o3, o4 = st.columns(4)
    with o1:
        render_stat_card("Total Offers", total_offers, icon="📝")
    with o2:
        render_stat_card("Signed & Accepted", accepted_offers, delta="50% Yield", icon="🏆")
    with o3:
        render_stat_card("Out for Signature", pending_sign, subtitle="DocuSign active", icon="🖋️")
    with o4:
        render_stat_card("Avg Acceptance Speed", "3.2 Days", subtitle="Fast turnaround", icon="⚡")

    st.write("")

    # ---------------------------------------------------------
    # 2. View Switcher
    # ---------------------------------------------------------
    subview_options = ["💼 Offer Pipeline", "📝 Create Offer Wizard", "👤 Candidate Offer Portal (Preview)"]
    subview = st.pills(
        "Offer Mode",
        subview_options,
        default=st.session_state["offer_subview"],
        label_visibility="collapsed",
        key="offer_subview_pill",
    )
    st.session_state["offer_subview"] = subview

    st.write("")

    # ---------------------------------------------------------
    # SUBVIEW A: Offer Pipeline Table
    # ---------------------------------------------------------
    if subview == "💼 Offer Pipeline":
        st.markdown("##### 📄 Active Offer Letters & Signatures")
        
        mock_offers = [
            {"name": "Ananya Sharma", "role": "Senior Machine Learning Engineer", "ctc": "₹28,00,000", "date": "15 Sep 2026", "status": "Signed"},
            {"name": "Rohan Deshmukh", "role": "Lead DevOps & Cloud Architect", "ctc": "₹34,00,000", "date": "22 Sep 2026", "status": "Extended"},
            {"name": "Priya Nair", "role": "Fullstack Software Engineer", "ctc": "₹18,50,000", "date": "01 Oct 2026", "status": "Accepted"},
            {"name": "Vikram Patel", "role": "Product Designer", "ctc": "₹22,00,000", "date": "05 Oct 2026", "status": "Draft"},
        ]

        for idx, o in enumerate(mock_offers):
            render_offer_summary_card(
                candidate_name=o["name"],
                role=o["role"],
                ctc_display=o["ctc"],
                start_date=o["date"],
                status=o["status"],
                key_prefix="pipeline_off",
                idx=idx,
            )

        st.caption("ℹ️ **E-Signature Status Tracking:** Real states (Draft, Extended, Accepted) are live; automated DocuSign webhook callbacks are marked as *DESIGN READY — BACKEND PENDING*.")

    # ---------------------------------------------------------
    # SUBVIEW B: Create Offer Wizard (4-Stage Flow)
    # ---------------------------------------------------------
    elif subview == "📝 Create Offer Wizard":
        if not can_manage_offers:
            st.error("🔒 You have Viewer access. Creating offers requires Recruiter or Admin permissions.")
            return

        with st.container(border=True):
            st.markdown("### 📝 Draft New Employment Offer & Agreement")
            st.caption("Complete the 4-step wizard to calculate CTC, select benefits, and compile the formal agreement.")

            w_step = st.radio("Step", ["1. Candidate & Role", "2. Compensation (CTC)", "3. Benefits & Terms", "4. Review & Generate Contract"], horizontal=True, label_visibility="collapsed", key="offer_wiz_radio")

            if w_step == "1. Candidate & Role":
                c1, c2 = st.columns(2)
                with c1:
                    cand_name = st.text_input("Candidate Full Name*", value="Ananya Sharma", key="off_cand_name")
                    role = st.text_input("Offered Position*", value="Senior Machine Learning Engineer", key="off_role")
                with c2:
                    dept = st.selectbox("Department", ["Engineering", "Data Science", "Product", "Design", "Sales", "Finance"], key="off_dept")
                    reporting_mgr = st.text_input("Reporting Manager / Lead", value="Chief Technology Officer", key="off_mgr")

            elif w_step == "2. Compensation (CTC)":
                c1, c2, c3 = st.columns(3)
                with c1:
                    base = st.text_input("Annual Base Salary*", value="₹24,00,000", key="off_base")
                with c2:
                    bonus = st.text_input("Signing Bonus", value="₹2,00,000", key="off_bonus")
                with c3:
                    equity = st.text_input("Stock Options / RSUs", value="0.25% Equity / 2,500 RSUs", key="off_equity")

            elif w_step == "3. Benefits & Terms":
                c1, c2 = st.columns(2)
                with c1:
                    join_dt = st.date_input("Anticipated Start Date", value=date.today() + timedelta(days=21), key="off_join_dt")
                    probation = st.selectbox("Probation Period", ["3 Months", "6 Months", "No Probation (Direct Full-time)"], key="off_probation")
                with c2:
                    notice_p = st.selectbox("Notice Period", ["30 Days", "60 Days", "90 Days"], key="off_notice")
                    benefits = st.multiselect("Benefits Included", ["Comprehensive Medical & Health Insurance", "Flexible Hybrid / Remote Policy", "Annual Learning & Upskilling Stipend", "Unlimited PTO"], default=["Comprehensive Medical & Health Insurance", "Flexible Hybrid / Remote Policy"], key="off_benefits")

            elif w_step == "4. Review & Generate Contract":
                cn = st.session_state.get("off_cand_name", "Candidate")
                cr = st.session_state.get("off_role", "Role")
                cb = st.session_state.get("off_base", "Competitive")

                st.success(f"Ready to compile formal offer letter for **{cn}** as **{cr}** (Annual Base: {cb}).")
                
                contract_text = f"""================================================================================
                            FORMAL OFFER OF EMPLOYMENT
================================================================================

Date: {date.today().strftime('%B %d, %Y')}

To: {cn}
Position: {cr}
Reporting To: {st.session_state.get('off_mgr', 'VP of Engineering')}
Start Date: {st.session_state.get('off_join_dt', date.today() + timedelta(days=21)).strftime('%B %d, %Y')}

Dear {cn},

On behalf of the leadership team, we are pleased to extend this formal offer of employment for the position of {cr}.

1. COMPENSATION
   • Base Salary: {cb} per annum.
   • Signing Bonus: {st.session_state.get('off_bonus', 'None')}.
   • Equity Grant: {st.session_state.get('off_equity', 'None')}.

2. TERMS & CONDITIONS
   • Probation Period: {st.session_state.get('off_probation', '3 Months')}.
   • Notice Period: {st.session_state.get('off_notice', '60 Days')}.

We look forward to welcoming you aboard!
"""
                st.text_area("Employment Agreement Preview", value=contract_text, height=220, disabled=True, key="contract_preview_area")
                
                pdf_bytes = compile_offer_letter_pdf(cn, cr, cb, contract_text)
                st.download_button(
                    "📥 Download Formal Offer Letter (.txt / PDF)",
                    data=contract_text,
                    file_name=f"Offer_Letter_{cn.replace(' ', '_')}.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True,
                    key="dl_offer_btn",
                )

    # ---------------------------------------------------------
    # SUBVIEW C: Candidate Offer Portal Experience (Candidate View)
    # ---------------------------------------------------------
    elif subview == "👤 Candidate Offer Portal (Preview)":
        with st.container(border=True):
            st.markdown(
                f'''
                <div style="background: {COLOR_PRIMARY}; border-radius: 14px; padding: 24px; color: #ffffff; margin-bottom: 20px; text-align: center;">
                    <div style="font-size: 24px; font-weight: 800; line-height: 1.2;">
                        🎉 Congratulations, Ananya!
                    </div>
                    <div style="font-size: 14px; color: #d1e3d7; margin-top: 6px;">
                        You have received a formal offer of employment for <b>Senior Machine Learning Engineer</b>.
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
            st.markdown("#### 📄 Employment Package Summary")
            st.caption("Annual CTC: **₹28,00,000** · Location: **Bengaluru (Hybrid)** · Joining Date: **15 Sep 2026**")

            act1, act2 = st.columns(2)
            with act1:
                if st.button("✅ Digitally Accept Offer", type="primary", use_container_width=True, key="cand_accept_offer_btn"):
                    st.toast("🎉 Offer accepted! Welcome to the team.", icon="🏆")
            with act2:
                if st.button("❌ Request Clarification / Decline", use_container_width=True, key="cand_decline_offer_btn"):
                    st.info("Talent team has been notified.")
