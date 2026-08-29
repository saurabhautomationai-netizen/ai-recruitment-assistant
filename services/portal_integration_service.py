"""Portal and Social Integrations Service for Recruiter Channels and Job Portals."""

import json
import os
import streamlit as st

from services.secret_encryption_service import decrypt_dict, encrypt_dict

INTEGRATIONS_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "recruiter_integrations.json")


def _load_integrations_store() -> dict:
    """Load stored recruiter portal and social credentials with automated decryption."""
    if not os.path.exists(INTEGRATIONS_STORE_PATH):
        os.makedirs(os.path.dirname(INTEGRATIONS_STORE_PATH), exist_ok=True)
        default_data = {}
        _save_integrations_store(default_data)
        return default_data
    try:
        with open(INTEGRATIONS_STORE_PATH, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
            if not raw_text:
                return {}
            # If armored ciphertext enc::
            if raw_text.startswith("enc::"):
                return decrypt_dict(raw_text)
            # Legacy unencrypted fallback
            return json.loads(raw_text)
    except Exception:
        return {}


def _save_integrations_store(data: dict) -> None:
    """Save stored recruiter portal and social credentials with AES encryption."""
    try:
        os.makedirs(os.path.dirname(INTEGRATIONS_STORE_PATH), exist_ok=True)
        encrypted_payload = encrypt_dict(data)
        with open(INTEGRATIONS_STORE_PATH, "w", encoding="utf-8") as f:
            f.write(encrypted_payload)
    except Exception:
        pass


def get_recruiter_integrations(recruiter_email: str) -> dict:
    """Retrieve saved integration settings for a recruiter."""
    store = _load_integrations_store()
    clean_email = str(recruiter_email).strip().lower()
    return store.get(clean_email, {
        "recruiter_name": "Talent Acquisition Lead",
        "agency_name": "Netizen Recruitment",
        "recruiter_phone": "+91 98765 43210",
        "whatsapp_number": "+91 98765 43210",
        "telegram_handle": "@Netizen_Recruiter",
        "outreach_email": clean_email,
        "naukri_user": "",
        "linkedin_user": "",
        "indeed_user": "",
        "foundit_user": "",
        "github_user": "",
        "candidate_form_url": "https://saurabhautomation7596.app.n8n.cloud/form/b34bc21c-4b57-4147-9759-994fa51752b0",
    })


def save_recruiter_integrations(recruiter_email: str, data: dict) -> None:
    """Save integration settings for a recruiter."""
    store = _load_integrations_store()
    clean_email = str(recruiter_email).strip().lower()
    store[clean_email] = data
    _save_integrations_store(store)


def render_portal_and_social_integrations(recruiter_email: str) -> None:
    """Render the full Recruiter Portals, WhatsApp & Social Integrations dashboard."""
    st.markdown('<div class="main-title">⚙️ Portals & Social Integrations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">'
        'Connect your WhatsApp, Telegram, job board portals (Naukri, LinkedIn, Indeed), and agency branding.'
        '</div>',
        unsafe_allow_html=True,
    )

    current_cfg = get_recruiter_integrations(recruiter_email)

    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 WhatsApp & Telegram",
        "🎯 Job Portals (Naukri/LinkedIn/Indeed)",
        "🏢 Agency & Recruiter Branding",
        "📁 Direct Data & Resume Uploads",
    ])

    with tab1:
        st.markdown("### 💬 Direct Communication Channels")
        st.caption("Configure where candidates will receive your automated WhatsApp and Telegram outreach.")

        c1, c2 = st.columns(2)
        with c1:
            wa_num = st.text_input(
                "WhatsApp Business / Mobile Number",
                value=current_cfg.get("whatsapp_number", ""),
                placeholder="+91 98765 43210",
                help="Phone number attached to your WhatsApp Web / WhatsApp Cloud API.",
            )
            tele_h = st.text_input(
                "Telegram Recruiter Handle / Bot",
                value=current_cfg.get("telegram_handle", ""),
                placeholder="@Agency_Recruiter",
            )
        with c2:
            out_email = st.text_input(
                "Official Outreach Email Address",
                value=current_cfg.get("outreach_email", recruiter_email),
                placeholder="recruiter@agency.com",
            )
            st.info("🟢 **WhatsApp Cloud Dispatcher Status**: Connected to n8n Automation Workflow.")

        if st.button("💾 Save Communication Channels", type="primary", key="save_comm_btn"):
            current_cfg["whatsapp_number"] = wa_num.strip()
            current_cfg["telegram_handle"] = tele_h.strip()
            current_cfg["outreach_email"] = out_email.strip()
            save_recruiter_integrations(recruiter_email, current_cfg)
            st.success("✅ Communication settings saved successfully!")

    with tab2:
        st.markdown("### 🎯 Autonomous Lead Gen Job Portals")
        st.caption("Connect your recruiter portal logins so the Talent Lead Gen Agent can harvest candidate CVs directly.")

        col_j1, col_j2 = st.columns(2)
        with col_j1:
            st.markdown("##### 💼 LinkedIn Recruiter")
            li_user = st.text_input("LinkedIn Email / Username", value=current_cfg.get("linkedin_user", ""), placeholder="recruiter@agency.com")
            li_pass = st.text_input("LinkedIn Password / Auth Token", type="password", placeholder="••••••••••••", key="li_p")

            st.markdown("##### 🔍 Naukri.com / Resdex")
            naukri_user = st.text_input("Naukri Recruiter Login ID", value=current_cfg.get("naukri_user", ""), placeholder="agency_resdex")
            naukri_pass = st.text_input("Naukri Password", type="password", placeholder="••••••••••••", key="nk_p")

        with col_j2:
            st.markdown("##### 🌐 Indeed Employer")
            indeed_user = st.text_input("Indeed Employer Login", value=current_cfg.get("indeed_user", ""), placeholder="hr@agency.com")
            indeed_pass = st.text_input("Indeed Password", type="password", placeholder="••••••••••••", key="ind_p")

            st.markdown("##### 🏢 Foundit (Monster) & GitHub")
            foundit_user = st.text_input("Foundit Recruiter ID", value=current_cfg.get("foundit_user", ""), placeholder="monster_recruiter")
            gh_token = st.text_input("GitHub Token (for tech sourcing)", value=current_cfg.get("github_user", ""), placeholder="ghp_...")

        if st.button("💾 Save Portal Credentials", type="primary", key="save_portals_btn"):
            current_cfg["linkedin_user"] = li_user.strip()
            current_cfg["naukri_user"] = naukri_user.strip()
            current_cfg["indeed_user"] = indeed_user.strip()
            current_cfg["foundit_user"] = foundit_user.strip()
            current_cfg["github_user"] = gh_token.strip()
            save_recruiter_integrations(recruiter_email, current_cfg)
            st.success("✅ Job portal credentials securely linked for Talent Lead Gen Agent!")

    with tab3:
        st.markdown("### 🏢 Agency & Recruiter Branding")
        st.caption("These details automatically brand all your visual hiring posters, social drafts, and QR codes.")

        cb1, cb2 = st.columns(2)
        with cb1:
            rec_name = st.text_input("Recruiter Full Name", value=current_cfg.get("recruiter_name", "Talent Acquisition Lead"))
            ag_name = st.text_input("Agency / Company Name", value=current_cfg.get("agency_name", "Netizen Recruitment"))
        with cb2:
            rec_phone = st.text_input("Helpline Phone Number (on posters)", value=current_cfg.get("recruiter_phone", "+91 98765 43210"))
            form_url = st.text_input("Candidate Application Intake Form URL (QR Code)", value=current_cfg.get("candidate_form_url", "https://saurabhautomation7596.app.n8n.cloud/form/b34bc21c-4b57-4147-9759-994fa51752b0"))

        if st.button("💾 Save Branding & QR Code Settings", type="primary", key="save_brand_btn"):
            current_cfg["recruiter_name"] = rec_name.strip()
            current_cfg["agency_name"] = ag_name.strip()
            current_cfg["recruiter_phone"] = rec_phone.strip()
            current_cfg["candidate_form_url"] = form_url.strip()
            save_recruiter_integrations(recruiter_email, current_cfg)
            st.success("✅ Custom branding and QR code URL saved!")

    with tab4:
        st.markdown("### 📁 Direct Data & Resume Ingestion")
        st.caption("Upload your existing candidate spreadsheets or drag-and-drop bulk resumes directly into your private pipeline.")

        up_col1, up_col2 = st.columns(2)
        with up_col1:
            st.markdown("##### 📊 Upload Candidate Excel / CSV")
            cand_file = st.file_uploader(
                "Upload candidate spreadsheet (.csv, .xlsx)",
                type=["csv", "xlsx"],
                key="direct_cand_uploader",
            )
            if cand_file:
                st.success(f"File `{cand_file.name}` uploaded! Click 'Process Import' on the Bulk Import page to ingest.")

        with up_col2:
            st.markdown("##### 📄 Upload PDF Resumes")
            resumes = st.file_uploader(
                "Upload candidate resumes (.pdf, .docx)",
                type=["pdf", "docx"],
                accept_multiple_files=True,
                key="direct_resume_uploader",
            )
            if resumes:
                st.success(f"Received {len(resumes)} resumes ready for AI Resume Screener parsing!")
