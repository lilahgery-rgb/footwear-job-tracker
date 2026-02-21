"""
api_fetcher.py — Fetches jobs via the JSearch API on RapidAPI.

JSearch aggregates job listings from LinkedIn, Indeed, Glassdoor, and more.
This supplements our Workday scraper by catching jobs posted on those platforms
that might not appear on a company's own careers page.

Docs: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Generator

import requests

from config import (
    JSEARCH_API_KEY,
    JSEARCH_QUERIES,
    MAX_AGE_DAYS,
    KEYWORDS,
    ENTRY_LEVEL_TITLE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_RETAIL_KEYWORDS,
)

logger = logging.getLogger(__name__)

JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}


def _is_recent(date_posted: str | None) -> bool:
    """Return True if the job was posted within MAX_AGE_DAYS days."""
    if not date_posted:
        return True  # Can't determine age, include it
    try:
        posted_dt = datetime.fromisoformat(date_posted.replace("Z", "+00:00"))
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=MAX_AGE_DAYS)
        return posted_dt >= cutoff
    except (ValueError, TypeError):
        return True


def _passes_filters(job: dict) -> bool:
    """
    Return True only if the job passes all three filters:
      1. Title contains an entry-level/internship keyword
      2. Title does NOT contain a seniority keyword
      3. Title does NOT contain a retail/store keyword
    """
    title = (job.get("job_title") or "").lower()

    if not any(kw in title for kw in ENTRY_LEVEL_TITLE_KEYWORDS):
        return False
    if any(kw in title for kw in EXCLUDE_TITLE_KEYWORDS):
        return False
    if any(kw in title for kw in EXCLUDE_RETAIL_KEYWORDS):
        return False
    if KEYWORDS:
        return any(kw.lower() in title for kw in KEYWORDS)

    return True


def fetch_jsearch_query(query: str, num_pages: int = 1) -> list[dict]:
    """
    Run a single JSearch query and return a list of normalized job dicts.
    """
    if not JSEARCH_API_KEY:
        logger.warning("JSEARCH_API_KEY not set — skipping API fetch.")
        return []

    all_jobs = []
    for page in range(1, num_pages + 1):
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "date_posted": "today",  # Only today's postings
        }
        try:
            resp = requests.get(
                JSEARCH_BASE_URL,
                headers=JSEARCH_HEADERS,
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.warning("JSearch request failed for '%s': %s", query, exc)
            break
        except ValueError:
            logger.warning("JSearch returned non-JSON for '%s'", query)
            break

        raw_jobs = data.get("data", [])
        for rj in raw_jobs:
            if not _is_recent(rj.get("job_posted_at_datetime_utc")):
                continue
            if not _passes_filters(rj):
                continue

            normalized = {
                "id": f"jsearch-{rj.get('job_id', '')}",
                "title": rj.get("job_title", "Unknown Title"),
                "company": rj.get("employer_name", "Unknown Company"),
                "location": _format_location(rj),
                "url": rj.get("job_apply_link") or rj.get("job_google_link", ""),
                "source": "jsearch_api",
                "posted_on": rj.get("job_posted_at_datetime_utc", ""),
            }
            all_jobs.append(normalized)

        if not raw_jobs:
            break  # No more results

    return all_jobs


def _format_location(rj: dict) -> str:
    parts = [
        rj.get("job_city"),
        rj.get("job_state"),
        rj.get("job_country"),
    ]
    return ", ".join(p for p in parts if p)


def fetch_all_api_jobs() -> Generator[dict, None, None]:
    """
    Run all configured JSearch queries and yield normalized job dicts.
    """
    seen_ids: set[str] = set()
    for query in JSEARCH_QUERIES:
        logger.info("Querying JSearch: '%s'…", query)
        jobs = fetch_jsearch_query(query)
        for job in jobs:
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                yield job
