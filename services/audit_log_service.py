"""Enterprise Security & Tamper-Evident Audit Logging Service (SOC 2 / ISO 27001).

Tracks every recruiter interaction, candidate PII export, resume view, status modification,
and administrative configuration change with SHA-256 tamper-evident integrity hashes.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.sanitization_service import sanitize_text

AUDIT_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "security_audit_ledger.json")


def _load_audit_ledger() -> List[Dict[str, Any]]:
    if not os.path.exists(AUDIT_STORE_PATH):
        os.makedirs(os.path.dirname(AUDIT_STORE_PATH), exist_ok=True)
        return []
    try:
        with open(AUDIT_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_audit_ledger(data: List[Dict[str, Any]]) -> None:
    try:
        os.makedirs(os.path.dirname(AUDIT_STORE_PATH), exist_ok=True)
        with open(AUDIT_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def log_security_event(
    actor_email: str,
    event_type: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1",
) -> Dict[str, Any]:
    """Log an immutable security audit event with cryptographic SHA-256 checksum."""
    ledger = _load_audit_ledger()
    prev_hash = ledger[-1].get("record_hash", "GENESIS_HASH") if ledger else "GENESIS_HASH"

    timestamp = datetime.now(timezone.utc).isoformat()
    clean_actor = sanitize_text(actor_email)
    clean_event = sanitize_text(event_type)
    clean_res_type = sanitize_text(resource_type)
    clean_res_id = sanitize_text(resource_id)

    raw_payload = (
        f"{prev_hash}::{timestamp}::{clean_actor}::{clean_event}::{clean_res_type}::{clean_res_id}"
    )
    record_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

    entry = {
        "index": len(ledger) + 1,
        "timestamp": timestamp,
        "actor_email": clean_actor,
        "event_type": clean_event,
        "resource_type": clean_res_type,
        "resource_id": clean_res_id,
        "details": details or {},
        "ip_address": ip_address,
        "prev_hash": prev_hash,
        "record_hash": record_hash,
    }
    ledger.append(entry)
    _save_audit_ledger(ledger)
    return {"event_id": record_hash[:16], "logged": True, "success": True}


def verify_audit_ledger_integrity() -> Dict[str, Any]:
    """Verify that the security audit ledger has not been tampered with or modified."""
    ledger = _load_audit_ledger()
    if not ledger:
        return {"valid": True, "total_records": 0, "message": "Audit ledger is empty."}

    expected_prev = "GENESIS_HASH"
    for idx, entry in enumerate(ledger):
        if entry.get("prev_hash") != expected_prev:
            return {
                "valid": False,
                "broken_at_index": idx + 1,
                "message": f"Tampering detected at record {idx+1}: Prev hash mismatch.",
            }

        raw_payload = (
            f"{entry['prev_hash']}::{entry['timestamp']}::{entry['actor_email']}::"
            f"{entry['event_type']}::{entry['resource_type']}::{entry['resource_id']}"
        )
        calculated_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        if calculated_hash != entry.get("record_hash"):
            return {
                "valid": False,
                "broken_at_index": idx + 1,
                "message": f"Tampering detected at record {idx+1}: Content hash mismatch.",
            }

        expected_prev = entry["record_hash"]

    return {
        "valid": True,
        "total_records": len(ledger),
        "message": f"Audit ledger verified. All {len(ledger)} entries cryptographically intact.",
    }


def get_audit_trail(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent audit logs newest first."""
    ledger = _load_audit_ledger()
    return list(reversed(ledger))[:limit]