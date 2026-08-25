"""Automated Unit Tests for Enterprise Real-World Recruitment Features."""

from datetime import datetime, timezone, timedelta
import pytest

from services.deduplication_service import (
    find_candidate_duplicate,
    normalize_email,
    normalize_phone,
)
from services.calendar_sync_service import (
    generate_google_calendar_url,
    generate_outlook_calendar_url,
    generate_ics_file_content,
)
from services.offer_letter_service import (
    calculate_ctc_breakdown,
    generate_offer_letter_pdf,
)


class TestCandidateDeduplication:
    def test_normalize_phone_e164_and_prefixes(self):
        assert normalize_phone("+91-98765-43210") == "9876543210"
        assert normalize_phone("09876543210") == "9876543210"
        assert normalize_phone("9876543210") == "9876543210"
        assert normalize_phone("") == ""

    def test_normalize_email_canonicalization(self):
        assert normalize_email("Rahul.Sharma+recruitment@gmail.com") == "rahulsharma@gmail.com"
        assert normalize_email("saurabh.automation@company.org") == "saurabh.automation@company.org"

    def test_duplicate_candidate_detection_exact_email(self):
        existing = [
            {"id": "cand_01", "full_name": "Pooja Patel", "email": "pooja.patel@gmail.com", "phone": "9876543211"}
        ]
        new_cand = {"full_name": "Pooja Patel", "email": "poojapatel+work@gmail.com", "phone": "1234567890"}
        match = find_candidate_duplicate(new_cand, existing)
        assert match["is_duplicate"] is True
        assert match["match_type"] == "exact_email_match"
        assert match["matched_candidate_id"] == "cand_01"

    def test_duplicate_candidate_detection_exact_phone(self):
        existing = [
            {"id": "cand_02", "full_name": "Amit Verma", "email": "amit@yahoo.com", "phone": "9876543212"}
        ]
        new_cand = {"full_name": "Amit V.", "email": "different@company.com", "phone": "+91-98765-43212"}
        match = find_candidate_duplicate(new_cand, existing)
        assert match["is_duplicate"] is True
        assert match["match_type"] == "exact_phone_match"
        assert match["matched_candidate_id"] == "cand_02"

    def test_non_duplicate_candidate(self):
        existing = [
            {"id": "cand_03", "full_name": "Vikram Singh", "email": "vikram@gmail.com", "phone": "9876543213"}
        ]
        new_cand = {"full_name": "Neha Sharma", "email": "neha@gmail.com", "phone": "9123456789"}
        match = find_candidate_duplicate(new_cand, existing)
        assert match["is_duplicate"] is False


class TestCalendarSync:
    def test_google_calendar_url_generation(self):
        start = datetime.now(timezone.utc) + timedelta(days=2)
        end = start + timedelta(hours=1)
        url = generate_google_calendar_url("Tech Round 1 - AI Engineer", start, end, "Google Meet Call", "Online")
        assert "calendar.google.com/calendar/render" in url
        assert "action=TEMPLATE" in url

    def test_outlook_calendar_url_generation(self):
        start = datetime.now(timezone.utc) + timedelta(days=2)
        end = start + timedelta(hours=1)
        url = generate_outlook_calendar_url("Final HR Round", start, end)
        assert "outlook.live.com/calendar" in url
        assert "rru=addevent" in url

    def test_ics_file_content_rfc5545_compliance(self):
        start = datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 9, 1, 11, 0, 0, tzinfo=timezone.utc)
        ics = generate_ics_file_content("Leadership Interview", start, end, "Interview with Director", "Zoom Room")
        assert "BEGIN:VCALENDAR" in ics
        assert "VERSION:2.0" in ics
        assert "BEGIN:VEVENT" in ics
        assert "DTSTART:20260901T100000Z" in ics
        assert "DTEND:20260901T110000Z" in ics
        assert "SUMMARY:Leadership Interview" in ics
        assert "END:VEVENT" in ics
        assert "END:VCALENDAR" in ics


class TestOfferLetterGeneration:
    def test_ctc_breakdown_percentages(self):
        ctc = calculate_ctc_breakdown(2400000)
        assert ctc["annual_ctc"] == 2400000.0
        assert ctc["basic_annual"] == 1200000.0  # 50%
        assert ctc["hra_annual"] == 600000.0     # 25%
        assert ctc["special_annual"] == 360000.0 # 15%
        assert ctc["pf_annual"] == 240000.0      # 10%
        assert ctc["monthly_ctc"] == 200000.0

    def test_offer_letter_pdf_binary_generation(self):
        pdf = generate_offer_letter_pdf(
            candidate_name="Sneha Rao",
            job_title="Lead AI Engineer",
            annual_ctc=2800000,
            joining_date="15 October 2026",
            company_name="Netizen AI Labs",
            location="Bangalore",
        )
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 2000