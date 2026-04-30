"""
main.py -- Footwear Job Tracker
"""

import json
import logging
from pathlib import Path

from scraper import scrape_all_companies
from api_fetcher import fetch_all_api_jobs
from db import init_db, is_new_job, mark_job_seen
from notifier import send_jobs_to_slack
from generate_dashboard import load_jobs, generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

JOBS_LOG = Path(__file__).parent / "all_jobs.json"


def load_existing_jobs():
    if not JOBS_LOG.exists():
        return []
    with open(JOBS_LOG) as f:
        return json.load(f)


def save_jobs(jobs):
    with open(JOBS_LOG, "w") as f:
        json.dump(jobs, f, indent=2)


def run():
    logger.info("=" * 60)
    logger.info("Footwear Job Tracker - starting run")
    logger.info("=" * 60)

    init_db()
    new_jobs = []

    # Phase 1: Scraper (TeamWork Online)
    logger.info("Phase 1: Scraping career pages...")
    for job in scrape_all_companies():
        if is_new_job(job["id"]):
            mark_job_seen(job)
            new_jobs.append(job)
            logger.info("  NEW  [%s] %s @ %s", job["source"], job["title"], job["company"])

    # Phase 2: JSearch API
    logger.info("Phase 2: Fetching from JSearch API...")
    for job in fetch_all_api_jobs():
        if is_new_job(job["id"]):
            mark_job_seen(job)
            new_jobs.append(job)
            logger.info("  NEW  [%s] %s @ %s", job["source"], job["title"], job["company"])

    # Phase 3: Update dashboard
    logger.info("Phase 3: Updating job log and dashboard...")
    all_jobs = load_existing_jobs()
    all_jobs.extend(new_jobs)
    save_jobs(all_jobs)
    logger.info("Logged %d new job(s) to all_jobs.json", len(new_jobs))
    generate(load_jobs())
    logger.info("Dashboard regenerated.")

    # Phase 4: Notify
    logger.info("Phase 4: Sending notifications...")
    if new_jobs:
        logger.info("Found %d new job(s).", len(new_jobs))
        send_jobs_to_slack(new_jobs)
    else:
        logger.info("No new jobs this run.")

    logger.info("Run complete.")


if __name__ == "__main__":
    run()
