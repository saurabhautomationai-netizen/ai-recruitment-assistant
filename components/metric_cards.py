import streamlit as st


def metric_card(
    title: str,
    value: str | int,
    change: str,
    icon: str,
) -> None:
    """Render one reusable dashboard metric card."""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <span class="metric-icon">{icon}</span>
                <span class="metric-change">{change}</span>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )