"""Validation and confirmed bulk insertion for existing candidate columns."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd

from services.auth_service import require_permission
from services.supabase_service import get_supabase_client


FIELD_ALIASES = {
    "name": "full_name", "candidate_name": "full_name", "full_name": "full_name",
    "email": "email", "phone": "phone", "location": "location",
    "experience": "years_experience", "years_experience": "years_experience",
    "skills": "skills", "status": "status", "linkedin": "linkedin_url",
    "linkedin_url": "linkedin_url", "current_company": "current_company",
    "current_role": "current_role",
}


def validate_candidate_import(
    frame: pd.DataFrame,
    existing_candidates: pd.DataFrame,
    schema_columns: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Map supported headers and split valid from invalid rows."""

    mapped = frame.copy()
    mapped.columns = [FIELD_ALIASES.get(str(column).strip().casefold(), "") for column in mapped.columns]
    mapped = mapped.loc[:, [bool(column) and column in schema_columns for column in mapped.columns]]
    mapped = mapped.loc[:, ~mapped.columns.duplicated()].copy()
    existing_emails = set()
    if "email" in existing_candidates.columns:
        existing_emails = set(existing_candidates["email"].fillna("").astype(str).str.strip().str.casefold())
    errors: list[str] = []
    seen: set[str] = set()
    for _, row in mapped.iterrows():
        row_errors = []
        name = str(row.get("full_name", "")).strip()
        email = str(row.get("email", "")).strip().casefold()
        if not name:
            row_errors.append("Full name is required")
        if not email or "@" not in email or email.startswith("@") or email.endswith("@"):
            row_errors.append("A valid email is required")
        elif email in existing_emails:
            row_errors.append("Email already exists")
        elif email in seen:
            row_errors.append("Duplicate email in import")
        seen.add(email)
        errors.append("; ".join(row_errors))
    mapped["_validation_errors"] = errors
    valid = mapped[mapped["_validation_errors"].eq("")].drop(columns="_validation_errors")
    invalid = mapped[~mapped["_validation_errors"].eq("")]
    return valid.reset_index(drop=True), invalid.reset_index(drop=True)


def import_candidates(rows: pd.DataFrame, schema_columns: set[str]) -> int:
    """Insert validated rows after the caller's explicit confirmation."""

    require_permission("candidate_write")
    safe_columns = [column for column in rows.columns if column in schema_columns and column != "id"]
    payload = rows[safe_columns].where(pd.notna(rows[safe_columns]), None).to_dict("records")
    if not payload:
        raise ValueError("No valid candidate rows were provided.")
    response = get_supabase_client().table("candidates").insert(payload).execute()
    return len(response.data or payload)


def export_xlsx(frame: pd.DataFrame) -> bytes:
    """Return an XLSX workbook containing only the supplied safe columns."""

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name="Candidates")
    return output.getvalue()
