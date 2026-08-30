"""Consistent Status Chips & Badges for ZERO Recruit."""

from ui.theme import (
    COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER,
    COLOR_ACCENT_BLUE, COLOR_BLUE_BG, COLOR_BLUE_BORDER,
    COLOR_ACCENT_VIOLET, COLOR_VIOLET_BG, COLOR_VIOLET_BORDER,
    COLOR_ACCENT_SUCCESS, COLOR_SUCCESS_BG, COLOR_SUCCESS_BORDER,
    COLOR_ACCENT_DANGER, COLOR_DANGER_BG, COLOR_DANGER_BORDER,
    COLOR_ACCENT_AMBER, COLOR_AMBER_BG, COLOR_AMBER_BORDER,
    COLOR_TEXT_MUTED
)

def get_status_style(status_raw: str) -> tuple[str, str, str]:
    """Returns (color, background, border) for any stage/status."""
    clean = str(status_raw or "").strip().lower()
    if any(k in clean for k in ["shortlist", "shortlisted"]):
        return COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER
    elif any(k in clean for k in ["schedule", "scheduled"]):
        return COLOR_ACCENT_BLUE, COLOR_BLUE_BG, COLOR_BLUE_BORDER
    elif any(k in clean for k in ["interview", "technical", "in interview"]):
        return COLOR_ACCENT_VIOLET, COLOR_VIOLET_BG, COLOR_VIOLET_BORDER
    elif any(k in clean for k in ["select", "selected", "hire", "hired", "offer"]):
        return COLOR_ACCENT_SUCCESS, COLOR_SUCCESS_BG, COLOR_SUCCESS_BORDER
    elif any(k in clean for k in ["reject", "rejected", "disqualif"]):
        return COLOR_ACCENT_DANGER, COLOR_DANGER_BG, COLOR_DANGER_BORDER
    else:
        return COLOR_TEXT_MUTED, "#F8FAFC", "#E2E8F0"

def render_status_pill_html(status_raw: str, prefix: str = "") -> str:
    """Returns HTML for a status badge."""
    color, bg, border = get_status_style(status_raw)
    display_text = f"{prefix} {status_raw}".strip() if prefix else str(status_raw)
    return (
        f'<span style="background: {bg}; color: {color}; border: 1px solid {border}; '
        f'font-size: 11px; font-weight: 750; padding: 3px 10px; border-radius: 12px; display: inline-block; white-space: nowrap;">'
        f'{display_text}</span>'
    )

def render_ats_badge_html(score: int | float) -> str:
    """Returns HTML for an ATS Fit Score pill."""
    try:
        val = int(float(score))
    except Exception:
        val = 75

    if val >= 80:
        color, bg, border = COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG, COLOR_EMERALD_BORDER
    elif val >= 60:
        color, bg, border = COLOR_ACCENT_BLUE, COLOR_BLUE_BG, COLOR_BLUE_BORDER
    else:
        color, bg, border = COLOR_ACCENT_AMBER, COLOR_AMBER_BG, COLOR_AMBER_BORDER

    return (
        f'<span style="background: {bg}; color: {color}; border: 1px solid {border}; '
        f'font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; display: inline-block;">'
        f'{val}% ATS</span>'
    )
