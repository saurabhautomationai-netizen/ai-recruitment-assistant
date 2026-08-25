"""Automated PDF Offer Letter & CTC Breakup Generation Service."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.sanitization_service import sanitize_text


def calculate_ctc_breakdown(annual_ctc: float) -> Dict[str, float]:
    """Calculate standard Indian/Global CTC component breakdown."""
    annual_ctc = max(float(annual_ctc), 100000.0)
    basic = annual_ctc * 0.50
    hra = annual_ctc * 0.25
    special = annual_ctc * 0.15
    pf = annual_ctc * 0.10
    return {
        "annual_ctc": round(annual_ctc, 2),
        "monthly_ctc": round(annual_ctc / 12, 2),
        "basic_annual": round(basic, 2),
        "basic_monthly": round(basic / 12, 2),
        "hra_annual": round(hra, 2),
        "hra_monthly": round(hra / 12, 2),
        "special_annual": round(special, 2),
        "special_monthly": round(special / 12, 2),
        "pf_annual": round(pf, 2),
        "pf_monthly": round(pf / 12, 2),
    }


def generate_offer_letter_pdf(
    candidate_name: str,
    job_title: str,
    annual_ctc: float,
    joining_date: str,
    company_name: str = "Netizen AI Automation Ltd.",
    location: str = "Pune / Hybrid",
) -> bytes:
    """Generate an official high-resolution PDF offer letter."""
    clean_name = sanitize_text(candidate_name) or "Valued Candidate"
    clean_role = sanitize_text(job_title) or "Software Engineer"
    clean_company = sanitize_text(company_name)
    clean_location = sanitize_text(location)
    clean_joining = sanitize_text(joining_date) or datetime.today().strftime("%d %B %Y")

    breakdown = calculate_ctc_breakdown(annual_ctc)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
    )
    bold_body = ParagraphStyle(
        "DocBoldBody",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    story = []

    # Header Banner
    story.append(Paragraph(clean_company.upper(), title_style))
    story.append(Paragraph("OFFICIAL LETTER OF EMPLOYMENT OFFER", subtitle_style))
    story.append(Spacer(1, 15))

    # Date and Recipient
    today_str = datetime.today().strftime("%d %B %Y")
    story.append(Paragraph(f"<b>Date:</b> {today_str}", body_style))
    story.append(Paragraph(f"<b>To:</b> {clean_name}", body_style))
    story.append(Spacer(1, 12))

    # Congratulatory Opening
    opening_text = (
        f"Dear <b>{clean_name}</b>,<br/><br/>"
        f"On behalf of <b>{clean_company}</b>, we are thrilled to offer you the position of "
        f"<b>{clean_role}</b> based in <b>{clean_location}</b>. "
        f"We were immensely impressed by your skills, experience, and interview performance, "
        "and we look forward to welcoming you to our high-impact team."
    )
    story.append(Paragraph(opening_text, body_style))
    story.append(Spacer(1, 12))

    # Key Terms
    terms_text = (
        f"<b>Designation:</b> {clean_role}<br/>"
        f"<b>Date of Joining:</b> {clean_joining}<br/>"
        f"<b>Total Annual Compensation (CTC):</b> INR {breakdown['annual_ctc']:,.2f} per annum<br/>"
        f"<b>Work Location:</b> {clean_location}"
    )
    story.append(Paragraph(terms_text, body_style))
    story.append(Spacer(1, 15))

    # Compensation Table
    story.append(Paragraph("<b>ANNEXURE A: COMPENSATION & BENEFITS BREAKDOWN</b>", bold_body))
    story.append(Spacer(1, 6))

    table_data = [
        ["Salary Component", "Monthly (INR)", "Annual (INR)"],
        ["Basic Salary (50%)", f"{breakdown['basic_monthly']:,.2f}", f"{breakdown['basic_annual']:,.2f}"],
        ["House Rent Allowance (HRA - 25%)", f"{breakdown['hra_monthly']:,.2f}", f"{breakdown['hra_annual']:,.2f}"],
        ["Special Allowance (15%)", f"{breakdown['special_monthly']:,.2f}", f"{breakdown['special_annual']:,.2f}"],
        ["Provident Fund / Benefits (10%)", f"{breakdown['pf_monthly']:,.2f}", f"{breakdown['pf_annual']:,.2f}"],
        ["Total Cost to Company (CTC)", f"INR {breakdown['monthly_ctc']:,.2f}", f"INR {breakdown['annual_ctc']:,.2f}"],
    ]

    t = Table(table_data, colWidths=[240, 140, 140])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ])
    )
    story.append(t)
    story.append(Spacer(1, 20))

    # Sign-off & Acceptance
    sign_off = (
        "<b>Acceptance of Offer:</b><br/>"
        "Please sign and return a duplicate copy of this letter within 3 business days "
        "to confirm your acceptance of this offer.<br/><br/>"
        f"Sincerely,<br/><b>Authorized HR Signatory</b><br/>{clean_company}"
    )
    story.append(Paragraph(sign_off, body_style))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes