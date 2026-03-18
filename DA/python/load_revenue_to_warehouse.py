"""
Load revenue raw data (JSON) into the warehouse.
Events under "events"; amount sometimes string; dates mixed; content_id/campaign_id may be null, missing, or "".

Run from project root: py python/load_revenue_to_warehouse.py
"""

import json
import sqlite3
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_REVENUE = PROJECT_ROOT / "raw" / "api" / "revenue_2024q1.json"
WAREHOUSE_DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
SCHEMA_SQL = PROJECT_ROOT / "warehouse" / "schema.sql"
SEED_SQL = PROJECT_ROOT / "warehouse" / "seed_dimensions.sql"
SEED_CAMPAIGNS_SQL = PROJECT_ROOT / "warehouse" / "seed_campaigns.sql"


def normalize_date(value):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    s = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        mo, day, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{yr}-{mo:02d}-{day:02d}"
    return None


def safe_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "" or s.lower() == "null":
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def optional_id(value):
    """Return stripped string or None for FK columns (content_id, campaign_id)."""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def run_sql_file(conn, path):
    with open(path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def main():
    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WAREHOUSE_DB)

    run_sql_file(conn, SCHEMA_SQL)
    run_sql_file(conn, SEED_SQL)
    run_sql_file(conn, SEED_CAMPAIGNS_SQL)
    conn.commit()

    with open(RAW_REVENUE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    events = raw.get("events", [])

    cleaned = []
    for e in events:
        event_id = (e.get("id") or "").strip()
        if not event_id:
            continue
        date_iso = normalize_date(e.get("date"))
        if not date_iso:
            continue
        amount = safe_float(e.get("amount"))
        if amount is None:
            continue
        etype = (e.get("type") or "").strip()
        if not etype:
            continue
        content_id = optional_id(e.get("content_id"))
        campaign_id = optional_id(e.get("campaign_id"))
        cleaned.append({
            "event_id": event_id,
            "content_id": content_id,
            "campaign_id": campaign_id,
            "date": date_iso,
            "amount": amount,
            "type": etype,
        })

    cur = conn.cursor()
    for row in cleaned:
        cur.execute(
            """
            INSERT OR REPLACE INTO fact_revenue_events
            (event_id, content_id, campaign_id, date, amount, type)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["event_id"],
                row["content_id"],
                row["campaign_id"],
                row["date"],
                row["amount"],
                row["type"],
            ),
        )
    conn.commit()
    conn.close()
    print(f"Loaded {len(cleaned)} revenue events into fact_revenue_events.")


if __name__ == "__main__":
    main()
