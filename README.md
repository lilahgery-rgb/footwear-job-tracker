# 👟 Footwear Job Tracker

Automatically monitors job postings across major footwear brands and sends real-time Slack notifications.

**Tracks:** Nike, Adidas, New Balance, Puma, Skechers, Under Armour, Reebok, On Running, Hoka, Brooks, Asics, Salomon, Converse, Vans, Timberland, UGG, Birkenstock, Crocs, Merrell, and more.

**Sources:**
- 🏢 **Workday career pages** — Direct scraping of each brand's own ATS
- 🌐 **JSearch API** — Aggregates listings from LinkedIn, Indeed, Glassdoor

---

## 🚀 Quick Start

### 1. Clone this repo
```bash
git clone https://github.com/YOUR_USERNAME/footwear-job-tracker.git
cd footwear-job-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up a Slack Incoming Webhook
1. Go to https://api.slack.com/apps and create a new app (or use an existing one)
2. Enable **Incoming Webhooks** under "Features"
3. Click **Add New Webhook to Workspace** and select your channel
4. Copy the webhook URL

### 4. Get a JSearch API key (optional but recommended)
1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Subscribe to the free tier (500 requests/month)
3. Copy your RapidAPI key

### 5. Configure environment variables

**For local use**, create a `.env` file (never commit this):
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
JSEARCH_API_KEY=your_rapidapi_key_here

# Optional: only notify for jobs matching these keywords (comma-separated)
# Leave unset to receive ALL job postings
JOB_KEYWORDS=product manager,design,marketing
```

Then load it before running:
```bash
export $(cat .env | xargs) && python main.py
```

**For GitHub Actions**, add secrets at:
`Your Repo → Settings → Secrets and variables → Actions → New repository secret`

Add:
- `SLACK_WEBHOOK_URL`
- `JSEARCH_API_KEY`
- `JOB_KEYWORDS` *(optional)*

### 6. Run it
```bash
python main.py
```

The tracker will run, check for new jobs, and post any findings to your Slack channel.

---

## 📅 Automated Scheduling (GitHub Actions)

Push this repo to GitHub. The included workflow (`.github/workflows/job_tracker.yml`) will automatically run the tracker **twice daily** at 8 AM and 5 PM UTC.

The SQLite database is cached between runs so you won't be re-notified about jobs you've already seen.

To change the schedule, edit the `cron` values in the workflow file:
```yaml
- cron: "0 8 * * *"   # 8 AM UTC
- cron: "0 17 * * *"  # 5 PM UTC
```
Use https://crontab.guru to build your schedule.

---

## 🔧 Configuration

All configuration lives in `config.py`:

| Setting | Description |
|---|---|
| `WORKDAY_COMPANIES` | List of brands to scrape via Workday |
| `JSEARCH_QUERIES` | Search queries sent to JSearch |
| `MAX_AGE_DAYS` | Only include API jobs posted within N days |
| `KEYWORDS` | Filter jobs by title/description keywords |

### Adding a new company
If a company uses Workday, add them to `WORKDAY_COMPANIES` in `config.py`:
```python
{
    "name": "Merrell",
    "tenant": "merrell",
    "subdomain": "merrell.wd5",
    "url": "https://careers.merrell.com",
},
```
To find the tenant and subdomain, visit the company's careers page and look at the URL — it will contain something like `merrell.wd5.myworkdayjobs.com`.

---

## 📁 Project Structure

```
footwear-job-tracker/
├── main.py              # Entry point — runs the full pipeline
├── config.py            # All configuration (companies, keywords, etc.)
├── scraper.py           # Workday career page scraper
├── api_fetcher.py       # JSearch API client
├── notifier.py          # Slack notification sender
├── db.py                # SQLite deduplication store
├── requirements.txt
└── .github/
    └── workflows/
        └── job_tracker.yml  # GitHub Actions scheduler
```

---

## 💡 Tips

- **Filter by role type** — Set `JOB_KEYWORDS=design,marketing,engineering` to only get notified for roles that match your interests.
- **Adjust frequency** — Change the cron schedule to run hourly if you want faster alerts.
- **Multiple Slack channels** — Modify `notifier.py` to route different companies to different channels.
