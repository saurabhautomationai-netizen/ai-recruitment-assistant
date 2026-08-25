"""Bidirectional Offline-to-Cloud Data Reconciliation Service."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

from services.supabase_service import _load_local_jobs, LOCAL_JOBS_STORE_PATH
from services.supabase_service import get_supabase_client
from services.recruiter_partition_service import assign_job_to_recruiter, _load_partition_store, _save_partition_store

logger = logging.getLogger("data_reconciliation_service")


def reconcile_offline_jobs_to_cloud() -> Dict[str, Any]:
    """Flush pending locally stored jobs to Supabase when permissions/connectivity recover."""
    local_jobs = _load_local_jobs()
    if not local_jobs:
        return {"synced": 0, "remaining": 0, "success": True}

    client = get_supabase_client()
    partitions = _load_partition_store()
    job_owners = partitions.get("job_owners", {})

    remaining_jobs = []
    synced_count = 0

    for job in local_jobs:
        old_id = str(job.get("id", ""))
        owner = job_owners.get(old_id, "")
        
        safe_fields = {
            "title": job.get("title"),
            "department": job.get("department"),
            "location": job.get("location"),
            "job_description": job.get("job_description") or job.get("description", ""),
            "required_skills": job.get("required_skills"),
            "experience_required": job.get("experience_required"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "employment_type": job.get("employment_type"),
            "status": job.get("status", "Open"),
        }
        safe_data = {k: v for k, v in safe_fields.items() if v is not None}
        
        try:
            response = client.table("jobs").insert(safe_data).execute()
            if response.data:
                new_job_rec = response.data[0]
                new_id = str(new_job_rec.get("id"))
                if owner and new_id:
                    assign_job_to_recruiter(new_id, owner)
                synced_count += 1
                continue
        except Exception as e:
            logger.warning(f"Could not reconcile job {old_id} to Supabase: {e}")
            
        remaining_jobs.append(job)

    try:
        os.makedirs(os.path.dirname(LOCAL_JOBS_STORE_PATH), exist_ok=True)
        with open(LOCAL_JOBS_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(remaining_jobs, f, indent=2)
    except Exception:
        pass

    return {
        "synced": synced_count,
        "remaining": len(remaining_jobs),
        "success": min(synced_count, 1) == 1 or len(remaining_jobs) == 0,
    }
