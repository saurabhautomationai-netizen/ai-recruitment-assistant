"""
Candidate Self-Service Booking View (Phase 3).
Adheres strictly to the approved Stitch candidate booking experience.
Preserves booking token behavior, time-slot selection, and calendar synchronization.
"""

import streamlit as st
from ui.theme import COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER
from components.self_service_booking import render_self_service_booking

def render_self_service_booking_workspace(applications_list: list[dict]):
    """Renders the Forest Enterprise candidate self-service booking portal."""
    st.markdown(
        '''
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
            <div>
                <div style="font-size: 26px; font-weight: 850; color: #162E20; letter-spacing: -0.02em; line-height: 1.2;">
                    Self-Service Candidate Interview Booking
                </div>
                <div style="font-size: 13.5px; color: #64748B; margin-top: 3px;">
                    Shareable 1-click slot selection links with automated Google & Outlook calendar integration.
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    render_self_service_booking(applications=applications_list)
