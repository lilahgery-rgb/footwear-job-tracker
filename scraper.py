"""
scraper.py — Scrapes Workday-based career pages.

Most major footwear brands (Nike, Adidas, New Balance, Puma, etc.) use Workday
as their ATS. Workday exposes a consistent internal JSON API that we can query
directly — no fragile HTML parsing needed.

Workday API endpoint pattern:
  POST https://{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{path}/jobs
"""

import logging
from typing import Generator

import requests

from config import (
    WORKDAY_COMPANIES,
    KEYWORDS,
    ENTRY_LEVEL_TITLE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_RETAIL_KEYWORDS,
)

logger = logging.getLogger(__name__)

WORKDAY_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def _build_workday_url(company: dict) -> str:
    subdomain = company["subdomain"]
    tenant = company["tenant"]
    return (
        f"https://{subdomain}.myworkdayjobs.com"
        f"/wday/cxs/{tenant}/{tenant}/jobs"
    )


def _passes_filters(job: dict) -> bool:
    """
    Return True only if the job passes all three filters:
      1. Title contains an entry-level/internship keyword
      2. Title does NOT contain a seniority keyword (senior, manager, etc.)
      3. Title does NOT contain a retail/store keyword
    """
    title = (job.get("title") or "").lower()

    # Must match at least one entry-level keyword
    if not any(kw in title for kw in ENTRY_LEVEL_TITLE_KEYWORDS):
        return False

    # Must not match any seniority exclusion
    if any(kw in title for kw in EXCLUDE_TITLE_KEYWORDS):
        return False

    # Must not match any retail/store exclusion
    if any(kw in title for kw in EXCLUDE_RETAIL_KEYWORDS):
        return False

    # Optional: extra keyword filter from env var
    if KEYWORDS:
        return any(kw.lower() in title for kw in KEYWORDS)

    return True


def scrape_workday_company(company: dict, offset: int = 0, limit: int = 20) -> list[dict]:
    """
    Fetch one page of jobs from a Workday career site.
    Returns a list of normalized job dicts.
    """
    url = _build_workday_url(company)
    payload = {
        "appliedFacets": {},
        "limit": limit,
        "offset": offset,
        "searchText": "",
    }

    try:
        resp = requests.post(url, json=payload, headers=WORKDAY_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.warning("Failed to scrape %s: %s", company["name"], exc)
        return []
    except ValueError:
        logger.warning("Non-JSON response from %s", company["name"])
        return []

    raw_jobs = data.get("jobPostings", [])
    jobs = []
    for rj in raw_jobs:
        job_id = rj.get("bulletFields", [None])[0] or rj.get("title", "")
        # Build a stable unique ID from company + external ID
        external_path = rj.get("externalPath", "")
        stable_id = f"workday-{company['tenant']}-{external_path or job_id}"

        # Build the apply URL
        apply_url = (
            f"https://{company['subdomain']}.myworkdayjobs.com"
            f"/en-US/{company['tenant']}{external_path}"
        )

        location_parts = rj.get("locationsText", "") or ""

        normalized = {
            "id": stable_id,
            "title": rj.get("title", "Unknown Title"),
            "company": company["name"],
            "location": location_parts,
            "url": apply_url,
            "source": "workday_scrape",
            "posted_on": rj.get("postedOn", ""),
        }
        if _passes_filters(normalized):
            jobs.append(normalized)

    return jobs


def scrape_all_companies(max_per_company: int = 200) -> Generator[dict, None, None]:
    """
    Scrape all configured Workday companies and yield normalized job dicts.
    Paginates up to max_per_company results per company.
    """
    for company in WORKDAY_COMPANIES:
        logger.info("Scraping %s…", company["name"])
        fetched = 0
        offset = 0
        limit = 20

        while fetched < max_per_company:
            batch = scrape_workday_company(company, offset=offset, limit=limit)
            if not batch:
                break
            for job in batch:
                yield job
            fetched += len(batch)
            if len(batch) < limit:
                break  # No more pages
            offset += limit
