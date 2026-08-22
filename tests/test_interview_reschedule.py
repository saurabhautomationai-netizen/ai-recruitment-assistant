from __future__ import annotations

from datetime import date, time
import unittest
from unittest.mock import patch

import pandas as pd

from services.supabase_service import (
    build_interview_reschedule_updates,
    parse_interview_datetime_series,
    update_interview,
)


CURRENT_DATE = "2026-08-09T07:30:00+00:00"  # 1:00 PM Asia/Kolkata


class _Response:
    def __init__(self, data):
        self.data = data


class _InterviewTable:
    def __init__(self, row):
        self.row = row
        self.operation = "select"
        self.pending_updates = {}

    def select(self, _columns):
        self.operation = "select"
        return self

    def update(self, updates):
        self.operation = "update"
        self.pending_updates = dict(updates)
        return self

    def eq(self, _column, _value):
        return self

    def limit(self, _count):
        return self

    def execute(self):
        if self.operation == "update":
            self.row.update(self.pending_updates)
        return _Response([dict(self.row)])


class _Client:
    def __init__(self, row):
        self.interviews = _InterviewTable(row)

    def table(self, name):
        if name != "interviews":
            raise AssertionError(f"Unexpected table: {name}")
        return self.interviews


class InterviewRescheduleTests(unittest.TestCase):
    def test_date_only_change_preserves_local_time(self):
        updates = build_interview_reschedule_updates(
            current_interview_date=CURRENT_DATE,
            revised_date=date(2026, 8, 10),
        )
        self.assertEqual(
            updates["interview_date"], "2026-08-10T07:30:00+00:00"
        )

    def test_time_only_change_preserves_local_date(self):
        updates = build_interview_reschedule_updates(
            current_interview_date=CURRENT_DATE,
            revised_time=time(14, 0),
        )
        self.assertEqual(
            updates["interview_date"], "2026-08-09T08:30:00+00:00"
        )

    def test_date_and_time_change_uses_recruiter_timezone(self):
        updates = build_interview_reschedule_updates(
            current_interview_date=CURRENT_DATE,
            revised_date=date(2026, 8, 10),
            revised_time=time(13, 0),
        )
        self.assertEqual(
            updates["interview_date"], "2026-08-10T07:30:00+00:00"
        )

    def test_location_only_change_does_not_touch_date(self):
        feedback = {
            "interview_type": "Technical",
            "meeting_link": "Old room",
            "notes": "Preserve me",
            "feedback": "Strong answer",
            "_history": [{"changed_at": "earlier"}],
        }
        updates = build_interview_reschedule_updates(
            current_interview_date=CURRENT_DATE,
            feedback=feedback,
            meeting_location="Birla college",
        )
        self.assertNotIn("interview_date", updates)
        self.assertEqual(updates["feedback"]["meeting_link"], "Birla college")
        self.assertEqual(updates["feedback"]["interview_type"], "Technical")
        self.assertEqual(updates["feedback"]["notes"], "Preserve me")
        self.assertEqual(updates["feedback"]["feedback"], "Strong answer")

    def test_date_time_and_metadata_persist_together(self):
        row = {
            "interview_date": CURRENT_DATE,
            "interviewer": "Pravin Kulkarni",
            "status": "Scheduled",
            "feedback": {
                "interview_type": "Technical",
                "location": "Old location",
                "notes": "Preserve me",
                "feedback": "Existing feedback",
            },
            "rating": 4,
        }
        updates = build_interview_reschedule_updates(
            current_interview_date=row["interview_date"],
            revised_date=date(2026, 8, 10),
            revised_time=time(13, 0),
            interviewer="Pravin Kulkarni",
            feedback=row["feedback"],
            meeting_location="Birla college",
        )
        client = _Client(row)
        with patch(
            "services.supabase_service.require_permission",
            return_value={"id": "recruiter-1"},
        ), patch(
            "services.supabase_service.get_supabase_client",
            return_value=client,
        ):
            update_interview("interview-1", updates)

        self.assertEqual(row["interview_date"], "2026-08-10T07:30:00+00:00")
        self.assertEqual(row["feedback"]["location"], "Birla college")
        self.assertEqual(row["feedback"]["interview_type"], "Technical")
        self.assertEqual(row["feedback"]["notes"], "Preserve me")
        self.assertEqual(row["feedback"]["feedback"], "Existing feedback")
        self.assertEqual(row["rating"], 4)
        self.assertEqual(row["status"], "Scheduled")

    def test_reload_parses_mixed_supabase_timestamp_formats(self):
        values = pd.Series(
            [
                "2026-08-01T10:00:00.000000+00:00",
                "2026-08-10T07:30:00+00:00",
            ]
        )
        reloaded = parse_interview_datetime_series(values)
        self.assertFalse(reloaded.isna().any())
        self.assertEqual(reloaded.iloc[1].date(), date(2026, 8, 10))
        self.assertEqual(reloaded.iloc[1].time().replace(tzinfo=None), time(13, 0))


if __name__ == "__main__":
    unittest.main()
