"""
runtime_settings.py
--------------------
Reads Ollama/Supabase settings: Settings page (session) first,
then .streamlit/secrets.toml / .env as fallback.
"""

import os

try:
    import streamlit as st
except Exception:
    st = None


def _get(key: str, default: str = "") -> str:
    if st is not None and key in st.session_state and st.session_state[key]:
        return st.session_state[key]
    value = os.getenv(key)
    if value:
        return value
    if st is not None:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
    return default


def get_ollama_settings():
    return {
        "base_url": _get("OLLAMA_BASE_URL", "https://ollama.com"),
        "api_key": _get("OLLAMA_API_KEY", ""),
        "model": _get("OLLAMA_MODEL", "gpt-oss:20b"),
    }


def get_supabase_settings():
    return {
        "url": _get("SUPABASE_URL", ""),
        "key": _get("SUPABASE_KEY", ""),
    }


def settings_are_configured() -> bool:
    ollama = get_ollama_settings()
    supabase = get_supabase_settings()
    return bool(
        ollama["base_url"] and ollama["model"] and ollama["api_key"]
        and supabase["url"] and supabase["key"]
    )