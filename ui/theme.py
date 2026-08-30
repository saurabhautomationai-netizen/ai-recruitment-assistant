"""
Forest Enterprise Design Tokens & Theme Specification for ZERO Recruit.
Source of Truth: DESIGN.md and Google Stitch approved designs.
"""

# Brand Colors
COLOR_PRIMARY = "#162E20"          # Executive Forest Green
COLOR_PRIMARY_HOVER = "#0E1F15"    # Deep Pine
COLOR_CANVAS = "#F3F4F1"           # Pearl White / Soft Mist
COLOR_SURFACE = "#FFFFFF"          # Pure White
COLOR_BORDER = "#E8EAE6"           # Subtle Slate Border
COLOR_BORDER_STRONG = "#CBD5E1"    # Medium Gray Border

# Accent & Signal Colors
COLOR_ACCENT_EMERALD = "#059669"   # Emerald Pulse (Primary Action / High Match)
COLOR_EMERALD_BG = "#ECFDF5"
COLOR_EMERALD_BORDER = "#A7F3D0"

COLOR_ACCENT_BLUE = "#2563EB"      # Cobalt Blue (Interview / Active)
COLOR_BLUE_BG = "#EFF6FF"
COLOR_BLUE_BORDER = "#BFDBFE"

COLOR_ACCENT_VIOLET = "#7C3AED"    # Royal Violet (In Interview)
COLOR_VIOLET_BG = "#F5F3FF"
COLOR_VIOLET_BORDER = "#DDD6FE"

COLOR_ACCENT_SUCCESS = "#16A34A"   # Green (Selected / Hired)
COLOR_SUCCESS_BG = "#F0FDF4"
COLOR_SUCCESS_BORDER = "#BBF7D0"

COLOR_ACCENT_DANGER = "#DC2626"    # Ruby Red (Rejected)
COLOR_DANGER_BG = "#FEF2F2"
COLOR_DANGER_BORDER = "#FECACA"

COLOR_ACCENT_AMBER = "#D97706"     # Amber (Gap / Review)
COLOR_AMBER_BG = "#FFFBEB"
COLOR_AMBER_BORDER = "#FDE68A"

# Typography Colors
COLOR_TEXT_HEADING = "#162E20"
COLOR_TEXT_BODY = "#334155"
COLOR_TEXT_MUTED = "#64748B"
COLOR_TEXT_SUBTLE = "#94A3B8"

# Stage Meta Mapping
STAGE_META = {
    "shortlisted": {
        "id": "shortlisted",
        "title": "Shortlisted",
        "icon": "📋",
        "color": COLOR_ACCENT_EMERALD,
        "bg": COLOR_EMERALD_BG,
        "border": COLOR_EMERALD_BORDER,
    },
    "scheduled": {
        "id": "scheduled",
        "title": "Scheduled for Interview",
        "icon": "📅",
        "color": COLOR_ACCENT_BLUE,
        "bg": COLOR_BLUE_BG,
        "border": COLOR_BLUE_BORDER,
    },
    "interview": {
        "id": "interview",
        "title": "Moved to Interview",
        "icon": "🎙️",
        "color": COLOR_ACCENT_VIOLET,
        "bg": COLOR_VIOLET_BG,
        "border": COLOR_VIOLET_BORDER,
    },
    "selected": {
        "id": "selected",
        "title": "Selected Candidates",
        "icon": "🏆",
        "color": COLOR_ACCENT_SUCCESS,
        "bg": COLOR_SUCCESS_BG,
        "border": COLOR_SUCCESS_BORDER,
    },
    "rejected": {
        "id": "rejected",
        "title": "Rejected Candidates",
        "icon": "❌",
        "color": COLOR_ACCENT_DANGER,
        "bg": COLOR_DANGER_BG,
        "border": COLOR_DANGER_BORDER,
    },
}
