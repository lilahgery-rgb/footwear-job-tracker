"""
scraper.py — TeamWork Online scraper for sports industry jobs.

Workday API is blocked so all company scraping is handled by JSearch
in api_fetcher.py. This module scrapes TeamWork Online which is the
dedicated job board for sports business roles — leagues, teams, agencies.
It's free, no API key needed, and covers roles that don't show on LinkedIn.
"""

import logging
from typing import Generator

import requests
from bs4 import BeautifulSoup

from config import (
    ENTRY_LEVEL_TITLE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_RETAIL_KEYWORDS,
    KEYWORDS,
    WORKDAY_COMPANIES,
)

logger = logging.getLogger(__name__)

HEADERS = {
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


def scrape_teamwork_online(max_pages: int = 5) -> list[dict]:
    """
    Scrape TeamWork Online for entry-level sports business jobs.
    Covers leagues, teams, agencies, and sports media companies.
    URL: https://www.teamworkonline.com/jobs-in-sports
    """
    jobs = []
    seen_ids = set()

    for page in range(1, max_pages + 1):
        url = f"https://www.teamworkonline.com/jobs-in-sports?page={page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("TeamWork Online page %d failed: %s", page, exc)
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        # TeamWork Online job cards
        job_cards = soup.find_all("li", class_=lambda c: c and "job" in c.lower())
        if not job_cards:
            # Try alternate selectors
            job_cards = soup.find_all("div", class_=lambda c: c and "job-listing" in str(c).lower())
        if not job_cards:
            job_cards = soup.select("article") or soup.select(".job-post")

        if not job_cards:
            logger.info("TeamWork Online page %d — no job cards found, stopping", page)
            break

        for card in job_cards:
            # Extract title
            title_el = card.find(["h2", "h3", "h4", "a"])
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title or not _passes_filters(title):
                continue

            # Extract link
            link_el = card.find("a", href=True)
            job_url = ""
            if link_el:
                href = link_el["href"]
                job_url = href if href.startswith("http") else f"https://www.teamworkonline.com{href}"

            # Extract company
            company_el = card.find(class_=lambda c: c and "company" in str(c).lower())
            company = company_el.get_text(strip=True) if company_el else "Sports Organization"

            # Extract location
            loc_el = card.find(class_=lambda c: c and "location" in str(c).lower())
            location = loc_el.get_text(strip=True) if loc_el else ""

            job_id = f"teamwork-{hash(job_url)}"
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            jobs.append({
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "source": "teamwork_online",
                "posted_on": "",
            })

    logger.info("TeamWork Online → %d jobs found", len(jobs))
    return jobs


def scrape_all_companies(max_per_company: int = 200) -> Generator[dict, None, None]:
    """
    Scrape TeamWork Online for sports industry jobs.
    All other companies are handled by JSearch in api_fetcher.py.
    """
    logger.info("Scraping TeamWork Online (sports industry jobs)…")
    for job in scrape_teamwork_online():
        yield job
