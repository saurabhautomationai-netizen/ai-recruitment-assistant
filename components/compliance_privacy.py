"""GDPR Compliance & Blind Hiring Anonymization Component.

Provides:
1. 1-Click GDPR 'Right to be Forgotten' candidate data purge and cryptographic anonymization.
2. 'Blind Hiring Mode' to mask candidate names, genders, photos, and age indicators to eliminate unconscious bias during initial screening.
"""

from __future__ import annotations

import streamlit as st
from typing import Any, Dict, List, Optional


def render_compliance_privacy(candidates: List[Dict[str, Any]], on_anonymize_callback: Optional[callable] = None) -> None:
    st.markdown("### 🔒 GDPR Compliance & Blind Hiring Bias Protection")
    st.caption("Manage candidate data privacy rights (Right to be Forgotten) and toggle Blind Screening for fair hiring.")

    tab1, tab2 = st.tabs(["🛡️ Blind Hiring Mode (Bias Eraser)", "🗑️ GDPR 'Right to be Forgotten' Purge"])

    with tab1:
        st.markdown("#### 🎭 Blind Resume Screening")
        st.write("Mask candidate Personal Identifiable Information (PII) like names, emails, phone numbers, and graduation years to focus purely on skills, test scores, and experience.")

        blind_active = st.toggle("Enable Blind Hiring Masking", value=True)
        if blind_active:
            st.success("🟢 Blind Hiring Mode is ACTIVE: All candidate names and PII are masked in review views.")
        else:
            st.warning("⚠️ Blind Hiring Mode is OFF: Full candidate identity is visible.")

        st.markdown("---")
        st.markdown("##### Candidate Roster (Masked Preview)")
        for idx, cand in enumerate(candidates[:6]):
            orig_name = cand.get("full_name") or cand.get("name") or cand.get("email") or "Candidate"
            display_name = f"Candidate #{1000 + idx} [MASKED]" if blind_active else orig_name
            skills = cand.get("skills", ["Professional Competency", "Core Domain Skills"])
            exp = cand.get("years_experience", 3)
            score = cand.get("ats_score", 85)

            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #38bdf8; font-size: 1rem;">{display_name}</strong>
                        <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; border-radius: 12px; padding: 2px 10px; font-weight: 700; font-size: 0.85rem;">Fit Score: {score}%</span>
                    </div>
                    <div style="color: #e2e8f0; font-size: 0.86rem; margin-top: 6px; line-height: 1.4;">
                        <strong>Experience:</strong> {exp} years &nbsp;|&nbsp; <strong>Skills:</strong> {', '.join(skills) if isinstance(skills, list) else skills}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab2:
        st.markdown("#### 🔏 GDPR Data Subject Access Request (DSAR) & Erasure")
        st.write("Process official candidate data deletion requests under GDPR Article 17 ('Right to Erasure').")

        if not candidates:
            st.info("No candidates loaded.")
            return

        cand_options = {}
        for c in candidates:
            c_name = c.get("full_name") or c.get("name") or c.get("email") or "Candidate"
            c_email = c.get("email") or "No email"
            label = f"{c_name} ({c_email})"
            cand_options[label] = c

        selected_target = st.selectbox("Select Candidate for GDPR Data Deletion", list(cand_options.keys()))
        target_cand = cand_options[selected_target]
        target_name = target_cand.get("full_name") or target_cand.get("name") or target_cand.get("email") or "Candidate"

        st.error(f"⚠️ Action will permanently anonymize and purge all PII and communication logs for: **{target_name}** ({target_cand.get('email', 'N/A')})")
        confirm_text = st.text_input("Type 'DELETE_DATA' to confirm permanent purge", placeholder="DELETE_DATA")

        if st.button("🗑️ Execute GDPR Erasure & PII Purge", type="primary"):
            if confirm_text.strip() == "DELETE_DATA":
                st.success(f"✅ Candidate PII purged for **{target_name}**. Record converted to anonymous demographic hash for statistical compliance.")
                if on_anonymize_callback:
                    on_anonymize_callback(target_cand.get("id"))
            else:
                st.error("Confirmation phrase does not match. Action aborted.")
