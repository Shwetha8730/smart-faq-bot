"""
pages/1_⚙️_Settings.py
-----------------------
Connection settings page (auto-added to sidebar nav by Streamlit
because it lives in pages/).
"""

import streamlit as st
from src.runtime_settings import get_ollama_settings, get_supabase_settings

st.set_page_config(page_title="Settings — Smart FAQ Bot", page_icon="⚙️")

st.title("⚙️ Connection Settings")
st.caption("Enter your Ollama Cloud and Supabase details to run this bot.")

current_ollama = get_ollama_settings()
current_supabase = get_supabase_settings()

st.subheader("🦙 Ollama Cloud")

ollama_base_url = st.text_input("Ollama base URL", value=current_ollama["base_url"])
ollama_api_key = st.text_input("Ollama API key", value=current_ollama["api_key"], type="password")
ollama_model = st.text_input("Ollama model name", value=current_ollama["model"])

st.divider()
st.subheader("🗄️ Supabase")

supabase_url = st.text_input("Supabase Project URL", value=current_supabase["url"])
supabase_key = st.text_input("Supabase anon/public API key", value=current_supabase["key"], type="password")

st.divider()

if st.button("💾 Save settings", use_container_width=True, type="primary"):
    st.session_state["OLLAMA_BASE_URL"] = ollama_base_url.strip()
    st.session_state["OLLAMA_API_KEY"] = ollama_api_key.strip()
    st.session_state["OLLAMA_MODEL"] = ollama_model.strip()
    st.session_state["SUPABASE_URL"] = supabase_url.strip()
    st.session_state["SUPABASE_KEY"] = supabase_key.strip()
    st.success("Saved! Go back to the main chat page to use it.")

st.caption("⚠️ Session-only. For permanent defaults, edit .streamlit/secrets.toml instead.")