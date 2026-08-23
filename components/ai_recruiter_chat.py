"""Streamlit UI for the read-only AI Recruiter chat."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st

from services.ai_recruiter_service import answer_recruiter_query
from services.ai_persistence_service import (
    list_conversations,
    list_bookmarks,
    save_conversation,
    toggle_bookmark,
)


SUGGESTIONS = [
    "Show Python candidates",
    "Show candidates with more than 5 years experience",
    "Show candidates with ATS score above 80",
    "Show candidates scheduled this week",
]


def _display_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "Not available"
    if value is None:
        return "Not available"
    try:
        if pd.isna(value):
            return "Not available"
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    return text or "Not available"


def hydrate_candidate_bookmarks(
    bookmarks: list[dict[str, Any]],
    candidates: pd.DataFrame,
    applications: pd.DataFrame,
    jobs: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    """Resolve persisted candidate bookmark IDs into display metadata."""

    title_by_job_id: dict[str, str] = {}
    if not jobs.empty and {"id", "title"}.issubset(jobs.columns):
        title_by_job_id = {
            str(row.get("id", "")).strip(): _display_value(row.get("title"))
            for _, row in jobs.iterrows()
            if str(row.get("id", "")).strip()
        }

    latest_job_by_candidate_id: dict[str, str] = {}
    if (
        not applications.empty
        and {"candidate_id", "job_id"}.issubset(applications.columns)
    ):
        candidate_applications = applications.copy()
        if "applied_at" in candidate_applications.columns:
            candidate_applications["_applied_at"] = pd.to_datetime(
                candidate_applications["applied_at"],
                errors="coerce",
                utc=True,
            )
            candidate_applications = candidate_applications.sort_values(
                "_applied_at",
                ascending=False,
                na_position="last",
            )
        candidate_applications = candidate_applications.drop_duplicates(
            "candidate_id",
            keep="first",
        )
        latest_job_by_candidate_id = {
            str(row.get("candidate_id", "")).strip(): str(
                row.get("job_id", "")
            ).strip()
            for _, row in candidate_applications.iterrows()
            if str(row.get("candidate_id", "")).strip()
        }

    hydrated: dict[str, dict[str, Any]] = {}
    for bookmark in bookmarks:
        candidate_id = str(bookmark.get("candidate_id", "")).strip()
        if not candidate_id:
            continue
        candidate_matches = pd.DataFrame()
        if not candidates.empty and "id" in candidates.columns:
            candidate_matches = candidates[
                candidates["id"].astype(str).eq(candidate_id)
            ]
        if candidate_matches.empty:
            hydrated[candidate_id] = {
                **bookmark,
                "candidate_id": candidate_id,
                "Candidate": "Candidate no longer available",
                "Job": "Role not available",
            }
            continue

        candidate = candidate_matches.iloc[0]
        job_id = latest_job_by_candidate_id.get(candidate_id, "")
        associated_job = title_by_job_id.get(job_id, "")
        current_role = _display_value(candidate.get("current_role"))
        hydrated[candidate_id] = {
            **bookmark,
            "candidate_id": candidate_id,
            "Candidate": _display_value(candidate.get("full_name")),
            "Job": (
                associated_job
                or (current_role if current_role != "Not available" else "Not assigned")
            ),
        }
    return hydrated


def _candidate_card(candidate: dict[str, Any], card_key: str) -> None:
    candidate_id = str(candidate.get("candidate_id", "")).strip()
    cand_name = _display_value(candidate.get("Candidate"))
    job_title = _display_value(candidate.get("Job"))
    stage = _display_value(candidate.get("Stage"))
    exp = _display_value(candidate.get("Experience"))
    score_raw = candidate.get("Candidate score")
    ats_raw = candidate.get("ATS score")
    skills = _display_value(candidate.get("Skills"))
    recommendation = _display_value(candidate.get("Recommendation"))

    try:
        score = int(float(score_raw))
    except Exception:
        score = 75

    try:
        ats = int(float(ats_raw))
    except Exception:
        ats = 80

    initials = "".join([p[0].upper() for p in cand_name.split()[:2]]) if cand_name != "Not available" else "CD"

    stage_lower = stage.lower()
    if any(s in stage_lower for s in ("select", "hire", "join")):
        badge_bg, badge_color = "#dcfce7", "#15803d"
    elif any(s in stage_lower for s in ("interview", "sched")):
        badge_bg, badge_color = "#e0e7ff", "#4338ca"
    elif any(s in stage_lower for s in ("reject", "disqual")):
        badge_bg, badge_color = "#fee2e2", "#b91c1c"
    else:
        badge_bg, badge_color = "#fef3c7", "#b45309"

    bookmarks = st.session_state.setdefault("ai_candidate_bookmarks", {})
    is_bookmarked = candidate_id in bookmarks if candidate_id else False

    with st.container(border=True):
        c_top1, c_top2 = st.columns([4, 1])
        with c_top1:
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:12px;">'
                f'<div style="width:42px; height:42px; border-radius:12px; background:#ecfdf5; color:#059669; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:15px; border:1px solid #a7f3d0;">{initials}</div>'
                f'<div>'
                f'<div style="font-weight:750; color:#0f172a; font-size:16px;">{html.escape(cand_name)}</div>'
                f'<div style="color:#64748b; font-size:12px;">{html.escape(job_title)} • ⏳ {exp} yrs exp</div>'
                f'</div>'
                f'<span style="background:{badge_bg}; color:{badge_color}; border-radius:20px; padding:3px 10px; font-size:11px; font-weight:700; margin-left:8px;">{stage}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        with c_top2:
            if candidate_id:
                if st.button(
                    "Saved" if is_bookmarked else "Bookmark",
                    icon=":material/bookmark:" if is_bookmarked else ":material/bookmark_add:",
                    key=f"bookmark_{card_key}_{candidate_id}",
                    use_container_width=True
                ):
                    saved, storage = toggle_bookmark(
                        "candidate",
                        candidate_id,
                        {
                            "Candidate": cand_name,
                            "Job": job_title,
                        },
                    )
                    if storage == "database":
                        if saved:
                            bookmarks[candidate_id] = candidate
                        else:
                            bookmarks.pop(candidate_id, None)
                    st.rerun()

        st.markdown(
            f'<div style="display:flex; gap:16px; margin: 10px 0 8px 0;">'
            f'<div style="flex:1;">'
            f'<div style="display:flex; justify-content:space-between; font-size:11px; color:#64748b; margin-bottom:3px;"><span>Candidate Fit Score</span><strong style="color:#0f172a;">{score}%</strong></div>'
            f'<div style="width:100%; height:6px; background:#f1f5f9; border-radius:10px; overflow:hidden;"><div style="width:{min(max(score, 0), 100)}%; height:100%; background:linear-gradient(90deg, #10b981, #84cc16); border-radius:10px;"></div></div>'
            f'</div>'
            f'<div style="flex:1;">'
            f'<div style="display:flex; justify-content:space-between; font-size:11px; color:#64748b; margin-bottom:3px;"><span>ATS Resume Match</span><strong style="color:#0f172a;">{ats}%</strong></div>'
            f'<div style="width:100%; height:6px; background:#f1f5f9; border-radius:10px; overflow:hidden;"><div style="width:{min(max(ats, 0), 100)}%; height:100%; background:linear-gradient(90deg, #059669, #10b981); border-radius:10px;"></div></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.caption(f"**Skills:** `{skills}`")
        if recommendation != "Not available":
            st.caption(f"**Recommendation:** `{recommendation}`")


def _render_response(response: dict[str, Any], prefix: str = "r0") -> None:
    st.markdown(response["summary"])
    st.caption(f"Confidence: {response['confidence']}")
    with st.expander("How this answer was determined"):
        st.write(response["reasoning"])

    comparison = response.get("comparison", [])
    if comparison:
        comparison_frame = pd.DataFrame(comparison)
        for column in comparison_frame.columns:
            comparison_frame[column] = comparison_frame[column].map(
                _display_value
            )
        st.dataframe(
            comparison_frame,
            hide_index=True,
            width="stretch",
        )

    candidates = response.get("candidates", [])
    if candidates:
        for index, candidate in enumerate(candidates):
            _candidate_card(candidate, f"{prefix}_{response.get('intent', 'result')}_{index}")
    elif response.get("intent") not in {"blocked", "empty", "unsupported", "no_data"}:
        st.info("No candidates matched this question.")


def render_ai_recruiter_chat(
    candidates: pd.DataFrame,
    applications: pd.DataFrame,
    jobs: pd.DataFrame,
    interviews: pd.DataFrame,
) -> None:
    """Render chat history and route new questions to safe local tools."""

    st.session_state.setdefault("ai_recruiter_messages", [])
    st.session_state.setdefault("ai_recruiter_suggestion", None)
    st.session_state.setdefault("ai_recent_searches", [])
    st.session_state.setdefault("ai_saved_conversations", [])
    st.session_state.setdefault("ai_candidate_bookmarks", {})

    header, action = st.columns([4, 2])
    with header:
        st.markdown('<div class="main-title">AI Recruiter</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="main-subtitle">Ask read-only questions about candidates, '
            'applications, jobs and interviews.</div>',
            unsafe_allow_html=True,
        )
    with action:
        with st.container(horizontal=True, horizontal_alignment="right"):
            with st.popover("Save conversation", icon=":material/save:"):
                conversation_title = st.text_input(
                    "Conversation title",
                    value=(
                        st.session_state.ai_recruiter_messages[0].get("content", "")[:80]
                        if st.session_state.ai_recruiter_messages else ""
                    ),
                    key="ai_conversation_title",
                )
                if st.button(
                    "Save",
                    type="primary",
                    disabled=not st.session_state.ai_recruiter_messages,
                    key="save_ai_conversation",
                ):
                    try:
                        _, storage = save_conversation(
                            conversation_title,
                            st.session_state.ai_recruiter_messages,
                        )
                    except Exception as error:
                        st.error(f"Conversation could not be saved: {error}")
                    else:
                        st.toast(f"Conversation saved to {storage} storage.")
            if st.button(
                "Clear chat",
                icon=":material/delete_sweep:",
                disabled=not st.session_state.ai_recruiter_messages,
            ):
                st.session_state.ai_recruiter_messages = []
                st.session_state.ai_recruiter_suggestion = None
                st.rerun()

    messages_json = json.dumps(
        st.session_state.ai_recruiter_messages,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
    with st.container(horizontal=True):
        st.download_button(
            "Export conversation",
            data=messages_json,
            file_name="ai-recruiter-conversation.json",
            mime="application/json",
            icon=":material/download:",
            disabled=not st.session_state.ai_recruiter_messages,
        )
        with st.popover("Recent searches", icon=":material/history:"):
            if not st.session_state.ai_recent_searches:
                st.caption("No recent searches yet.")
            for index, search in enumerate(st.session_state.ai_recent_searches):
                if st.button(search, key=f"recent_search_{index}", width="stretch"):
                    st.session_state.ai_recruiter_suggestion = search
                    st.rerun()
        with st.popover("Saved conversations", icon=":material/folder_open:"):
            if st.button("Load saved conversations", key="load_saved_ai_conversations"):
                conversations, storage = list_conversations()
                st.session_state["ai_loaded_conversations"] = conversations
                st.session_state["ai_conversation_storage"] = storage
            saved_conversations = st.session_state.get("ai_loaded_conversations", [])
            if not saved_conversations:
                st.caption("No conversations loaded.")
            else:
                st.caption(
                    f"Source: {st.session_state.get('ai_conversation_storage', 'session')}"
                )
                for conversation in saved_conversations:
                    if st.button(
                        conversation.get("title", "Untitled conversation"),
                        key=f"reload_conversation_{conversation.get('id')}",
                        width="stretch",
                    ):
                        st.session_state.ai_recruiter_messages = conversation.get(
                            "messages", []
                        )
                        st.rerun()
                    st.caption(
                        str(
                            conversation.get("updated_at")
                            or conversation.get("created_at")
                            or conversation.get("saved_at", "")
                        )
                    )
        with st.popover("Bookmarks", icon=":material/bookmarks:"):
            if st.button("Load candidate bookmarks", key="load_candidate_bookmarks"):
                loaded_bookmarks, source = list_bookmarks("candidate")
                hydrated_bookmarks = hydrate_candidate_bookmarks(
                    loaded_bookmarks,
                    candidates,
                    applications,
                    jobs,
                )
                st.session_state.ai_candidate_bookmarks.update(
                    hydrated_bookmarks
                )
                st.session_state["ai_bookmark_storage"] = source
            if not st.session_state.ai_candidate_bookmarks:
                st.caption("No bookmarked candidates yet.")
            for bookmark in st.session_state.ai_candidate_bookmarks.values():
                st.write(
                    f"**{bookmark.get('Candidate') or 'Candidate no longer available'}**"
                )
                st.caption(bookmark.get("Job") or "Role not available")

    if not st.session_state.ai_recruiter_messages:
        st.info(
            "Questions are mapped to allowlisted, read-only operations. Your text is "
            "never executed as SQL."
        )
        selected = st.pills(
            "Try asking",
            SUGGESTIONS,
            label_visibility="collapsed",
            key="ai_recruiter_suggestion_pills",
        )
        if selected:
            st.session_state.ai_recruiter_suggestion = selected

    for m_idx, message in enumerate(st.session_state.ai_recruiter_messages):
        msg_avatar = "🤖" if message["role"] == "assistant" else "🧑‍💼"
        with st.chat_message(message["role"], avatar=msg_avatar):
            if message["role"] == "assistant":
                _render_response(message["response"], prefix=f"turn_{m_idx}")
            else:
                st.write(message["content"])

    prompt = st.chat_input(
        "Ask about candidates, stages, jobs or interviews",
        key="ai_recruiter_input",
    )
    if not prompt and st.session_state.ai_recruiter_suggestion:
        prompt = st.session_state.ai_recruiter_suggestion
        st.session_state.ai_recruiter_suggestion = None

    if prompt:
        recent = st.session_state.ai_recent_searches
        recent[:] = [item for item in recent if item != prompt]
        recent.insert(0, prompt)
        del recent[8:]
        st.session_state.ai_recruiter_messages.append(
            {"role": "user", "content": prompt}
        )
        response = answer_recruiter_query(
            prompt,
            candidates,
            applications,
            jobs,
            interviews,
        )
        st.session_state.ai_recruiter_messages.append(
            {"role": "assistant", "response": response}
        )
        st.rerun()
