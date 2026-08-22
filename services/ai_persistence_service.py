"""Database-first AI conversation and bookmark persistence with session fallback."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

from services.auth_service import require_permission
from services.supabase_service import get_supabase_client


def _user_id() -> str:
    return str(require_permission("ai").get("id", ""))


def save_conversation(title: str, messages: list[dict]) -> tuple[dict, str]:
    user_id = _user_id()
    clean_title = " ".join(title.strip().split())[:120]
    if not clean_title:
        raise ValueError("Conversation title is required.")
    record = {
        "id": str(uuid4()),
        "user_id": user_id,
        "title": clean_title,
        "messages": deepcopy(messages),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        response = (
            get_supabase_client().table("ai_conversations")
            .insert({key: value for key, value in record.items() if key != "id"})
            .execute()
        )
        if response.data:
            return response.data[0], "database"
    except Exception:
        pass
    saved = st.session_state.setdefault("ai_saved_conversations", [])
    saved.insert(0, record)
    del saved[20:]
    return record, "session"


def list_conversations() -> tuple[list[dict], str]:
    user_id = _user_id()
    try:
        response = (
            get_supabase_client().table("ai_conversations")
            .select("id,title,messages,created_at,updated_at")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .limit(20)
            .execute()
        )
        return response.data or [], "database"
    except Exception:
        return st.session_state.setdefault("ai_saved_conversations", []), "session"


def toggle_bookmark(kind: str, item_id: str, metadata: dict) -> tuple[bool, str]:
    user_id = _user_id()
    if kind not in {"candidate", "job"}:
        raise ValueError("Bookmark type is invalid.")
    table = f"{kind}_bookmarks"
    id_column = f"{kind}_id"
    try:
        existing = (
            get_supabase_client().table(table)
            .select(id_column).eq("user_id", user_id).eq(id_column, item_id).limit(1).execute()
        )
        if existing.data:
            get_supabase_client().table(table).delete().eq("user_id", user_id).eq(id_column, item_id).execute()
            return False, "database"
        get_supabase_client().table(table).insert({"user_id": user_id, id_column: item_id}).execute()
        return True, "database"
    except Exception:
        key = f"ai_{kind}_bookmarks"
        bookmarks = st.session_state.setdefault(key, {})
        if item_id in bookmarks:
            bookmarks.pop(item_id)
            return False, "session"
        bookmarks[item_id] = metadata | {id_column: item_id, "saved_at": datetime.now(timezone.utc).isoformat()}
        return True, "session"


def list_bookmarks(kind: str) -> tuple[list[dict], str]:
    """List the current user's candidate or job bookmarks."""

    user_id = _user_id()
    if kind not in {"candidate", "job"}:
        raise ValueError("Bookmark type is invalid.")
    table = f"{kind}_bookmarks"
    id_column = f"{kind}_id"
    try:
        response = (
            get_supabase_client().table(table)
            .select(f"{id_column},created_at")
            .eq("user_id", user_id).order("created_at", desc=True).execute()
        )
        return response.data or [], "database"
    except Exception:
        return list(
            st.session_state.setdefault(f"ai_{kind}_bookmarks", {}).values()
        ), "session"
