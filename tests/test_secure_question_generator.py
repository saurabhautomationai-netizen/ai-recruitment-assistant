import pytest
from services.secure_question_generator import (
    InterviewGuide,
    InterviewQuestion,
    PIIScrubber,
    SecureQuestionGenerator,
)


def test_pii_scrubber_removes_contact_info():
    dirty_text = (
        "Candidate John Doe, email: john.doe@example.com, phone: 415-555-0199. "
        "LinkedIn: linkedin.com/in/johndoe-dev and GitHub: github.com/johndoe."
    )
    clean = PIIScrubber.scrub(dirty_text)
    assert "john.doe@example.com" not in clean
    assert "[REDACTED_EMAIL]" in clean
    assert "415-555-0199" not in clean
    assert "[REDACTED_PHONE]" in clean
    assert "[REDACTED_LINKEDIN]" in clean
    assert "[REDACTED_GITHUB]" in clean


def test_question_generator_produces_structured_guide():
    gen = SecureQuestionGenerator()
    jd = "Looking for a Senior Python & AI Engineer with Supabase, FastAPI, and Docker experience."
    resume = "Candidate with 6 years building Python backends, LLM agents, and PostgreSQL databases."

    guide = gen.generate_guide(raw_job_desc=jd, raw_candidate_profile=resume, difficulty="Senior")
    
    assert isinstance(guide, InterviewGuide)
    assert len(guide.questions) >= 3
    assert guide.difficulty_level == "Senior"
    
    for q in guide.questions:
        assert isinstance(q, InterviewQuestion)
        assert len(q.question) > 10
        assert len(q.target_competency) > 0
        assert len(q.expected_answer_signals) > 0
        assert len(q.red_flags) > 0


def test_question_generator_handles_empty_inputs():
    gen = SecureQuestionGenerator()
    guide = gen.generate_guide(raw_job_desc="", raw_candidate_profile="", difficulty="Mid")
    assert isinstance(guide, InterviewGuide)
    assert len(guide.questions) >= 1
