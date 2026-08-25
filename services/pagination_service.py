"""Server-Side & Dataframe Pagination Service for High-Scale Datasets."""

from __future__ import annotations

import math
import pandas as pd
import streamlit as st
from typing import Any, Dict, Tuple


def paginate_dataframe(
    df: pd.DataFrame,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Slice a dataframe to a specific page and return pagination metadata."""
    if df is None or df.empty:
        return pd.DataFrame(), {
            "total_rows": 0,
            "total_pages": 1,
            "current_page": 1,
            "page_size": page_size,
            "has_prev": False,
            "has_next": False,
            "start_idx": 0,
            "end_idx": 0,
        }

    total_rows = len(df)
    page_size = max(page_size, 1)
    total_pages = max(math.ceil(total_rows / page_size), 1)
    current_page = min(max(page, 1), total_pages)

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)

    sliced_df = df.iloc[start_idx:end_idx].copy()

    meta = {
        "total_rows": total_rows,
        "total_pages": total_pages,
        "current_page": current_page,
        "page_size": page_size,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
        "start_idx": start_idx + 1,
        "end_idx": end_idx,
    }
    return sliced_df, meta


def render_pagination_controls(meta: Dict[str, Any], key_prefix: str = "pagination") -> int:
    """Render a sleek, accessible Streamlit pagination bar."""
    total_pages = meta.get("total_pages", 1)
    current_page = meta.get("current_page", 1)
    total_rows = meta.get("total_rows", 0)
    start_idx = meta.get("start_idx", 0)
    end_idx = meta.get("end_idx", 0)

    if total_pages <= 1 and total_rows <= 25:
        return current_page

    c, col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1, 1])
    with c:
        st.caption(f"Showing {start_idx}-{end_idx} of {total_rows}")

    with col1:
        if st.button("⏮️ First", key=f"{key_prefix}_first", disabled=not meta.get("has_prev")):
            return 1

    with col2:
        if st.button("◀️ Prev", key=f"{key_prefix}_prev", disabled=not meta.get("has_prev")):
            return max(current_page - 1, 1)

    with col3:
        st.markdown(f"<div style='text-align:center; font-size:12px; padding-top:8px;'>Page <b>{current_page}</b> of <b>{total_pages}</b></div>", unsafe_allow_html=True)

    with col4:
        if st.button("Next ▶️", key=f"{key_prefix}_next", disabled=not meta.get("has_next")):
            return min(current_page + 1, total_pages)

    with col5:
        if st.button("Last ⏭️", key=f"{key_prefix}_last", disabled=not meta.get("has_next")):
            return total_pages

    return current_page
