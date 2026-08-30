"""
Portals & Marketplace Integrations Hub (Phase 4).
Adheres strictly to the approved Stitch Forest Enterprise layout.
Preserves 75+ job board syndication, connector configurations, and credential masking.
"""

import streamlit as st
import pandas as pd
from ui.theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER,
    COLOR_TEXT_HEADING, COLOR_TEXT_BODY, COLOR_TEXT_MUTED
)
from ui.components.stat_cards import render_stat_card
from services.job_syndication_service import SYNDICATION_CHANNELS

def render_integrations_workspace():
    """Renders the Forest Enterprise Integrations Hub."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Integrations & Sourcing Channels Hub
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Manage global job board feeds (75+ boards), WhatsApp Business Cloud tokens, and enterprise ATS connectors.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        render_stat_card("Job Board Feeds", "75+ Active", delta="Global", icon="🌐")
    with h2:
        render_stat_card("Connected Apps", "6 Active", subtitle="Marketplace connectors", icon="🔌")
    with h3:
        render_stat_card("WhatsApp Cloud", "Configured", subtitle="Outbound active", icon="📱")
    with h4:
        render_stat_card("API Webhooks", "4 Live", subtitle="Secure endpoints", icon="⚡")

    st.write("")

    tab1, tab2, tab3 = st.tabs(["🌐 Sourcing Channels & 75+ Job Boards", "📱 WhatsApp Cloud API Settings", "🔌 Enterprise Marketplace Connectors"])

    with tab1:
        st.markdown("##### 📡 Automated Job Board Distribution Channels")
        st.caption("Requisitions published in ZERO Recruit automatically syndicate to these candidate sourcing aggregators:")
        
        c_cols = st.columns(3)
        for i, ch in enumerate(SYNDICATION_CHANNELS[:12]):
            col = c_cols[i % 3]
            with col:
                st.markdown(
                    f'''
                    <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
                        <div style="font-weight: 750; color: {COLOR_TEXT_HEADING}; font-size: 13px;">{ch.get("name", "Channel")}</div>
                        <div style="font-size: 11px; color: {COLOR_TEXT_MUTED};">Reach: {ch.get("reach", "Global")} · <span style="color: #047857; font-weight: 700;">● Active Feed</span></div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("##### 📱 WhatsApp Business Cloud API Configuration")
        st.caption("Manage token credentials and template IDs for automated candidate status dispatches.")
        
        wc1, wc2 = st.columns(2)
        with wc1:
            st.text_input("WhatsApp Business Phone Number ID", value="109283746501928", disabled=True, key="wa_phone_id_view")
            st.text_input("Webhook Verification Token", value="sk_live_************************", type="password", disabled=True, key="wa_verify_tok_view")
        with wc2:
            st.text_input("WhatsApp Cloud API Access Token", value="EAAQ********************************", type="password", disabled=True, key="wa_access_tok_view")
            st.caption("🔒 All access tokens and secrets are AES-256 encrypted at rest in local secret vaults.")

    with tab3:
        st.markdown("##### 🔌 200+ Enterprise App Connectors")
        st.caption("Pre-integrated hiring, screening, and background check connectors:")

        apps = [
            {"name": "DocuSign Digital Signatures", "cat": "E-Sign", "status": "Simulated Active"},
            {"name": "Checkr Background Checks", "cat": "Screening", "status": "Ready to Connect"},
            {"name": "HackerRank Code Assessments", "cat": "Technical Eval", "status": "Ready to Connect"},
            {"name": "Slack Notification Channel", "cat": "Team Alerts", "status": "Active"},
        ]

        for a in apps:
            st.markdown(
                f'''
                <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 12px 16px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 750; color: {COLOR_TEXT_HEADING}; font-size: 14px;">{a["name"]}</div>
                        <div style="font-size: 12px; color: {COLOR_TEXT_MUTED};">Category: {a["cat"]}</div>
                    </div>
                    <span style="background: #f0fdf4; color: #047857; border: 1px solid #a7f3d0; font-size: 11px; font-weight: 750; padding: 3px 8px; border-radius: 8px;">
                        {a["status"]}
                    </span>
                </div>
                ''',
                unsafe_allow_html=True,
            )
