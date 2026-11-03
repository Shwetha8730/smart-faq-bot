
"""
rag_chain.py
------------
Multilingual RAG engine using Groq and Gemini.

Features:
- Automatic government scheme detection
- Scheme-specific Chroma retrieval
- Multilingual question support
- Groq as primary LLM
- Gemini as fallback LLM
- Source document tracking
- Answer caching
"""

import sys
import re
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# ============================================================
# LANGCHAIN IMPORTS
# ============================================================

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# ============================================================
# RUNTIME SETTINGS
# ============================================================

from src.runtime_settings import (
    get_groq_settings,
    get_gemini_settings,
)

# ============================================================
# CONFIG
# ============================================================

from src.config import (
    VECTORSTORE_DIR,
    EMBEDDING_MODEL_NAME,
    TOP_K,
    SYSTEM_PROMPT,
    FALLBACK_MESSAGE,
    SUPPORTED_LANGUAGES,
)

# ============================================================
# GLOBAL OBJECTS
# ============================================================

_embeddings = None
_vectorstore = None
_answer_cache = {}

# ============================================================
# SCHEME ALIASES
# These names match the scheme metadata in ingest.py.
# ============================================================

SCHEME_ALIASES = {
    "Ayushman Bharat (PM-JAY)": [
        "ayushman bharat",
        "ayushman",
        "pm-jay",
        "pmjay",
        "pradhan mantri jan aarogya",
        "jan arogya",
    ],

    "PM-KISAN – Pradhan Mantri Kisan Samman Nidhi": [
        "pm-kisan",
        "pm kisan",
        "pmkisan",
        "kisan samman",
    ],

    "Pradhan Mantri Fasal Bima Yojana (PMFBY)": [
        "pmfby",
        "fasal bima",
        "crop insurance",
    ],

    "Shakti Yojana – Free Bus Scheme": [
        "shakti yojana",
        "free bus scheme",
    ],

    "Gruha Jyothi Scheme": [
        "gruha jyothi",
        "gruhajyothi",
    ],

    "Mission Shakti – Women Empowerment Programme": [
        "mission shakti",
    ],

    "National Scholarship for Postgraduate Studies": [
        "national scholarship",
        "postgraduate scholarship",
        "nsp",
    ],

    "Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY)": [
        "pm-ajay",
        "pm ajay",
        "pm ajay scheme",
    ],

    "PM POSHAN – Pradhan Mantri Poshan Shakti Nirman": [
        "pm poshan",
        "poshan shakti",
    ],

    "PM SVANidhi – Street Vendor's AtmaNirbhar Nidhi": [
        "pm svanidhi",
        "svanidhi",
    ],

    "Ministry of Minority Affairs – Detailed Demands for Grants": [
        "minority affairs",
        "ministry of minority affairs",
    ],
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text: str) -> str:
    """
    Convert text into lowercase words.
    Handles punctuation and hyphen variations.
    """

    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


# ============================================================
# AUTOMATIC SCHEME DETECTION
# ============================================================

def detect_scheme(question: str):
    """
    Detect the government scheme mentioned in the question.

    Returns:
        Exact scheme metadata name if detected.
        None if no scheme is identified.
    """

    normalized_question = normalize_text(question)

    padded_question = f" {normalized_question} "

    matches = []

    for scheme, aliases in SCHEME_ALIASES.items():

        for alias in aliases:

            normalized_alias = normalize_text(alias)

            padded_alias = f" {normalized_alias} "

            if padded_alias in padded_question:

                matches.append(
                    (len(normalized_alias), scheme)
                )

    if not matches:
        return None

    # Prefer the most specific matching scheme alias.
    matches.sort(reverse=True)

    return matches[0][1]


# ============================================================
# LOAD VECTOR DATABASE
# ============================================================

def _get_vectorstore():

    global _embeddings
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    if (
        not VECTORSTORE_DIR.exists()
        or not any(VECTORSTORE_DIR.iterdir())
    ):
        raise FileNotFoundError(
            "Vector database not found.\n\n"
            "Run this first:\n"
            "python -m src.ingest"
        )

    _embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )

    _vectorstore = Chroma(
        persist_directory=str(VECTORSTORE_DIR),
        embedding_function=_embeddings,
        collection_name="government_schemes",
    )

    return _vectorstore


# ============================================================
# GROQ + GEMINI LLM
# ============================================================

def _generate_answer(prompt: str) -> str:

    groq_settings = get_groq_settings()
    gemini_settings = get_gemini_settings()

    groq_error = None

    # --------------------------------------------------------
    # PRIMARY: GROQ
    # --------------------------------------------------------

    if groq_settings["api_key"]:

        try:

            print("Using Groq LLM...")

            llm = ChatGroq(
                api_key=groq_settings["api_key"],
                model=groq_settings["model"],
                temperature=0.2,
            )

            response = llm.invoke(prompt)

            return str(response.content)

        except Exception as e:

            groq_error = e

            print(f"Groq failed: {e}")
            print("Trying Gemini fallback...")

    # --------------------------------------------------------
    # FALLBACK: GEMINI
    # --------------------------------------------------------

    if gemini_settings["api_key"]:

        try:

            print("Using Gemini LLM...")

            llm = ChatGoogleGenerativeAI(
                google_api_key=gemini_settings["api_key"],
                model=gemini_settings["model"],
                temperature=0.2,
            )

            response = llm.invoke(prompt)

            return str(response.content)

        except Exception as gemini_error:

            raise RuntimeError(
                "Both LLM providers failed.\n"
                f"Groq error: {groq_error}\n"
                f"Gemini error: {gemini_error}"
            )

    if groq_error:

        raise RuntimeError(
            f"Groq failed and Gemini API key is missing: "
            f"{groq_error}"
        )

    raise RuntimeError(
        "No LLM API key configured. "
        "Please add your Groq or Gemini API key."
    )


