"""Candidate Self-Service Interview Booking Component.

Provides a Calendly-style booking flow: Recruiters generate shareable booking links,
and candidates pick time slots that automatically write interview events into the schedule.
"""

from __future__ import annotations

import streamlit as st
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


def render_self_service_booking(applications: List[Dict[str, Any]], on_booking_confirmed: Optional[callable] = None) -> None:
    st.markdown("### 📅 Candidate Self-Service Interview Booking (Calendly-Style)")
    st.caption("Generate instant booking links for shortlisted candidates or simulate the candidate's self-serve slot selection.")

    tab1, tab2 = st.tabs(["🔗 Generate Candidate Booking Link", "📱 Candidate Booking Experience Simulator"])

    with tab1:
        st.markdown("#### 1. Select Candidate Application to Invite")
        if not applications:
            st.info("No active applications available.")
            return

        app_options = {
            f"{a.get('candidate_name', 'Candidate')} — {a.get('job_title', 'Role')} ({a.get('stage', 'Stage')})": a
            for a in applications
        }
        selected_label = st.selectbox("Select Candidate Application", list(app_options.keys()))
        selected_app = app_options[selected_label]

        col1, col2 = st.columns(2)
        with col1:
            interview_type = st.selectbox("Interview Type", ["Initial Technical Screen (30m)", "Hiring Manager Deep Dive (45m)", "System Architecture (60m)", "Executive Culture Fit (30m)"])
            interviewer = st.text_input("Lead Interviewer", value="Engineering Lead")
        with col2:
            time_window = st.selectbox("Available Days Window", ["Next 3 Business Days", "Next 5 Business Days", "Next 10 Days"])
            meeting_platform = st.selectbox("Meeting Platform", ["Google Meet (Auto-generated)", "Zoom Meeting", "Microsoft Teams"])

        booking_token = f"zero-book-{abs(hash(selected_label)) % 1000000}"
        booking_url = f"https://recruit.yourdomain.com/book/{booking_token}"

        st.markdown("---")
        st.markdown("#### 2. Generated Shareable Booking Link")
        st.code(booking_url, language="text")

        email_preview = f"""Hi {selected_app.get('candidate_name', 'there')},

We were impressed by your background for the {selected_app.get('job_title', 'open')} role and would love to invite you for a {interview_type}.

Please pick a time that works best for you using our self-service scheduling link below:
👉 {booking_url}

Looking forward to speaking with you!

Best regards,
{interviewer} & The Recruiting Team"""

        with st.expander("✉️ View Ready-to-Send Email / WhatsApp Invite", expanded=True):
            st.text_area("Message Preview", value=email_preview, height=160)
            if st.button("📤 Send Booking Invite via Email & WhatsApp", key="send_booking_btn"):
                st.success(f"✅ Booking invite dispatched to {selected_app.get('candidate_email', 'candidate')}!")

    with tab2:
        st.markdown("#### 🗓️ Candidate Self-Serve Calendar Picker")
        st.info("This is what the candidate sees when clicking their personalized booking link.")

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### 1. Select Date")
            today = date.today()
            selected_date = st.date_input("Choose Interview Date", min_value=today + timedelta(days=1), max_value=today + timedelta(days=14), value=today + timedelta(days=1))
            user_tz = st.selectbox("Your Timezone", ["Asia/Kolkata (IST)", "America/New_York (EST)", "America/Los_Angeles (PST)", "Europe/London (GMT)"])

        with c2:
            st.markdown("##### 2. Select Available Time Slot")
            slots = ["10:00 AM - 10:30 AM", "11:30 AM - 12:00 PM", "02:00 PM - 02:30 PM", "04:30 PM - 05:00 PM", "06:00 PM - 06:30 PM"]
            selected_slot = st.radio("Available Slots on " + selected_date.strftime("%B %d, %Y"), slots)

        cand_notes = st.text_input("Anything specific you'd like us to know before the call?", placeholder="e.g. My portfolio showcases my recent microservices work.")

        if st.button("🎉 Confirm Interview Booking", type="primary", use_container_width=True):
            st.balloons()
            st.success(f"📅 Confirmed! Your {interview_type} is booked for {selected_date.strftime('%B %d, %Y')} at {selected_slot} ({user_tz}). Calendar invites sent.")
            if on_booking_confirmed:
                on_booking_confirmed({
                    "date": str(selected_date),
                    "slot": selected_slot,
                    "type": interview_type,
                    "candidate": selected_app.get("candidate_name", "Candidate"),
                    "notes": cand_notes,
                })
