import unittest
import pandas as pd
from components.candidate_kanban_board import (
    KANBAN_STAGES,
    normalize_stage,
    DOMAIN_SKILLS_MAP,
    _execute_stage_transition,
)


class TestCandidateKanbanBoard(unittest.TestCase):
    def test_kanban_stages_structure(self):
        self.assertEqual(len(KANBAN_STAGES), 5)
        stage_ids = [s["id"] for s in KANBAN_STAGES]
        self.assertIn("shortlisted", stage_ids)
        self.assertIn("scheduled", stage_ids)
        self.assertIn("interview", stage_ids)
        self.assertIn("selected", stage_ids)
        self.assertIn("rejected", stage_ids)

    def test_normalize_stage(self):
        self.assertEqual(normalize_stage("Shortlisted"), "shortlisted")
        self.assertEqual(normalize_stage("Interview Scheduled"), "scheduled")
        self.assertEqual(normalize_stage("Scheduled for Interview"), "scheduled")
        self.assertEqual(normalize_stage("Moved to Interview"), "interview")
        self.assertEqual(normalize_stage("In Interview"), "interview")
        self.assertEqual(normalize_stage("Technical Interview"), "interview")
        self.assertEqual(normalize_stage("Selected"), "selected")
        self.assertEqual(normalize_stage("Selected Candidates"), "selected")
        self.assertEqual(normalize_stage("Hired"), "selected")
        self.assertEqual(normalize_stage("Offer Extended"), "selected")
        self.assertEqual(normalize_stage("Rejected"), "rejected")
        self.assertEqual(normalize_stage("Disqualified"), "rejected")
        self.assertEqual(normalize_stage(""), "shortlisted")
        self.assertEqual(normalize_stage(None), "shortlisted")

    def test_domain_skills_map(self):
        self.assertIn("IT & Software", DOMAIN_SKILLS_MAP)
        self.assertIn("Healthcare & Medicine", DOMAIN_SKILLS_MAP)
        self.assertIn("Engineering & Manufacturing", DOMAIN_SKILLS_MAP)
        self.assertIn("Human Resources (HR)", DOMAIN_SKILLS_MAP)
        self.assertIn("Finance & Business", DOMAIN_SKILLS_MAP)
        self.assertIn("BPO & Customer Operations", DOMAIN_SKILLS_MAP)
        self.assertIn("Animation & Creative", DOMAIN_SKILLS_MAP)
        # Verify skills exist
        self.assertIn("Python", DOMAIN_SKILLS_MAP["IT & Software"])
        self.assertIn("Clinical Care", DOMAIN_SKILLS_MAP["Healthcare & Medicine"])
        self.assertIn("AutoCAD", DOMAIN_SKILLS_MAP["Engineering & Manufacturing"])


if __name__ == "__main__":
    unittest.main()
