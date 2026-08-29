"""Staffing Agency Billing, Timesheet Management & Invoice Generation Service.

Matches Zoho Recruit's Staffing Agency Edition:
1. Gross Margin & Client Bill Rate vs. Candidate Pay Rate Calculator.
2. Candidate Timesheet Tracker with Weekly Approvals.
3. 1-Click Client Invoice PDF Generation with Tax & Billing Summary.
"""

from __future__ import annotations

import io
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.sanitization_service import sanitize_text

TIMESHEET_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "agency_timesheets.json")


def _load_timesheets() -> List[Dict[str, Any]]:
    if not os.path.exists(TIMESHEET_STORE_PATH):
        os.makedirs(os.path.dirname(TIMESHEET_STORE_PATH), exist_ok=True)
        return []
    try:
        with open(TIMESHEET_STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_timesheets(data: List[Dict[str, Any]]) -> None:
    try:
        os.makedirs(os.path.dirname(TIMESHEET_STORE_PATH), exist_ok=True)
        with open(TIMESHEET_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def calculate_staffing_margin(
    bill_rate: float,
    pay_rate: float,
    statutory_burden_pct: float = 12.0,
) -> Dict[str, float]:
    """Calculate direct cost, gross profit spread, gross margin %, and markup %."""
    b_rate = max(float(bill_rate), 0.0)
    p_rate = max(float(pay_rate), 0.0)
    burden = max(float(statutory_burden_pct), 0.0)

    burden_cost = p_rate * (burden / 100.0)
    total_cost = p_rate + burden_cost
    gross_profit = b_rate - total_cost

    margin_pct = (gross_profit / b_rate * 100.0) if b_rate > 0 else 0.0
    markup_pct = ((b_rate - p_rate) / p_rate * 100.0) if p_rate > 0 else 0.0

    return {
        "bill_rate": round(b_rate, 2),
        "pay_rate": round(p_rate, 2),
        "burden_pct": round(burden, 2),
        "burden_cost": round(burden_cost, 2),
        "total_cost": round(total_cost, 2),
        "gross_profit_hourly": round(gross_profit, 2),
        "gross_margin_pct": round(margin_pct, 2),
        "markup_pct": round(markup_pct, 2),
    }


def record_candidate_timesheet(
    candidate_name: str,
    client_name: str,
    job_title: str,
    week_ending_date: str,
    regular_hours: float,
    overtime_hours: float = 0.0,
    bill_rate: float = 1200.0,
    pay_rate: float = 800.0,
) -> Dict[str, Any]:
    """Record weekly timesheet submission with automated margin calculation."""
    reg_h = max(float(regular_hours), 0.0)
    ot_h = max(float(overtime_hours), 0.0)
    total_h = reg_h + ot_h

    margin = calculate_staffing_margin(bill_rate, pay_rate)
    total_client_bill = (reg_h * margin["bill_rate"]) + (ot_h * margin["bill_rate"] * 1.5)
    total_candidate_pay = (reg_h * margin["pay_rate"]) + (ot_h * margin["pay_rate"] * 1.5)

    entry = {
        "timesheet_id": f"ts_{uuid.uuid4().hex[:8]}",
        "candidate_name": sanitize_text(candidate_name),
        "client_name": sanitize_text(client_name),
        "job_title": sanitize_text(job_title),
        "week_ending": sanitize_text(week_ending_date),
        "regular_hours": reg_h,
        "overtime_hours": ot_h,
        "total_hours": total_h,
        "total_billed": round(total_client_bill, 2),
        "total_paid": round(total_candidate_pay, 2),
        "gross_profit": round(total_client_bill - total_candidate_pay, 2),
        "status": "APPROVED",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    existing = _load_timesheets()
    existing.append(entry)
    _save_timesheets(existing)
    return entry


def generate_agency_invoice_pdf(
    client_name: str,
    candidate_name: str,
    job_title: str,
    billing_period: str,
    total_hours: float,
    hourly_bill_rate: float,
    tax_pct: float = 18.0,
    agency_name: str = "Netizen Staffing Solutions Ltd.",
) -> bytes:
    """Generate official client billing invoice in PDF format."""
    subtotal = float(total_hours) * float(hourly_bill_rate)
    tax_amount = subtotal * (float(tax_pct) / 100.0)
    total_payable = subtotal + tax_amount
    invoice_no = f"INV-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:4].upper()}"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("InvTitle", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#0f172a"), fontName="Helvetica-Bold")
    body_style = ParagraphStyle("InvBody", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#334155"), leading=14)

    story = []
    story.append(Paragraph(f"<b>{agency_name.upper()}</b>", title_style))
    story.append(Paragraph("CLIENT STAFFING SERVICES INVOICE", body_style))
    story.append(Spacer(1, 15))

    details = (
        f"<b>Invoice Number:</b> {invoice_no}<br/>"
        f"<b>Invoice Date:</b> {datetime.today().strftime('%d %B %Y')}<br/>"
        f"<b>Bill To:</b> {sanitize_text(client_name)}<br/>"
        f"<b>Billing Period:</b> {sanitize_text(billing_period)}"
    )
    story.append(Paragraph(details, body_style))
    story.append(Spacer(1, 15))

    table_data = [
        ["Resource Placed", "Role", "Hours Billed", "Hourly Rate (INR)", "Line Total (INR)"],
        [sanitize_text(candidate_name), sanitize_text(job_title), f"{total_hours:.1f}", f"{hourly_bill_rate:,.2f}", f"{subtotal:,.2f}"],
        ["", "", "", "GST / Tax (18%):", f"{tax_amount:,.2f}"],
        ["", "", "", "Total Due (INR):", f"INR {total_payable:,.2f}"],
    ]

    t = Table(table_data, colWidths=[130, 110, 80, 100, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Payment Terms:</b> Due within 15 days of invoice date. Thank you for partnering with us!", body_style))
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes