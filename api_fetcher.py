"""
api_fetcher.py — JSearch API client.

Plan: Pro ($25/month) = 10,000 requests
Strategy: 300 queries x 1 page = 300 requests/day x 30 days = 9,000/month
"""

import logging
import time
from typing import Generator

import requests

from config import (
    JSEARCH_API_KEY,
    ENTRY_LEVEL_TITLE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_RETAIL_KEYWORDS,
    KEYWORDS,
)

logger = logging.getLogger(__name__)

JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}

PAGES_PER_QUERY = 1  # 1 page x 10 results = 10 per query, 300 queries/day


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


def _format_location(rj: dict) -> str:
    parts = [rj.get("job_city"), rj.get("job_state"), rj.get("job_country")]
    return ", ".join(p for p in parts if p)


def fetch_jsearch_query(query: str) -> list[dict]:
    results = []
    seen_ids = set()

    for page in range(1, PAGES_PER_QUERY + 1):
        params = {
            "query": query,
            "page": str(page),
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
                logger.warning("Rate limit hit — pausing 60s")
                time.sleep(60)
                continue
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.warning("JSearch failed for '%s' page %d: %s", query, page, exc)
            break

        raw_jobs = data.get("data", [])
        if not raw_jobs:
            break

        for rj in raw_jobs:
            job_id = f"jsearch-{rj.get('job_id', '')}"
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            title = rj.get("job_title", "")
            if not _passes_filters(title):
                continue

            results.append({
                "id": job_id,
                "title": title,
                "company": rj.get("employer_name", ""),
                "location": _format_location(rj),
                "url": rj.get("job_apply_link") or rj.get("job_google_link", ""),
                "source": "jsearch_api",
                "posted_on": rj.get("job_posted_at_datetime_utc", ""),
            })

        time.sleep(0.3)

    return results


JSEARCH_QUERIES = [

    # ── Nike ──────────────────────────────────────────────────────────────────
    "Nike marketing coordinator",
    "Nike brand coordinator",
    "Nike product coordinator",
    "Nike merchandiser",
    "Nike merchandising coordinator",
    "Nike product line manager",
    "Nike business analyst",
    "Nike digital analyst",
    "Nike brand associate",
    "Nike ecommerce coordinator",
    "Nike sports marketing coordinator",

    # ── Adidas ────────────────────────────────────────────────────────────────
    "Adidas marketing coordinator",
    "Adidas brand coordinator",
    "Adidas product coordinator",
    "Adidas merchandiser",
    "Adidas merchandising coordinator",
    "Adidas product line manager",
    "Adidas business analyst",
    "Adidas brand associate",
    "Adidas digital coordinator",

    # ── Puma ──────────────────────────────────────────────────────────────────
    "Puma marketing coordinator",
    "Puma brand analyst",
    "Puma product coordinator",
    "Puma merchandiser",
    "Puma brand associate",

    # ── New Balance ───────────────────────────────────────────────────────────
    "New Balance marketing coordinator",
    "New Balance brand analyst",
    "New Balance product coordinator",
    "New Balance merchandiser",
    "New Balance merchandising coordinator",

    # ── Under Armour ──────────────────────────────────────────────────────────
    "Under Armour marketing coordinator",
    "Under Armour brand analyst",
    "Under Armour product coordinator",
    "Under Armour merchandiser",
    "Under Armour brand associate",

    # ── ASICS / Brooks / On / HOKA ────────────────────────────────────────────
    "ASICS marketing coordinator",
    "ASICS brand analyst",
    "ASICS product coordinator",
    "Brooks Running coordinator analyst",
    "Brooks Running product coordinator",
    "HOKA brand coordinator",
    "HOKA marketing analyst",
    "HOKA product coordinator",
    "On Running coordinator",
    "On Running brand analyst",
    "On Running product coordinator",

    # ── Skechers / Allbirds / Converse / Reebok ───────────────────────────────
    "Skechers marketing coordinator",
    "Skechers brand analyst",
    "Converse brand coordinator",
    "Converse marketing analyst",
    "Reebok brand coordinator",
    "Reebok marketing analyst",

    # ── Salomon / Merrell / Wolverine ─────────────────────────────────────────
    "Salomon marketing coordinator",
    "Salomon product coordinator",
    "Wolverine Worldwide coordinator",
    "Merrell brand coordinator",
    "Merrell product coordinator",

    # ── Crocs / Birkenstock / Steve Madden ────────────────────────────────────
    "Crocs marketing coordinator",
    "Crocs brand analyst",
    "Birkenstock coordinator analyst",
    "Steve Madden coordinator analyst",
    "Steve Madden merchandiser",

    # ── Deckers Brands (HOKA, UGG, Teva, Sanuk) ──────────────────────────────
    "Deckers Brands coordinator",
    "Deckers Brands analyst",
    "Deckers Brands product coordinator",
    "UGG brand coordinator",
    "UGG marketing analyst",
    "UGG merchandiser",
    "Teva brand coordinator",

    # ── VF Corporation (Vans, Timberland, North Face, Dickies, Altra) ─────────
    "VF Corporation analyst coordinator",
    "Vans brand coordinator",
    "Vans marketing analyst",
    "Vans product coordinator",
    "Vans merchandiser",
    "Timberland brand coordinator",
    "Timberland marketing analyst",
    "The North Face coordinator",
    "The North Face brand analyst",
    "The North Face product coordinator",
    "Altra Running coordinator",

    # ── Outdoor & Apparel ─────────────────────────────────────────────────────
    "Patagonia coordinator analyst",
    "Patagonia brand associate",
    "Columbia Sportswear coordinator",
    "Columbia Sportswear analyst",
    "Columbia Sportswear product coordinator",
    "Arcteryx coordinator analyst",
    "Arcteryx brand associate",
    "Wilson Sporting Goods coordinator",
    "Wilson Sporting Goods analyst",
    "Vuori brand coordinator",
    "Vuori marketing analyst",
    "Alo Yoga brand coordinator",
    "Alo Yoga marketing analyst",
    "lululemon coordinator analyst",
    "lululemon brand associate",
    "lululemon product coordinator",
    "lululemon merchandiser",
    "Gymshark coordinator analyst",
    "Fabletics brand coordinator",

    # ── Gap Inc. brands ───────────────────────────────────────────────────────
    "Athleta brand coordinator",
    "Athleta marketing analyst",

    # ── Lifestyle & Denim ─────────────────────────────────────────────────────

    # ── Gear / Outdoor ────────────────────────────────────────────────────────
    "YETI brand coordinator",
    "YETI marketing analyst",
    "Hydro Flask coordinator analyst",
    "REI coordinator analyst",
    "REI brand associate",

    # ── Specialty Retail corporate ────────────────────────────────────────────
    "Foot Locker corporate coordinator",
    "Foot Locker brand analyst",
    "DICKS Sporting Goods coordinator",
    "DICKS Sporting Goods analyst",
    "Academy Sports coordinator analyst",

    # ── Drinkware / Gear ─────────────────────────────────────────────────────
    "Stanley brand coordinator",
    "Stanley marketing analyst",
    "Stanley product coordinator",
    "Owala brand coordinator",
    "Owala marketing analyst",

    # ── Hockey ────────────────────────────────────────────────────────────────
    "Bauer Hockey coordinator analyst",
    "Bauer brand coordinator",
    "Bauer product coordinator",

    # ── Golf ──────────────────────────────────────────────────────────────────
    "Callaway Golf coordinator analyst",
    "TaylorMade coordinator analyst",
    "Titleist coordinator analyst",

    # ── Action Sports / Snow ──────────────────────────────────────────────────
    "Burton Snowboards coordinator analyst",
    "Burton brand coordinator",
    "Quiksilver coordinator analyst",
    "Billabong coordinator analyst",
    "Volcom brand coordinator",
    "Hurley brand coordinator",

    # ── Footwear gaps ─────────────────────────────────────────────────────────
    "Mizuno coordinator analyst",
    "Mizuno product coordinator",
    "Saucony brand coordinator",
    "Saucony marketing analyst",
    "Sperry brand coordinator",
    "Sperry marketing analyst",
    "Keen Footwear coordinator analyst",
    "Keen brand coordinator",
    "K-Swiss brand coordinator",
    "Fila brand coordinator",
    "Fila marketing analyst",
    "Speedo coordinator analyst",
    "Speedo brand associate",



    # ── Apparel gaps ──────────────────────────────────────────────────────────
    "Champion brand coordinator",
    "Hanesbrands coordinator analyst",
    "Smartwool brand coordinator",
    "Icebreaker brand coordinator",
    "Cotopaxi coordinator analyst",
    "Outdoor Research coordinator analyst",
    "Black Diamond coordinator analyst",

    # ── Sports Tech / Wearables ───────────────────────────────────────────────
    "WHOOP coordinator analyst",
    "Oura Ring coordinator analyst",
    "Garmin marketing coordinator",
    "Garmin brand analyst",
    "Peloton coordinator analyst",

    # ── Sports Media ──────────────────────────────────────────────────────────
    "ESPN coordinator analyst",
    "ESPN brand associate",
    "Disney Sports coordinator",
    "FOX Sports coordinator analyst",
    "NBC Sports coordinator analyst",
    "Turner Sports coordinator analyst",
    "Warner Bros Discovery sports coordinator",
    "Bleacher Report coordinator analyst",
    "The Athletic coordinator analyst",

    # ── Sports Leagues ────────────────────────────────────────────────────────
    "NBA coordinator analyst",
    "NBA business associate",
    "NBA marketing coordinator",
    "NFL coordinator analyst",
    "NFL business associate",
    "NFL marketing coordinator",
    "MLB coordinator analyst",
    "MLB business associate",
    "MLB marketing coordinator",
    "MLS coordinator analyst",
    "MLS brand associate",
    "NHL coordinator analyst",
    "NHL business associate",
    "PGA Tour coordinator analyst",
    "USTA coordinator analyst",
    "US Soccer coordinator",
    "Formula 1 coordinator analyst",
    "NASCAR coordinator analyst",

    # ── United Airlines only ──────────────────────────────────────────────────
    "United Airlines brand coordinator",
    "United Airlines marketing analyst",
    "United Airlines coordinator analyst",

    # ── CPG — per company ─────────────────────────────────────────────────────
    "Procter Gamble brand analyst",
    "Procter Gamble marketing coordinator",
    "Procter Gamble associate brand manager",
    "Unilever brand analyst",
    "Unilever marketing coordinator",
    "Unilever associate brand manager",
    "PepsiCo brand analyst",
    "PepsiCo marketing coordinator",
    "PepsiCo associate brand manager",
    "Coca-Cola brand analyst",
    "Coca-Cola marketing coordinator",
    "Coca-Cola associate brand manager",
    "Kraft Heinz brand analyst",
    "Kraft Heinz marketing coordinator",
    "Mondelez brand analyst",
    "Mondelez marketing coordinator",
    "Mars brand analyst",
    "Mars marketing coordinator",
    "Mars associate brand manager",
    "Nestle brand analyst",
    "Nestle marketing coordinator",
    "General Mills brand analyst",
    "General Mills marketing coordinator",
    "General Mills associate brand manager",
    "Kellanova brand analyst",
    "Kellanova marketing coordinator",
    "Conagra brand analyst",
    "Conagra marketing coordinator",
    "Clorox brand analyst",
    "Clorox marketing coordinator",
    "Keurig Dr Pepper coordinator analyst",
    "Church Dwight brand analyst",
    "Henkel brand coordinator",
    "Edgewell brand coordinator",
    "Colgate Palmolive coordinator analyst",
    "SC Johnson brand coordinator",
    "Energizer brand coordinator",

    # ── International — Europe (broad sweeps) ───────────────────────────────
    "footwear brand coordinator Europe",
    "footwear brand analyst Europe",
    "footwear brand product coordinator Europe",
    "sportswear brand coordinator Europe",
    "sportswear brand analyst Europe",
    "athletic apparel coordinator London UK",
    "athletic apparel coordinator Netherlands",
    "athletic apparel coordinator Germany",
    "athletic apparel coordinator Switzerland",
    "outdoor apparel coordinator Europe",
    "CPG brand coordinator London UK",
    "CPG brand analyst London UK",
    "CPG marketing coordinator Europe",
    "consumer goods coordinator Amsterdam",
    "consumer goods coordinator Germany",

    # ── International — Australia ─────────────────────────────────────────────
    "Nike coordinator Australia",
    "Adidas coordinator Australia",
    "lululemon coordinator Australia",
    "New Balance coordinator Australia",
    "ASICS coordinator Australia",
    "Under Armour coordinator Australia",
    "Deckers coordinator Australia",
    "PepsiCo coordinator Australia",
    "Nestle coordinator Australia",
    "Unilever coordinator Australia",
    "Columbia Sportswear coordinator Australia",

    # ── Broad sweeps — Footwear & Sportswear ──────────────────────────────────
    "footwear brand product coordinator",
    "footwear brand product line manager",
    "footwear brand merchandiser",
    "footwear brand merchandising coordinator",
    "footwear brand product testing coordinator",
    "footwear brand marketing coordinator",
    "footwear brand business analyst",
    "footwear brand digital analyst",
    "footwear brand ecommerce coordinator",
    "sportswear product coordinator full time",
    "sportswear product line manager",
    "sportswear merchandiser full time",
    "sportswear merchandising coordinator",
    "sportswear marketing coordinator",
    "sportswear brand analyst associate",
    "athletic apparel product coordinator",
    "athletic apparel merchandiser",
    "athletic apparel product line manager",
    "athletic apparel marketing coordinator",
    "athletic brand coordinator full time",
    "athletic brand business analyst",
    "outdoor apparel product coordinator",
    "outdoor apparel merchandiser",
    "outdoor apparel brand coordinator",
    "outdoor apparel brand analyst",
    "lifestyle brand product coordinator",
    "lifestyle brand merchandiser",
    "lifestyle brand marketing coordinator",

    # ── Broad sweeps — CPG & Sports ───────────────────────────────────────────
    "sports brand marketing analyst full time",
    "sports brand coordinator full time",
    "sports brand digital coordinator",
    "sports media coordinator full time",
    "sports business analyst full time",
    "sports league coordinator full time",
    "sports marketing coordinator full time",
    "sports sponsorship coordinator analyst",
    "brand partnerships coordinator analyst",
    "CPG brand analyst full time",
    "CPG marketing coordinator full time",
    "CPG associate brand manager full time",
    "consumer goods brand analyst full time",
    "consumer goods marketing coordinator",
    "consumer goods coordinator associate",
    "FMCG marketing coordinator analyst",
    "brand management coordinator full time",
    "digital marketing coordinator brand",
    "product marketing coordinator analyst",
    "ecommerce coordinator analyst brand",
    "social media coordinator brand full time",
    "category analyst coordinator brand",
    "trade marketing coordinator analyst",
    "merchandising coordinator analyst brand",
    "consumer insights analyst brand",
    "market research analyst brand",
]


def fetch_all_api_jobs() -> Generator[dict, None, None]:
    if not JSEARCH_API_KEY:
        logger.warning("JSEARCH_API_KEY not set — skipping JSearch.")
        return

    seen_ids: set = set()
    total = len(JSEARCH_QUERIES)

    for i, query in enumerate(JSEARCH_QUERIES, 1):
        logger.info("Query %d/%d: '%s'", i, total, query)
        jobs = fetch_jsearch_query(query)
        new = 0
        for job in jobs:
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                new += 1
                yield job
        logger.info("  → %d new results", new)
        time.sleep(0.2)
