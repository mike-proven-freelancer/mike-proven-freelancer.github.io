# Phase 3: Revenue sources summaries (same as Python).
# Run: Rscript r/phase3_revenue_sources.R

library(DBI)
library(RSQLite)

project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
db <- file.path(project_root, "warehouse", "brightwave.sqlite")
out_dir <- file.path(project_root, "reports", "phase-3")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

conn <- dbConnect(RSQLite::SQLite(), db)

write.csv(
  dbGetQuery(conn, "
    SELECT type AS revenue_type, COUNT(*) AS event_count, ROUND(SUM(amount), 2) AS total_revenue
    FROM fact_revenue_events GROUP BY type ORDER BY total_revenue DESC;
  "),
  file.path(out_dir, "revenue_by_type.csv"),
  row.names = FALSE
)

write.csv(
  dbGetQuery(conn, "
    SELECT COALESCE(c.content_id, '(unattributed)') AS content_id,
           COALESCE(c.title, '') AS title,
           COUNT(*) AS event_count,
           ROUND(SUM(r.amount), 2) AS total_revenue
    FROM fact_revenue_events r
    LEFT JOIN dim_content c ON c.content_id = r.content_id
    WHERE r.content_id IS NOT NULL AND TRIM(r.content_id) != ''
    GROUP BY c.content_id, c.title
    ORDER BY total_revenue DESC;
  "),
  file.path(out_dir, "revenue_top_content.csv"),
  row.names = FALSE
)

write.csv(
  dbGetQuery(conn, "
    SELECT COALESCE(r.campaign_id, '(direct/none)') AS campaign_id,
           COALESCE(cam.name, '') AS campaign_name,
           r.type AS revenue_type,
           COUNT(*) AS event_count,
           ROUND(SUM(r.amount), 2) AS total_revenue
    FROM fact_revenue_events r
    LEFT JOIN dim_campaign cam ON cam.campaign_id = r.campaign_id
    GROUP BY r.campaign_id, cam.name, r.type
    ORDER BY total_revenue DESC;
  "),
  file.path(out_dir, "revenue_by_campaign_attribution.csv"),
  row.names = FALSE
)

dbDisconnect(conn)
message("Wrote revenue summaries to ", out_dir)
