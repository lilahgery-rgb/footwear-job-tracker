"""
config.py — Central configuration.

Set your secrets as environment variables (or in a .env file).
Never hardcode API keys here.
"""

import os

# ── Slack ─────────────────────────────────────────────────────────────────────
# Create an Incoming Webhook at https://api.slack.com/apps → your app → Incoming Webhooks
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# ── JSearch API (RapidAPI) ────────────────────────────────────────────────────
# Sign up at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY", "")

# ── Job filtering ─────────────────────────────────────────────────────────────
# Keywords to narrow down results. Leave empty to get ALL roles.
KEYWORDS = os.environ.get("JOB_KEYWORDS", "").split(",") if os.environ.get("JOB_KEYWORDS") else []

# Only notify for jobs posted within this many days (used for API results)
MAX_AGE_DAYS = 1

# ── Workday companies to scrape ───────────────────────────────────────────────
# Format: { display_name, workday_tenant, base_url }
# To find a company's Workday tenant, look at their careers URL:
#   e.g. nike.wd1.myworkdayjobs.com → tenant = "nike"
WORKDAY_COMPANIES = [
    {
        "name": "Nike",
        "tenant": "nike",
        "subdomain": "nike.wd1",
        "url": "https://jobs.nike.com",
    },
    {
        "name": "Adidas",
        "tenant": "adidas",
        "subdomain": "adidas.wd3",
        "url": "https://careers.adidas.com",
    },
    {
        "name": "New Balance",
        "tenant": "newbalance",
        "subdomain": "newbalance.wd1",
        "url": "https://jobs.newbalance.com",
    },
    {
        "name": "Puma",
        "tenant": "puma",
        "subdomain": "puma.wd3",
        "url": "https://about.puma.com/en/careers",
    },
    {
        "name": "Skechers",
        "tenant": "skechers",
        "subdomain": "skechers.wd5",
        "url": "https://careers.skechers.com",
    },
    {
        "name": "Under Armour",
        "tenant": "underarmour",
        "subdomain": "underarmour.wd5",
        "url": "https://careers.underarmour.com",
    },
    {
        "name": "Reebok",
        "tenant": "adidasshoesource",  # Reebok uses Adidas's parent ATS
        "subdomain": "adidasshoesource.wd3",
        "url": "https://careers.reebok.com",
    },
    {
        "name": "On Running",
        "tenant": "onrunning",
        "subdomain": "onrunning.wd3",
        "url": "https://www.onrunning.com/en-us/careers",
    },
]

# ── JSearch company queries ───────────────────────────────────────────────────
# These are the search queries sent to JSearch to supplement scraping.
JSEARCH_QUERIES = [
    "Nike jobs",
    "Adidas jobs",
    "New Balance jobs",
    "Puma jobs",
    "Skechers jobs",
    "Under Armour jobs",
    "Reebok jobs",
    "On Running jobs",
    "Hoka jobs",
    "Brooks Running jobs",
    "Asics jobs",
    "Salomon footwear jobs",
    "Converse jobs",
    "Vans jobs",
    "Timberland jobs",
    "UGG jobs",
    "Birkenstock jobs",
    "Crocs jobs",
    "Merrell jobs",
    "footwear brand jobs",
]
