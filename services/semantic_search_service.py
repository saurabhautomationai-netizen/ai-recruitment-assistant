"""Safe local relevance fallback and pgvector migration boundary."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

import pandas as pd


TEXT_FIELDS = (
    "full_name", "skills", "resume_summary", "summary", "experience",
    "education", "previous_companies", "current_company", "current_role",
)


def candidate_search_text(candidate: dict[str, Any]) -> str:
    """Compose search text only from fields already present on a candidate."""

    parts = []
    for field in TEXT_FIELDS:
        if field not in candidate:
            continue
        value = candidate.get(field)
        if isinstance(value, dict):
            value = " ".join(f"{key} {item}" for key, item in value.items())
        elif isinstance(value, (list, tuple, set)):
            value = " ".join(map(str, value))
        if value is not None and str(value).strip():
            parts.append(str(value).strip())
    return "\n".join(parts)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#.-]{2,}", text.casefold())


def rank_candidates_locally(query: str, candidates: pd.DataFrame) -> pd.DataFrame:
    """Rank real candidate text with deterministic cosine term relevance.

    This is an explicitly labelled fallback, not an embedding search.
    """

    if candidates.empty or not query.strip():
        return pd.DataFrame()
    query_counts = Counter(_tokens(query))
    if not query_counts:
        return pd.DataFrame()
    query_norm = math.sqrt(sum(value * value for value in query_counts.values()))
    rows = []
    for candidate in candidates.to_dict("records"):
        text = candidate_search_text(candidate)
        counts = Counter(_tokens(text))
        norm = math.sqrt(sum(value * value for value in counts.values()))
        dot = sum(value * counts.get(token, 0) for token, value in query_counts.items())
        score = dot / (query_norm * norm) if norm else 0.0
        if score > 0:
            row = dict(candidate)
            row["relevance_score"] = round(score * 100, 1)
            rows.append(row)
    return pd.DataFrame(rows).sort_values("relevance_score", ascending=False) if rows else pd.DataFrame()
