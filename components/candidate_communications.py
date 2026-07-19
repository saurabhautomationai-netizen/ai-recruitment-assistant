"""Reusable candidate communication draft templates."""


MESSAGE_TYPES = [
    "Shortlisted",
    "Interview Invite",
    "Selected",
    "Rejected",
]


def _display(value: str | None, fallback: str) -> str:
    """Return cleaned template data with a professional fallback."""

    if value is None or not str(value).strip():
        return fallback

    return str(value).strip()


def build_candidate_messages(
    message_type: str,
    candidate_name: str,
    job_title: str,
    application_stage: str,
    interview_date: str | None = None,
    interview_time: str | None = None,
    interviewer: str | None = None,
    meeting_location: str | None = None,
) -> dict[str, str]:
    """Build editable email and WhatsApp drafts without sending them."""

    name = _display(candidate_name, "Candidate")
    job = _display(job_title, "the role")
    stage = _display(application_stage, "Under review")

    if message_type == "Interview Invite":
        date_text = _display(interview_date, "To be confirmed")
        time_text = _display(interview_time, "To be confirmed")
        interviewer_text = _display(interviewer, "To be confirmed")
        location_text = _display(
            meeting_location,
            "To be confirmed",
        )
        subject = f"Interview invitation – {job}"
        email_body = (
            f"Dear {name},\n\n"
            f"We would like to invite you to interview for the {job} "
            "position.\n\n"
            f"Interview date: {date_text}\n"
            f"Interview time: {time_text}\n"
            f"Interviewer: {interviewer_text}\n"
            f"Meeting link or location: {location_text}\n\n"
            "Please confirm your availability.\n\n"
            "Best regards,\nRecruitment Team"
        )
        whatsapp_body = (
            f"Hello {name}, you are invited to interview for the {job} "
            f"position. Date: {date_text}. Time: {time_text}. "
            f"Interviewer: {interviewer_text}. Meeting link or location: "
            f"{location_text}. Please confirm your availability."
        )
    elif message_type == "Selected":
        subject = f"Application update – selected for {job}"
        email_body = (
            f"Dear {name},\n\n"
            f"We are pleased to let you know that you have been selected "
            f"for the {job} position. Our recruitment team will contact "
            "you with the next steps shortly.\n\n"
            "Congratulations, and thank you for your time throughout the "
            "selection process.\n\n"
            "Best regards,\nRecruitment Team"
        )
        whatsapp_body = (
            f"Hello {name}, congratulations! You have been selected for "
            f"the {job} position. Our recruitment team will contact you "
            "with the next steps shortly."
        )
    elif message_type == "Rejected":
        subject = f"Application update – {job}"
        email_body = (
            f"Dear {name},\n\n"
            f"Thank you for your interest in the {job} position and for "
            "the time you invested in our recruitment process. After "
            "careful consideration, we will not be progressing with your "
            "application at this time.\n\n"
            "We appreciate your interest and wish you success in your job "
            "search.\n\n"
            "Best regards,\nRecruitment Team"
        )
        whatsapp_body = (
            f"Hello {name}, thank you for your interest in the {job} "
            "position. After careful consideration, we will not be "
            "progressing with your application at this time. We appreciate "
            "your time and wish you success."
        )
    else:
        subject = f"Application shortlisted – {job}"
        email_body = (
            f"Dear {name},\n\n"
            f"We are pleased to inform you that your application for the "
            f"{job} position has been shortlisted. Our recruitment team "
            "will contact you regarding the next stage of the process.\n\n"
            f"Current application stage: {stage}.\n\n"
            "Best regards,\nRecruitment Team"
        )
        whatsapp_body = (
            f"Hello {name}, your application for the {job} position has "
            "been shortlisted. Our recruitment team will contact you about "
            f"the next stage. Current stage: {stage}."
        )

    return {
        "email_subject": subject,
        "email_body": email_body,
        "whatsapp_body": whatsapp_body,
    }
