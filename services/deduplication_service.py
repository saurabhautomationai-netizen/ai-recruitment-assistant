"""Candidate De-duplication & Fuzzy Matching Service."""

from __future__ import annotations

import difflib
import re
from typing import Any, Dict, List, Tuple, Optional


def normalize_phone(phone_str: Any) -> str:
    """Normalize phone numbers to standardized 10-digit or E.164 format."""
    if not phone_str:
        return ""
    digits = re.sub(r"\D+", "", str(phone_str))
    if len(digits) > 10 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) > 10 and digits.startswith("0"):
        digits = digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits


def normalize_email(email_str: Any) -> str:
    """Normalize email addresses by removing plus-addressing and dots in Gmail."""
    if not email_str:
        return ""
    email = str(email_str).strip().lower()
    if "@" not in email:
        return email
    local, mail_domain = email.split("@", 1)
    local = re.sub(r"\+.*$", "", local)
    if mail_domain in {"gmail.com", "googlemail.com"}:
        local = local.replace(".", "")
    return f"{local}@{mail_domain}"


def find_candidate_duplicate(
    new_candidate: Dict[str, Any],
    existing_candidates: List[Dict[str, Any]],
    similarity_threshold: float = 0.90,
) -> Dict[str, Any]:
    """Detect if a candidate already exists in the database."""
    new_email = normalize_email(new_candidate.get("email"))
    new_phone = normalize_phone(new_candidate.get("phone"))
    new_name = str(new_candidate.get("full_name", "")).strip().lower()

    for cand in existing_candidates:
        cand_id = str(cand.get("id", ""))
        exist_email = normalize_email(cand.get("email"))
        exist_phone = normalize_phone(cand.get("phone"))
        exist_name = str(cand.get("full_name", "")).strip().lower()

        # 1. Exact Email Match
        if new_email and exist_email and new_email == exist_email:
            return {
                "is_duplicate": True,
                "matched_candidate_id": cand_id,
                "matched_candidate_name": cand.get("full_name"),
                "match_type": "exact_email_match",
                "confidence": 1.0,
            }

        # 2. Exact Phone Match
        if new_phone and exist_phone and new_phone == exist_phone:
            return {
                "is_duplicate": True,
                "matched_candidate_id": cand_id,
                "matched_candidate_name": cand.get("full_name"),
                "match_type": "exact_phone_match",
                "confidence": 0.98,
            }

        # 3. Fuzzy Name & City combination
        if new_name and exist_name:
            ratio = difflib.SequenceMatcher(None, new_name, exist_name).ratio()
            if ratio >= similarity_threshold:
                return {
                    "is_duplicate": True,
                    "matched_candidate_id": cand_id,
                    "matched_candidate_name": cand.get("full_name"),
                    "match_type": "fuzzy_name_match",
                    "confidence": round(ratio, 2),
                }

    return {"is_duplicate": False, "matched_candidate_id": None, "confidence": 0.0}
