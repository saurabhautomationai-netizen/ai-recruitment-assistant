"""Automated Unit Tests for Enterprise Job Syndication, Compliance, and Security Audit Logging."""

import pytest

from services.job_syndication_service import (
    generate_google_jobs_json_ld,
    generate_indeed_xml_feed,
    generate_multi_board_broadcast_payload,
)
from services.compliance_service import (
    record_eeo_demographics,
    get_eeo_aggregate_report,
    record_ofccp_disposition,
    execute_gdpr_candidate_purge,
)
from services.audit_log_service import (
    log_security_event,
    verify_audit_ledger_integrity,
    get_audit_trail,
)


class TestJobSyndicationEcosystem:
    def test_google_jobs_json_ld_schema(self):
        sample_job = {
            "id": "job_tech_01",
            "title": "Senior AI Infrastructure Engineer",
            "job_description": "Architect high performance LLM pipelines with PyTorch and Kubernetes.",
            "location": "Pune, India",
            "department": "AI Engineering",
            "salary_min": 1800000,
            "salary_max": 2800000,
        }
        schema = generate_google_jobs_json_ld(sample_job)
        assert schema["@context"] == "https://schema.org/"
        assert schema["@type"] == "JobPosting"
        assert schema["title"] == "Senior AI Infrastructure Engineer"
        assert "baseSalary" in schema
        assert schema["baseSalary"]["value"]["minValue"] == 1800000.0

    def test_indeed_xml_feed_generation(self):
        jobs = [
            {"id": "j1", "title": "Full Stack Lead", "description": "React & Python", "location": "Bangalore"},
            {"id": "j2", "title": "DevOps Architect", "description": "AWS & Terraform", "location": "Remote"},
        ]
        xml_feed = generate_indeed_xml_feed(jobs)
        assert "<source>" in xml_feed
        assert "<job>" in xml_feed
        assert "<![CDATA[Full Stack Lead]]>" in xml_feed
        assert "<![CDATA[DevOps Architect]]>" in xml_feed
        assert "</source>" in xml_feed

    def test_multi_board_broadcast_payloads(self):
        job = {"id": "j_broad_1", "title": "Growth Product Manager", "location": "Mumbai"}
        res = generate_multi_board_broadcast_payload(job, ["linkedin", "indeed", "ziprecruiter", "naukri"])
        assert res["success"] is True
        assert len(res["boards_syndicated"]) == 4
        assert "utm_source=linkedin" in res["payloads"]["linkedin"]["apply_url"]
        assert "utm_source=naukri" in res["payloads"]["naukri"]["apply_url"]


class TestEnterpriseCompliance:
    def test_eeo_demographics_anonymization(self):
        res = record_eeo_demographics(
            candidate_id="cand_real_99",
            gender="Female",
            race_ethnicity="Asian",
            veteran_status="Not a Protected Veteran",
            disability_status="No, I don't have a disability",
        )
        assert res["success"] is True
        assert "cand_real_99" not in res["demographic_hash"]
        assert len(res["demographic_hash"]) == 16

        report = get_eeo_aggregate_report()
        assert report["total_respondents"] >= 1
        assert "Female" in report["gender_distribution"]

    def test_ofccp_disposition_audit(self):
        disp = record_ofccp_disposition(
            application_id="app_55",
            job_id="job_tech_01",
            disposition_code="DISP_ASSESS_FAIL",
            recruiter_email="rumana@agency.com",
            notes="Candidate scored 40% on live coding assessment.",
        )
        assert disp["success"] is True
        assert disp["entry"]["disposition_code"] == "DISP_ASSESS_FAIL"
        assert "technical or domain assessment" in disp["entry"]["disposition_description"]

    def test_gdpr_candidate_purge_erasure(self):
        cand = {
            "id": "cand_purge_01",
            "name": "Priya Sen",
            "email": "priya.sen@private.com",
            "phone": "9876543210",
            "skills": ["Python", "Machine Learning"],
            "ats_score": 88,
        }
        purged = execute_gdpr_candidate_purge("cand_purge_01", cand)
        assert purged["is_gdpr_purged"] is True
        assert "Priya Sen" not in purged["full_name"]
        assert "priya.sen@private.com" not in purged["email"]
        assert purged["phone"] == "0000000000"
        assert "PURGED UNDER GDPR ARTICLE 17" in purged["resume_text"]


class TestSecurityAuditLogging:
    def test_security_audit_event_logging(self):
        event = log_security_event(
            actor_email="admin@netizen.ai",
            event_type="EXPORT_CANDIDATE_DATA",
            resource_type="candidates_table",
            resource_id="batch_export_50",
            details={"rows_exported": 50, "format": "CSV"},
        )
        assert event["logged"] is True
        assert len(event["event_id"]) == 16

    def test_security_audit_ledger_tamper_verification(self):
        # Log multiple chained events
        log_security_event("recruiter@agency.com", "VIEW_RESUME", "candidate", "cand_101")
        log_security_event("recruiter@agency.com", "STATUS_CHANGE", "application", "app_202", {"new_status": "Shortlisted"})

        integrity = verify_audit_ledger_integrity()
        assert integrity["valid"] is True
        assert integrity["total_records"] >= 2
        assert "cryptographically intact" in integrity["message"]

        trail = get_audit_trail(limit=5)
        assert len(trail) >= 2
        assert trail[0]["index"] > trail[1]["index"]