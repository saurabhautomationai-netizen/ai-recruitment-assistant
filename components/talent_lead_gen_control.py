"""Talent Lead Gen Agent Controllable Dashboard Component.

Provides a full interactive control center for autonomous candidate sourcing,
supporting 30+ candidate generation across all domains & major job boards (Naukri, Indeed, Foundit, LinkedIn, GitHub).
"""

from __future__ import annotations

import json
import urllib.parse
import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional

from services.talent_lead_gen_service import DEFAULT_TALENT_CLIENT, TalentLeadGenServiceClient
from services.supabase_service import get_jobs, get_candidates


def render_talent_lead_gen_dashboard(client: Optional[TalentLeadGenServiceClient] = None) -> None:
    """Renders the comprehensive Talent Lead Gen Agent Control Center."""
    talent_client = client or DEFAULT_TALENT_CLIENT

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 28px; font-weight: 750; color: #152238; margin-bottom: 4px;">
                🎯 Talent Lead Gen Control Center
            </h1>
            <p style="color: #6b7280; font-size: 14px; margin: 0;">
                Autonomous multi-channel sourcing from <b>Naukri.com, Indeed, Foundit, LinkedIn, GitHub, Behance & ICAI</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Connection & Live Telemetry Health Bar
    health = talent_client.check_health()
    is_connected = health.get("connected", False)

    col_status1, col_status2, col_status3, col_status4 = st.columns([1.5, 1.2, 1.2, 1.1])
    
    with col_status1:
        if is_connected:
            st.success("🟢 Agent Online (Port 8005)")
        else:
            st.error("🔴 Agent Offline (Port 8005)")
    with col_status2:
        status_data = talent_client.get_status() if is_connected else {}
        state = status_data.get("state", "OFFLINE")
        st.metric("Pipeline State", state)
    with col_status3:
        st.metric("Sourcing Capacity", "30 Top Leads / Batch")
    with col_status4:
        st.metric("Integrated Portals", "Naukri • Indeed • Foundit")

    if not is_connected:
        st.warning(
            "⚠️ **Talent Lead Gen Agent API is currently not detected on http://127.0.0.1:8005.**\n\n"
            "To launch the standalone agent server, execute:\n"
            "`uvicorn lead_gen_core.api.webhook_server:app --port 8005 --reload`\n\n"
            "*Note: Simulated on-demand execution is enabled for previewing candidate generation.*"
        )

    st.divider()

    # 2. Sourcing Configuration & Control Panel
    st.markdown("### 🎛️ Sourcing Control Panel")
    
    jobs_df = get_jobs()
    job_options: Dict[str, Dict[str, Any]] = {}
    
    if not jobs_df.empty and "id" in jobs_df.columns:
        for _, row in jobs_df.iterrows():
            job_id_str = str(row["id"])
            title = row.get("title", "Untitled Role")
            dept = row.get("department", "General")
            skills = row.get("required_skills", [])
            loc = row.get("location", "Pune")
            job_options[f"{title} ({dept}) — ID: {job_id_str[:8]}"] = {
                "id": job_id_str,
                "title": title,
                "department": dept,
                "skills": skills if isinstance(skills, list) else [s.strip() for s in str(skills).split(",") if s.strip()],
                "location": loc,
            }

    tab_control, tab_live_leads, tab_portals = st.tabs([
        "🚀 Launch & Configure Sourcing",
        "👥 Sourced Candidate Leads (30 Profiles)",
        "🔍 Job Board X-Ray & Search Strings (Naukri/Indeed/Foundit)",
    ])

    with tab_control:
        col_c1, col_c2 = st.columns([1.2, 1])

        with col_c1:
            st.markdown("#### 1. Target Requisition")
            sourcing_mode = st.radio(
                "Requisition Source",
                ["Select from Open Jobs", "Custom / Ad-Hoc Requisition"],
                horizontal=True,
            )

            PRESET_TEMPLATES = {
                "📞 BPO - International UK/US Voice Process": {
                    "title": "International Voice Process Executive (UK/US Shifts)",
                    "skills": "English Fluency, UK Accent, Customer Support, CRM, Active Listening, Inbound Calls, Rotational Night Shifts",
                    "location": "Pune / Mumbai, India",
                    "domain": "bpo_voice",
                },
                "💬 BPO - Non-Voice (Chat & Email)": {
                    "title": "Non-Voice Customer Support Executive (Chat & Email)",
                    "skills": "Written English, Live Chat Support, Zendesk, Freshdesk, Email Handling, Typing Speed 50+ WPM",
                    "location": "Pune / Bangalore, India",
                    "domain": "bpo_non_voice",
                },
                "🧠 KPO - Senior Financial & Equity Research": {
                    "title": "Senior Financial & Market Research Analyst",
                    "skills": "Financial Modeling, Equity Valuation, Advanced Excel, Secondary Research, Bloomberg, DCF Modeling",
                    "location": "Mumbai / Pune, India",
                    "domain": "kpo_finance",
                },
                "🏥 KPO - US Healthcare Claims & Billing": {
                    "title": "Medical Billing & US Healthcare Claims Specialist",
                    "skills": "US Healthcare, Medical Billing, HIPAA Compliance, Claims Adjudication, Denial Management, AR Calling",
                    "location": "Pune / Hyderabad, India",
                    "domain": "kpo_healthcare",
                },
                "💼 Inside Sales & Telemarketing": {
                    "title": "Inside Sales & Business Development Specialist",
                    "skills": "B2B Sales, Cold Calling, Lead Qualification, HubSpot, Pipeline Management, Target Driven",
                    "location": "Pune / Bangalore, India",
                    "domain": "sales_bd",
                },
                "🤖 AI Automations & LLM Ops": {
                    "title": "AI Automation Architect & Agentic Engineer",
                    "skills": "Python, LangChain, n8n, FastAPI, PostgreSQL, Prompt Engineering, Docker",
                    "location": "Pune, India",
                    "domain": "ai_automation",
                },
            }

            selected_job_data: Dict[str, Any] = {}
            if sourcing_mode == "Select from Open Jobs" and job_options:
                chosen_label = st.selectbox("Select Active Job Requisition", list(job_options.keys()))
                selected_job_data = job_options[chosen_label]
                req_title = selected_job_data["title"]
                req_skills = selected_job_data["skills"]
                req_location = selected_job_data["location"]
                req_id = selected_job_data["id"]
                default_domain_idx = 0
            else:
                st.caption("✨ **Quick 1-Click Role Presets:**")
                preset_choice = st.selectbox(
                    "Select Pre-configured Industry Template",
                    ["-- Custom Role --"] + list(PRESET_TEMPLATES.keys()),
                    index=1,
                    key="preset_role_choice",
                )
                
                if preset_choice in PRESET_TEMPLATES:
                    p_data = PRESET_TEMPLATES[preset_choice]
                    req_title = st.text_input("Job Title *", value=p_data["title"])
                    req_skills_str = st.text_input("Core Required Skills", value=p_data["skills"])
                    req_location = st.text_input("Target Location", value=p_data["location"])
                else:
                    req_title = st.text_input("Job Title *", value="International Voice Process Executive", placeholder="e.g. UK Voice Process / Senior Research Analyst")
                    req_skills_str = st.text_input("Core Required Skills", value="English Fluency, Customer Care, Active Listening, UK Shifts", placeholder="Comma-separated skills")
                    req_location = st.text_input("Target Location", value="Pune, Maharashtra, India")
                
                req_skills = [s.strip() for s in req_skills_str.split(",") if s.strip()]
                req_id = f"custom_{abs(hash(req_title)) % 100000}"

            domain_options = {
                "Auto-Detect Domain (Recommended)": None,
                "📞 BPO - International Voice Process (UK/US Shifts)": "bpo_voice",
                "💬 BPO - Non-Voice (Chat, Email & Back-Office)": "bpo_non_voice",
                "🧠 KPO - Financial & Market Research / Analytics": "kpo_finance",
                "🏥 KPO/BPO - US Healthcare Claims & Medical Billing": "kpo_healthcare",
                "💼 Inside Sales, Telemarketing & Business Development": "sales_bd",
                "🤖 AI Automations & LLM Ops": "ai_automation",
                "💻 Software Engineering & Tech": "engineering",
            }
            selected_domain_label = st.selectbox("Operational Job Domain", list(domain_options.keys()))
            selected_domain = domain_options[selected_domain_label]

        with col_c2:
            st.markdown("#### 2. Sourcing Parameters")
            target_count = st.slider("Target Candidates to Source", min_value=5, max_value=50, value=30, step=5)
            min_score = st.slider("Minimum Fit Score Threshold (0-100)", min_value=50, max_value=90, value=65, step=5)
            
            st.markdown("#### 3. Active Sourcing Channels")
            c_ch1, c_ch2 = st.columns(2)
            with c_ch1:
                ch_naukri = st.checkbox("🇮🇳 Naukri.com (Resdex / X-Ray)", value=True)
                ch_indeed = st.checkbox("🌐 Indeed.com Resumes", value=True)
                ch_foundit = st.checkbox("🎯 Foundit.in (Monster)", value=True)
            with c_ch2:
                ch_linkedin = st.checkbox("💼 LinkedIn Recruiter", value=True)
                ch_github = st.checkbox("💻 GitHub / Behance / Portals", value=True)
                ch_enrich = st.checkbox("📱 Direct Phone & Email Enrichment", value=True)

        st.markdown("---")
        
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.5, 1, 1, 1])
        
        with btn_col1:
            start_btn = st.button("⚡ Start Autonomous Sourcing (30 Top Leads)", type="primary", use_container_width=True)
        with btn_col2:
            pause_btn = st.button("⏸️ Pause Engine", use_container_width=True, disabled=not is_connected)
        with btn_col3:
            resume_btn = st.button("▶️ Resume", use_container_width=True, disabled=not is_connected)
        with btn_col4:
            clear_btn = st.button("🧹 Clear Leads", use_container_width=True)

        if pause_btn and is_connected:
            res = talent_client.send_control_action("PAUSE", req_id)
            st.info(f"Pipeline status updated: {res.get('state', 'PAUSED')}")
            st.rerun()

        if resume_btn and is_connected:
            res = talent_client.send_control_action("RESUME", req_id)
            st.success(f"Pipeline status updated: {res.get('state', 'RUNNING')}")
            st.rerun()

        if clear_btn:
            if is_connected:
                talent_client.send_control_action("CLEAR", req_id)
            st.session_state.pop("last_sourcing_result", None)
            st.success("Leads cleared for current requisition.")
            st.rerun()

        if start_btn:
            with st.spinner(f"Agent actively sourcing {target_count} top candidate leads across Naukri, Indeed, Foundit & LinkedIn for '{req_title}'..."):
                try:
                    if is_connected:
                        result = talent_client.trigger_sourcing(
                            job_id=req_id,
                            title=req_title,
                            skills=req_skills,
                            location=req_location,
                            target_count=target_count,
                            min_score=min_score,
                            domain=selected_domain,
                        )
                    else:
                        from lead_gen_core.orchestrator import DEFAULT_ORCHESTRATOR
                        result = DEFAULT_ORCHESTRATOR.execute_sourcing_pipeline(
                            job_id=req_id,
                            title=req_title,
                            skills=req_skills,
                            location=req_location,
                            target_count=target_count,
                            min_score=min_score,
                            domain_override=selected_domain,
                        )

                    st.session_state["last_sourcing_result"] = result
                    st.success(f"🎉 Successfully sourced, evaluated, and ingested {result.get('sourced_count', 0)} top candidates for '{req_title}'!")
                except Exception as err:
                    st.error(f"Sourcing error: {err}")

    with tab_live_leads:
        last_res = st.session_state.get("last_sourcing_result")
        
        candidates = []
        if last_res and "candidates" in last_res:
            candidates = last_res["candidates"]
        elif is_connected:
            candidates = talent_client.get_leads()

        if not candidates:
            st.info("No sourced candidates found yet. Launch a sourcing run from the control panel!")
        else:
            st.markdown(f"#### 📋 Vetted Candidates ({len(candidates)} Profiles Sourced)")
            
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                search_kw = st.text_input("Filter by name, skill, or keyword", placeholder="Type to filter...")
            with f_col2:
                tier_filter = st.selectbox("Filter Fit Tier", ["All Tiers", "TIER_1 (85%+)", "TIER_2 (70-84%)", "TIER_3 (<70%)"])

            filtered_candidates = []
            for c in candidates:
                name = c.get("name") or c.get("full_name", "")
                skills_text = " ".join(c.get("skills", []))
                bio = c.get("resume_text", "")
                tier = c.get("fit_tier", "TIER_2")
                
                if search_kw:
                    q = search_kw.lower()
                    if q not in name.lower() and q not in skills_text.lower() and q not in bio.lower():
                        continue
                if tier_filter != "All Tiers":
                    selected_tier_code = tier_filter.split(" ")[0]
                    if tier != selected_tier_code:
                        continue
                filtered_candidates.append(c)

            st.write(f"Showing **{len(filtered_candidates)}** candidates matching criteria:")

            for i, cand in enumerate(filtered_candidates, 1):
                name = cand.get("name") or cand.get("full_name", f"Candidate {i}")
                title = cand.get("current_role") or cand.get("title", "Professional")
                score = cand.get("match_score", 85)
                tier = cand.get("fit_tier", "TIER_1")
                email = cand.get("email", "Not provided")
                phone = cand.get("phone", "Not provided")
                loc = cand.get("location", "Pune, India")
                exp = cand.get("years_experience") or cand.get("experience_years", 5.0)
                company = cand.get("current_company", "Leading Industry Firm")
                linkedin = cand.get("linkedin_url")
                github = cand.get("github_url")
                portfolio = cand.get("portfolio_url")
                skills_list = cand.get("skills", [])
                interview_qs = cand.get("interview_questions", [])

                with st.container(border=True):
                    header_col, score_col = st.columns([3, 1])
                    with header_col:
                        st.markdown(f"### {i}. {name}")
                        st.markdown(f"**{title}** • {company} • 📍 {loc} • ⏳ **{exp} years exp**")
                    with score_col:
                        badge_color = "#137a52" if score >= 85 else ("#2457a6" if score >= 70 else "#b42318")
                        st.markdown(
                            f"""
                            <div style="background: {badge_color}15; border: 1px solid {badge_color}; border-radius: 12px; padding: 8px 12px; text-align: center;">
                                <div style="font-size: 20px; font-weight: 750; color: {badge_color};">{score}/100</div>
                                <div style="font-size: 11px; font-weight: 600; color: {badge_color};">{tier} MATCH</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    links_md = []
                    if email and email != "Not provided":
                        links_md.append(f"📧 `{email}`")
                    if phone and phone != "Not provided":
                        links_md.append(f"📱 `{phone}`")
                    if linkedin:
                        links_md.append(f"[🔗 LinkedIn Profile]({linkedin})")
                    if github and "github" in github:
                        links_md.append(f"[💻 GitHub]({github})")
                    if portfolio:
                        links_md.append(f"[🎨 Portfolio / Credential]({portfolio})")

                    st.markdown(" • ".join(links_md))

                    if skills_list:
                        skills_html = " ".join(
                            f"<span style='background: #eef4ff; color: #2457a6; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin-right: 4px;'>{s}</span>"
                            for s in skills_list
                        )
                        st.markdown(f"<div style='margin: 8px 0;'>{skills_html}</div>", unsafe_allow_html=True)

                    if interview_qs:
                        with st.expander("💡 Recommended Domain Interview Focus Questions"):
                            for q in interview_qs:
                                st.markdown(f"- *{q}*")

    with tab_portals:
        st.markdown("#### 🔍 Job Board Google X-Ray & Search Queries")
        st.caption("Copy or directly click to search live candidate databases across India's top portals:")
        
        last_res = st.session_state.get("last_sourcing_result")
        if last_res and "strategy" in last_res:
            strat = last_res["strategy"]
            naukri_q = strat.get("naukri_xray_query", "")
            indeed_q = strat.get("indeed_xray_query", "")
            foundit_q = strat.get("foundit_xray_query", "")
            li_q = strat.get("linkedin_xray_query", "")

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.markdown("##### 🇮🇳 Naukri.com Profile X-Ray")
                st.code(naukri_q, language="text")
                st.link_button("🌐 Search Naukri on Google", f"https://www.google.com/search?q={urllib.parse.quote(naukri_q)}", use_container_width=True)

                st.markdown("##### 🎯 Foundit.in (Monster) X-Ray")
                st.code(foundit_q, language="text")
                st.link_button("🌐 Search Foundit on Google", f"https://www.google.com/search?q={urllib.parse.quote(foundit_q)}", use_container_width=True)

            with c_p2:
                st.markdown("##### 🌐 Indeed.com Resume Search")
                st.code(indeed_q, language="text")
                st.link_button("🌐 Search Indeed on Google", f"https://www.google.com/search?q={urllib.parse.quote(indeed_q)}", use_container_width=True)

                st.markdown("##### 💼 LinkedIn Recruiter X-Ray")
                st.code(li_q, language="text")
                st.link_button("🌐 Search LinkedIn on Google", f"https://www.google.com/search?q={urllib.parse.quote(li_q)}", use_container_width=True)
        else:
            st.info("Execute a sourcing run to generate tailored Naukri, Indeed, Foundit, and LinkedIn queries.")
