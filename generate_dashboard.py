"""
generate_dashboard.py — Generates a static HTML dashboard from all_jobs.json.

Run automatically by the GitHub Action after each tracker run.
The output (dashboard.html) is deployed to GitHub Pages.
"""

import json
import os
from datetime import datetime
from pathlib import Path

JOBS_LOG = Path(__file__).parent / "all_jobs.json"
OUTPUT = Path(__file__).parent / "dashboard.html"


def load_jobs() -> list[dict]:
    if not JOBS_LOG.exists():
        return []
    with open(JOBS_LOG) as f:
        return json.load(f)


def generate(jobs: list[dict]):
    total = len(jobs)
    companies = sorted(set(j["company"] for j in jobs))
    sources = sorted(set(j["source"] for j in jobs))
    last_updated = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")

    # Build job rows for the table
    rows = ""
    for job in reversed(jobs):  # Most recent first
        source_label = "Job Board" if job["source"] == "jsearch_api" else "Career Page"
        source_class = "badge-api" if job["source"] == "jsearch_api" else "badge-workday"
        posted = job.get("posted_on", "")[:10] or "—"
        rows += f"""
        <tr>
            <td><a href="{job['url']}" target="_blank" rel="noopener">{job['title']}</a></td>
            <td>{job['company']}</td>
            <td>{job.get('location') or '—'}</td>
            <td>{posted}</td>
            <td><span class="badge {source_class}">{source_label}</span></td>
        </tr>"""

    company_options = "".join(f'<option value="{c}">{c}</option>' for c in companies)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Footwear & Sports Job Tracker</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #1d1d1f; }}

  header {{
    background: #1d1d1f;
    color: white;
    padding: 32px 40px;
  }}
  header h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
  header p {{ margin-top: 6px; color: #a1a1a6; font-size: 14px; }}

  .stats {{
    display: flex;
    gap: 16px;
    padding: 24px 40px;
    background: white;
    border-bottom: 1px solid #e5e5e7;
    flex-wrap: wrap;
  }}
  .stat {{
    background: #f5f5f7;
    border-radius: 10px;
    padding: 14px 22px;
    min-width: 140px;
  }}
  .stat-value {{ font-size: 26px; font-weight: 700; color: #1d1d1f; }}
  .stat-label {{ font-size: 12px; color: #6e6e73; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }}

  .controls {{
    padding: 20px 40px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
    background: white;
    border-bottom: 1px solid #e5e5e7;
  }}
  input, select {{
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 14px;
    outline: none;
    background: #f5f5f7;
    color: #1d1d1f;
  }}
  input {{ width: 260px; }}
  input:focus, select:focus {{ border-color: #0071e3; background: white; }}
  .result-count {{ margin-left: auto; font-size: 13px; color: #6e6e73; }}

  .table-wrap {{ padding: 24px 40px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  th {{ background: #f5f5f7; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #6e6e73; padding: 12px 16px; text-align: left; border-bottom: 1px solid #e5e5e7; }}
  td {{ padding: 13px 16px; font-size: 14px; border-bottom: 1px solid #f0f0f2; vertical-align: middle; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #fafafa; }}
  td a {{ color: #0071e3; text-decoration: none; font-weight: 500; }}
  td a:hover {{ text-decoration: underline; }}

  .badge {{ display: inline-block; padding: 3px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
  .badge-api {{ background: #e8f4fd; color: #0071e3; }}
  .badge-workday {{ background: #e9fbe9; color: #1a7f37; }}

  .empty {{ text-align: center; padding: 60px; color: #6e6e73; }}

  footer {{ text-align: center; padding: 24px; font-size: 12px; color: #a1a1a6; }}
</style>
</head>
<body>

<header>
  <h1>👟 Footwear & Sports Job Tracker</h1>
  <p>Entry-level & internship roles • Updated {last_updated}</p>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-value">{total}</div>
    <div class="stat-label">Total Jobs</div>
  </div>
  <div class="stat">
    <div class="stat-value">{len(companies)}</div>
    <div class="stat-label">Companies</div>
  </div>
  <div class="stat">
    <div class="stat-value" id="filtered-count">{total}</div>
    <div class="stat-label">Showing</div>
  </div>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Search by title, company, location…" oninput="filterTable()">
  <select id="company-filter" onchange="filterTable()">
    <option value="">All Companies</option>
    {company_options}
  </select>
  <select id="source-filter" onchange="filterTable()">
    <option value="">All Sources</option>
    <option value="Career Page">Career Page</option>
    <option value="Job Board">Job Board</option>
  </select>
</div>

<div class="table-wrap">
  <table id="jobs-table">
    <thead>
      <tr>
        <th>Title</th>
        <th>Company</th>
        <th>Location</th>
        <th>Posted</th>
        <th>Source</th>
      </tr>
    </thead>
    <tbody id="table-body">
      {rows if rows else '<tr><td colspan="5" class="empty">No jobs found yet. Run the tracker to populate this dashboard.</td></tr>'}
    </tbody>
  </table>
</div>

<footer>Auto-generated by Footwear Job Tracker • Filters: Entry-level & Internships only • No retail/store roles</footer>

<script>
  function filterTable() {{
    const search = document.getElementById('search').value.toLowerCase();
    const company = document.getElementById('company-filter').value.toLowerCase();
    const source = document.getElementById('source-filter').value.toLowerCase();
    const rows = document.querySelectorAll('#table-body tr');
    let visible = 0;
    rows.forEach(row => {{
      const text = row.textContent.toLowerCase();
      const matchSearch = !search || text.includes(search);
      const matchCompany = !company || text.includes(company);
      const matchSource = !source || text.includes(source);
      const show = matchSearch && matchCompany && matchSource;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    document.getElementById('filtered-count').textContent = visible;
  }}
</script>

</body>
</html>"""

    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Dashboard generated: {OUTPUT} ({total} jobs)")


if __name__ == "__main__":
    jobs = load_jobs()
    generate(jobs)
