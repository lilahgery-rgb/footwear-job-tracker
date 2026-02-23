"""
scraper.py — Scrapes Workday-based career pages.

Most major footwear brands use Workday as their ATS. Workday exposes a 
consistent internal JSON API we can query directly.

Workday API endpoint pattern:
  POST https://{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{tenant}/jobs
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


def _passes_filters(job: dict) -> bool:
    title = (job.get("title") or "").lower()
    if not any(kw in title for kw in ENTRY_LEVEL_TITLE_KEYWORDS):
        return False
    if any(kw in title for kw in EXCLUDE_TITLE_KEYWORDS):
        return False
    if any(kw in title for kw in EXCLUDE_RETAIL_KEYWORDS):
        return False
    if KEYWORDS:
        return any(kw.lower() in title for kw in KEYWORDS)
    return True


def scrape_workday_company(company: dict, offset: int = 0, limit: int = 20) -> list[dict]:
    subdomain = company["subdomain"]
    tenant = company["tenant"]
    url = f"https://{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{tenant}/jobs"

    payload = {
        "appliedFacets": {},
        "limit": limit,
        "offset": offset,
        "searchText": "",
    }

    try:
        resp = requests.post(url, json=payload, headers=WORKDAY_HEADERS, timeout=15)
        logger.info("    %s → HTTP %s", company["name"], resp.status_code)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.warning("    FAILED %s: %s", company["name"], exc)
        return []
    except ValueError:
        logger.warning("    Non-JSON from %s", company["name"])
        return []

    raw_jobs = data.get("jobPostings", [])
    total_available = data.get("total", 0)
    logger.info("    %s → %d jobs available, %d returned", company["name"], total_available, len(raw_jobs))

    jobs = []
    for rj in raw_jobs:
        external_path = rj.get("externalPath", "")
        stable_id = f"workday-{tenant}-{external_path}"
        apply_url = (
            f"https://{subdomain}.myworkdayjobs.com"
            f"/en-US/{tenant}{external_path}"
        )
        normalized = {
            "id": stable_id,
            "title": rj.get("title", "Unknown Title"),
            "company": company["name"],
            "location": rj.get("locationsText", "") or "",
            "url": apply_url,
            "source": "workday_scrape",
            "posted_on": rj.get("postedOn", ""),
        }
        if _passes_filters(normalized):
            jobs.append(normalized)

    return jobs


def scrape_all_companies(max_per_company: int = 200) -> Generator[dict, None, None]:
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
                break
            offset += limit
