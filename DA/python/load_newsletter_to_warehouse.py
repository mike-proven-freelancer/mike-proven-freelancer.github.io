"""
Load newsletter TSV (raw/vendor/newsletter_2024q1.tsv) into fact_newsletter_daily.
Tab-separated; mixed date formats; skip footer line.

Run from project root: py python/load_newsletter_to_warehouse.py
"""

import csv
import re
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_NEWSLETTER = PROJECT_ROOT / "raw" / "vendor" / "newsletter_2024q1.tsv"
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


def main():
    WAREHOUSE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WAREHOUSE_DB)

    run_sql_file(conn, SCHEMA_SQL)
    run_sql_file(conn, SEED_SQL)
    run_sql_file(conn, SEED_CAMPAIGNS_SQL)
    conn.commit()

    rows = []
    with open(RAW_NEWSLETTER, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            date_iso = normalize_date(r.get("Date Sent"))
            if not date_iso:
                continue
            recipients = safe_int(r.get("Recipients"))
            sends = safe_int(r.get("Sends"))
            opens = safe_int(r.get("Opens"))
            clicks = safe_int(r.get("Clicks"))
            unsubscribes = safe_int(r.get("Unsubscribes"))
            bounces = safe_int(r.get("Bounces"))
            rows.append({
                "date": date_iso,
                "recipients": recipients if recipients is not None else 0,
                "sends": sends if sends is not None else 0,
                "opens": opens if opens is not None else 0,
                "clicks": clicks if clicks is not None else 0,
                "unsubscribes": unsubscribes if unsubscribes is not None else 0,
                "bounces": bounces if bounces is not None else 0,
            })

    cur = conn.cursor()
    for row in rows:
        cur.execute(
            """
            INSERT OR REPLACE INTO fact_newsletter_daily
            (date, recipients, sends, opens, clicks, unsubscribes, bounces)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["date"],
                row["recipients"],
                row["sends"],
                row["opens"],
                row["clicks"],
                row["unsubscribes"],
                row["bounces"],
            ),
        )
    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} newsletter rows into fact_newsletter_daily.")


if __name__ == "__main__":
    main()
