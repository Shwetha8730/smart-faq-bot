"""
history.py
----------
Supabase-based recent query history (replaces SQLite for cloud deployment).
"""

from datetime import datetime
from supabase import create_client
from src.runtime_settings import get_supabase_settings


def _get_client():
    settings = get_supabase_settings()
    if not settings["url"] or not settings["key"]:
        return None
    return create_client(settings["url"], settings["key"])


def add_query(question: str):
    if not question or not question.strip():
        return

    client = _get_client()
    if client is None:
        return

    question = question.strip()

    try:
        client.table("query_history").delete().eq("question", question).execute()
        client.table("query_history").insert(
            {"question": question, "timestamp": datetime.utcnow().isoformat()}
        ).execute()

        result = client.table("query_history").select("id").order("id", desc=True).execute()
        ids = [row["id"] for row in result.data]
        if len(ids) > 10:
            client.table("query_history").delete().in_("id", ids[10:]).execute()
    except Exception:
        pass


def get_recent_queries(limit=5):
    client = _get_client()
    if client is None:
        return []
    try:
        result = (
            client.table("query_history")
            .select("*")
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception:
        return []


def clear_history():
    client = _get_client()
    if client is None:
        return
    try:
        client.table("query_history").delete().neq("id", 0).execute()
    except Exception:
        pass