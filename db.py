"""
db.py — SQLite deduplication store.
Tracks which job IDs have already been seen so we never notify twice.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs_seen.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the jobs table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_jobs (
                id          TEXT PRIMARY KEY,
                title       TEXT,
                company     TEXT,
                location    TEXT,
                source      TEXT,
                seen_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def is_new_job(job_id: str) -> bool:
    """Return True if this job_id has never been seen before."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return row is None


def mark_job_seen(job: dict):
    """Insert a job into the seen table so it won't be notified again."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO seen_jobs (id, title, company, location, source)
            VALUES (:id, :title, :company, :location, :source)
            """,
            job,
        )
        conn.commit()
