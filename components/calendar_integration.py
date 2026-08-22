"""Safe calendar event preview and credential-bound integration UI."""

from __future__ import annotations

import streamlit as st
from services.auth_service import has_permission

from services.calendar_service import build_calendar_event, create_calendar_event, get_calendar_configuration


def render_calendar_integration(**event_values) -> None:
    with st.expander("Calendar integration", icon=":material/calendar_add_on:"):
        provider = st.selectbox(
            "Calendar provider",
            ("n8n Calendar Automation", "Google Calendar", "Outlook Calendar")
        )
        configuration = get_calendar_configuration(provider)
        try:
            event = build_calendar_event(**event_values)
        except ValueError as error:
            st.info(str(error))
            return
        st.json(event, expanded=False)
        if not configuration.configured:
            st.warning(
                f"{provider} is not configured. Missing environment variables: "
                + ", ".join(configuration.missing)
            )
        confirmed = st.checkbox(
            "I confirm this calendar event preview",
            disabled=(
                not configuration.configured
                or not has_permission("interview_write")
            ),
        )
        if st.button(
            "Create calendar event",
            type="primary",
            disabled=(
                not confirmed
                or not configuration.configured
                or not has_permission("interview_write")
            ),
        ):
            try:
                res = create_calendar_event(provider, event, confirmed=True)
                st.success("Calendar event successfully created / dispatched!")
            except Exception as error:
                st.error(str(error))
