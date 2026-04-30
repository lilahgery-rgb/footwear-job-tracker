"""
api_fetcher.py

JSearch is now used for SECONDARY brands only (CPG, sports leagues, sports media,
airlines, sports tech). The top 30 footwear brands are handled by brand_scrapers.py
which queries their ATS directly - guaranteeing no missed jobs.

For secondary brands we use broad company-name queries (no role keywords) so we
catch everything, then filter out retail.
"""

import logging
import time
from typing import Generator

import requests

from config import JSEARCH_API_KEY

logger = logging.getLogger(__name__)

JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

RETAIL_EXCLUDE = [
    "retail", "store manager", "sales associate", "store associate",
    "stock associate", "stocking associate", "shipping associate",
    "inventory associate", "cashier", "floor supervisor",
    "key holder", "keyholder", "outlet", "factory store",
    "part-time", "part time", "seasonal", "temporary",
    "child care", "daycare", "janitor", "custodian",
]


def _is_retail(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in RETAIL_EXCLUDE)


def _format_location(rj: dict) -> str:
    parts = [rj.get("job_city"), rj.get("job_state"), rj.get("job_country")]
    return ", ".join(p for p in parts if p)


def fetch_jsearch_query(query: str) -> list[dict]:
    """Run a single broad JSearch query."""
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "month",
        "employment_types": "FULLTIME",
    }
    try:
        resp = requests.get(
            JSEARCH_BASE_URL,
            headers=JSEARCH_HEADERS,
            params=params,
            timeout=15,
        )
        if resp.status_code == 429:
            logger.warning("Rate limit hit - pausing 60s")
            time.sleep(60)
            return []
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.warning("JSearch failed for '%s': %s", query, exc)
        return []

    results = []
    for rj in data.get("data", []):
        title = rj.get("job_title", "")
        if _is_retail(title):
            continue
        results.append({
            "id": f"jsearch-{rj.get('job_id', '')}",
            "title": title,
            "company": rj.get("employer_name", ""),
            "location": _format_location(rj),
            "url": rj.get("job_apply_link") or rj.get("job_google_link", ""),
            "source": "jsearch_api",
            "posted_on": (rj.get("job_posted_at_datetime_utc") or "")[:10],
        })

    time.sleep(0.3)
    return results


# =============================================================================
# QUERIES - Secondary brands only. Broad company name searches.
# Top 30 footwear brands are handled by brand_scrapers.py
# =============================================================================

JSEARCH_QUERIES = [

    # ── CPG ───────────────────────────────────────────────────────────────────
    "Procter Gamble jobs",
    "Procter Gamble associate brand manager",
    "Unilever jobs careers",
    "Unilever associate brand manager",
    "PepsiCo jobs careers",
    "PepsiCo associate brand manager",
    "Coca-Cola jobs careers",
    "Coca-Cola associate brand manager",
    "Kraft Heinz jobs careers",
    "Mondelez jobs careers",
    "Mars Incorporated jobs careers",
    "Nestle USA jobs careers",
    "General Mills jobs careers",
    "General Mills associate brand manager",
    "Kellanova jobs careers",
    "Conagra Brands jobs careers",
    "Clorox Company jobs careers",
    "Keurig Dr Pepper jobs careers",
    "Church Dwight jobs careers",
    "Colgate Palmolive jobs careers",
    "SC Johnson jobs careers",
    "Henkel jobs careers",
    "Edgewell jobs careers",
    "Energizer jobs careers",

    # ── Sports Leagues ────────────────────────────────────────────────────────
    "NBA league office jobs",
    "NFL league office jobs",
    "MLB league office jobs",
    "MLS league office jobs",
    "NHL league office jobs",
    "PGA Tour jobs careers",
    "USTA jobs careers",
    "US Soccer Federation jobs",
    "Formula 1 jobs careers",
    "NASCAR jobs careers",

    # ── Sports Media ──────────────────────────────────────────────────────────
    "ESPN jobs careers",
    "FOX Sports jobs careers",
    "NBC Sports jobs careers",
    "Turner Sports jobs careers",
    "Warner Bros Discovery sports jobs",
    "The Athletic jobs careers",

    # ── Sports Tech ───────────────────────────────────────────────────────────
    "WHOOP jobs careers",
    "Garmin jobs careers",
    "Peloton jobs careers",
    "Oura Ring jobs careers",

    # ── United Airlines ───────────────────────────────────────────────────────
    "United Airlines jobs corporate",

    # ── Sports Equipment ──────────────────────────────────────────────────────
    "Wilson Sporting Goods jobs",
    "Callaway Golf jobs careers",
    "TaylorMade Golf jobs careers",
    "Titleist jobs careers",
    "Bauer Hockey jobs careers",
    "Rawlings jobs careers",

    # ── Gear & Drinkware ──────────────────────────────────────────────────────
    "YETI jobs careers",
    "Stanley PMI jobs careers",
    "Owala jobs careers",
    "Hydro Flask jobs careers",
    "REI jobs corporate careers",

    # ── Apparel ───────────────────────────────────────────────────────────────
    "Athleta jobs careers",
    "Fabletics jobs careers",
    "Gymshark jobs careers",
    "Champion Hanesbrands jobs careers",
    "Speedo jobs careers",

    # ── Action Sports ─────────────────────────────────────────────────────────
    "Burton Snowboards jobs careers",
    "Quiksilver Boardriders jobs careers",

    # ── International ─────────────────────────────────────────────────────────
    "footwear brand jobs London UK",
    "sportswear brand jobs Amsterdam Netherlands",
    "athletic brand jobs Germany",
    "consumer goods jobs London UK",
    "footwear jobs Australia",
    "sportswear jobs Australia",
    "athletic brand jobs Sydney Melbourne",

    # ── Broad sweeps ─────────────────────────────────────────────────────────
    "footwear brand associate analyst coordinator",
    "sportswear brand associate analyst coordinator",
    "athletic apparel associate analyst coordinator",
    "outdoor apparel associate analyst coordinator",
    "CPG associate brand manager full time",
    "consumer goods brand analyst coordinator",
    "sports business analyst coordinator",
    "sports marketing coordinator analyst",
    "brand partnerships coordinator analyst",
    "consumer insights analyst brand",
    "product marketing analyst coordinator brand",
    "ecommerce analyst coordinator brand",
    "category analyst consumer goods",
    "trade marketing analyst coordinator",
]


def fetch_all_api_jobs() -> Generator[dict, None, None]:
    if not JSEARCH_API_KEY:
        logger.warning("JSEARCH_API_KEY not set - skipping JSearch.")
        return

    seen_ids: set = set()
    total = len(JSEARCH_QUERIES)

    for i, query in enumerate(JSEARCH_QUERIES, 1):
        logger.info("JSearch query %d/%d: '%s'", i, total, query)
        jobs = fetch_jsearch_query(query)
        new = 0
        for job in jobs:
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                new += 1
                yield job
        logger.info("  -> %d new results", new)
        time.sleep(0.2)
