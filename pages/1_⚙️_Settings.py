
import streamlit as st

from src.runtime_settings import (
    get_groq_settings,
    get_gemini_settings,
    get_supabase_settings,
)

st.set_page_config(
    page_title="Settings | Smart FAQ Bot",
    page_icon="⚙️",
    layout="centered"
)

st.title("⚙️ Connection Settings")
st.caption("Configure the AI providers and database.")

groq = get_groq_settings()
gemini = get_gemini_settings()
supabase = get_supabase_settings()

st.subheader("⚡ Groq AI")

groq_api_key = st.text_input(
    "Groq API Key",
    value=groq["api_key"],
    type="password"
)

groq_model = st.text_input(
    "Groq Model",
    value=groq["model"]
)

st.divider()

st.subheader("✨ Google Gemini AI")

gemini_api_key = st.text_input(
    "Gemini API Key",
    value=gemini["api_key"],
    type="password"
)

gemini_model = st.text_input(
    "Gemini Model",
    value=gemini["model"]
)

st.divider()

st.subheader("🗄️ Supabase Database")

supabase_url = st.text_input(
    "Supabase Project URL",
    value=supabase["url"]
)

supabase_key = st.text_input(
    "Supabase API Key",
    value=supabase["key"],
    type="password"
)

st.divider()

if st.button("💾 Save Settings", type="primary", use_container_width=True):
    st.session_state["GROQ_API_KEY"] = groq_api_key.strip()
    st.session_state["GROQ_MODEL"] = groq_model.strip()
    st.session_state["GEMINI_API_KEY"] = gemini_api_key.strip()
    st.session_state["GEMINI_MODEL"] = gemini_model.strip()
    st.session_state["SUPABASE_URL"] = supabase_url.strip()
    st.session_state["SUPABASE_KEY"] = supabase_key.strip()

    st.success("Settings saved for this session.")

st.info(
    "Groq is the primary AI provider. Gemini is the fallback provider."
)

st.caption("Settings are stored for the current Streamlit session.")
