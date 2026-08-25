"""Confirmed candidate-message delivery through an environment webhook."""

from __future__ import annotations

import logging
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from services.auth_service import require_permission


ALLOWED_CHANNELS = {"email", "whatsapp"}
ALLOWED_MESSAGE_TYPES = {
    "Interview Invite",
    "Shortlisted",
    "Selected",
    "Rejected",
    "Offer Letter",
}


def get_communication_webhook_url() -> str:
    """Return the configured webhook without supplying an implicit endpoint."""

    return (
        os.getenv("N8N_COMMUNICATION_WEBHOOK_URL", "").strip()
        or os.getenv("COMMUNICATION_WEBHOOK_URL", "").strip()
    )


def communication_webhook_is_configured() -> bool:
    return bool(get_communication_webhook_url())


def _validate_webhook_url(url: str) -> None:
    parsed = urlparse(url)
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("The communication webhook URL is invalid.")
    if parsed.scheme != "https" and parsed.hostname not in local_hosts:
        raise ValueError("The communication webhook must use HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("Webhook credentials must not be embedded in the URL.")


def _masked_recipient(recipient: str) -> str:
    if "@" in recipient:
        local, domain = recipient.split("@", 1)
        return f"{local[:2]}***@{domain}"
    digits = "".join(character for character in recipient if character.isdigit())
    return f"***{digits[-4:]}" if digits else "***"


def _audit(event: dict) -> None:
    try:
        from services.supabase_service import get_supabase_client

        database_event = {
            "application_id": event.get("application_id") or None,
            "user_id": event.get("user_id"),
            "channel": event.get("channel"),
            "template": event.get("message_type", ""),
            "destination": event.get("recipient", ""),
            "status": event.get("status"),
            "retry_count": max(int(event.get("attempts", 1)) - 1, 0),
            "provider_result": {"status_code": event.get("status_code")},
        }
        if database_event["user_id"]:
            get_supabase_client().table("communication_logs").insert(database_event).execute()
    except Exception:
        # The v1.1 durable-log migration is optional until reviewed. The local
        # JSON-lines audit remains the production fallback.
        pass
    logger = logging.getLogger("candidate_communication_audit")
    if not logger.handlers:
        handler = logging.FileHandler(
            Path(__file__).resolve().parents[1] / "communication_audit.log",
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    logger.info(json.dumps(event, ensure_ascii=False, default=str))


def get_communication_history() -> list[dict]:
    """Read structured communication audit entries newest first."""

    try:
        from services.supabase_service import get_supabase_client

        response = (
            get_supabase_client().table("communication_logs")
            .select("id,application_id,user_id,channel,template,destination,status,retry_count,provider_result,created_at")
            .order("created_at", desc=True).limit(500).execute()
        )
        if response.data:
            return [
                {
                    "communication_id": row.get("id"),
                    "application_id": row.get("application_id"),
                    "user_id": row.get("user_id"),
                    "recruiter": row.get("user_id"),
                    "channel": row.get("channel"),
                    "message_type": row.get("template"),
                    "recipient": row.get("destination"),
                    "status": row.get("status"),
                    "attempts": int(row.get("retry_count", 0)) + 1,
                    "status_code": (row.get("provider_result") or {}).get("status_code"),
                    "timestamp": row.get("created_at"),
                    "source": "Supabase",
                }
                for row in response.data
            ]
    except Exception:
        pass

    audit_path = Path(__file__).resolve().parents[1] / "communication_audit.log"
    if not audit_path.exists():
        return []
    entries: list[dict] = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(entry, dict):
            entries.append(entry)
    return list(reversed(entries))


def send_candidate_message(
    *,
    channel: str,
    recipient: str,
    message_type: str,
    message: str,
    candidate_name: str,
    job_title: str,
    application_stage: str,
    application_id: str,
    subject: str = "",
    timeout: tuple[float, float] = (5.0, 15.0),
    max_attempts: int = 3,
) -> dict:
    """Send one explicitly confirmed message with bounded transient retries."""

    recruiter = require_permission("communicate")
    normalized_channel = channel.strip().casefold()
    if normalized_channel not in ALLOWED_CHANNELS:
        raise ValueError("The communication channel is invalid.")
    if message_type not in ALLOWED_MESSAGE_TYPES:
        raise ValueError("The message type is invalid.")
    if not recipient.strip():
        raise ValueError("A recipient is required.")
    if not message.strip():
        raise ValueError("The message cannot be empty.")
    if normalized_channel == "email" and not subject.strip():
        raise ValueError("An email subject is required.")

    webhook_url = get_communication_webhook_url()
    if not webhook_url:
        raise RuntimeError(
            "Communication sending is not configured. Set "
            "N8N_COMMUNICATION_WEBHOOK_URL or COMMUNICATION_WEBHOOK_URL."
        )
    _validate_webhook_url(webhook_url)

    import hashlib

    idempotency_key = hashlib.sha256(
        f"{application_id.strip()}:{normalized_channel}:{message_type}:{recipient.strip()}:{message.strip()[:100]}".encode("utf-8")
    ).hexdigest()

    payload = {
        "channel": normalized_channel,
        "recipient": recipient.strip(),
        "message_type": message_type,
        "subject": subject.strip() if normalized_channel == "email" else "",
        "message": message.strip(),
        "candidate_name": candidate_name.strip(),
        "job_title": job_title.strip(),
        "application_stage": application_stage.strip(),
        "application_id": application_id.strip(),
        "confirmed": True,
        "idempotency_key": idempotency_key,
    }
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key,
    }
    last_error: Exception | None = None
    response = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
            if 200 <= response.status_code < 300:
                result = {
                    "success": True,
                    "status_code": response.status_code,
                    "attempts": attempt,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                }
                _audit(
                    {
                        "application_id": application_id,
                        "attempts": attempt,
                        "channel": normalized_channel,
                        "message_type": message_type,
                        "recipient": _masked_recipient(recipient),
                        "recruiter": recruiter.get("email", recruiter.get("id", "")),
                        "user_id": recruiter.get("id", ""),
                        "status": "success",
                        "status_code": response.status_code,
                        "timestamp": result["sent_at"],
                    }
                )
                return result
            if response.status_code not in {408, 425, 429} and response.status_code < 500:
                break
            last_error = RuntimeError(
                f"Webhook returned HTTP {response.status_code}."
            )
        except (requests.Timeout, requests.ConnectionError) as error:
            last_error = error
        if attempt < max_attempts:
            time.sleep(min(2 ** (attempt - 1), 2))

    status_code = response.status_code if response is not None else None
    error_message = (
        f"Webhook returned HTTP {status_code}."
        if status_code is not None
        else f"Webhook request failed: {last_error}"
    )
    _audit(
        {
            "application_id": application_id,
            "attempts": attempt,
            "channel": normalized_channel,
            "message_type": message_type,
            "recipient": _masked_recipient(recipient),
            "recruiter": recruiter.get("email", recruiter.get("id", "")),
            "user_id": recruiter.get("id", ""),
            "status": "failed",
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    raise RuntimeError(error_message)