# ============================================================
# RETRIEVE DOCUMENT CHUNKS
# ============================================================

def retrieve_chunks(
    question: str,
    k: int = TOP_K,
):

    vectorstore = _get_vectorstore()

    # Automatically identify the scheme.
    detected_scheme = detect_scheme(question)

    print(
        "Detected scheme:",
        detected_scheme or "No specific scheme detected"
    )

    # --------------------------------------------------------
    # SCHEME-SPECIFIC RETRIEVAL
    # --------------------------------------------------------

    if detected_scheme:

        print(
            f"Searching only in: {detected_scheme}"
        )

        chunks = vectorstore.similarity_search(
            question,
            k=k,
            filter={
                "scheme": detected_scheme
            },
        )

        # Do not silently search unrelated documents
        # if a specifically identified scheme has no chunks.
        if not chunks:

            print(
                "No matching chunks found for the detected scheme."
            )

        return chunks

    # --------------------------------------------------------
    # GENERAL RETRIEVAL
    # --------------------------------------------------------

    print(
        "Searching across all available scheme documents..."
    )

    return vectorstore.similarity_search(
        question,
        k=k,
    )


# ============================================================
# ANSWER FROM DOCUMENTS
# ============================================================

def _answer_from_documents(
    question: str,
    question_language: str,
):

    chunks = retrieve_chunks(question)

    if not chunks:
        return None, [], []

    context_parts = []
    sources = []

    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    for chunk in chunks:

        scheme = chunk.metadata.get(
            "scheme",
            "Unknown Scheme",
        )

        source_file = chunk.metadata.get(
            "source_file",
            "",
        )

        document_language = chunk.metadata.get(
            "language",
            "unknown",
        )

        context_parts.append(
            f"""
SOURCE SCHEME:
{scheme}

SOURCE FILE:
{source_file}

SOURCE DOCUMENT LANGUAGE:
{document_language}

CONTENT:
{chunk.page_content}
"""
        )

        source_name = (
            f"{scheme} ({source_file})"
            if source_file
            else scheme
        )

        if source_name not in sources:
            sources.append(source_name)

    context = "\n\n--------------------\n\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # QUESTION LANGUAGE
    # --------------------------------------------------------

    language_name = SUPPORTED_LANGUAGES.get(
        question_language,
        "English",
    )

    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    prompt = SYSTEM_PROMPT

    prompt = prompt.replace(
        "{source_information}",
        ", ".join(sources),
    )

    prompt = prompt.replace(
        "{context}",
        context,
    )

    prompt = prompt.replace(
        "{question}",
        question,
    )

    prompt = prompt.replace(
        "{question_language}",
        language_name,
    )

    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    answer = _generate_answer(prompt)

    return answer, sources, chunks


# ============================================================
# MAIN ANSWER FUNCTION
# ============================================================

def answer_question(
    question: str,
    question_language: str = "en",
):

    question = question.strip()

    if not question:

        return (
            FALLBACK_MESSAGE,
            [],
            [],
            False,
        )

    # --------------------------------------------------------
    # CACHE
    # --------------------------------------------------------

    cache_key = (
        question.lower(),
        question_language,
    )

    if cache_key in _answer_cache:
        return _answer_cache[cache_key]

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    try:

        answer, sources, chunks = _answer_from_documents(
            question,
            question_language,
        )

    except Exception as e:

        result = (
            f"⚠️ RAG error: {e}",
            [],
            [],
            False,
        )

        return result

    # --------------------------------------------------------
    # NO DOCUMENTS
    # --------------------------------------------------------

    if not chunks:

        result = (
            FALLBACK_MESSAGE,
            [],
            [],
            False,
        )

        _answer_cache[cache_key] = result

        return result

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    result = (
        answer,
        sources,
        chunks,
        False,
    )

    _answer_cache[cache_key] = result

    return result


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print("\nSmart FAQ Bot")
    print("Automatic Scheme Detection")
    print("Multilingual RAG Test")
    print("Type 'quit' to exit.\n")

    while True:

        question = input(
            "Ask a question: "
        ).strip()

        if question.lower() in ("quit", "exit"):
            break

        if not question:
            continue

        print("\nChecking documents...\n")

        print(
            "Scheme detected:",
            detect_scheme(question)
        )

        answer, sources, _, _ = answer_question(
            question,
            "en",
        )

        print("\nAnswer:\n")
        print(answer)

        print("\nSources:")

        if sources:

            for source in sources:
                print(f"  - {source}")

        else:
            print("  None")

        print("\n" + "-" * 60)

