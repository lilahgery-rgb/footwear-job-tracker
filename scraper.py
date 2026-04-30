"""
scraper.py

TeamWork Online scraper for sports industry jobs.
All top footwear/apparel brands are now handled by brand_scrapers.py.
This module covers sports leagues, teams, and agencies that only post
on TeamWork Online and not on LinkedIn/Indeed.
"""

import logging
import re
from typing import Generator

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

RETAIL_EXCLUDE = [
    "retail", "store manager", "sales associate", "store associate",
    "stock associate", "cashier", "warehouse", "shipping",
]


def _is_retail(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in RETAIL_EXCLUDE)


def scrape_teamwork_online(max_pages: int = 5) -> list[dict]:
    """Scrape TeamWork Online for sports industry jobs."""
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
        job_cards = (
            soup.find_all("li", class_=lambda c: c and "job" in c.lower())
            or soup.find_all("article")
            or soup.select(".job-post")
        )

        if not job_cards:
            logger.info("TeamWork Online page %d - no cards found, stopping", page)
            break

        for card in job_cards:
            title_el = card.find(["h2", "h3", "h4", "a"])
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title or _is_retail(title):
                continue

            link_el = card.find("a", href=True)
            job_url = ""
            if link_el:
                href = link_el["href"]
                job_url = (
                    href if href.startswith("http")
                    else f"https://www.teamworkonline.com{href}"
                )

            company_el = card.find(
                class_=lambda c: c and "company" in str(c).lower()
            )
            company = (
                company_el.get_text(strip=True)
                if company_el else "Sports Organization"
            )

            loc_el = card.find(
                class_=lambda c: c and "location" in str(c).lower()
            )
            location = loc_el.get_text(strip=True) if loc_el else ""

            job_id = f"teamwork-{abs(hash(job_url))}"
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

    logger.info("TeamWork Online: %d jobs found", len(jobs))
    return jobs


def fetch_all_scraper_jobs() -> Generator[dict, None, None]:
    """Run all supplementary scrapers."""
    logger.info("Scraping TeamWork Online (sports industry)...")
    for job in scrape_teamwork_online():
        yield job            break

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
