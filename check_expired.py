"""
check_expired.py — Checks each job URL and removes listings that are no longer active.

Runs automatically as part of the GitHub Actions workflow before the dashboard
is regenerated. Dead links (404s, redirects to homepage) are removed from
all_jobs.json so they don't clutter your dashboard.
"""

import json
import logging
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

JOBS_LOG = Path(__file__).parent / "all_jobs.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# If a URL redirects to any of these, the job is gone
DEAD_URL_SIGNALS = [
    "/jobs",
    "/careers",
    "/search",
    "?q=",
    "no-longer",
    "expired",
    "not found",
    "job-not-found",
]


def is_job_active(url: str) -> bool:
    """
    Return True if the job URL still appears to be a live posting.
    Returns True on any error so we don't accidentally remove jobs
    due to network issues.
    """
    if not url:
        return True
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)

        # Hard 404 — job is definitely gone
        if resp.status_code == 404:
            return False

        # If we got redirected to a generic search/careers page, job is gone
        final_url = resp.url.lower()
        if any(signal in final_url for signal in DEAD_URL_SIGNALS):
            # Make sure the final URL is meaningfully different from the original
            if len(final_url) < len(url) * 0.8:
                return False

        return True

    except requests.RequestException:
        # Network error — assume still active to be safe
        return True


def remove_expired_jobs():
    """
    Load all_jobs.json, check each URL, remove expired ones, and save.
    Returns the number of jobs removed.
    """
    if not JOBS_LOG.exists():
        logger.info("No jobs log found — skipping expiration check.")
        return 0

    with open(JOBS_LOG) as f:
        jobs = json.load(f)

    if not jobs:
        return 0

    logger.info("Checking %d jobs for expiration…", len(jobs))

    active_jobs = []
    removed = 0

    for i, job in enumerate(jobs):
        url = job.get("url", "")
        active = is_job_active(url)

        if active:
            active_jobs.append(job)
        else:
            removed += 1
            logger.info(
                "  EXPIRED  [%s] %s @ %s",
                job.get("source", ""),
                job.get("title", ""),
                job.get("company", ""),
            )

        # Be polite — don't hammer servers
        if i % 10 == 0:
            time.sleep(0.5)

    with open(JOBS_LOG, "w") as f:
        json.dump(active_jobs, f, indent=2, default=str)

    logger.info(
        "Expiration check complete: %d active, %d removed.",
        len(active_jobs),
        removed,
    )
    return removed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
    remove_expired_jobs()
