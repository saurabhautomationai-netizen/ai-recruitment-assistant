"""Calendar integration boundary; no event is created without OAuth setup."""

from __future__ import annotations

import os
import requests
from dataclasses import dataclass
from typing import Any

from services.auth_service import require_permission


@dataclass(frozen=True)
class CalendarConfiguration:
    provider: str
    configured: bool
    missing: tuple[str, ...]


REQUIRED_ENV = {
    "Google Calendar": ("GOOGLE_CALENDAR_CLIENT_ID", "GOOGLE_CALENDAR_CLIENT_SECRET", "GOOGLE_CALENDAR_REFRESH_TOKEN"),
    "Outlook Calendar": ("OUTLOOK_CALENDAR_CLIENT_ID", "OUTLOOK_CALENDAR_CLIENT_SECRET", "OUTLOOK_CALENDAR_TENANT_ID", "OUTLOOK_CALENDAR_REFRESH_TOKEN"),
    "n8n Calendar Automation": ("N8N_CALENDAR_WEBHOOK_URL",),
}


def get_calendar_configuration(provider: str) -> CalendarConfiguration:
    if provider == "n8n Calendar Automation":
        # Fallback to N8N_COMMUNICATION_WEBHOOK_URL or COMMUNICATION_WEBHOOK_URL if N8N_CALENDAR_WEBHOOK_URL is not set
        url = (
            os.getenv("N8N_CALENDAR_WEBHOOK_URL", "").strip()
            or os.getenv("N8N_COMMUNICATION_WEBHOOK_URL", "").strip()
            or os.getenv("COMMUNICATION_WEBHOOK_URL", "").strip()
        )
        return CalendarConfiguration(provider, bool(url), () if url else ("N8N_CALENDAR_WEBHOOK_URL",))
    required = REQUIRED_ENV.get(provider, ())
    missing = tuple(name for name in required if not os.getenv(name, "").strip())
    return CalendarConfiguration(provider, bool(required) and not missing, missing)


def build_calendar_event(**values: Any) -> dict[str, Any]:
    """Build a provider-neutral event preview without external side effects."""

    required = ("candidate", "interviewer", "job", "start", "location")
    missing = [field for field in required if not str(values.get(field, "")).strip()]
    if missing:
        raise ValueError("Missing calendar event fields: " + ", ".join(missing))
    return {field: values[field] for field in required} | {"candidate_email": values.get("candidate_email", "")}


def create_calendar_event(provider: str, event: dict[str, Any], confirmed: bool) -> dict:
    """Create a calendar event via the configured provider or n8n webhook."""

    require_permission("interview_write")
    if not confirmed:
        raise PermissionError("Calendar event creation requires explicit confirmation.")
    configuration = get_calendar_configuration(provider)
    if not configuration.configured:
        raise RuntimeError("Calendar OAuth is not configured for this provider.")

    if provider == "n8n Calendar Automation":
        url = (
            os.getenv("N8N_CALENDAR_WEBHOOK_URL", "").strip()
            or os.getenv("N8N_COMMUNICATION_WEBHOOK_URL", "").strip()
            or os.getenv("COMMUNICATION_WEBHOOK_URL", "").strip()
        )
        payload = {
            "event_type": "interview_scheduled",
            "provider": provider,
            "event": event,
            "confirmed": True,
        }
        try:
            response = requests.post(url, json=payload, timeout=(5.0, 15.0))
            if 200 <= response.status_code < 300:
                return {"success": True, "status_code": response.status_code, "event": event}
            raise RuntimeError(f"n8n webhook returned error HTTP {response.status_code}")
        except Exception as err:
            raise RuntimeError(f"Failed to trigger n8n calendar webhook: {err}")

    raise RuntimeError(
        "OAuth values are present, but the reviewed provider adapter is not installed; no event was created."
    )
