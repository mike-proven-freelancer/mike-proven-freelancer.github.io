# Load revenue raw data (JSON) into the warehouse.
# Events under "events"; amount sometimes string; content_id/campaign_id may be missing or "".
# Required: DBI, RSQLite, jsonlite
# Run from project root: Rscript r/load_revenue_to_warehouse.R

library(DBI)
library(RSQLite)
library(jsonlite)

`%||%` <- function(a, b) if (!is.null(a)) a else b

project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
raw_revenue <- file.path(project_root, "raw", "api", "revenue_2024q1.json")
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

optional_id <- function(x) {
  if (is.null(x)) return(NA_character_)
  s <- trimws(as.character(x))
  if (nchar(s) == 0) return(NA_character_)
  s
}

# ---- Main ----

dir.create(dirname(warehouse_db), recursive = TRUE, showWarnings = FALSE)
conn <- dbConnect(RSQLite::SQLite(), warehouse_db)

run_sql_file(conn, schema_sql)
run_sql_file(conn, seed_sql)
run_sql_file(conn, seed_campaigns_sql)

raw <- read_json(raw_revenue)
events <- raw$events

event_id   <- vapply(events, function(e) trimws(e$id %||% ""), character(1))
date_iso   <- vapply(events, function(e) normalize_date(e$date), character(1))
amount     <- vapply(events, function(e) safe_float(e$amount), numeric(1))
etype      <- vapply(events, function(e) trimws(e$type %||% ""), character(1))
content_id <- vapply(events, function(e) optional_id(e$content_id), character(1))
campaign_id <- vapply(events, function(e) optional_id(e$campaign_id), character(1))

# REV-011 has no campaign_id key: jsonlite gives NULL, optional_id -> NA_character_
# Replace "" with NA for DB NULL
content_id[content_id == ""] <- NA_character_
campaign_id[campaign_id == ""] <- NA_character_

keep <- nchar(event_id) > 0 & !is.na(date_iso) & !is.na(amount) & nchar(etype) > 0
event_id   <- event_id[keep]
content_id <- content_id[keep]
campaign_id <- campaign_id[keep]
date_iso   <- date_iso[keep]
amount     <- amount[keep]
etype      <- etype[keep]

for (i in seq_along(event_id)) {
  dbExecute(conn,
    "INSERT OR REPLACE INTO fact_revenue_events (event_id, content_id, campaign_id, date, amount, type) VALUES (?, ?, ?, ?, ?, ?)",
    params = list(event_id[i], content_id[i], campaign_id[i], date_iso[i], amount[i], etype[i]))
}

dbDisconnect(conn)
message("Loaded ", sum(keep), " revenue events into fact_revenue_events.")
