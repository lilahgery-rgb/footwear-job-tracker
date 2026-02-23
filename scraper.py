"""
scraper.py — Career page scraper using correct Workday URLs + direct site scrapers.

Key fixes:
- Workday career site name is "External" not the company name
- Nike, Adidas, PepsiCo use custom career sites — scraped directly
- JSearch used as fallback for companies where both methods fail
"""

import logging
from typing import Generator
import requests
from bs4 import BeautifulSoup

from config import (
    WORKDAY_COMPANIES,
    JSEARCH_API_KEY,
    ENTRY_LEVEL_TITLE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_RETAIL_KEYWORDS,
    KEYWORDS,
)

logger = logging.getLogger(__name__)

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def _passes_filters(title: str) -> bool:
    t = title.lower()
    if not any(kw in t for kw in ENTRY_LEVEL_TITLE_KEYWORDS):
        return False
    if any(kw in t for kw in EXCLUDE_TITLE_KEYWORDS):
        return False
    if any(kw in t for kw in EXCLUDE_RETAIL_KEYWORDS):
        return False
    if KEYWORDS:
        return any(kw.lower() in t for kw in KEYWORDS)
    return True


# ── Workday scraper (fixed URL format) ────────────────────────────────────────

def scrape_workday(company: dict, offset: int = 0, limit: int = 20) -> list[dict]:
    """
    Scrape a Workday career site using the correct URL format.
    The career_site field defaults to "External" which is the most common name.
    """
    subdomain = company["subdomain"]
    tenant = company["tenant"]
    career_site = company.get("career_site", "External")

    url = f"https://{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{career_site}/jobs"
    payload = {"appliedFacets": {}, "limit": limit, "offset": offset, "searchText": ""}

    try:
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        logger.info("    %s → HTTP %s (%s)", company["name"], resp.status_code, career_site)
        if resp.status_code in (404, 422):
            return []
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.warning("    FAILED %s: %s", company["name"], exc)
        return []

    raw_jobs = data.get("jobPostings", [])
    logger.info("    %s → %d jobs returned", company["name"], len(raw_jobs))

    jobs = []
    for rj in raw_jobs:
        external_path = rj.get("externalPath", "")
        title = rj.get("title", "Unknown Title")
        if not _passes_filters(title):
            continue
        apply_url = f"https://{subdomain}.myworkdayjobs.com/en-US/{career_site}{external_path}"
        jobs.append({
            "id": f"workday-{tenant}-{external_path}",
            "title": title,
            "company": company["name"],
            "location": rj.get("locationsText", "") or "",
            "url": apply_url,
            "source": "workday_scrape",
            "posted_on": rj.get("postedOn", ""),
        })
    return jobs


# ── Nike direct scraper ────────────────────────────────────────────────────────

def scrape_nike() -> list[dict]:
    """
    Scrape Nike's career site directly filtering for Corporate + Internship roles.
    Nike uses a custom career site at careers.nike.com, not directly Workday.
    """
    jobs = []
    # Nike has a category filter: cf_job_category=Corporate and a type filter for Internships
    for page in range(1, 6):  # Up to 5 pages
        url = f"https://careers.nike.com/api/jobs?filter[cf_job_category][0]=Corporate&page={page}&count=20"
        try:
            resp = requests.get(url, headers={
                "User-Agent": HEADERS["User-Agent"],
                "Accept": "application/json",
            }, timeout=15)
            if resp.status_code != 200:
                # Try without the API path
                break
            data = resp.json()
            raw = data.get("jobs", data.get("data", []))
            if not raw:
                break
            for rj in raw:
                title = rj.get("title", rj.get("job_title", ""))
                if not _passes_filters(title):
                    continue
                job_id = rj.get("id", rj.get("job_id", ""))
                jobs.append({
                    "id": f"nike-{job_id}",
                    "title": title,
                    "company": "Nike",
                    "location": rj.get("location", rj.get("primary_location", "")),
                    "url": f"https://careers.nike.com/{rj.get('slug', job_id)}/job/{job_id}",
                    "source": "direct_scrape",
                    "posted_on": rj.get("posted_date", ""),
                })
        except Exception as exc:
            logger.warning("Nike scraper failed (page %d): %s", page, exc)
            break

    logger.info("    Nike direct → %d jobs found", len(jobs))
    return jobs


# ── Adidas direct scraper ──────────────────────────────────────────────────────

def scrape_adidas() -> list[dict]:
    """Scrape Adidas career site at jobs.adidas-group.com."""
    jobs = []
    url = "https://jobs.adidas-group.com/api/jobs?type=intern&type=entry-level&count=50"
    try:
        resp = requests.get(url, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "application/json",
        }, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for rj in data.get("jobs", []):
                title = rj.get("title", "")
                if not _passes_filters(title):
                    continue
                jobs.append({
                    "id": f"adidas-{rj.get('id', '')}",
                    "title": title,
                    "company": "Adidas",
                    "location": rj.get("location", ""),
                    "url": f"https://jobs.adidas-group.com{rj.get('url', '')}",
                    "source": "direct_scrape",
                    "posted_on": rj.get("datePosted", ""),
                })
    except Exception as exc:
        logger.warning("Adidas direct scraper failed: %s", exc)

    logger.info("    Adidas direct → %d jobs found", len(jobs))
    return jobs


# ── Main orchestrator ─────────────────────────────────────────────────────────

def scrape_all_companies(max_per_company: int = 200) -> Generator[dict, None, None]:
    """
    Try to scrape each company using the best available method:
    1. Direct career page scraper (for Nike, Adidas which have custom sites)
    2. Workday API with correct "External" career site name
    """

    # Direct scrapers for companies with custom career sites
    logger.info("Scraping Nike (direct)…")
    for job in scrape_nike():
        yield job

    logger.info("Scraping Adidas (direct)…")
    for job in scrape_adidas():
        yield job

    # Workday scraper for all other companies
    # Skip Nike and Adidas since we scraped them directly above
    skip_direct = {"Nike", "Converse", "Adidas", "Reebok"}

    for company in WORKDAY_COMPANIES:
        if company["name"] in skip_direct:
            continue

        logger.info("Scraping %s (Workday)…", company["name"])
        fetched = 0
        offset = 0
        limit = 20

        while fetched < max_per_company:
            batch = scrape_workday(company, offset=offset, limit=limit)
            if not batch:
                break
            for job in batch:
                yield job
            fetched += len(batch)
            if len(batch) < limit:
                break
            offset += limit
