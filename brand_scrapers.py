"""
brand_scrapers.py

Queries each brand's ATS (Applicant Tracking System) API directly.
Returns EVERY job posted - no keyword filtering, no missed jobs.
Only filter: exclude retail store jobs.

ATS systems:
- Workday:        Nike, New Balance, Under Armour, Deckers/HOKA/UGG,
                  lululemon, Columbia, VF Corp (Vans, TNF, Timberland),
                  Skechers, Wolverine (Merrell, Sperry)
- Greenhouse:     On Running, Arc'teryx, Allbirds, Vuori, Alo Yoga,
                  Patagonia, Crocs, Stanley, Owala
- SmartRecruiters: ASICS, Brooks Running, Salomon, Burton, Gymshark
- iCIMS:          Wilson, New Era, Fabletics
- Lever:          Birkenstock, WHOOP
"""

import logging
import re
import time
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
    "Accept": "application/json",
}

# The ONLY filter we apply - retail store jobs
RETAIL_EXCLUDE = [
    "retail", "store manager", "sales associate", "store associate",
    "stock associate", "stocking associate", "shipping associate",
    "inventory associate", "cashier", "floor supervisor",
    "key holder", "keyholder", "outlet", "factory store",
    "part-time", "part time", "seasonal", "temporary",
    "child care", "daycare", "janitor", "custodian", "security guard",
]


def _is_retail(title: str, extra: str = "") -> bool:
    combined = (title + " " + extra).lower()
    return any(kw in combined for kw in RETAIL_EXCLUDE)


# =============================================================================
# WORKDAY
# =============================================================================
# Workday has a public POST endpoint that returns JSON job listings.
# tenant = the company's Workday subdomain
# site   = the career site name (usually "External" or company-specific)

WORKDAY_COMPANIES = {
    "Nike":           ("nike",              "Nike_Ext"),
    "New Balance":    ("newbalance",        "newbalance"),
    "Under Armour":   ("underarmour",       "underarmour"),
    "Hoka":           ("deckers",           "HOKA"),
    "UGG":            ("deckers",           "UGG"),
    "Deckers":        ("deckers",           "Deckers_Ext"),
    "lululemon":      ("lululemon",         "lululemon"),
    "Columbia":       ("columbia",          "Columbia_Ext"),
    "The North Face": ("vfc",              "TNF_Ext"),
    "Vans":           ("vfc",              "Vans_Ext"),
    "Timberland":     ("vfc",              "Timberland_Ext"),
    "Wolverine":      ("wolverineworldwide", "Wolverine_Ext"),
    "Merrell":        ("wolverineworldwide", "Merrell_Ext"),
    "Sperry":         ("wolverineworldwide", "Sperry_Ext"),
    "Skechers":       ("skechers",          "Skechers_Ext"),
}


def scrape_workday(company_name: str, tenant: str, site: str) -> list[dict]:
    url = (
        f"https://{tenant}.wd1.myworkdayjobs.com"
        f"/wday/cxs/{tenant}/{site}/jobs"
    )
    payload = {"limit": 20, "offset": 0, "searchText": ""}
    jobs = []
    offset = 0

    while True:
        payload["offset"] = offset
        try:
            resp = requests.post(url, json=payload, headers=HEADERS, timeout=15)
            if resp.status_code not in (200, 201):
                logger.warning(
                    "Workday %s: HTTP %s", company_name, resp.status_code
                )
                break
            data = resp.json()
        except Exception as exc:
            logger.warning("Workday %s: %s", company_name, exc)
            break

        postings = data.get("jobPostings", [])
        if not postings:
            break

        for job in postings:
            title = job.get("title", "")
            if _is_retail(title):
                continue
            path = job.get("externalPath", "")
            job_url = (
                f"https://{tenant}.wd1.myworkdayjobs.com"
                f"/en-US/{site}{path}"
            )
            jobs.append({
                "id": f"wd-{tenant}-{site}-{hash(path)}",
                "title": title,
                "company": company_name,
                "location": job.get("locationsText", ""),
                "url": job_url,
                "source": "brand_scraper",
                "posted_on": job.get("postedOn", ""),
            })

        total = data.get("total", 0)
        offset += 20
        if offset >= total:
            break
        time.sleep(0.3)

    logger.info("  Workday %s: %d jobs", company_name, len(jobs))
    return jobs


