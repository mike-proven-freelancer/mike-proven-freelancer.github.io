"""
Load campaign spend raw CSVs into the warehouse.
Handles schema drift: Q1 has (Campaign ID, Date, Spend, Impressions, Clicks),
Q2 has (campaign_id, date, spend_usd, impr, click_count).
Skips footer lines; normalizes dates; empty Spend -> 0.

Run from project root: py python/load_campaign_spend_to_warehouse.py
"""

import csv
import sqlite3
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_Q1 = PROJECT_ROOT / "raw" / "vendor" / "campaign_spend_2024q1.csv"
RAW_Q2 = PROJECT_ROOT / "raw" / "vendor" / "campaign_spend_2024q2.csv"
WAREHOUSE_DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
SCHEMA_SQL = PROJECT_ROOT / "warehouse" / "schema.sql"
SEED_SQL = PROJECT_ROOT / "warehouse" / "seed_dimensions.sql"
SEED_CAMPAIGNS_SQL = PROJECT_ROOT / "warehouse" / "seed_campaigns.sql"


def normalize_date(value):
    """Parse common date formats to YYYY-MM-DD. Returns None if invalid."""
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


def safe_int(value):
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


def read_q1(path):
    """Q1: Campaign ID, Date, Spend, Impressions, Clicks. Skip footer."""
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = (r.get("Campaign ID") or "").strip()
            if not cid.startswith("CAMP-"):
                continue
            date_iso = normalize_date(r.get("Date"))
            if not date_iso:
                continue
            spend = safe_float(r.get("Spend"))
            impressions = safe_int(r.get("Impressions"))
            clicks = safe_int(r.get("Clicks"))
            rows.append({
                "campaign_id": cid,
                "date": date_iso,
                "spend": spend if spend is not None else 0.0,
                "impressions": impressions if impressions is not None else 0,
                "clicks": clicks if clicks is not None else 0,
            })
    return rows


def read_q2(path):
    """Q2: campaign_id, date, spend_usd, impr, click_count."""
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = (r.get("campaign_id") or "").strip()
            if not cid.startswith("CAMP-"):
                continue
            date_iso = normalize_date(r.get("date"))
            if not date_iso:
                continue
            spend = safe_float(r.get("spend_usd"))
            impressions = safe_int(r.get("impr"))
            clicks = safe_int(r.get("click_count"))
            rows.append({
                "campaign_id": cid,
                "date": date_iso,
                "spend": spend if spend is not None else 0.0,
                "impressions": impressions if impressions is not None else 0,
                "clicks": clicks if clicks is not None else 0,
            })
    return rows


def main():
    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WAREHOUSE_DB)

    run_sql_file(conn, SCHEMA_SQL)
    run_sql_file(conn, SEED_SQL)
    run_sql_file(conn, SEED_CAMPAIGNS_SQL)
    conn.commit()

    all_rows = []
    if RAW_Q1.exists():
        all_rows.extend(read_q1(RAW_Q1))
    if RAW_Q2.exists():
        all_rows.extend(read_q2(RAW_Q2))

    # Dedupe by (campaign_id, date) — keep last (Q2 overwrites Q1 if same key)
    seen = {}
    for row in all_rows:
        key = (row["campaign_id"], row["date"])
        seen[key] = row
    unique = list(seen.values())

    cur = conn.cursor()
    for row in unique:
        cur.execute(
            """
            INSERT OR REPLACE INTO fact_campaign_spend_daily
            (campaign_id, date, spend, impressions, clicks)
            VALUES (?, ?, ?, ?, ?)
            """,
            (row["campaign_id"], row["date"], row["spend"], row["impressions"], row["clicks"]),
        )
    conn.commit()
    conn.close()
    print(f"Loaded {len(unique)} campaign spend rows into fact_campaign_spend_daily.")


if __name__ == "__main__":
    main()
