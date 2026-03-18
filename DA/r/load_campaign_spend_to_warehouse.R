# Load campaign spend raw CSVs into the warehouse.
# Handles schema drift: Q1 (Campaign ID, Date, Spend, ...) vs Q2 (campaign_id, date, spend_usd, impr, click_count).
# Required: DBI, RSQLite (jsonlite not needed for this script)
# Run from project root: Rscript r/load_campaign_spend_to_warehouse.R

library(DBI)
library(RSQLite)

# Paths (assume working directory is project root)
project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
raw_q1 <- file.path(project_root, "raw", "vendor", "campaign_spend_2024q1.csv")
raw_q2 <- file.path(project_root, "raw", "vendor", "campaign_spend_2024q2.csv")
warehouse_db <- file.path(project_root, "warehouse", "brightwave.sqlite")
schema_sql <- file.path(project_root, "warehouse", "schema.sql")
seed_sql <- file.path(project_root, "warehouse", "seed_dimensions.sql")
seed_campaigns_sql <- file.path(project_root, "warehouse", "seed_campaigns.sql")

run_sql_file <- function(conn, path) {
  sql <- paste(readLines(path, encoding = "UTF-8"), collapse = "\n")
  statements <- strsplit(sql, ";\\s*\n")[[1]]
  for (s in statements) {
    s <- trimws(s)
    if (nchar(s) > 0) dbExecute(conn, s)
  }
}

normalize_date <- function(value) {
  if (is.null(value) || (is.character(value) && trimws(value) == ""))
    return(NA_character_)
  s <- trimws(as.character(value))
  if (grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}", s)) return(substr(s, 1, 10))
  d <- as.Date(s, format = "%m/%d/%Y")
  if (!is.na(d)) return(format(d, "%Y-%m-%d"))
  NA_character_
}

safe_float <- function(x) {
  if (is.null(x)) return(NA_real_)
  if (is.character(x) && trimws(x) %in% c("", "null", "NULL")) return(NA_real_)
  as.numeric(x)
}

safe_int <- function(x) {
  if (is.null(x)) return(NA_integer_)
  if (is.character(x) && trimws(x) %in% c("", "null", "NULL")) return(NA_integer_)
  as.integer(round(as.numeric(x)))
}

# Read Q1 CSV: Campaign ID, Date, Spend, Impressions, Clicks (skip footer)
read_q1 <- function(path) {
  if (!file.exists(path)) return(data.frame())
  d <- read.csv(path, stringsAsFactors = FALSE)
  d$campaign_id <- trimws(d$Campaign.ID)
  d <- d[grepl("^CAMP-", d$campaign_id), , drop = FALSE]
  d$date <- vapply(d$Date, function(x) normalize_date(x), character(1))
  d <- d[!is.na(d$date), , drop = FALSE]
  spend <- vapply(d$Spend, safe_float, numeric(1))
  impressions <- vapply(d$Impressions, safe_int, integer(1))
  clicks <- vapply(d$Clicks, safe_int, integer(1))
  data.frame(
    campaign_id = d$campaign_id,
    date = d$date,
    spend = ifelse(is.na(spend), 0, spend),
    impressions = ifelse(is.na(impressions), 0L, impressions),
    clicks = ifelse(is.na(clicks), 0L, clicks),
    stringsAsFactors = FALSE
  )
}

# Read Q2 CSV: campaign_id, date, spend_usd, impr, click_count
read_q2 <- function(path) {
  if (!file.exists(path)) return(data.frame())
  d <- read.csv(path, stringsAsFactors = FALSE)
  d$campaign_id <- trimws(d$campaign_id)
  d <- d[grepl("^CAMP-", d$campaign_id), , drop = FALSE]
  d$date_norm <- vapply(d$date, function(x) normalize_date(x), character(1))
  d <- d[!is.na(d$date_norm), , drop = FALSE]
  spend <- vapply(d$spend_usd, safe_float, numeric(1))
  impressions <- vapply(d$impr, safe_int, integer(1))
  clicks <- vapply(d$click_count, safe_int, integer(1))
  data.frame(
    campaign_id = d$campaign_id,
    date = d$date_norm,
    spend = ifelse(is.na(spend), 0, spend),
    impressions = ifelse(is.na(impressions), 0L, impressions),
    clicks = ifelse(is.na(clicks), 0L, clicks),
    stringsAsFactors = FALSE
  )
}

# ---- Main ----

dir.create(dirname(warehouse_db), recursive = TRUE, showWarnings = FALSE)
conn <- dbConnect(RSQLite::SQLite(), warehouse_db)

run_sql_file(conn, schema_sql)
run_sql_file(conn, seed_sql)
run_sql_file(conn, seed_campaigns_sql)

df1 <- read_q1(raw_q1)
df2 <- read_q2(raw_q2)
all_rows <- rbind(df1, df2)

# Dedupe by (campaign_id, date) — keep last
all_rows <- all_rows[!duplicated(all_rows[, c("campaign_id", "date")], fromLast = TRUE), ]

for (i in seq_len(nrow(all_rows))) {
  r <- all_rows[i, ]
  dbExecute(conn,
    "INSERT OR REPLACE INTO fact_campaign_spend_daily (campaign_id, date, spend, impressions, clicks) VALUES (?, ?, ?, ?, ?)",
    params = list(r$campaign_id, r$date, r$spend, r$impressions, r$clicks))
}

dbDisconnect(conn)
message("Loaded ", nrow(all_rows), " campaign spend rows into fact_campaign_spend_daily.")
