"""Reusable Activity Feed & Event Stream Component (Forest Enterprise)."""

import streamlit as st
from ui.theme import (
    COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_HEADING,
    COLOR_TEXT_BODY, COLOR_TEXT_MUTED, COLOR_PRIMARY
)

def render_activity_item(
    title: str,
    subtitle: str,
    timestamp: str = None,
    icon: str = "⚡",
    status_pill_html: str = None,
):
    """Renders a single high-density activity item."""
    time_html = f'<span style="font-size: 11px; color: {COLOR_TEXT_MUTED}; font-weight: 500;">{timestamp}</span>' if timestamp else ""
    pill_html = f'<div style="margin-top: 4px;">{status_pill_html}</div>' if status_pill_html else ""

    item_html = f'''
    <div style="background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 10px 14px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 12px;">
        <div style="width: 32px; height: 32px; border-radius: 8px; background: #f0fdf4; border: 1px solid #bbf7d0; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0;">
            {icon}
        </div>
        <div style="flex-grow: 1; overflow: hidden;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 13px; font-weight: 750; color: {COLOR_TEXT_HEADING}; line-height: 1.2;">
                    {title}
                </div>
                {time_html}
            </div>
            <div style="font-size: 12px; color: {COLOR_TEXT_BODY}; margin-top: 2px;">
                {subtitle}
            </div>
            {pill_html}
        </div>
    </div>
    '''
    st.html(item_html)
