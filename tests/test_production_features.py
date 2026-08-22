from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from components.candidate_communications import build_candidate_messages
from services.ai_recruiter_service import answer_recruiter_query
from services.supabase_service import (
    normalize_years_experience,
    update_candidate,
    update_job,
)


class ProductionFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidates = pd.DataFrame(
            [
                {
                    "id": "c1",
                    "full_name": "Alex Doe",
                    "email": "alex@example.com",
                    "phone": "123",
                    "location": "Pune",
                    "years_experience": 6,
                    "status": "Pending Review",
                    "skills": ["Python"],
                    "created_at": "2026-01-01",
                }
            ]
        )
        self.applications = pd.DataFrame(
            [
                {
                    "id": "a1",
                    "candidate_id": "c1",
                    "job_id": "j1",
                    "application_stage": "Shortlisted",
                    "candidate_score": 80,
                    "ats_score": 85,
                    "applied_at": "2026-01-02",
                    "recommendation": "Strong",
                }
            ]
        )
        self.jobs = pd.DataFrame(
            [
                {
                    "id": "j1",
                    "title": "Engineer",
                    "department": "Technology",
                    "location": "Remote",
                    "description": "Build systems",
                    "status": "Open",
                    "created_at": "2026-01-01",
                }
            ]
        )
        self.interviews = pd.DataFrame(
            [
                {
                    "id": "i1",
                    "application_id": "a1",
                    "interview_date": "2026-08-01T10:00:00+00:00",
                    "interviewer": "Sam",
                    "feedback": {
                        "interview_type": "Technical",
                        "location": "https://meet.example",
                        "_history": [],
                    },
                    "status": "Scheduled",
                    "rating": 3,
                }
            ]
        )

    @patch("services.supabase_service._update_record")
    def test_candidate_and_job_lifecycle_use_allowlisted_updates(self, update):
        update_candidate("c1", {"status": "Archived"})
        self.assertEqual(update.call_args.args[:3], ("candidates", "c1", {"status": "Archived"}))
        update_job("j1", {"status": "Closed"})
        self.assertEqual(update.call_args.args[:3], ("jobs", "j1", {"status": "Closed"}))

    @patch("services.supabase_service._update_record")
    def test_candidate_experience_is_normalized_before_update(self, update):
        for supplied, expected in (
            (1, 1),
            (1.0, 1),
            ("1.0", 1),
            ("", None),
            (None, None),
        ):
            with self.subTest(supplied=supplied):
                update.reset_mock()
                update_candidate(
                    "c1",
                    {"years_experience": supplied, "location": "Delhi"},
                )
                payload = update.call_args.args[2]
                self.assertEqual(payload["years_experience"], expected)
                self.assertEqual(payload["location"], "Delhi")

        with self.assertRaises(ValueError):
            normalize_years_experience("1.5")

    def test_communication_template_contains_interview_changes(self):
        drafts = build_candidate_messages(
            "Interview Invite",
            "Alex Doe",
            "Engineer",
            "Interview",
            "1 Aug 2026",
            "10:00 AM",
            "Sam",
            "https://meet.example",
        )
        self.assertIn("https://meet.example", drafts["email_body"])
        self.assertIn("Sam", drafts["whatsapp_body"])

    def test_ai_query_logic_remains_read_only_and_filters(self):
        result = answer_recruiter_query(
            "Show Python candidates",
            self.candidates,
            self.applications,
            self.jobs,
            self.interviews,
        )
        self.assertEqual(result["intent"], "skill")
        self.assertEqual(len(result["candidates"]), 1)
        blocked = answer_recruiter_query(
            "delete rows from table candidates",
            self.candidates,
            self.applications,
            self.jobs,
            self.interviews,
        )
        self.assertEqual(blocked["intent"], "blocked")

    def test_every_streamlit_page_renders(self):
        notes = pd.DataFrame(
            [
                {
                    "id": "n1",
                    "application_id": "a1",
                    "note": "Good",
                    "recruiter_name": "Recruiter",
                    "created_at": "2026-01-03",
                }
            ]
        )
        patches = [
            patch("services.auth_service.is_authenticated", return_value=True),
            patch("services.supabase_service.get_candidates", return_value=self.candidates),
            patch("services.supabase_service.get_applications", return_value=self.applications),
            patch("services.supabase_service.get_jobs", return_value=self.jobs),
            patch("services.supabase_service.get_interviews", return_value=self.interviews),
            patch("services.supabase_service.get_recruiter_notes", return_value=notes),
            patch("services.communication_service.get_communication_history", return_value=[]),
        ]
        for active_patch in patches:
            active_patch.start()
        try:
            app_path = str(Path(__file__).resolve().parents[1] / "app.py")
            app = AppTest.from_file(app_path, default_timeout=20)
            app.session_state["auth_user"] = {
                "id": "recruiter-1",
                "email": "recruiter@example.com",
            }
            app.run()
            for page in (
                "Overview",
                "Candidates",
                "Applications",
                "Jobs",
                "Interviews",
                "AI Interview Copilot",
                "Resume Semantic Search",
                "Bulk Import / Export",
                "Communication History",
                "AI Recruiter",
                "Analytics",
            ):
                navigation = next(
                    radio for radio in app.radio if radio.label == "Navigation"
                )
                navigation.set_value(page)
                app.run()
                self.assertFalse(
                    app.exception,
                    f"{page} raised {[error.message for error in app.exception]}",
                )
        finally:
            for active_patch in reversed(patches):
                active_patch.stop()

    def test_unauthenticated_session_cannot_render_navigation(self):
        with patch("services.auth_service.is_authenticated", return_value=False):
            app_path = str(Path(__file__).resolve().parents[1] / "app.py")
            app = AppTest.from_file(app_path, default_timeout=20)
            app.run()
        self.assertFalse(app.exception)
        self.assertFalse(app.radio)
        self.assertTrue(
            any(button.label == "Sign in" for button in app.button)
        )


if __name__ == "__main__":
    unittest.main()
