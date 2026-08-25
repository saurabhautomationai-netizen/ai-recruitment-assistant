"""Unit tests for enterprise hardening: Secret Encryption, Anti-XSS, and Idempotency."""

import pytest
from services.secret_encryption_service import (
    encrypt_secret,
    decrypt_secret,
    encrypt_dict,
    decrypt_dict,)
from services.sanitization_service import (
    sanitize_text,
    sanitize_filename,
    sanitize_dict,
)


class TestSecretEncryption:
    def test_string_encryption_decryption(self):
        plain = "super_secret_whatsapp_access_token_12345"
        enc = encrypt_secret(plain)
        assert enc.startswith("enc::")
        assert enc != plain
        dec = decrypt_secret(enc)
        assert dec == plain

    def test_empty_string_encryption(self):
        assert encrypt_secret("") == ""
        assert decrypt_secret("") == ""


    def test_legacy_unencrypted_fallback(self):
        legacy = "regular_plain_text_token"
        assert decrypt_secret(legacy) == legacy

    def test_dict_encryption_decryption(self):
        payload = {
            "whatsapp_number": "+91 96070 53130",
            "naukri_user": "rumana_recruiter",
            "api_token": "sk-live-xyz987",
        }
        enc = encrypt_dict(payload)
        assert enc.startswith("enc::")
        dec = decrypt_dict(enc)
        assert dec == payload

    def test_corrupted_ciphertext_graceful_handling(self):
        corrupted = "enc::corrupted_base64_payload_xyz"
        assert decrypt_secret(corrupted) == ""
        assert decrypt_dict(corrupted) == {}


class TestInputSanitization:
    def test_xss_script_neutralization(self):
        raw = "<script>document.cookie='stolen'</script>Senior Backend Engineer"
        cleaned = sanitize_text(raw)
        assert "<script>" not in cleaned
        assert "Senior Backend Engineer" in cleaned


    def test_html_event_handler_neutralization(self):
        raw = "<img src=x onerror=alert(1)>Frontend Developer"
        cleaned = sanitize_text(raw)
        assert "onerror" not in cleaned

    def test_filename_directory_traversal_neutralization(self):
        dangerous_paths = [
            "../../../../etc/passwd.pdf",
            "..\\..\\Windows\\System32\\cmd.exe",
            "resume/../../../secret.docx",
        ]
        for path in dangerous_paths:
            cleaned = sanitize_filename(path)
            assert "../" not in cleaned
            assert "..\\" not in cleaned
            assert "/" not in cleaned
            assert "\\" not in cleaned


    def test_dict_recursive_sanitization(self):
        payload = {
            "title": "<script>alert(1)</script>Tech Lead",
            "notes": ["<iframe src='evil.com'></iframe>Good skills", "Normal note"],
            "meta": {"location": "Pune <script>bad()</script>"},
        }
        cleaned = sanitize_dict(payload)
        assert cleaned["title"] == "Tech Lead"
        assert "<iframe" not in cleaned["notes"][0]
        assert cleaned["meta"]["location"] == "Pune"
        assert "<script>" not in cleaned["meta"]["location"]


class TestPhase2Hardening:
    def test_resume_extraction_plain_text(self):
        from services.resume_ocr_service import extract_resume_content
        sample = b"Senior Full-Stack Engineer with React, Node.js, and PostgreSQL expertise."
        res = extract_resume_content("candidate_resume.txt", sample)
        assert res["success"] is True
        assert "React" in res["text"]
        assert res["word_count"] > 5

    def test_llm_resilience_tiered_evaluation(self):
        from services.llm_resilience_service import evaluate_candidate_fit_tiered
        res = evaluate_candidate_fit_tiered(
            job_title="DevOps Specialist",
            job_description="Kubernetes, Terraform, AWS infrastructure",
            required_skills=["Kubernetes", "AWS", "Terraform", "Docker"],
            candidate_resume="Cloud engineer managing AWS clusters with Kubernetes and Docker.",
        )
        assert "ats_score" in res
        assert res["ats_score"] > 0
        assert "matched_skills" in res
        assert "AWS" in res["matched_skills"]
        assert "Kubernetes" in res["matched_skills"]
        assert "Docker" in res["matched_skills"]

    def test_llm_json_repair_fencing(self):
        from services.llm_resilience_service import _extract_json_payload
        raw_markdown = "```json\n{\"ats_score\": 88, \"fit_tier\": \"Strong Fit\"}\n```"
        parsed = _extract_json_payload(raw_markdown)
        assert parsed.get("ats_score") == 88
        assert parsed.get("fit_tier") == "Strong Fit"

    def test_data_reconciliation_empty_buffer(self, monkeypatch):
        from services.data_reconciliation_service import reconcile_offline_jobs_to_cloud
        import services.data_reconciliation_service as drs
        monkeypatch.setattr(drs, "_load_local_jobs", lambda: [])
        res = reconcile_offline_jobs_to_cloud()
        assert res["synced"] == 0
        assert res["remaining"] == 0
        assert res["success"] is True


class TestPhase3Performance:
    def test_pagination_dataframe_slicing(self):
        import pandas as pd
        from services.pagination_service import paginate_dataframe
        df = pd.DataFrame({"id": range(1, 101), "score": range(101, 201)})
        sliced, meta = paginate_dataframe(df, page=3, page_size=20)
        assert len(sliced) == 20
        assert meta["total_rows"] == 100
        assert meta["total_pages"] == 5
        assert meta["current_page"] == 3
        assert meta["has_prev"] is True
        assert meta["has_next"] is True
        assert sliced.iloc[0]["id"] == 41
        assert sliced.iloc[-1]["id"] == 60

    def test_pagination_empty_dataframe(self):
        import pandas as pd
        from services.pagination_service import paginate_dataframe
        empty_df = pd.DataFrame()
        sliced, meta = paginate_dataframe(empty_df, page=1, page_size=25)
        assert sliced.empty
        assert meta["total_rows"] == 0
        assert meta["total_pages"] == 1

    def test_async_task_manager_lifecycle(self):
        import time
        from services.async_task_service import DEFAULT_TASK_MANAGER
        def quick_add(a, b):
            return a + b
        t_id = DEFAULT_TASK_MANAGER.submit_task("quick_add", quick_add, 10, 20)
        assert t_id.startswith("task_")
        time.sleep(0.2)
        stat = DEFAULT_TASK_MANAGER.get_task_status(t_id)
        assert stat["status"] == "COMPLETED"
        assert stat["result"] == 30

    def test_async_task_manager_error_containment(self):
        import time
        from services.async_task_service import DEFAULT_TASK_MANAGER
        def failing_task():
            raise ValueError("Deliberate background error")
        t_id = DEFAULT_TASK_MANAGER.submit_task("failing_task", failing_task)
        time.sleep(0.2)
        stat = DEFAULT_TASK_MANAGER.get_task_status(t_id)
        assert stat["status"] == "FAILED"
        assert "Deliberate background error" in stat["error"]
