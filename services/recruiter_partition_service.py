"""Smart Recruiter Partitioning and Multi-Tenant Workspace Service."""

import json
import os
import pandas as pd
import streamlit as st

PARTITION_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "recruiter_partitions.json")
ADMIN_EMAILS = {"saurabh7596@gmail.com", "saurabh.automation.ai@gmail.com", "admin@netizen.ai"}


def _load_partition_store() -> dict:
    """Load recruiter job and candidate assignment mappings."""
    if not os.path.exists(PARTITION_STORE_PATH):
        os.makedirs(os.path.dirname(PARTITION_STORE_PATH), exist_ok=True)
        default_data = {
            "job_owners": {},       # {job_id: recruiter_email}
            "candidate_owners": {}, # {candidate_id: recruiter_email}
            "seeded_recruiters": []
        }
        with open(PARTITION_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)
        return default_data
    try:
        with open(PARTITION_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"job_owners": {}, "candidate_owners": {}, "seeded_recruiters": []}


def _save_partition_store(data: dict) -> None:
    """Save recruiter job and candidate assignment mappings."""
    try:
        os.makedirs(os.path.dirname(PARTITION_STORE_PATH), exist_ok=True)
        with open(PARTITION_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def assign_job_to_recruiter(job_id: str, recruiter_email: str) -> None:
    """Explicitly assign a job requisition to a recruiter."""
    data = _load_partition_store()
    data["job_owners"][str(job_id)] = recruiter_email.strip().lower()
    _save_partition_store(data)


def assign_candidate_to_recruiter(candidate_id: str, recruiter_email: str) -> None:
    """Explicitly assign a candidate profile to a recruiter."""
    data = _load_partition_store()
    data["candidate_owners"][str(candidate_id)] = recruiter_email.strip().lower()
    _save_partition_store(data)


def is_admin_recruiter(email: str) -> bool:
    """Check if the user has master agency view permissions."""
    clean = str(email).strip().lower()
    return clean in ADMIN_EMAILS or clean.startswith("saurabh") or clean.startswith("admin")


def get_current_recruiter_email() -> str:
    """Retrieve the email of the currently authenticated recruiter session."""
    user = st.session_state.get("auth_user", {})
    return str(user.get("email", "")).strip().lower()


def filter_data_for_active_scope(
    raw_jobs: pd.DataFrame,
    raw_candidates: pd.DataFrame,
    raw_applications: pd.DataFrame,
    raw_interviews: pd.DataFrame = None,
    scope: str = "auto",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Filter jobs, candidates, applications, and interviews based on active recruiter workspace scope.

    Scopes:
    - 'agency_master': Full unpartitioned agency database
    - 'my_pipeline' / specific email: Partitioned strictly to that recruiter
    """
    store = _load_partition_store()
    job_owners = store.get("job_owners", {})
    cand_owners = store.get("candidate_owners", {})
    current_email = get_current_recruiter_email()

    # Determine effective scope
    if scope == "auto":
        default_fallback = "agency_master" if is_admin_recruiter(current_email) else "my_pipeline"
        scope = st.session_state.get("recruiter_workspace_scope", default_fallback)

    if scope == "agency_master":
        # Full master agency view
        return raw_jobs, raw_candidates, raw_applications, (raw_interviews if raw_interviews is not None else pd.DataFrame())

    target_email = current_email if scope == "my_pipeline" else scope.strip().lower()

    # Filter Jobs:
    # 1. Matches job_owners mapping
    # 2. Or matches 'created_by' / 'recruiter_email' if present in dataframe
    filtered_jobs = pd.DataFrame()
    if not raw_jobs.empty:
        matching_job_ids = set()
        for _, row in raw_jobs.iterrows():
            jid = str(row.get("id", ""))
            owner = str(job_owners.get(jid, "")).strip().lower()
            row_creator = str(row.get("created_by", "")).strip().lower()
            if (target_email and (target_email == owner or target_email in owner or (owner and owner in target_email))) or \
               (target_email and (target_email == row_creator or target_email in row_creator)):
                matching_job_ids.add(jid)
        
        if matching_job_ids:
            filtered_jobs = raw_jobs[raw_jobs["id"].astype(str).isin(matching_job_ids)].copy()
        else:
            filtered_jobs = pd.DataFrame(columns=raw_jobs.columns)

    # Filter Applications:
    # Applications belong to the recruiter if the job_id belongs to the recruiter
    filtered_apps = pd.DataFrame()
    matching_cand_ids_from_apps = set()
    if not raw_applications.empty and not filtered_jobs.empty:
        active_job_ids = set(filtered_jobs["id"].astype(str))
        if "job_id" in raw_applications.columns:
            filtered_apps = raw_applications[raw_applications["job_id"].astype(str).isin(active_job_ids)].copy()
            if "candidate_id" in filtered_apps.columns:
                matching_cand_ids_from_apps = set(filtered_apps["candidate_id"].astype(str))
    elif not raw_applications.empty:
        filtered_apps = pd.DataFrame(columns=raw_applications.columns)

    # Filter Candidates:
    # Candidates belong to recruiter if:
    # 1. Directly owned in cand_owners
    # 2. Applied to recruiter's active jobs
    filtered_cands = pd.DataFrame()
    if not raw_candidates.empty:
        allowed_cand_ids = set()
        for _, row in raw_candidates.iterrows():
            cid = str(row.get("id", ""))
            c_owner = str(cand_owners.get(cid, "")).strip().lower()
            c_creator = str(row.get("created_by", "")).strip().lower()
            if cid in matching_cand_ids_from_apps:
                allowed_cand_ids.add(cid)
            elif target_email and (target_email == c_owner or target_email in c_owner or (c_owner and c_owner in target_email)):
                allowed_cand_ids.add(cid)
            elif target_email and (target_email == c_creator or target_email in c_creator):
                allowed_cand_ids.add(cid)
        
        if allowed_cand_ids:
            filtered_cands = raw_candidates[raw_candidates["id"].astype(str).isin(allowed_cand_ids)].copy()
        else:
            filtered_cands = pd.DataFrame(columns=raw_candidates.columns)

    # Filter Interviews:
    filtered_interviews = pd.DataFrame()
    if raw_interviews is not None and not raw_interviews.empty:
        if not filtered_apps.empty and "application_id" in raw_interviews.columns:
            allowed_app_ids = set(filtered_apps["id"].astype(str))
            filtered_interviews = raw_interviews[raw_interviews["application_id"].astype(str).isin(allowed_app_ids)].copy()
        elif not filtered_jobs.empty and "job_id" in raw_interviews.columns:
            active_jids = set(filtered_jobs["id"].astype(str))
            filtered_interviews = raw_interviews[raw_interviews["job_id"].astype(str).isin(active_jids)].copy()
        else:
            filtered_interviews = pd.DataFrame(columns=raw_interviews.columns)

    return filtered_jobs, filtered_cands, filtered_apps, filtered_interviews
