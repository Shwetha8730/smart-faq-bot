"""
gov_documents.py
-----------------
Fetches official government scheme PDFs directly from verified government
portals, instead of requiring manual upload — and stores them in Supabase
Storage so they persist across redeploys (local disk on most cloud hosts,
including this one, does NOT persist between restarts).
"""

import re
import requests
from pathlib import Path
from urllib.parse import urlparse

from src.config import DATA_DIR
from src.runtime_settings import get_supabase_settings
from supabase import create_client


# ============================================================
# ALLOWED OFFICIAL DOMAINS
# Only URLs on these domains are treated as "verified government portals."
# ============================================================

ALLOWED_DOMAINS = [
    "gov.in",
    "nic.in",
    "myscheme.gov.in",
]


def is_official_url(url: str) -> bool:
    """Returns True only if the URL's domain ends with a trusted gov domain."""
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return False
    return any(domain == d or domain.endswith("." + d) for d in ALLOWED_DOMAINS)


# ============================================================
# CURATED LIST OF SCHEMES → OFFICIAL DOCUMENT URL
#
# IMPORTANT: These URLs are placeholders. Government portals restructure
# their sites often, so verify each exact PDF link yourself in a browser
# before relying on it — paste the real, current direct-PDF link here.
# ============================================================

OFFICIAL_DOCUMENTS = {
    "PM-KISAN Operational Guidelines": "https://pmkisan.gov.in/Documents/RevisedPM-KISANGuidelines.pdf",
    # Add more like this, verifying each URL yourself first:
    # "Ayushman Bharat (PM-JAY) Guidelines": "https://pmjay.gov.in/.../guidelines.pdf",
    # "National Scholarship Portal Guidelines": "https://scholarships.gov.in/.../guidelines.pdf",
}


def _safe_filename(scheme_name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9]+", "_", scheme_name).strip("_").lower()
    return f"{name}.pdf"


def download_official_pdf(url: str):
    """
    Downloads a PDF from a verified government URL.
    Returns (success: bool, message: str, file_bytes: bytes | None)
    """
    if not is_official_url(url):
        return False, f"Refused: {url} is not on an approved government domain.", None

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except Exception as e:
        return False, f"Could not download the document: {e}", None

    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower() and not response.content[:4] == b"%PDF":
        return False, "The URL did not return a PDF file.", None

    return True, "Downloaded successfully.", response.content


def upload_to_supabase_storage(filename: str, file_bytes: bytes):
    """Uploads PDF bytes to the 'scheme-documents' Supabase Storage bucket."""
    settings = get_supabase_settings()
    if not settings["url"] or not settings["key"]:
        return False, "Supabase is not configured. Set it up on the Settings page first."

    try:
        client = create_client(settings["url"], settings["key"])
        client.storage.from_("scheme-documents").upload(
            filename,
            file_bytes,
            {"content-type": "application/pdf", "upsert": "true"},
        )
        return True, "Saved to persistent storage."
    except Exception as e:
        return False, f"Supabase storage error: {e}"


def sync_supabase_storage_to_local():
    """
    Downloads every PDF from Supabase Storage into data/schemes/ locally.
    Call this on app startup so previously-fetched official documents
    survive a redeploy (local disk doesn't persist, Supabase does).
    """
    settings = get_supabase_settings()
    if not settings["url"] or not settings["key"]:
        return 0

    try:
        client = create_client(settings["url"], settings["key"])
        files = client.storage.from_("scheme-documents").list()

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        synced = 0

        for f in files:
            local_path = DATA_DIR / f["name"]
            if not local_path.exists():
                data = client.storage.from_("scheme-documents").download(f["name"])
                local_path.write_bytes(data)
                synced += 1

        return synced
    except Exception:
        return 0


def fetch_and_index_official_document(scheme_name: str):
    """
    Full pipeline for the 'Fetch and index official guideline' button:
    download -> validate -> save to Supabase Storage -> save locally ->
    ready for ingestion.
    Returns (success: bool, message: str)
    """
    url = OFFICIAL_DOCUMENTS.get(scheme_name)
    if not url:
        return False, "Unknown scheme."

    ok, msg, file_bytes = download_official_pdf(url)
    if not ok:
        return False, msg

    filename = _safe_filename(scheme_name)

    ok, msg = upload_to_supabase_storage(filename, file_bytes)
    if not ok:
        return False, msg

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / filename).write_bytes(file_bytes)

    return True, f"'{scheme_name}' fetched and saved. Re-run ingestion to index it."