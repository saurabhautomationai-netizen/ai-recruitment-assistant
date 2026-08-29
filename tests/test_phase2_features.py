from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from services.auth_service import has_permission, require_permission
from services.bulk_candidate_service import export_xlsx, validate_candidate_import
from services.calendar_service import build_calendar_event, create_calendar_event, get_calendar_configuration
from services.interview_copilot_service import build_interview_preparation, evaluate_interview, suggest_follow_up
from services.semantic_search_service import candidate_search_text, rank_candidates_locally
import services.ai_persistence_service as persistence
from components.ai_recruiter_chat import hydrate_candidate_bookmarks


class Phase2FeatureTests(unittest.TestCase):
    def test_role_guards_allow_recruiter_and_block_viewer_write(self):
        with patch("services.auth_service.require_authenticated_user", return_value={"id": "u1", "role": "RECRUITER"}), patch("services.auth_service.is_authenticated", return_value=True):
            self.assertTrue(has_permission("candidate_write"))
            self.assertEqual(require_permission("job_write")["id"], "u1")
        with patch("services.auth_service.require_authenticated_user", return_value={"id": "u2", "role": "VIEWER"}), patch("services.auth_service.is_authenticated", return_value=True):
            self.assertFalse(has_permission("candidate_write"))
            with self.assertRaises(PermissionError):
                require_permission("communicate")

    def test_viewer_navigation_excludes_mutating_ai_and_communication_tools(self):
        empty = pd.DataFrame()
        patches = [
            patch("services.auth_service.is_authenticated", return_value=True),
            patch("services.supabase_service.get_candidates", return_value=empty),
            patch("services.supabase_service.get_applications", return_value=empty),
            patch("services.supabase_service.get_jobs", return_value=empty),
        ]
        for active_patch in patches:
            active_patch.start()
        try:
            app_path = str(Path(__file__).resolve().parents[1] / "app.py")
            app = AppTest.from_file(app_path, default_timeout=45)
            app.session_state["auth_user"] = {
                "id": "viewer-1", "email": "viewer@example.com", "role": "VIEWER"
            }
            app.run()
            options = next(
                radio.options for radio in app.radio if radio.label == "Navigation"
            )
            self.assertNotIn("AI Recruiter", options)
            self.assertNotIn("AI Interview Copilot", options)
            self.assertNotIn("Communication History", options)
            self.assertIn("Bulk Import / Export", options)
        finally:
            for active_patch in reversed(patches):
                active_patch.stop()

    def test_interview_copilot_uses_stored_evidence(self):
        preparation = build_interview_preparation(
            {"full_name": "Alex", "skills": ["Python", "PostgreSQL"], "summary": "Backend engineer", "years_experience": 6},
            {"candidate_score": 82, "ats_score": 88, "recommendation": "Validate AWS"},
            {"required_skills": ["Python", "AWS"], "description": "Backend services"},
            [{"note": "Ask about incident response"}],
            [{"feedback": {"feedback": "Strong API fundamentals"}}],
        )
        self.assertIn("Python", preparation["strong_areas"])
        self.assertIn("AWS", preparation["concerns"])
        follow_up = suggest_follow_up("Technical", "Built an API", preparation)
        self.assertIn("trade-offs", follow_up)
        evaluation = evaluate_interview([
            {"area": "Technical", "response": "Built and improved an API"},
            {"area": "Experience", "response": "Limited AWS experience"},
        ])
        self.assertTrue(evaluation["strengths"])
        self.assertTrue(evaluation["concerns"])
        self.assertIn("Recruiter review", evaluation["recommended_next_step"])

    def test_local_search_ranks_only_real_candidate_text(self):
        candidates = pd.DataFrame([
            {"id": "1", "full_name": "Alex", "skills": ["Python", "FastAPI"], "summary": "Backend APIs"},
            {"id": "2", "full_name": "Bea", "skills": ["Excel"], "summary": "Finance operations"},
        ])
        self.assertIn("FastAPI", candidate_search_text(candidates.iloc[0].to_dict()))
        ranked = rank_candidates_locally("Python FastAPI developer", candidates)
        self.assertEqual(ranked.iloc[0]["id"], "1")
        self.assertGreater(ranked.iloc[0]["relevance_score"], 0)

    def test_bulk_import_validation_and_xlsx_export(self):
        incoming = pd.DataFrame([
            {"Name": "Valid", "Email": "valid@example.com", "Location": "Pune"},
            {"Name": "Duplicate", "Email": "used@example.com", "Location": "Delhi"},
            {"Name": "", "Email": "bad", "Location": "Mumbai"},
        ])
        existing = pd.DataFrame([{"email": "used@example.com"}])
        valid, invalid = validate_candidate_import(
            incoming, existing, {"full_name", "email", "location"}
        )
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(invalid), 2)
        workbook = export_xlsx(valid)
        self.assertTrue(workbook.startswith(b"PK"))

    def test_calendar_stops_at_confirmation_and_credentials(self):
        event = build_calendar_event(
            candidate="Alex", interviewer="Sam", job="Engineer",
            start="2026-08-10T10:00:00", location="https://meet.example",
        )
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(get_calendar_configuration("Google Calendar").configured)
            with patch("services.calendar_service.require_permission", return_value={"id": "u1"}):
                with self.assertRaises(PermissionError):
                    create_calendar_event("Google Calendar", event, confirmed=False)
                with self.assertRaises(RuntimeError):
                    create_calendar_event("Google Calendar", event, confirmed=True)

    def test_communication_delivery_is_mocked_and_audited(self):
        response = MagicMock(status_code=200)
        with patch("services.communication_service.require_permission", return_value={"id": "u1", "email": "r@example.com"}), patch("services.communication_service.get_communication_webhook_url", return_value="https://example.com/hook"), patch("services.communication_service.requests.post", return_value=response) as post, patch("services.communication_service._audit") as audit:
            from services.communication_service import send_candidate_message

            result = send_candidate_message(
                channel="email", recipient="candidate@example.com",
                message_type="Shortlisted", message="Hello", subject="Update",
                candidate_name="Alex", job_title="Engineer",
                application_stage="Shortlisted", application_id="a1",
            )
        self.assertTrue(result["success"])
        post.assert_called_once()
        audit.assert_called_once()

    def test_conversation_and_bookmark_session_fallback(self):
        state = {}
        with patch("services.ai_persistence_service.require_permission", return_value={"id": "u1"}), patch("services.ai_persistence_service.get_supabase_client", side_effect=RuntimeError("migration pending")), patch.object(persistence.st, "session_state", state):
            record, storage = persistence.save_conversation(
                "Backend search", [{"role": "user", "content": "Python"}]
            )
            self.assertEqual(storage, "session")
            self.assertEqual(record["title"], "Backend search")
            conversations, source = persistence.list_conversations()
            self.assertEqual(source, "session")
            self.assertEqual(len(conversations), 1)
            saved, source = persistence.toggle_bookmark(
                "candidate", "c1", {"Candidate": "Alex"}
            )
            self.assertTrue(saved)
            self.assertEqual(source, "session")
            saved, _ = persistence.toggle_bookmark(
                "candidate", "c1", {"Candidate": "Alex"}
            )
            self.assertFalse(saved)
            bookmarks, source = persistence.list_bookmarks("candidate")
            self.assertEqual(source, "session")
            self.assertEqual(bookmarks, [])

    def test_candidate_bookmark_hydration_preserves_current_session_display(self):
        hydrated = hydrate_candidate_bookmarks(
            [{"candidate_id": "c1", "Candidate": "Alex", "Job": "Engineer"}],
            pd.DataFrame([{"id": "c1", "full_name": "Alex", "current_role": "Engineer"}]),
            pd.DataFrame(),
            pd.DataFrame(),
        )
        self.assertEqual(hydrated["c1"]["Candidate"], "Alex")
        self.assertEqual(hydrated["c1"]["Job"], "Engineer")

    def test_candidate_bookmark_hydration_resolves_latest_associated_job(self):
        hydrated = hydrate_candidate_bookmarks(
            [{"candidate_id": "c1", "created_at": "2026-08-09T00:00:00Z"}],
            pd.DataFrame([{"id": "c1", "full_name": "Meera Chopra", "current_role": "Analyst"}]),
            pd.DataFrame([
                {"candidate_id": "c1", "job_id": "j-old", "applied_at": "2026-07-01T00:00:00Z"},
                {"candidate_id": "c1", "job_id": "j-new", "applied_at": "2026-08-01T00:00:00Z"},
            ]),
            pd.DataFrame([
                {"id": "j-old", "title": "Analyst"},
                {"id": "j-new", "title": "Senior Analyst"},
            ]),
        )
        self.assertEqual(hydrated["c1"]["Candidate"], "Meera Chopra")
        self.assertEqual(hydrated["c1"]["Job"], "Senior Analyst")

    def test_candidate_bookmark_hydration_handles_missing_candidate(self):
        hydrated = hydrate_candidate_bookmarks(
            [{"candidate_id": "missing-candidate"}],
            pd.DataFrame(columns=["id", "full_name"]),
            pd.DataFrame(),
            pd.DataFrame(),
        )
        self.assertEqual(
            hydrated["missing-candidate"]["Candidate"],
            "Candidate no longer available",
        )
        self.assertEqual(
            hydrated["missing-candidate"]["Job"],
            "Role not available",
        )

    def test_fresh_session_bookmark_load_hydrates_database_record(self):
        query = MagicMock()
        query.select.return_value = query
        query.eq.return_value = query
        query.order.return_value = query
        query.execute.return_value = MagicMock(
            data=[{"candidate_id": "c1", "created_at": "2026-08-09T00:00:00Z"}]
        )
        client = MagicMock()
        client.table.return_value = query
        with patch(
            "services.ai_persistence_service.require_permission",
            return_value={"id": "u1"},
        ), patch(
            "services.ai_persistence_service.get_supabase_client",
            return_value=client,
        ), patch.object(persistence.st, "session_state", {}):
            loaded, source = persistence.list_bookmarks("candidate")

        hydrated = hydrate_candidate_bookmarks(
            loaded,
            pd.DataFrame([{"id": "c1", "full_name": "Meera Chopra"}]),
            pd.DataFrame(),
            pd.DataFrame(),
        )
        self.assertEqual(source, "database")
        self.assertEqual(hydrated["c1"]["Candidate"], "Meera Chopra")
        self.assertNotEqual(hydrated["c1"]["Candidate"], "c1")


if __name__ == "__main__":
    unittest.main()
