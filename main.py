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

import json
import logging
import sys
from pathlib import Path

from db import init_db, is_new_job, mark_job_seen
from scraper import scrape_all_companies
from api_fetcher import fetch_all_api_jobs
from notifier import send_jobs_to_slack, send_heartbeat
from generate_dashboard import load_jobs, generate

JOBS_LOG = Path(__file__).parent / "all_jobs.json"

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def log_jobs_to_file(new_jobs: list[dict]):
    """Append new jobs to the persistent JSON log and regenerate the dashboard."""
    existing = load_jobs()
    existing_ids = {j["id"] for j in existing}
    to_add = [j for j in new_jobs if j["id"] not in existing_ids]
    if to_add:
        updated = existing + to_add
        with open(JOBS_LOG, "w") as f:
            json.dump(updated, f, indent=2, default=str)
        logger.info("Logged %d new job(s) to all_jobs.json", len(to_add))
    generate(load_jobs())
    logger.info("Dashboard regenerated.")


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

    # ── 3. Log to file + regenerate dashboard ──────────────────────────────────
    logger.info("Phase 3: Updating job log and dashboard…")
    log_jobs_to_file(new_jobs)

    # ── 4. Send Slack notifications ────────────────────────────────────────────
    logger.info("Phase 4: Sending notifications…")
    logger.info("Found %d new job(s) out of %d checked.", len(new_jobs), total_checked)

    if new_jobs:
        send_jobs_to_slack(new_jobs)

    send_heartbeat(total_checked=total_checked, new_found=len(new_jobs))

    logger.info("Run complete.")


if __name__ == "__main__":
    run()
