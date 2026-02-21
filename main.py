"""
main.py — Footwear Job Tracker entry point.

Run this script on a schedule to detect new job postings across major
footwear brands and get notified in Slack.

Usage:
    python main.py

Environment variables (required):
    SLACK_WEBHOOK_URL   — Your Slack Incoming Webhook URL
    JSEARCH_API_KEY     — Your RapidAPI key for JSearch (optional but recommended)

Optional:
    JOB_KEYWORDS        — Comma-separated keywords to filter jobs
                          e.g. "product manager,marketing,design"
"""

import logging
import sys

from db import init_db, is_new_job, mark_job_seen
from scraper import scrape_all_companies
from api_fetcher import fetch_all_api_jobs
from notifier import send_jobs_to_slack, send_heartbeat

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run():
    logger.info("=" * 60)
    logger.info("Footwear Job Tracker — starting run")
    logger.info("=" * 60)

    # Initialize the database
    init_db()

    new_jobs: list[dict] = []
    total_checked = 0

    # ── 1. Scrape Workday career pages ─────────────────────────────────────────
    logger.info("Phase 1: Scraping Workday career pages…")
    for job in scrape_all_companies():
        total_checked += 1
        if is_new_job(job["id"]):
            new_jobs.append(job)
            mark_job_seen(job)
            logger.info("  NEW  [%s] %s @ %s", job["source"], job["title"], job["company"])

    # ── 2. Fetch from JSearch API ──────────────────────────────────────────────
    logger.info("Phase 2: Fetching from JSearch API…")
    for job in fetch_all_api_jobs():
        total_checked += 1
        if is_new_job(job["id"]):
            new_jobs.append(job)
            mark_job_seen(job)
            logger.info("  NEW  [%s] %s @ %s", job["source"], job["title"], job["company"])

    # ── 3. Send Slack notifications ────────────────────────────────────────────
    logger.info("Phase 3: Sending notifications…")
    logger.info("Found %d new job(s) out of %d checked.", len(new_jobs), total_checked)

    if new_jobs:
        send_jobs_to_slack(new_jobs)

    send_heartbeat(total_checked=total_checked, new_found=len(new_jobs))

    logger.info("Run complete.")


if __name__ == "__main__":
    run()
