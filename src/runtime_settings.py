
"""
runtime_settings.py
--------------------
Reads Groq, Gemini and Supabase settings.

Priority:
1. Streamlit session state
2. Environment variables (.env)
3. Streamlit secrets (cloud deployment)
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


def get_groq_settings():
    return {
        "api_key": _get("GROQ_API_KEY", ""),
        "model": _get("GROQ_MODEL", "openai/gpt-oss-20b"),
    }


def get_gemini_settings():
    return {
        "api_key": _get("GEMINI_API_KEY", ""),
        "model": _get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    }


def get_supabase_settings():
    return {
        "url": _get("SUPABASE_URL", ""),
        "key": _get("SUPABASE_KEY", ""),
    }


def settings_are_configured() -> bool:
    groq = get_groq_settings()
    gemini = get_gemini_settings()
    supabase = get_supabase_settings()

    llm_configured = bool(
        groq["api_key"] or gemini["api_key"]
    )

    supabase_configured = bool(
        supabase["url"] and supabase["key"]
    )

    return llm_configured and supabase_configured
