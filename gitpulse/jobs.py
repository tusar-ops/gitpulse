"""
jobs.py — SerpApi Google Jobs integration for GitPulse

Takes a detected tech stack (from analyzer.py) and returns matching
job listings via SerpApi's Google Jobs engine.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root, if present

SERPAPI_ENDPOINT = "https://serpapi.com/search"


class JobsFetchError(Exception):
    """Raised when the SerpApi request fails or returns an error."""
    pass


def get_api_key():
    """
    Reads the SerpApi key from the SERPAPI_KEY environment variable.
    Raises JobsFetchError if it's missing, instead of failing silently.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise JobsFetchError(
            "SERPAPI_KEY not set. Get a free key at https://serpapi.com/ "
            "and export it: export SERPAPI_KEY=your_key_here"
        )
    return api_key


def build_query(top_languages, role_hint=None):
    """
    Builds a Google Jobs search query string from detected languages.

    top_languages: list[str], e.g. ["Python", "JavaScript"]
    role_hint: optional str, e.g. "developer" (default) or "engineer"
    """
    if not top_languages:
        raise ValueError("top_languages is empty — nothing to search for")

    primary = top_languages[0]
    role = role_hint or "developer"
    return f"{primary} {role}"


def fetch_jobs(top_languages, location="India", role_hint=None, limit=10):
    """
    Fetches job listings matching the given tech stack.

    Returns a list of dicts:
        [{"title": ..., "company": ..., "location": ...,
          "via": ..., "posted": ...}, ...]

    Raises JobsFetchError on network/API failure.
    """
    api_key = get_api_key()
    query = build_query(top_languages, role_hint)

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "gl": "in",
        "hl": "en",
        "api_key": api_key,
    }

    try:
        response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        # one retry — helps with transient network blips
        try:
            response = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise JobsFetchError(f"SerpApi request failed: {e}")

    data = response.json()

    if "error" in data:
        raise JobsFetchError(f"SerpApi returned an error: {data['error']}")

    raw_jobs = data.get("jobs_results", [])

    jobs = []
    for job in raw_jobs[:limit]:
        detected = job.get("detected_extensions", {})
        jobs.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "via": job.get("via", "N/A"),
            "posted": detected.get("posted_at", "N/A"),
        })

    return jobs
