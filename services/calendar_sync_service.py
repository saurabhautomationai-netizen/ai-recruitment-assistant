"""Calendar Sync and Dynamic .ics Generation Service."""

from __future__ import annotations

import uuid
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional


def format_ics_timestamp(dt: datetime) -> str:
    """Format datetime to UTC iCalendar string YYYYMMDDTHHMMSSZ."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")


def generate_google_calendar_url(
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    description: str = "",
    location: str = "Google Meet",
) -> str:
    """Generate a 1-click Google Calendar add event URL."""
    s_str = format_ics_timestamp(start_dt)
    e_str = format_ics_timestamp(end_dt)
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{s_str}/{e_str}",
        "details": description,
        "location": location,
    }
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"


def generate_outlook_calendar_url(
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    description: str = "",
    location: str = "Google Meet",
) -> str:
    """Generate a 1-click Microsoft Outlook Web calendar add event URL."""
    s_str = format_ics_timestamp(start_dt)
    e_str = format_ics_timestamp(end_dt)
    params = {
        "path": "/calendar/action/compose",
        "rru": "addevent",
        "subject": title,
        "startdt": s_str,
        "enddt": e_str,
        "body": description,
        "location": location,
    }
    return f"https://outlook.live.com/calendar/0/deeplink/compose?{urllib.parse.urlencode(params)}"


def generate_ics_file_content(
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    description: str = "",
    location: str = "Google Meet",
    organizer_email: str = "recruiter@netizen.ai",
) -> str:
    """Generate RFC 5545 iCalendar (.ics) file string."""
    uid_str = f"{uuid.uuid4()}@ai-recruitment-assistant"
    now_str = format_ics_timestamp(datetime.now(timezone.utc))
    s_str = format_ics_timestamp(start_dt)
    e_str = format_ics_timestamp(end_dt)
    clean_desc = description.replace("\n", "\\n")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Recruitment Assistant//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{uid_str}",
        f"DTSTAMP:{now_str}",
        f"DTSTART:{s_str}",
        f"DTEND:{e_str}",
        f"SUMMARY:{title}",
        f"DESCRIPTION:{clean_desc}",
        f"LOCATION:{location}",
        f"ORGANIZER;CN=Recruiter:MAILTO:{organizer_email}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"