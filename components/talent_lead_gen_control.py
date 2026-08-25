"""Talent Lead Gen Agent Controllable Dashboard Component.

Provides a full interactive control center for autonomous candidate sourcing,
supporting 30+ candidate generation across 9 Industry Verticals & 5-Tier Level Hierarchies (L1-L5).
"""

from __future__ import annotations

import json
import urllib.parse
import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional

from services.talent_lead_gen_service import DEFAULT_TALENT_CLIENT, TalentLeadGenServiceClient
from services.supabase_service import get_jobs, get_candidates
from services.industry_taxonomy import INDUSTRY_TAXONOMY, get_all_job_presets


def render_talent_lead_gen_dashboard(
    client: Optional[TalentLeadGenServiceClient] = None,
    jobs_df: Optional[pd.DataFrame] = None,
) -> None:
    """Renders the comprehensive Talent Lead Gen Agent Control Center."""
    talent_client = client or DEFAULT_TALENT_CLIENT

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 28px; font-weight: 750; color: #152238; margin-bottom: 4px;">
                🎯 Talent Lead Gen Control Center
            </h1>
            <p style="color: #6b7280; font-size: 14px; margin: 0;">
                Autonomous multi-channel sourcing across <b>9 Industry Verticals (IT, Finance, Marketing, Trading, Investments, BPO, KPO, Sales & Healthcare)</b> from <b>Naukri.com, Indeed, Foundit, LinkedIn, GitHub, Behance & ICAI</b>.
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
            st.info("⚡ Autonomous Engine Active (In-App)")
    with col_status2:
        status_data = talent_client.get_status() if is_connected else {}
        state = status_data.get("state", "IDLE")
        st.metric("Pipeline State", state)
    with col_status3:
        st.metric("Sourcing Capacity", "30 Top Leads / Batch")
    with col_status4:
        st.metric("Integrated Verticals", "9 Major Industries")

    st.divider()

    # 2. Sourcing Configuration & Control Panel
    st.markdown("### 🎛️ Sourcing Control Panel")
    
    active_jobs = jobs_df if jobs_df is not None else get_jobs()
    job_options: Dict[str, Dict[str, Any]] = {}
    
    if not active_jobs.empty and "id" in active_jobs.columns:
        seen_titles = set()
        for _, row in active_jobs.iterrows():
            job_id_str = str(row["id"])
            title = str(row.get("title", "Untitled Role")).strip()
            dept = str(row.get("department", "General")).strip()
            skills = row.get("required_skills", [])
            loc = str(row.get("location", "Pune")).strip()
            
            # Deduplicate multiple legacy rows with same title
            label = f"{title} ({dept})"
            if label not in seen_titles:
                seen_titles.add(label)
                job_options[f"{label} — ID: {job_id_str[:8]}"] = {
                    "id": job_id_str,
                    "title": title,
                    "department": dept,
                    "skills": skills if isinstance(skills, list) else [s.strip() for s in str(skills).split(",") if s.strip()],
                    "location": loc,
                }

    tab_control, tab_live_leads, tab_portals = st.tabs([
        "🚀 Launch & Configure Sourcing",
        "👥 Sourced Candidate Leads (30 Profiles)",
        "🔍 Job Board X-Ray & Search Strings (Naukri/Indeed/Foundit/LinkedIn)",
    ])

    with tab_control:
        col_c1, col_c2 = st.columns([1.25, 1])

        with col_c1:
            st.markdown("#### 1. Target Requisition")
            
            sourcing_mode_options = [
                "🏢 Browse 9 Industry Verticals & Role Hierarchy (L1-L5)",
                f"Select from My Open Jobs ({len(job_options)} active)",
                "✍️ Custom / Ad-Hoc Requisition",
            ]
            sourcing_mode = st.radio(
                "Requisition Source",
                sourcing_mode_options,
                index=0,
                horizontal=False,
            )

            selected_job_data: Dict[str, Any] = {}
            selected_domain_key = None
            
            if sourcing_mode.startswith("Select from My Open Jobs"):
                if job_options:
                    chosen_label = st.selectbox("Select Active Job Requisition", list(job_options.keys()))
                    selected_job_data = job_options[chosen_label]
                    req_title = selected_job_data["title"]
                    req_skills = selected_job_data["skills"]
                    req_location = selected_job_data["location"]
                    req_id = selected_job_data["id"]
                else:
                    st.info("ℹ️ No open jobs created in your private pipeline yet. Use '🏢 Browse 9 Industry Verticals' above to source candidates, or go to **Jobs** to post your requisition!")
                    req_title = "International Voice Process Executive"
                    req_skills = ["English Fluency", "UK Accent", "Customer Support", "CRM", "Active Listening"]
                    req_location = "Pune, Maharashtra, India"
                    req_id = "default_bpo"
                    selected_domain_key = "bpo"
            elif sourcing_mode.startswith("🏢 Browse 9 Industry Verticals"):
                # 9-Vertical Hierarchical Browser
                vertical_choices = {
                    f"{v_data['icon']} {v_data['name']}": v_key
                    for v_key, v_data in INDUSTRY_TAXONOMY.items()
                }
                v_label = st.selectbox("Industry Vertical", list(vertical_choices.keys()), index=5, key="v_browser_select")
                selected_domain_key = vertical_choices[v_label]
                v_info = INDUSTRY_TAXONOMY[selected_domain_key]

                col_lvl, col_role = st.columns([1, 1.8])
                with col_lvl:
                    level_options = {
                        f"{l_key}: {l_val['label']}": l_key
                        for l_key, l_val in v_info["levels"].items()
                    }
                    lvl_label = st.selectbox("Hierarchy Level", list(level_options.keys()), index=4, key=f"lvl_{selected_domain_key}")
                    selected_lvl_key = level_options[lvl_label]
                
                with col_role:
                    role_titles = v_info["levels"][selected_lvl_key]["titles"]
                    chosen_title = st.selectbox("Role Title", role_titles, index=0, key=f"role_{selected_domain_key}_{selected_lvl_key}")

                req_title = st.text_input("Target Requisition Title *", value=chosen_title, key=f"title_{chosen_title}")
                default_skills_str = ", ".join(v_info["default_skills"])
                req_skills_str = st.text_input("Required Skills", value=default_skills_str, key=f"skills_{chosen_title}")
                req_skills = [s.strip() for s in req_skills_str.split(",") if s.strip()]
                req_location = st.text_input("Target Location", value="Pune / Mumbai, Maharashtra, India", key=f"loc_{chosen_title}")
                req_id = f"tax_{selected_domain_key}_{selected_lvl_key}_{abs(hash(req_title)) % 10000}"
            else:
                # Custom freeform
                req_title = st.text_input("Job Title *", value="Senior Voice Process Specialist", placeholder="e.g. Quantitative Trader / Head of Operations")
                req_skills_str = st.text_input("Core Required Skills", value="English Fluency, Customer Care, Active Listening, UK Shifts", placeholder="Comma-separated skills")
                req_skills = [s.strip() for s in req_skills_str.split(",") if s.strip()]
                req_location = st.text_input("Target Location", value="Pune, Maharashtra, India")
                req_id = f"custom_{abs(hash(req_title)) % 100000}"
                selected_domain_key = None

            domain_options = {
                "Auto-Detect Domain (Recommended)": None,
                "💻 1. IT Services & Software Engineering": "it_services",
                "📊 2. Finance (Corporate & Enterprise)": "finance",
                "📈 3. Marketing & Growth": "marketing",
                "📉 4. Trading (Capital Markets & Proprietary)": "trading",
                "💰 5. Investments (PE, VC & Asset Management)": "investments",
                "📞 6. Business Process Outsourcing (BPO)": "bpo",
                "🧠 7. Knowledge Process Outsourcing (KPO)": "kpo",
                "🎯 8. Inside Sales & Business Development": "inside_sales",
                "🏥 9. Healthcare Operations & Medical Billing": "healthcare_ops",
            }
            
            # Match index if selected via vertical browser
            def_idx = 0
            if selected_domain_key:
                for idx, (k_label, k_val) in enumerate(domain_options.items()):
                    if k_val == selected_domain_key:
                        def_idx = idx
                        break

            selected_domain_label = st.selectbox(
                "Operational Job Domain",
                list(domain_options.keys()),
                index=def_idx,
                key=f"op_domain_select_{selected_domain_key}",
            )
            selected_domain = domain_options[selected_domain_label] or selected_domain_key

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
        if not candidates:
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
                bio = c.get("summary") or c.get("resume_text", "")
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

            st.caption(f"Showing **{len(filtered_candidates)}** candidates matching criteria:")

            for i, cand in enumerate(filtered_candidates, 1):
                name = cand.get("name") or cand.get("full_name", "Candidate")
                title = cand.get("current_role") or cand.get("title", "Specialist")
                score = cand.get("match_score", 85)
                tier = cand.get("fit_tier", "TIER_1")
                email = cand.get("email", "Not provided")
                phone = cand.get("phone", "Not provided")
                loc = cand.get("location", "Pune, India")
                exp = cand.get("years_experience") or cand.get("experience_years", 3.0)
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
                        links_md.append(f"[💻 GitHub / Portfolio]({github})")
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
