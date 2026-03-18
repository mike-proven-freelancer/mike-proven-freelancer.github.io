"""
Load engagement raw data (JSON) into the warehouse.
Step 1: Create DB and tables, seed dimensions.
Step 2: Read raw/api/engagement_2024q1.json, clean, dedupe, insert into fact_post_performance_daily.

Run from project root: python python/load_engagement_to_warehouse.py
Or from python/: python load_engagement_to_warehouse.py (paths assume project root is parent).
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

# Paths: assume script is in DA/python/, project root is DA/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_ENGAGEMENT = PROJECT_ROOT / "raw" / "api" / "engagement_2024q1.json"
WAREHOUSE_DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
SCHEMA_SQL = PROJECT_ROOT / "warehouse" / "schema.sql"
SEED_SQL = PROJECT_ROOT / "warehouse" / "seed_dimensions.sql"


def normalize_date(value):
    """Parse common date formats to YYYY-MM-DD. Returns None if invalid."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    s = str(value).strip()
    # ISO style
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # MM/DD/YYYY or M/D/YYYY
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        mo, day, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{yr}-{mo:02d}-{day:02d}"
    return None


def safe_int(value):
    """Coerce to int; return None for missing/invalid."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if s == "" or s.lower() == "null":
        return None
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return None


def run_sql_file(conn, path):
    with open(path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def main():
    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WAREHOUSE_DB)

    # 1. Create schema and seed dimensions
    run_sql_file(conn, SCHEMA_SQL)
    run_sql_file(conn, SEED_SQL)
    conn.commit()

    # 2. Read raw engagement JSON
    with open(RAW_ENGAGEMENT, "r", encoding="utf-8") as f:
        raw = json.load(f)
    rows = raw.get("data", {}).get("rows", [])

    # 3. Clean and normalize each row
    cleaned = []
    for r in rows:
        content_id = (r.get("post_id") or "").strip()
        date_raw = r.get("dt") or r.get("date")
        date_iso = normalize_date(date_raw)
        if not content_id or not date_iso:
            continue
        impressions = safe_int(r.get("impressions"))
        likes = safe_int(r.get("likes"))
        shares = safe_int(r.get("shares"))
        clicks = safe_int(r.get("clicks"))
        comments = safe_int(r.get("comments"))
        # Treat missing as 0 for metrics (optional: you could leave NULL)
        cleaned.append({
            "content_id": content_id,
            "date": date_iso,
            "impressions": impressions if impressions is not None else 0,
            "likes": likes if likes is not None else 0,
            "shares": shares if shares is not None else 0,
            "clicks": clicks if clicks is not None else 0,
            "comments": comments if comments is not None else 0,
        })

    # 4. Dedupe by (content_id, date) — keep first occurrence
    seen = set()
    unique = []
    for row in cleaned:
        key = (row["content_id"], row["date"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    # 5. Insert into fact_post_performance_daily (replace if re-run)
    cur = conn.cursor()
    for row in unique:
        cur.execute(
            """
            INSERT OR REPLACE INTO fact_post_performance_daily
            (content_id, date, impressions, likes, shares, clicks, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["content_id"],
                row["date"],
                row["impressions"],
                row["likes"],
                row["shares"],
                row["clicks"],
                row["comments"],
            ),
        )
    conn.commit()
    conn.close()
    print(f"Loaded {len(unique)} engagement rows into fact_post_performance_daily.")


if __name__ == "__main__":
    main()
