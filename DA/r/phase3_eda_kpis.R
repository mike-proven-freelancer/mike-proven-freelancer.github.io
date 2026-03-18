# Phase 3: EDA + KPI extracts (R).
#
# Reads from warehouse/brightwave.sqlite and writes CSVs to:
#   reports/phase-3/
#
# Run from project root:
#   Rscript r/phase3_eda_kpis.R

library(DBI)
library(RSQLite)

project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)

warehouse_db <- file.path(project_root, "warehouse", "brightwave.sqlite")
out_dir <- file.path(project_root, "reports", "phase-3")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

conn <- dbConnect(RSQLite::SQLite(), warehouse_db)

write_query_csv <- function(sql, out_name) {
  df <- dbGetQuery(conn, sql)
  out_path <- file.path(out_dir, out_name)
  write.csv(df, out_path, row.names = FALSE, fileEncoding = "UTF-8")
  nrow(df)
}

counts <- c(
  write_query_csv(
    "
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
    ",
    "kpi_content_performance.csv"
  ),
  write_query_csv(
    "
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
    ",
    "kpi_campaign_spend.csv"
  ),
  write_query_csv(
    "
    SELECT
      type,
      COUNT(*) AS event_count,
      ROUND(SUM(amount), 2) AS total_amount
    FROM fact_revenue_events
    GROUP BY type
    ORDER BY total_amount DESC;
    ",
    "kpi_revenue_by_type.csv"
  ),
  write_query_csv(
    "
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
    ",
    "kpi_revenue_attribution.csv"
  ),
  write_query_csv(
    "
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
    ",
    "kpi_newsletter_daily.csv"
  )
)

dbDisconnect(conn)
message("Wrote 5 CSVs to ", out_dir, " (", sum(counts), " total rows across extracts).")

