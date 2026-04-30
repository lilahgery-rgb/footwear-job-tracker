"""
notifier.py -- Sends Slack notifications for new jobs.
If no Slack webhook is set, silently skips notification.
"""

import logging
import requests
from config import SLACK_WEBHOOK_URL

logger = logging.getLogger(__name__)

MAX_JOBS_PER_MESSAGE = 10

COMPANY_EMOJI = {
    "Nike": "swoosh",
    "Adidas": "3️⃣",
    "New Balance": "🔵",
    "Puma": "🐆",
    "Wilson": "🎾",
    "Under Armour": "🛡️",
    "On Running": "⚡",
    "Hoka": "🏔️",
    "Brooks Running": "🏃",
    "lululemon": "🧘",
    "Arc'teryx": "🧗",
    "Patagonia": "🌊",
    "Default": "👟",
}


def _get_emoji(company):
    for name, emoji in COMPANY_EMOJI.items():
        if name.lower() in company.lower():
            return emoji
    return COMPANY_EMOJI["Default"]


def _job_block(job):
    emoji = _get_emoji(job["company"])
    location = job.get("location") or "Location not listed"
    source = job.get("source", "")
    source_label = "Job Board" if source == "jsearch_api" else "Career Page"

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "%s *<%s|%s>*\n*%s*  -  %s  -  %s"
                    % (emoji, job["url"], job["title"], job["company"], location, source_label)
                ),
            },
        },
        {"type": "divider"},
    ]


def _build_payload(jobs):
    header_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "👟 %d New Job%s Found!" % (len(jobs), "s" if len(jobs) != 1 else ""),
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    job_blocks = []
    for job in jobs:
        job_blocks.extend(_job_block(job))

    return {"blocks": header_blocks + job_blocks}


def send_jobs_to_slack(jobs):
    if not jobs:
        logger.info("No new jobs to notify.")
        return

    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL not set - skipping Slack notification.")
        return

    for i in range(0, len(jobs), MAX_JOBS_PER_MESSAGE):
        chunk = jobs[i: i + MAX_JOBS_PER_MESSAGE]
        payload = _build_payload(chunk)
        try:
            resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info(
                "Slack notification sent for %d job(s) (batch %d).",
                len(chunk),
                i // MAX_JOBS_PER_MESSAGE + 1,
            )
        except requests.RequestException as exc:
            logger.error("Failed to send Slack notification: %s", exc)
def _build_payload(jobs: list[dict]) -> dict:
    """Build the full Slack webhook payload for a list of jobs."""
    header_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"👟 {len(jobs)} New Footwear Job{'s' if len(jobs) != 1 else ''} Found!",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Powered by your Footwear Job Tracker • Sources: Workday career pages + JSearch API",
                }
            ],
        },
        {"type": "divider"},
    ]

    job_blocks = []
    for job in jobs:
        job_blocks.extend(_job_block(job))

    return {"blocks": header_blocks + job_blocks}


def send_jobs_to_slack(jobs: list[dict]):
    """
    Send a list of new jobs to Slack.
    Automatically chunks into multiple messages if needed.
    """
    if not jobs:
        logger.info("No new jobs to notify.")
        return

    if not SLACK_WEBHOOK_URL:
        logger.error("SLACK_WEBHOOK_URL is not set. Cannot send notification.")
        return

    # Chunk into batches to stay within Slack's block limits
    for i in range(0, len(jobs), MAX_JOBS_PER_MESSAGE):
        chunk = jobs[i : i + MAX_JOBS_PER_MESSAGE]
        payload = _build_payload(chunk)

        try:
            resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info(
                "Slack notification sent for %d job(s) (batch %d).",
                len(chunk),
                i // MAX_JOBS_PER_MESSAGE + 1,
            )
        except requests.RequestException as exc:
            logger.error("Failed to send Slack notification: %s", exc)


def send_heartbeat(total_checked: int, new_found: int):
    """
    Send a short summary/heartbeat message to Slack after each run.
    Useful for confirming the tracker is working even when no new jobs appear.
    """
    if not SLACK_WEBHOOK_URL:
        return

    status = "✅ All good" if new_found == 0 else f"🆕 {new_found} new job(s) sent above"
    payload = {
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"*Footwear Job Tracker* run complete  |  "
                            f"Checked *{total_checked}* listings  |  "
                            f"{status}"
                        ),
                    }
                ],
            }
        ]
    }

    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    except requests.RequestException as exc:
        logger.warning("Heartbeat notification failed: %s", exc)
