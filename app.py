"""
app.py
------
Smart FAQ Bot — Multilingual Streamlit Frontend
"""

import streamlit as st
from datetime import datetime


# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.rag_chain import answer_question
from src.config import DATA_DIR
from src.history import add_query, get_recent_queries
from src.i18n import (
    SUPPORTED_LANGUAGES,
    text_to_speech,
    speech_to_text_auto,
    detect_language,
)
from src.gov_documents import OFFICIAL_DOCUMENTS, fetch_and_index_official_document, sync_supabase_storage_to_local

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart FAQ Bot — Government Schemes",
    page_icon="🏛️",
    layout="centered",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600&family=Noto+Sans+Kannada:wght@400;500;600&family=Noto+Sans+Tamil:wght@400;500;600&family=Noto+Sans+Telugu:wght@400;500;600&family=Noto+Sans+Malayalam:wght@400;500;600&display=swap');

    :root {
        --gov-navy: #0B3D6B;
        --gov-navy-dark: #072A4D;
        --gov-navy-deeper: #051D36;
        --gov-gold: #C99A2E;
        --gov-gold-light: #E4C368;
        --gov-bg: #F6F7FA;
        --gov-card: #FFFFFF;
        --gov-border: #E2E6EE;
        --gov-text: #1B2130;
        --gov-muted: #667085;
        --gov-verified: #1E7A46;
        --gov-verified-bg: #EAF6EF;
        --gov-saffron: #FF9933;
        --gov-green: #138808;

        --font-display: 'Source Serif 4', 'Noto Serif Devanagari', Georgia, serif;
        --font-body: 'Noto Sans', 'Noto Sans Devanagari', 'Noto Sans Kannada',
                      'Noto Sans Tamil', 'Noto Sans Telugu', 'Noto Sans Malayalam',
                      -apple-system, sans-serif;
    }

    html, body, [class*="css"] {
        font-family: var(--font-body);
    }

    .stApp {
        background-color: var(--gov-bg);
        background-image:
            radial-gradient(circle at 15% 0%, rgba(11,61,107,0.035) 0%, transparent 45%),
            radial-gradient(circle at 100% 20%, rgba(201,154,46,0.04) 0%, transparent 40%);
    }

    .block-container {
        padding-top: 0.8rem;
        max-width: 760px;
    }

    /* ========================================================
       TRICOLOR FLAG STRIP
       ======================================================== */

    .tricolor-strip {
        height: 6px;
        width: 100%;
        border-radius: 6px;
        margin-bottom: 20px;
        background: linear-gradient(
            90deg,
            var(--gov-saffron) 0%, var(--gov-saffron) 33%,
            #FFFFFF 33%, #FFFFFF 66%,
            var(--gov-green) 66%, var(--gov-green) 100%
        );
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    /* ========================================================
       HEADER — letterhead treatment
       ======================================================== */

    .gov-banner {
        background: linear-gradient(160deg, var(--gov-navy) 0%, var(--gov-navy-dark) 55%, var(--gov-navy-deeper) 100%);
        border-radius: 14px;
        padding: 28px 30px 24px 30px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(5,29,54,0.22);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(201,154,46,0.35);
    }

    .gov-banner::before {
        content: "";
        position: absolute;
        inset: 0;
        background-image: repeating-linear-gradient(
            135deg,
            rgba(255,255,255,0.025) 0px,
            rgba(255,255,255,0.025) 1px,
            transparent 1px,
            transparent 14px
        );
        pointer-events: none;
    }

    .gov-banner::after {
        content: "";
        position: absolute;
        top: -30px;
        right: -30px;
        width: 160px;
        height: 160px;
        border: 1.5px solid rgba(201,154,46,0.18);
        border-radius: 50%;
    }

    .gov-banner-top {
        display: flex;
        align-items: center;
        gap: 16px;
        position: relative;
        z-index: 1;
    }

    /* Emblem — stylized Ashoka Chakra motif, not the official state seal */
    .gov-emblem {
        width: 56px;
        height: 56px;
        flex-shrink: 0;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, rgba(255,255,255,0.16), rgba(255,255,255,0.05));
        border: 1.5px solid var(--gov-gold);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 0 3px rgba(201,154,46,0.12);
    }

    .gov-emblem svg {
        width: 34px;
        height: 34px;
    }

    .gov-banner h1 {
        font-family: var(--font-display);
        color: #FFFFFF;
        font-size: 27px;
        font-weight: 600;
        margin: 0;
        line-height: 1.2;
        letter-spacing: 0.2px;
    }

    .gov-banner-tag {
        color: var(--gov-gold-light);
        font-size: 12.5px;
        font-weight: 500;
        letter-spacing: 0.3px;
        margin-top: 4px;
        font-family: var(--font-body);
    }

    /* ========================================================
       CAPTIONS / DISCLAIMER
       ======================================================== */

    .gov-subtext {
        font-size: 14px;
        color: var(--gov-muted);
        margin: 2px 0;
        line-height: 1.55;
    }

    .gov-disclaimer {
        background: #FFF8E8;
        border: 1px solid #F0DBA0;
        border-left: 3px solid var(--gov-gold);
        border-radius: 8px;
        padding: 11px 15px;
        margin: 10px 0;
        font-size: 13.5px;
        color: #6B5416;
        line-height: 1.5;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid var(--gov-border);
    }

    .sidebar-section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: var(--font-display);
        color: var(--gov-navy);
        font-weight: 600;
        font-size: 16px;
        margin-top: 4px;
        margin-bottom: 10px;
    }

    .sidebar-count-badge {
        background: var(--gov-navy);
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 600;
        font-family: var(--font-body);
        padding: 2px 9px;
        border-radius: 999px;
    }

    section[data-testid="stSidebar"] hr {
        margin-top: 18px;
        margin-bottom: 18px;
        border-color: var(--gov-border);
    }

    /* Scheme chips */
    .scheme-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    .scheme-chip {
        background: #EEF3FA;
        color: var(--gov-navy);
        border: 1px solid #D6E2F2;
        border-radius: 8px;
        padding: 6px 11px;
        font-size: 12.5px;
        font-weight: 500;
        white-space: nowrap;
        transition: background-color 0.15s ease, border-color 0.15s ease;
    }

    .scheme-chip:hover {
        background: #E1EBF9;
        border-color: var(--gov-gold);
    }

    .history-title {
        font-family: var(--font-display);
        font-size: 16px;
        font-weight: 600;
        color: var(--gov-navy);
        margin-top: 5px;
        margin-bottom: 4px;
    }

    .history-subtitle {
        font-size: 12px;
        color: var(--gov-muted);
        margin-bottom: 10px;
    }

    section[data-testid="stSidebar"] button {
        border-radius: 9px !important;
        text-align: left;
        border: 1px solid var(--gov-border) !important;
        font-size: 13.5px !important;
        transition: border-color 0.15s ease, background-color 0.15s ease;
    }

    section[data-testid="stSidebar"] button:hover {
        border-color: var(--gov-gold) !important;
        color: var(--gov-navy) !important;
        background-color: #FFFBF0 !important;
    }

    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(15,23,42,0.045);
        border: 1px solid var(--gov-border);
    }

    div[data-testid="stChatMessage"]:nth-of-type(odd) {
        background: var(--gov-card);
    }

    div[data-testid="stChatMessage"]:nth-of-type(even) {
        background: #F3F7FC;
        border-left: 3px solid var(--gov-navy);
    }

    /* ========================================================
       BADGES
       ======================================================== */

    .gov-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        font-weight: 600;
        padding: 5px 11px;
        border-radius: 7px;
        margin-top: 6px;
        margin-right: 6px;
        letter-spacing: 0.1px;
    }

    .gov-badge-lang {
        background: #EEF3FA;
        color: var(--gov-navy);
        border: 1px solid #D6E2F2;
    }

    .gov-badge-verified {
        background: var(--gov-verified-bg);
        color: var(--gov-verified);
        border: 1px solid #BFE3CC;
    }

    /* ========================================================
       CHAT INPUT — position unchanged, styling only
       ======================================================== */

    div[data-testid="stChatInput"] {
        border-radius: 14px;
        border: 1px solid var(--gov-border);
        box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    }

    h1, h2, h3 {
        font-family: var(--font-display);
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .gov-banner {
            padding: 20px 20px 18px 20px;
        }
        .gov-banner h1 {
            font-size: 21px;
        }
        .gov-emblem {
            width: 44px;
            height: 44px;
        }
        .gov-emblem svg {
            width: 26px;
            height: 26px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# RESTORE PREVIOUSLY-FETCHED OFFICIAL DOCUMENTS FROM SUPABASE
# (local disk doesn't persist across redeploys, Supabase does)
# ============================================================

if "synced_documents" not in st.session_state:
    synced_count = sync_supabase_storage_to_local()
    st.session_state["synced_documents"] = True
    if synced_count > 0:
        st.toast(f"Restored {synced_count} previously-fetched document(s).")


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# TRICOLOR ACCENT STRIP
# ============================================================

st.markdown('<div class="tricolor-strip"></div>', unsafe_allow_html=True)


# ============================================================
# PAGE HEADER — with Ashoka Chakra emblem (SVG, 24 spokes)
# ============================================================

import math as _math

ASHOKA_CHAKRA_SVG = (
    '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="50" cy="50" r="45" fill="none" stroke="#E4C368" stroke-width="3"/>'
    '<circle cx="50" cy="50" r="6" fill="#E4C368"/>'
    '<g stroke="#E4C368" stroke-width="2.2">'
)

for _i in range(24):
    _angle = (_math.pi * 2 * _i) / 24
    _x1 = 50 + 8 * _math.cos(_angle)
    _y1 = 50 + 8 * _math.sin(_angle)
    _x2 = 50 + 42 * _math.cos(_angle)
    _y2 = 50 + 42 * _math.sin(_angle)
    ASHOKA_CHAKRA_SVG += f'<line x1="{_x1:.1f}" y1="{_y1:.1f}" x2="{_x2:.1f}" y2="{_y2:.1f}"/>'

ASHOKA_CHAKRA_SVG += "</g></svg>"

st.markdown(
    f"""
    <div class="gov-banner">
        <div class="gov-banner-top">
            <div class="gov-emblem">{ASHOKA_CHAKRA_SVG}</div>
            <div>
                <h1>Smart FAQ Bot</h1>
                <div class="gov-banner-tag">Government Scheme Assistant · Citizen Services</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="gov-subtext">Ask about eligibility, documents, benefits, or how to apply for government schemes.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="gov-disclaimer">⚠️ Answers are generated only from approved scheme documents. Always verify with the official source before applying.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="gov-subtext">🌐 Type or speak in English, Hindi, Kannada, Tamil, Telugu, or Malayalam.</p>',
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

        # ========================================================
    # OFFICIAL GOVERNMENT DOCUMENTS (auto-fetch, no manual upload)
    # ========================================================

    st.header("📚 Official Government Documents")
    st.caption(
        "Documents are downloaded directly from verified government "
        "portals. No manual upload is required."
    )

    selected_scheme = st.selectbox(
        "Select an approved government guideline",
        list(OFFICIAL_DOCUMENTS.keys()),
    )

    if st.button("⬇️ Fetch and index official guideline", use_container_width=True):
        with st.spinner("Downloading from official portal..."):
            success, message = fetch_and_index_official_document(selected_scheme)

        if success:
            st.success(message)
            with st.spinner("Re-indexing document database..."):
                from src.ingest import main as run_ingestion
                run_ingestion()
            st.success("Indexed! You can now ask about this scheme.")
        else:
            st.error(message)

    st.caption(
        "The source URL is stored with the index. Verify the linked "
        "government portal before relying on an answer."
    )

    st.divider()

    # ========================================================
    # SCHEMES COVERED — as chip pills, with a count badge
    # ========================================================

    scheme_files = sorted(DATA_DIR.glob("*"))
    scheme_names = []

    for file_path in scheme_files:
        if file_path.suffix.lower() in (".pdf", ".txt"):
            scheme_names.append(
                file_path.stem.replace("_", " ").replace("-", " ").title()
            )

    st.markdown(
        f'<div class="sidebar-section-header">'
        f'<span>📄 Schemes Covered</span>'
        f'<span class="sidebar-count-badge">{len(scheme_names)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if scheme_names:
        chips_html = '<div class="scheme-chip-row">'
        for name in scheme_names:
            chips_html += f'<span class="scheme-chip">{name}</span>'
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.write("No scheme documents found in data/schemes/")

    # ========================================================
    # TRY ASKING
    # ========================================================

    st.divider()
    st.subheader("💡 Try asking")

    example_questions = [
        "Documents needed for Ayushman Bharat?",
        "How to apply for PM-Kisan?",
    ]

    for i, example in enumerate(example_questions):
        if st.button(example, key=f"example_question_{i}", use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()

    # ========================================================
    # RECENT HISTORY
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="history-title">🕘 Recent Queries</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="history-subtitle">Click a previous question to ask it again.</div>',
        unsafe_allow_html=True,
    )

    history = get_recent_queries(limit=5)

    if history:
        for item in history:
            query = item["question"]
            timestamp = item["timestamp"]

            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                display_time = dt.strftime("%I:%M %p")
            except Exception:
                display_time = timestamp

            display_query = query
            if len(display_query) > 42:
                display_query = display_query[:39] + "..."

            button_text = f"💬 {display_query}\n🕐 {display_time}"

            if st.button(button_text, key=f"history_{item['id']}", use_container_width=True):
                st.session_state.pending_question = query
                st.rerun()
    else:
        st.caption("No recent queries yet.")

    # ========================================================
    # CLEAR CHAT
    # ========================================================

    st.divider()

    if st.button("🗑️ Clear chat", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg["role"] == "assistant" and msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

        if msg["role"] == "assistant" and msg.get("sources"):
            st.caption("📄 Source: " + ", ".join(msg["sources"]))


# ============================================================
# CHAT INPUT — position unchanged
# ============================================================

chat_input = st.chat_input(
    "Ask about a government scheme...",
    accept_audio=True,
    audio_sample_rate=16000,
)


# ============================================================
# QUESTION VARIABLES
# ============================================================

question = None
input_was_voice = False
detected_lang = "en"


# ============================================================
# HANDLE CHAT INPUT
# ============================================================

if chat_input is not None:

    typed_text = ""
    if hasattr(chat_input, "text"):
        typed_text = chat_input.text

    audio_file = None
    if hasattr(chat_input, "audio"):
        audio_file = chat_input.audio

    if typed_text and typed_text.strip():
        question = typed_text.strip()
        input_was_voice = False

    elif audio_file is not None:
        with st.spinner("🎙️ Listening..."):
            try:
                audio_bytes = audio_file.read()
                transcribed, stt_lang = speech_to_text_auto(audio_bytes)
            except Exception:
                transcribed = None
                stt_lang = None

        if transcribed:
            question = transcribed
            detected_lang = stt_lang or "en"
            input_was_voice = True
        else:
            st.warning(
                "Couldn't understand the audio clearly. "
                "Please try again or type your question."
            )


# ============================================================
# SIDEBAR QUESTION
# ============================================================

if question is None and st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None
    input_was_voice = False


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    if not input_was_voice:
        detected_lang = detect_language(question)

    add_query(question)

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        with st.spinner("🔎 Checking approved documents..."):
            try:
                answer, sources, chunks, is_from_web = answer_question(
                    question,
                    question_language=detected_lang,
                )
            except FileNotFoundError as e:
                answer = f"⚠️ Setup issue: {e}"
                sources = []
                chunks = []
                is_from_web = False
            except Exception as e:
                answer = f"⚠️ Something went wrong: {e}"
                sources = []
                chunks = []
                is_from_web = False

        st.write(answer)

        st.markdown(
            f'<span class="gov-badge gov-badge-lang">🌐 '
            f'{SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)}</span>',
            unsafe_allow_html=True,
        )

        audio_bytes = None
        if input_was_voice:
            audio_bytes = text_to_speech(answer, detected_lang)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")

        if is_from_web:
            st.warning(
                "🌐 This answer came from a web source, not an approved document."
            )

        elif sources:
            st.markdown(
                f'<span class="gov-badge gov-badge-verified">✅ Verified: '
                f'{", ".join(sources)}</span>',
                unsafe_allow_html=True,
            )

            with st.expander("🔍 See the exact text used to answer this"):
                for i, chunk in enumerate(chunks, 1):
                    scheme = chunk.metadata.get("scheme", "Unknown")
                    document_language = chunk.metadata.get("language", "unknown")

                    st.markdown(f"**Chunk {i} — {scheme}**")
                    st.caption("Document language: " + document_language)

                    preview = chunk.page_content[:400]
                    if len(chunk.page_content) > 400:
                        preview += "..."

                    st.text(preview)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "audio": audio_bytes,
            "sources": sources,
            "is_from_web": is_from_web,
        }
    )
