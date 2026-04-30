"""
main.py -- Footwear Job Tracker

Run order:
  Phase 1: Brand scrapers  -- direct ATS queries for top 30 footwear brands
  Phase 2: JSearch API     -- broad queries for CPG, leagues, media, etc.
  Phase 3: Dashboard       -- rebuild HTML dashboard
  Phase 4: Notify          -- Slack/email new jobs
"""

import json
import logging
import os
import sys
from pathlib import Path

from brand_scrapers import fetch_all_brand_jobs
from api_fetcher import fetch_all_api_jobs
from db import JobDatabase
from notifier import notify
from generate_dashboard import load_jobs, generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

JOBS_LOG = Path(__file__).parent / "all_jobs.json"


def load_existing_jobs() -> list[dict]:
    if not JOBS_LOG.exists():
        return []
    with open(JOBS_LOG) as f:
        return json.load(f)


def save_jobs(jobs: list[dict]):
    with open(JOBS_LOG, "w") as f:
        json.dump(jobs, f, indent=2)


def run():
    logger.info("=" * 60)
    logger.info("Footwear Job Tracker - starting run")
    logger.info("=" * 60)

    db = JobDatabase()
    new_jobs = []

    # ── Phase 1: Brand scrapers (top 30 footwear brands, ALL jobs) ───────────
    logger.info("Phase 1: Direct brand ATS scrapers...")
    brand_count = 0
    for job in fetch_all_brand_jobs():
        if db.is_new(job["id"]):
            db.mark_seen(job["id"])
            new_jobs.append(job)
            brand_count += 1
            logger.info(
                "  NEW [%s] %s @ %s",
                job["source"], job["title"], job["company"]
            )
    logger.info("Phase 1 complete: %d new jobs from brand scrapers", brand_count)

    # ── Phase 2: JSearch (secondary brands, CPG, leagues, media) ────────────
    logger.info("Phase 2: JSearch API queries...")
    api_count = 0
    for job in fetch_all_api_jobs():
        if db.is_new(job["id"]):
            db.mark_seen(job["id"])
            new_jobs.append(job)
            api_count += 1
            logger.info(
                "  NEW [%s] %s @ %s",
                job["source"], job["title"], job["company"]
            )
    logger.info("Phase 2 complete: %d new jobs from JSearch", api_count)

    # ── Phase 3: Update dashboard ────────────────────────────────────────────
    logger.info("Phase 3: Updating job log and dashboard...")
    all_jobs = load_existing_jobs()
    all_jobs.extend(new_jobs)
    save_jobs(all_jobs)
    logger.info("Logged %d new job(s) to all_jobs.json", len(new_jobs))
    generate(all_jobs)
    logger.info("Dashboard regenerated.")

    # ── Phase 4: Notify ──────────────────────────────────────────────────────
    logger.info("Phase 4: Sending notifications...")
    if new_jobs:
        logger.info("Found %d new job(s).", len(new_jobs))
        notify(new_jobs)
    else:
        logger.info("No new jobs this run.")

    logger.info("Run complete.")


if __name__ == "__main__":
    run()    new_jobs: list[dict] = []
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
