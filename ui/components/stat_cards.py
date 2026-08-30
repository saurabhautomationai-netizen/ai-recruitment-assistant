"""Compact Enterprise Stat Cards."""

import streamlit as st
from ui.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_MUTED, COLOR_ACCENT_EMERALD, COLOR_EMERALD_BG
)

def render_stat_card(
    title: str,
    value: str | int,
    delta: str = None,
    subtitle: str = None,
    icon: str = None,
):
    """Renders a high-density, elevated metric card adhering to Forest Enterprise specs."""
    delta_html = ""
    if delta:
        delta_html = f'''
        <span style="background: {COLOR_EMERALD_BG}; color: {COLOR_ACCENT_EMERALD}; font-weight: 750; font-size: 11px; padding: 2px 7px; border-radius: 12px;">
            {delta}
        </span>
        '''

    icon_html = f'<span style="font-size: 16px; margin-right: 6px;">{icon}</span>' if icon else ""
    subtitle_html = f'<div style="font-size: 11.5px; color: {COLOR_TEXT_MUTED}; margin-top: 4px;">{subtitle}</div>' if subtitle else ""

    html = f'''
    <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 14px; padding: 14px 16px; box-shadow: 0 2px 8px rgba(22, 46, 32, 0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-size: 12px; font-weight: 700; color: {COLOR_TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.04em;">
                {icon_html}{title}
            </div>
            {delta_html}
        </div>
        <div style="font-size: 24px; font-weight: 800; color: {COLOR_TEXT_HEADING}; line-height: 1.1;">
            {value}
        </div>
        {subtitle_html}
    </div>
    '''
    st.html(html)
