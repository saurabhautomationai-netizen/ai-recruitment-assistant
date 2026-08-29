"""Automated Unit Tests for Hybrid Interview Question Kits, Staffing Agency Billing, and Marketplace Hub."""

import pytest

from services.hybrid_interview_kit_service import (
    create_manual_question,
    compile_unified_interview_kit,
    get_interview_kit,
)
from services.agency_billing_service import (
    calculate_staffing_margin,
    record_candidate_timesheet,
    generate_agency_invoice_pdf,
)
from services.marketplace_integration_service import (
    trigger_background_check,
    dispatch_coding_assessment,
    dispatch_esign_envelope,
    get_supported_industries,
    get_platforms_for_industry,
    dispatch_industry_assessment,
)


class TestHybridInterviewKits:
    def test_create_manual_question(self):
        q = create_manual_question(
            question_text="Explain how you handle race conditions in distributed databases.",
            target_competency="Distributed Systems",
            expected_answer_signals=["Optimistic Locking", "Two-Phase Commit", "Idempotency"],
            red_flags=["Suggests ignoring concurrency", "No understanding of transactions"],
            max_score=5,
        )
        assert q["origin"] == "MANUAL_RECRUITER"
        assert "race conditions" in q["question"]
        assert len(q["expected_answer_signals"]) == 3

    def test_compile_unified_interview_kit(self):
        ai_questions = [
            {
                "question": "Tell me about a time you optimized an API endpoint under high throughput.",
                "target_competency": "Performance Engineering",
                "expected_answer_signals": ["Profiling", "Caching", "Async I/O"],
                "red_flags": ["No metrics mentioned"],
            }
        ]
        manual_questions = [
            create_manual_question(
                question_text="Describe your experience mentoring junior developers.",
                target_competency="Leadership",
                max_score=5,
            )
        ]

        kit = compile_unified_interview_kit(
            job_id="job_lead_99",
            job_title="Lead AI Engineer",
            candidate_id="cand_123",
            ai_star_questions=ai_questions,
            manual_questions=manual_questions,
            interviewer_name="Saurabh Shinde",
        )
        assert kit["total_questions"] == 2
        assert kit["ai_questions_count"] == 1
        assert kit["manual_questions_count"] == 1
        assert kit["max_possible_score"] == 10
        assert kit["questions"][0]["origin"] == "AI_GROUNDED_STAR"
        assert kit["questions"][1]["origin"] == "MANUAL_RECRUITER"

        retrieved = get_interview_kit(kit["kit_id"])
        assert retrieved is not None
        assert retrieved["job_title"] == "Lead AI Engineer"


class TestAgencyBillingAndTimesheets:
    def test_staffing_margin_calculation(self):
        margin = calculate_staffing_margin(bill_rate=2000.0, pay_rate=1200.0, statutory_burden_pct=15.0)
        assert margin["bill_rate"] == 2000.0
        assert margin["pay_rate"] == 1200.0
        assert margin["burden_cost"] == 180.0     # 15% of 1200
        assert margin["total_cost"] == 1380.0      # 1200 + 180
        assert margin["gross_profit_hourly"] == 620.0 # 2000 - 1380
        assert margin["gross_margin_pct"] == 31.0  # 620 / 2000 * 100

    def test_record_candidate_timesheet(self):
        ts = record_candidate_timesheet(
            candidate_name="Rohit Verma",
            client_name="FinTech Global Inc.",
            job_title="Full Stack Contractor",
            week_ending_date="2026-08-28",
            regular_hours=40.0,
            overtime_hours=5.0,
            bill_rate=1500.0,
            pay_rate=1000.0,
        )
        assert ts["status"] == "APPROVED"
        assert ts["total_hours"] == 45.0
        assert ts["total_billed"] > 60000.0

    def test_generate_agency_invoice_pdf(self):
        pdf = generate_agency_invoice_pdf(
            client_name="CloudScale Enterprises",
            candidate_name="Ananya Sen",
            job_title="DevOps Specialist",
            billing_period="01 Aug - 15 Aug 2026",
            total_hours=80.0,
            hourly_bill_rate=1600.0,
            tax_pct=18.0,
        )
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 2000


class TestMarketplaceHub:
    def test_trigger_background_check(self):
        res = trigger_background_check("candidate@gmail.com", "Rohan Mehta", provider="CHECKR")
        assert res["success"] is True
        assert res["status"] == "SCREENING_INITIATED"
        assert res["provider"] == "CHECKR"

    def test_dispatch_coding_assessment(self):
        res = dispatch_coding_assessment("coder@dev.com", "Kavita Rao", platform="HACKERRANK")
        assert res["success"] is True
        assert res["status"] == "ASSESSMENT_INVITED"
        assert res["platform"] == "HACKERRANK"

    def test_dispatch_esign_envelope(self):
        res = dispatch_esign_envelope("signee@corp.com", "Siddharth Roy", provider="DOCUSIGN")
        assert res["success"] is True
        assert res["status"] == "SENT_FOR_SIGNATURE"

    def test_dynamic_industry_assessments(self):
        industries = get_supported_industries()
        assert "Healthcare & Medicine" in industries
        assert "Engineering & Manufacturing" in industries
        assert "Animation, Design & Creative" in industries
        assert "BPO, KPO & Customer Operations" in industries

        # Healthcare Nurse test
        health_res = dispatch_industry_assessment(
            candidate_email="nurse@hospital.org",
            candidate_name="Sarah Jenkins",
            industry="Healthcare & Medicine",
            role="Nurse",
        )
        assert health_res["success"] is True
        assert "Prophecy Health" in health_res["platform"] or "Relias" in health_res["platform"]
        assert "Pharmacology" in health_res["test_title"] or "RN Clinical" in health_res["test_title"]

        # Civil Engineer test
        eng_res = dispatch_industry_assessment(
            candidate_email="engineer@infra.com",
            candidate_name="Anil Kulkarni",
            industry="Engineering & Manufacturing",
            role="Civil Engineer",
        )
        assert eng_res["success"] is True
        assert "AutoCAD" in eng_res["platform"] or "SolidWorks" in eng_res["platform"]

        # Animation 3D Maya test
        anim_res = dispatch_industry_assessment(
            candidate_email="animator@studio.com",
            candidate_name="Leo Varma",
            industry="Animation, Design & Creative",
            role="3D Animator",
        )
        assert anim_res["success"] is True
        assert "Maya" in anim_res["test_title"] or "Blender" in anim_res["test_title"]