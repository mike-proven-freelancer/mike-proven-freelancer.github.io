"""
Phase 3: EDA + KPI extracts (no pandas required).

Reads from warehouse/brightwave.sqlite and writes a handful of small CSVs to:
  reports/phase-3/

Run from project root:
  py python/phase3_eda_kpis.py
"""

import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WAREHOUSE_DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
OUT_DIR = PROJECT_ROOT / "reports" / "phase-3"


def write_query_csv(conn: sqlite3.Connection, out_path: Path, query: str):
    cur = conn.execute(query)
    headers = [d[0] for d in cur.description]
    rows = cur.fetchall()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return len(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WAREHOUSE_DB)

    outputs = [
        (
            OUT_DIR / "kpi_content_performance.csv",
            """
            SELECT
              c.content_id,
              c.title,
              c.theme,
              MIN(p.date) AS first_date,
              MAX(p.date) AS last_date,
              SUM(p.impressions) AS impressions,
              SUM(p.clicks) AS clicks,
              SUM(p.likes) AS likes,
              SUM(p.shares) AS shares,
              SUM(p.comments) AS comments,
              ROUND(CASE WHEN SUM(p.impressions) > 0 THEN 1.0 * SUM(p.clicks) / SUM(p.impressions) END, 6) AS ctr
            FROM fact_post_performance_daily p
            JOIN dim_content c ON c.content_id = p.content_id
            GROUP BY c.content_id, c.title, c.theme
            ORDER BY clicks DESC;
            """,
        ),
        (
            OUT_DIR / "kpi_campaign_spend.csv",
            """
            SELECT
              s.campaign_id,
              c.name AS campaign_name,
              MIN(s.date) AS first_date,
              MAX(s.date) AS last_date,
              ROUND(SUM(s.spend), 2) AS spend,
              SUM(s.impressions) AS impressions,
              SUM(s.clicks) AS clicks,
              ROUND(CASE WHEN SUM(s.impressions) > 0 THEN 1.0 * SUM(s.clicks) / SUM(s.impressions) END, 6) AS ctr
            FROM fact_campaign_spend_daily s
            JOIN dim_campaign c ON c.campaign_id = s.campaign_id
            GROUP BY s.campaign_id, c.name
            ORDER BY spend DESC;
            """,
        ),
        (
            OUT_DIR / "kpi_revenue_by_type.csv",
            """
            SELECT
              type,
              COUNT(*) AS event_count,
              ROUND(SUM(amount), 2) AS total_amount
            FROM fact_revenue_events
            GROUP BY type
            ORDER BY total_amount DESC;
            """,
        ),
        (
            OUT_DIR / "kpi_revenue_attribution.csv",
            """
            SELECT
              COALESCE(r.content_id, '(none)') AS content_id,
              COALESCE(c.title, '(none)') AS content_title,
              COALESCE(r.campaign_id, '(none)') AS campaign_id,
              COALESCE(cam.name, '(none)') AS campaign_name,
              r.type,
              COUNT(*) AS event_count,
              ROUND(SUM(r.amount), 2) AS total_amount
            FROM fact_revenue_events r
            LEFT JOIN dim_content c ON c.content_id = r.content_id
            LEFT JOIN dim_campaign cam ON cam.campaign_id = r.campaign_id
            GROUP BY
              COALESCE(r.content_id, '(none)'),
              COALESCE(c.title, '(none)'),
              COALESCE(r.campaign_id, '(none)'),
              COALESCE(cam.name, '(none)'),
              r.type
            ORDER BY total_amount DESC;
            """,
        ),
        (
            OUT_DIR / "kpi_newsletter_daily.csv",
            """
            SELECT
              date,
              recipients,
              sends,
              opens,
              clicks,
              unsubscribes,
              bounces,
              ROUND(CASE WHEN sends > 0 THEN 1.0 * opens / sends END, 6) AS open_rate,
              ROUND(CASE WHEN sends > 0 THEN 1.0 * clicks / sends END, 6) AS ctr
            FROM fact_newsletter_daily
            ORDER BY date;
            """,
        ),
    ]

    total = 0
    for out_path, query in outputs:
        total += write_query_csv(conn, out_path, query)

    conn.close()
    print(f"Wrote {len(outputs)} CSVs to {OUT_DIR} ({total} total rows across extracts).")


if __name__ == "__main__":
    main()