# =============================================================================
# GREENHOUSE
# =============================================================================
# Greenhouse has a fully public REST API - no auth required.

GREENHOUSE_COMPANIES = {
    "On Running":  "on",
    "Arc'teryx":   "arcteryx",
    "Allbirds":    "allbirds",
    "Vuori":       "vuori",
    "Alo Yoga":    "aloyoga",
    "Patagonia":   "patagonia",
    "Crocs":       "crocs",
    "Stanley":     "stanleypmigroupinc",
    "Owala":       "owala",
    "Cotopaxi":    "cotopaxi",
}


def scrape_greenhouse(company_name: str, board_token: str) -> list[dict]:
    url = (
        f"https://api.greenhouse.io/v1/boards/{board_token}/jobs"
        f"?content=true"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            logger.warning(
                "Greenhouse %s: HTTP %s", company_name, resp.status_code
            )
            return []
        data = resp.json()
    except Exception as exc:
        logger.warning("Greenhouse %s: %s", company_name, exc)
        return []

    jobs = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        dept = ""
        if job.get("departments"):
            dept = job["departments"][0].get("name", "")
        if _is_retail(title, dept):
            continue
        location = job.get("location", {}).get("name", "")
        jobs.append({
            "id": f"gh-{board_token}-{job.get('id', '')}",
            "title": title,
            "company": company_name,
            "location": location,
            "url": job.get("absolute_url", ""),
            "source": "brand_scraper",
            "posted_on": (job.get("updated_at") or "")[:10],
        })

    logger.info("  Greenhouse %s: %d jobs", company_name, len(jobs))
    return jobs


# =============================================================================
# SMARTRECRUITERS
# =============================================================================

SMARTRECRUITERS_COMPANIES = {
    "ASICS":          "ASICS",
    "Brooks Running": "BrooksRunning",
    "Salomon":        "Salomon",
    "Burton":         "BurtonSnowboards",
    "Gymshark":       "Gymshark",
}


def scrape_smartrecruiters(company_name: str, company_id: str) -> list[dict]:
    url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
    params = {"limit": 100, "offset": 0}
    jobs = []

    while True:
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                logger.warning(
                    "SmartRecruiters %s: HTTP %s", company_name, resp.status_code
                )
                break
            data = resp.json()
        except Exception as exc:
            logger.warning("SmartRecruiters %s: %s", company_name, exc)
            break

        postings = data.get("content", [])
        if not postings:
            break

        for job in postings:
            title = job.get("name", "")
            dept = ""
            if job.get("department"):
                dept = job["department"].get("label", "")
            if _is_retail(title, dept):
                continue
            city = job.get("location", {}).get("city", "")
            country = job.get("location", {}).get("country", "")
            location = ", ".join(p for p in [city, country] if p)
            jobs.append({
                "id": f"sr-{company_id}-{job.get('id', '')}",
                "title": title,
                "company": company_name,
                "location": location,
                "url": job.get("ref", ""),
                "source": "brand_scraper",
                "posted_on": (job.get("updatedOn") or "")[:10],
            })

        total = data.get("totalFound", 0)
        params["offset"] = params.get("offset", 0) + 100
        if params["offset"] >= total:
            break
        time.sleep(0.3)

    logger.info("  SmartRecruiters %s: %d jobs", company_name, len(jobs))
    return jobs


# =============================================================================
# iCIMS
# =============================================================================

ICIMS_COMPANIES = {
    "Wilson":    "wilson",
    "New Era":   "newera",
    "Fabletics": "fabletics",
}


def scrape_icims(company_name: str, client_id: str) -> list[dict]:
    url = (
        f"https://careers-{client_id}.icims.com"
        f"/jobs/search?ss=1&searchRelation=keyword_all&in_iframe=1"
    )
    try:
        resp = requests.get(
            url,
            headers={**HEADERS, "Accept": "text/html"},
            timeout=15,
        )
        if resp.status_code != 200:
            logger.warning(
                "iCIMS %s: HTTP %s", company_name, resp.status_code
            )
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as exc:
        logger.warning("iCIMS %s: %s", company_name, exc)
        return []

    jobs = []
    job_cards = soup.find_all(
        "div", class_=re.compile(r"iCIMS_JobsTable_ListItem", re.I)
    ) or soup.find_all("li", class_=re.compile(r"job", re.I))

    for card in job_cards:
        title_el = card.find(["h2", "h3", "a"])
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title or _is_retail(title):
            continue
        link = card.find("a", href=True)
        job_url = link["href"] if link else ""
        if job_url and not job_url.startswith("http"):
            job_url = f"https://careers-{client_id}.icims.com{job_url}"
        loc_el = card.find(class_=re.compile(r"location", re.I))
        location = loc_el.get_text(strip=True) if loc_el else ""
        jobs.append({
            "id": f"icims-{client_id}-{abs(hash(job_url))}",
            "title": title,
            "company": company_name,
            "location": location,
            "url": job_url,
            "source": "brand_scraper",
            "posted_on": "",
        })

    logger.info("  iCIMS %s: %d jobs", company_name, len(jobs))
    return jobs


# =============================================================================
# LEVER
# =============================================================================

LEVER_COMPANIES = {
    "Birkenstock": "birkenstock",
    "WHOOP":       "whoop",
}


def scrape_lever(company_name: str, company_id: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{company_id}?mode=json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            logger.warning(
                "Lever %s: HTTP %s", company_name, resp.status_code
            )
            return []
        postings = resp.json()
    except Exception as exc:
        logger.warning("Lever %s: %s", company_name, exc)
        return []

    jobs = []
    for job in postings:
        title = job.get("text", "")
        dept = job.get("categories", {}).get("department", "")
        if _is_retail(title, dept):
            continue
        location = job.get("categories", {}).get("location", "")
        jobs.append({
            "id": f"lever-{company_id}-{job.get('id', '')}",
            "title": title,
            "company": company_name,
            "location": location,
            "url": job.get("hostedUrl", ""),
            "source": "brand_scraper",
            "posted_on": "",
        })

    logger.info("  Lever %s: %d jobs", company_name, len(jobs))
    return jobs


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def fetch_all_brand_jobs() -> Generator[dict, None, None]:
    """
    Pull ALL jobs from top footwear brands directly from their ATS.
    No keyword matching. Only retail jobs excluded.
    """
    seen_ids: set = set()

    def dedupe_yield(jobs):
        for job in jobs:
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                yield job

    logger.info("=== Phase 1: Workday brands ===")
    for company_name, (tenant, site) in WORKDAY_COMPANIES.items():
        yield from dedupe_yield(scrape_workday(company_name, tenant, site))
        time.sleep(0.5)

    logger.info("=== Phase 2: Greenhouse brands ===")
    for company_name, board_token in GREENHOUSE_COMPANIES.items():
        yield from dedupe_yield(scrape_greenhouse(company_name, board_token))
        time.sleep(0.3)

    logger.info("=== Phase 3: SmartRecruiters brands ===")
    for company_name, company_id in SMARTRECRUITERS_COMPANIES.items():
        yield from dedupe_yield(scrape_smartrecruiters(company_name, company_id))
        time.sleep(0.3)

    logger.info("=== Phase 4: iCIMS brands ===")
    for company_name, client_id in ICIMS_COMPANIES.items():
        yield from dedupe_yield(scrape_icims(company_name, client_id))
        time.sleep(0.3)

    logger.info("=== Phase 5: Lever brands ===")
    for company_name, company_id in LEVER_COMPANIES.items():
        yield from dedupe_yield(scrape_lever(company_name, company_id))
        time.sleep(0.3)
