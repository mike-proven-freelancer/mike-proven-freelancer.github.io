"""
Phase 3: Revenue sources — what's working / selling best (descriptive).

Writes reports/phase-3/revenue_by_type.csv, revenue_top_content.csv,
revenue_by_campaign_attribution.csv

Run: py python/phase3_revenue_sources.py
"""

import csv
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
OUT = PROJECT_ROOT / "reports" / "phase-3"


def write_rows(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)


def main():
    conn = sqlite3.connect(DB)

    q1 = """
    SELECT type, COUNT(*) AS events, ROUND(SUM(amount), 2) AS total_revenue
    FROM fact_revenue_events GROUP BY type ORDER BY total_revenue DESC;
    """
    write_rows(
        OUT / "revenue_by_type.csv",
        ["revenue_type", "event_count", "total_revenue"],
        conn.execute(q1).fetchall(),
    )

    q2 = """
    SELECT COALESCE(c.content_id, '(unattributed)') AS content_id,
           COALESCE(c.title, '') AS title,
           COUNT(*) AS events,
           ROUND(SUM(r.amount), 2) AS total_revenue
    FROM fact_revenue_events r
    LEFT JOIN dim_content c ON c.content_id = r.content_id
    WHERE r.content_id IS NOT NULL AND TRIM(r.content_id) != ''
    GROUP BY c.content_id, c.title
    ORDER BY total_revenue DESC;
    """
    write_rows(
        OUT / "revenue_top_content.csv",
        ["content_id", "title", "event_count", "total_revenue"],
        conn.execute(q2).fetchall(),
    )

    q3 = """
    SELECT COALESCE(r.campaign_id, '(direct/none)') AS campaign_id,
           COALESCE(cam.name, '') AS campaign_name,
           r.type,
           COUNT(*) AS events,
           ROUND(SUM(r.amount), 2) AS total_revenue
    FROM fact_revenue_events r
    LEFT JOIN dim_campaign cam ON cam.campaign_id = r.campaign_id
    GROUP BY r.campaign_id, cam.name, r.type
    ORDER BY total_revenue DESC;
    """
    write_rows(
        OUT / "revenue_by_campaign_attribution.csv",
        ["campaign_id", "campaign_name", "revenue_type", "event_count", "total_revenue"],
        conn.execute(q3).fetchall(),
    )

    conn.close()
    print(f"Wrote revenue summaries to {OUT}")


if __name__ == "__main__":
    main()
