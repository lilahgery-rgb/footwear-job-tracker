"""
generate_dashboard.py — Generates the HTML dashboard from all_jobs.json.

Each job row has three possible states:
- Default: visible, no action taken
- Applied: grayed out, hidden by default, tracked in browser storage
- Not a Fit: completely hidden, tracked in browser storage

Both states are saved in the browser so they persist across page refreshes.
"""

import json
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
    last_updated = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")

    rows = ""
    for job in reversed(jobs):
        source_label = "Job Board" if job["source"] == "jsearch_api" else "Career Page" if job["source"] == "workday_scrape" else "TeamWork Online"
        if job["source"] == "jsearch_api":
            source_class = "badge-api"
        elif job["source"] == "teamwork_online":
            source_class = "badge-teamwork"
        else:
            source_class = "badge-workday"
        posted = job.get("posted_on", "")[:10] or "—"
        job_id = job["id"].replace("'", "\\'").replace('"', '&quot;')
        rows += f"""
        <tr data-id="{job['id']}">
            <td><a href="{job['url']}" target="_blank" rel="noopener">{job['title']}</a></td>
            <td>{job['company']}</td>
            <td>{job.get('location') or '—'}</td>
            <td>{posted}</td>
            <td><span class="badge {source_class}">{source_label}</span></td>
            <td class="action-cell">
                <button class="apply-btn" onclick="markApplied('{job_id}', this)" title="Mark as applied">✓ Applied</button>
                <button class="dismiss-btn" onclick="markDismissed('{job_id}', this)" title="Not a good fit">✕ Not a Fit</button>
            </td>
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

  header {{ background: #1d1d1f; color: white; padding: 28px 40px; }}
  header h1 {{ font-size: 26px; font-weight: 700; letter-spacing: -0.5px; }}
  header p {{ margin-top: 6px; color: #a1a1a6; font-size: 13px; }}

  .stats {{
    display: flex; gap: 14px; padding: 20px 40px;
    background: white; border-bottom: 1px solid #e5e5e7; flex-wrap: wrap;
  }}
  .stat {{ background: #f5f5f7; border-radius: 10px; padding: 12px 20px; min-width: 120px; }}
  .stat-value {{ font-size: 24px; font-weight: 700; }}
  .stat-label {{ font-size: 11px; color: #6e6e73; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }}

  .controls {{
    padding: 16px 40px; display: flex; gap: 10px; flex-wrap: wrap;
    align-items: center; background: white; border-bottom: 1px solid #e5e5e7;
  }}
  input, select {{
    border: 1px solid #d2d2d7; border-radius: 8px; padding: 7px 12px;
    font-size: 14px; outline: none; background: #f5f5f7; color: #1d1d1f;
  }}
  input {{ width: 240px; }}
  input:focus, select:focus {{ border-color: #0071e3; background: white; }}

  .toggle-btn {{
    background: none; border: 1px solid #d2d2d7; border-radius: 8px;
    padding: 7px 12px; font-size: 13px; cursor: pointer; color: #6e6e73; white-space: nowrap;
  }}
  .toggle-btn:hover {{ border-color: #0071e3; color: #0071e3; }}
  .toggle-btn.active {{ background: #f0f7ff; border-color: #0071e3; color: #0071e3; }}

  .table-wrap {{ padding: 20px 40px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  th {{ background: #f5f5f7; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #6e6e73; padding: 11px 14px; text-align: left; border-bottom: 1px solid #e5e5e7; }}
  td {{ padding: 12px 14px; font-size: 14px; border-bottom: 1px solid #f0f0f2; vertical-align: middle; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #fafafa; }}
  td a {{ color: #0071e3; text-decoration: none; font-weight: 500; }}
  td a:hover {{ text-decoration: underline; }}

  .action-cell {{ display: flex; gap: 6px; align-items: center; }}

  .apply-btn, .dismiss-btn {{
    border: 1px solid #d2d2d7; border-radius: 6px;
    padding: 4px 9px; font-size: 11px; cursor: pointer;
    background: none; white-space: nowrap; color: #6e6e73;
    transition: all 0.15s;
  }}
  .apply-btn:hover {{ background: #e9fbe9; border-color: #1a7f37; color: #1a7f37; }}
  .dismiss-btn:hover {{ background: #fef0f0; border-color: #d93025; color: #d93025; }}

  /* Applied state — dim and hide */
  tr.applied-row {{ opacity: 0.4; display: none; }}
  tr.applied-row .apply-btn {{ background: #e9fbe9; border-color: #1a7f37; color: #1a7f37; }}
  body.show-applied tr.applied-row {{ display: table-row; }}

  /* Dismissed state — completely gone unless shown */
  tr.dismissed-row {{ display: none; }}
  body.show-dismissed tr.dismissed-row {{ display: table-row; opacity: 0.3; }}
  tr.dismissed-row .dismiss-btn {{ background: #fef0f0; border-color: #d93025; color: #d93025; }}

  .badge {{ display: inline-block; padding: 3px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
  .badge-api {{ background: #e8f4fd; color: #0071e3; }}
  .badge-workday {{ background: #e9fbe9; color: #1a7f37; }}
  .badge-teamwork {{ background: #f3eafd; color: #7c3aed; }}

  .empty {{ text-align: center; padding: 60px; color: #6e6e73; }}
  footer {{ text-align: center; padding: 20px; font-size: 12px; color: #a1a1a6; }}
</style>
</head>
<body>

<header>
  <h1>👟 Footwear & Sports Job Tracker</h1>
  <p>Entry-level corporate roles • Updated {last_updated}</p>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-value">{total}</div>
    <div class="stat-label">Total Found</div>
  </div>
  <div class="stat">
    <div class="stat-value" id="visible-count">{total}</div>
    <div class="stat-label">Showing</div>
  </div>
  <div class="stat">
    <div class="stat-value" id="applied-count">0</div>
    <div class="stat-label">Applied</div>
  </div>
  <div class="stat">
    <div class="stat-value" id="dismissed-count">0</div>
    <div class="stat-label">Dismissed</div>
  </div>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Search title, company, location…" oninput="filterTable()">
  <select id="company-filter" onchange="filterTable()">
    <option value="">All Companies</option>
    {company_options}
  </select>
  <select id="source-filter" onchange="filterTable()">
    <option value="">All Sources</option>
    <option value="Job Board">Job Board</option>
    <option value="Career Page">Career Page</option>
    <option value="TeamWork Online">TeamWork Online</option>
  </select>
  <button class="toggle-btn" id="toggle-applied-btn" onclick="toggleApplied()">👁 Show Applied</button>
  <button class="toggle-btn" id="toggle-dismissed-btn" onclick="toggleDismissed()">👁 Show Dismissed</button>
</div>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>Company</th>
        <th>Location</th>
        <th>Posted</th>
        <th>Source</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody id="table-body">
      {rows if rows else '<tr><td colspan="6" class="empty">No jobs yet — run the tracker to populate this dashboard.</td></tr>'}
    </tbody>
  </table>
</div>

<footer>Auto-updated daily • Entry-level corporate roles only • No retail or store positions</footer>

<script>
  // ── Storage helpers ──────────────────────────────────────────────────────
  function getList(key) {{
    try {{ return JSON.parse(localStorage.getItem(key) || '[]'); }}
    catch {{ return []; }}
  }}
  function saveList(key, arr) {{
    localStorage.setItem(key, JSON.stringify(arr));
  }}

  // ── Mark Applied ─────────────────────────────────────────────────────────
  function markApplied(jobId, btn) {{
    const applied = getList('appliedJobs');
    const row = btn.closest('tr');
    if (applied.includes(jobId)) {{
      saveList('appliedJobs', applied.filter(id => id !== jobId));
      row.classList.remove('applied-row');
    }} else {{
      saveList('appliedJobs', [...applied, jobId]);
      row.classList.add('applied-row');
    }}
    updateCounts();
  }}

  // ── Mark Dismissed (Not a Fit) ───────────────────────────────────────────
  function markDismissed(jobId, btn) {{
    const dismissed = getList('dismissedJobs');
    const row = btn.closest('tr');
    if (dismissed.includes(jobId)) {{
      // Un-dismiss
      saveList('dismissedJobs', dismissed.filter(id => id !== jobId));
      row.classList.remove('dismissed-row');
    }} else {{
      // Dismiss — also remove from applied if it was there
      const applied = getList('appliedJobs');
      saveList('appliedJobs', applied.filter(id => id !== jobId));
      row.classList.remove('applied-row');
      saveList('dismissedJobs', [...dismissed, jobId]);
      row.classList.add('dismissed-row');
    }}
    updateCounts();
  }}

  // ── Toggles ──────────────────────────────────────────────────────────────
  function toggleApplied() {{
    document.body.classList.toggle('show-applied');
    const btn = document.getElementById('toggle-applied-btn');
    btn.classList.toggle('active');
    btn.textContent = document.body.classList.contains('show-applied') ? '🙈 Hide Applied' : '👁 Show Applied';
    updateCounts();
  }}

  function toggleDismissed() {{
    document.body.classList.toggle('show-dismissed');
    const btn = document.getElementById('toggle-dismissed-btn');
    btn.classList.toggle('active');
    btn.textContent = document.body.classList.contains('show-dismissed') ? '🙈 Hide Dismissed' : '👁 Show Dismissed';
    updateCounts();
  }}

  // ── Filter ───────────────────────────────────────────────────────────────
  function filterTable() {{
    const search = document.getElementById('search').value.toLowerCase();
    const company = document.getElementById('company-filter').value.toLowerCase();
    const source = document.getElementById('source-filter').value.toLowerCase();
    document.querySelectorAll('#table-body tr').forEach(row => {{
      if (row.classList.contains('applied-row') || row.classList.contains('dismissed-row')) return;
      const text = row.textContent.toLowerCase();
      const show = (!search || text.includes(search)) &&
                   (!company || text.includes(company)) &&
                   (!source || text.includes(source));
      row.style.display = show ? '' : 'none';
    }});
    updateCounts();
  }}

  // ── Count visible rows ───────────────────────────────────────────────────
  function updateCounts() {{
    const rows = document.querySelectorAll('#table-body tr');
    let visible = 0;
    rows.forEach(r => {{
      if (!r.classList.contains('applied-row') &&
          !r.classList.contains('dismissed-row') &&
          r.style.display !== 'none') visible++;
    }});
    document.getElementById('visible-count').textContent = visible;
    document.getElementById('applied-count').textContent = getList('appliedJobs').length;
    document.getElementById('dismissed-count').textContent = getList('dismissedJobs').length;
  }}

  // ── Restore state on load ────────────────────────────────────────────────
  window.addEventListener('DOMContentLoaded', () => {{
    getList('appliedJobs').forEach(id => {{
      const row = document.querySelector(`tr[data-id="${{id}}"]`);
      if (row) row.classList.add('applied-row');
    }});
    getList('dismissedJobs').forEach(id => {{
      const row = document.querySelector(`tr[data-id="${{id}}"]`);
      if (row) row.classList.add('dismissed-row');
    }});
    updateCounts();
  }});
</script>
</body>
</html>"""

    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Dashboard generated: {OUTPUT} ({total} jobs)")


if __name__ == "__main__":
    jobs = load_jobs()
    generate(jobs)
