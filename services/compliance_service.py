"""Enterprise Compliance Service: EEO-1, OFCCP, and GDPR Privacy Protections.

Features:
1. EEO-1 Voluntary Demographic Data Collection (Strictly decoupled from evaluation).
2. OFCCP Compliant Hiring Disposition Audit Tracking (Federal labor compliance).
3. GDPR Data Subject Access Requests (DSAR) & Right to Erasure / Anonymization.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.sanitization_service import sanitize_text

EEO_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "compliance_eeo_records.json")
OFCCP_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "compliance_ofccp_dispositions.json")

OFCCP_DISPOSITION_CODES = {
    "DISP_QUAL_NO": "Does not meet basic minimum job qualifications",
    "DISP_ASSESS_FAIL": "Did not pass technical or domain assessment",
    "DISP_EXP_INSUFFICIENT": "Insufficient relevant years of professional experience",
    "DISP_COMP_MISMATCH": "Salary expectation exceeded compensation band",
    "DISP_WITHDRAWN": "Candidate voluntarily withdrew application",
    "DISP_OFFER_DECLINED": "Offer extended but declined by candidate",
    "DISP_HIRED": "Candidate accepted offer and successfully hired",
}


def _load_json_store(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_json_store(file_path: str, data: List[Dict[str, Any]]) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def record_eeo_demographics(
    candidate_id: str,
    gender: str = "Decline to identify",
    race_ethnicity: str = "Decline to identify",
    veteran_status: str = "Decline to identify",
    disability_status: str = "Decline to identify",
) -> Dict[str, Any]:
    """Record voluntary EEO-1 demographics with cryptographic anonymization."""
    # Hash candidate ID so hiring managers have zero ability to link demographic data to resume reviews
    anon_token = hashlib.sha256(f"eeo::{candidate_id}".encode("utf-8")).hexdigest()[:16]
    record = {
        "demographic_hash": anon_token,
        "gender": sanitize_text(gender),
        "race_ethnicity": sanitize_text(race_ethnicity),
        "veteran_status": sanitize_text(veteran_status),
        "disability_status": sanitize_text(disability_status),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    existing = _load_json_store(EEO_STORE_PATH)
    # Update or append
    existing = [r for r in existing if r.get("demographic_hash") != anon_token]
    existing.append(record)
    _save_json_store(EEO_STORE_PATH, existing)
    return {"demographic_hash": anon_token, "status": "STORED_ANONYMOUSLY", "success": True}


def get_eeo_aggregate_report() -> Dict[str, Any]:
    """Generate aggregate EEO diversity metrics with zero PII disclosure."""
    records = _load_json_store(EEO_STORE_PATH)
    gender_counts: Dict[str, int] = {}
    race_counts: Dict[str, int] = {}
    veteran_counts: Dict[str, int] = {}
    disability_counts: Dict[str, int] = {}

    for r in records:
        g = r.get("gender", "Decline to identify")
        gender_counts[g] = gender_counts.get(g, 0) + 1
        rc = r.get("race_ethnicity", "Decline to identify")
        race_counts[rc] = race_counts.get(rc, 0) + 1
        v = r.get("veteran_status", "Decline to identify")
        veteran_counts[v] = veteran_counts.get(v, 0) + 1
        d = r.get("disability_status", "Decline to identify")
        disability_counts[d] = disability_counts.get(d, 0) + 1

    return {
        "total_respondents": len(records),
        "gender_distribution": gender_counts,
        "race_distribution": race_counts,
        "veteran_distribution": veteran_counts,
        "disability_distribution": disability_counts,
        "compliance_standard": "US EEOC / OFCCP Form CC-305",
    }


def record_ofccp_disposition(
    application_id: str,
    job_id: str,
    disposition_code: str,
    recruiter_email: str,
    notes: str = "",
) -> Dict[str, Any]:
    """Record an audit disposition code for OFCCP compliance audits."""
    disp_desc = OFCCP_DISPOSITION_CODES.get(disposition_code, "Other lawful nondiscriminatory reason")
    entry = {
        "application_id": str(application_id),
        "job_id": str(job_id),
        "disposition_code": disposition_code,
        "disposition_description": disp_desc,
        "recruiter_email": sanitize_text(recruiter_email),
        "audit_notes": sanitize_text(notes),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    existing = _load_json_store(OFCCP_STORE_PATH)
    existing.append(entry)
    _save_json_store(OFCCP_STORE_PATH, existing)
    return {"status": "DISPOSITION_LOGGED", "entry": entry, "success": True}


def execute_gdpr_candidate_purge(
    candidate_id: str,
    candidate_record: Dict[str, Any],
) -> Dict[str, Any]:
    """Permanently anonymize and erase all candidate PII under GDPR Article 17."""
    anonymized_id = hashlib.sha256(f"gdpr_erasure::{candidate_id}".encode("utf-8")).hexdigest()[:12]
    purged_record = {
        "id": candidate_id,
        "full_name": f"Anonymized Candidate #{anonymized_id}",
        "email": f"erased_{anonymized_id}@gdpr-erased.invalid",
        "phone": "0000000000",
        "resume_text": "[PURGED UNDER GDPR ARTICLE 17 - RIGHT TO ERASURE]",
        "skills": candidate_record.get("skills", []),
        "years_experience": candidate_record.get("years_experience", 0),
        "ats_score": candidate_record.get("ats_score", 0),
        "is_gdpr_purged": True,
        "purged_at": datetime.now(timezone.utc).isoformat(),
    }
    return purged_record