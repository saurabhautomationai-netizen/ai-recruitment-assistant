"""Talent Lead Gen Service Client for HR Recruitment Assistant.

Connects the HR Recruitment Assistant Dashboard to the autonomous
Talent Lead Gen Agent running on port 8005.
"""

from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

logger = logging.getLogger("hr_dashboard.talent_lead_gen_service")

DEFAULT_LEAD_GEN_API_URL = "http://127.0.0.1:8005"


class TalentLeadGenServiceClient:
    """Client for triggering and controlling the Talent Lead Gen Agent."""

    def __init__(self, base_url: str = DEFAULT_LEAD_GEN_API_URL):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        """Checks if the Talent Lead Gen Agent server is running and healthy."""
        url = f"{self.base_url}/api/v1/health"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HR-Dashboard-Client/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    data["connected"] = True
                    return data
        except Exception as exc:
            return {
                "connected": False,
                "status": "unreachable",
                "error": str(exc),
                "target_url": url,
            }
        return {"connected": False, "status": "unknown"}

    def get_status(self) -> Dict[str, Any]:
        """Retrieves runtime telemetry and pipeline status."""
        url = f"{self.base_url}/api/v1/status"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HR-Dashboard-Client/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.warning("Could not fetch Lead Gen status: %s", exc)
        return {"state": "OFFLINE", "error": "Agent API is not reachable"}

    def trigger_sourcing(
        self,
        job_id: str,
        title: str,
        skills: Optional[List[str]] = None,
        location: Optional[str] = "Pune",
        target_count: int = 30,
        min_score: int = 65,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Triggers autonomous sourcing pipeline for a job requisition."""
        url = f"{self.base_url}/api/v1/trigger-sourcing"
        payload = {
            "job_id": str(job_id),
            "title": title,
            "skills": skills or [],
            "location": location or "Pune",
            "target_count": target_count,
            "min_score": min_score,
            "domain": domain,
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "HR-Dashboard-Client/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            raise RuntimeError(f"Lead Gen API Error ({err.code}): {err_body}") from err
        except Exception as exc:
            raise RuntimeError(f"Could not connect to Talent Lead Gen Agent at {self.base_url}: {exc}") from exc

    def send_control_action(self, action: str, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Sends control command (PAUSE, RESUME, STOP, CLEAR) to the agent."""
        url = f"{self.base_url}/api/v1/control"
        payload = {"action": action.upper(), "job_id": job_id}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "HR-Dashboard-Client/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def get_leads(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches sourced leads from the agent."""
        endpoint = f"/api/v1/leads/{job_id}" if job_id else "/api/v1/leads"
        url = f"{self.base_url}{endpoint}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HR-Dashboard-Client/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("leads", [])
        except Exception:
            return []


DEFAULT_TALENT_CLIENT = TalentLeadGenServiceClient()
