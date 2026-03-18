# Load engagement raw data (JSON) into the warehouse.
# Same steps as Python: init schema + seed dims, then read JSON, clean, dedupe, insert.
#
# Required: install.packages(c("DBI", "RSQLite", "jsonlite"))
# Run from project root: source("r/load_engagement_to_warehouse.R")
# Or in RStudio: setwd("path/to/DA") then source("r/load_engagement_to_warehouse.R")

library(DBI)
library(RSQLite)
library(jsonlite)

# Null coalesce (base R; no rlang needed)
`%||%` <- function(a, b) if (!is.null(a)) a else b

# Paths (assume working directory is project root, e.g. DA/)
project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
raw_engagement <- file.path(project_root, "raw", "api", "engagement_2024q1.json")
warehouse_db  <- file.path(project_root, "warehouse", "brightwave.sqlite")
schema_sql    <- file.path(project_root, "warehouse", "schema.sql")
seed_sql      <- file.path(project_root, "warehouse", "seed_dimensions.sql")

# Run a SQL file (multiple statements separated by ";")
run_sql_file <- function(conn, path) {
  sql <- paste(readLines(path, encoding = "UTF-8"), collapse = "\n")
  statements <- strsplit(sql, ";\\s*\n")[[1]]
  for (s in statements) {
    s <- trimws(s)
    if (nchar(s) > 0) {
      dbExecute(conn, s)
    }
  }
}

# Normalize date string to YYYY-MM-DD (character)
normalize_date <- function(value) {
  if (is.null(value) || (is.character(value) && trimws(value) == ""))
    return(NA_character_)
  s <- trimws(as.character(value))
  # ISO
  if (grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}", s))
    return(substr(s, 1, 10))
  # MM/DD/YYYY or M/D/YYYY
  d <- as.Date(s, format = "%m/%d/%Y")
  if (!is.na(d)) return(format(d, "%Y-%m-%d"))
  NA_character_
}

# Coerce to integer; NA for missing/invalid
safe_int <- function(x) {
  if (is.null(x)) return(NA_integer_)
  if (is.character(x) && trimws(x) %in% c("", "null", "NULL")) return(NA_integer_)
  as.integer(round(as.numeric(x)))
}

# ---- Main ----

dir.create(dirname(warehouse_db), recursive = TRUE, showWarnings = FALSE)
conn <- dbConnect(RSQLite::SQLite(), warehouse_db)

# 1. Schema and seed dimensions
run_sql_file(conn, schema_sql)
run_sql_file(conn, seed_sql)

# 2. Read raw engagement JSON
raw <- read_json(raw_engagement)
rows <- raw$data$rows

# 3. Clean and normalize
content_id <- vapply(rows, function(r) trimws(r$post_id %||% ""), character(1))
date_raw   <- lapply(rows, function(r) r$dt %||% r$date)
date_iso   <- vapply(date_raw, normalize_date, character(1))

# Drop rows with missing content_id or date
keep <- !is.na(date_iso) & nchar(content_id) > 0
rows <- rows[keep]
content_id <- content_id[keep]
date_iso   <- date_iso[keep]

impressions <- vapply(rows, function(r) safe_int(r$impressions), integer(1))
likes       <- vapply(rows, function(r) safe_int(r$likes), integer(1))
shares      <- vapply(rows, function(r) safe_int(r$shares), integer(1))
clicks      <- vapply(rows, function(r) safe_int(r$clicks), integer(1))
comments    <- vapply(rows, function(r) safe_int(r$comments), integer(1))

# Replace NA with 0 for metrics
impressions[is.na(impressions)] <- 0L
likes[is.na(likes)]             <- 0L
shares[is.na(shares)]           <- 0L
clicks[is.na(clicks)]           <- 0L
comments[is.na(comments)]        <- 0L

# 4. Dedupe by (content_id, date)
df <- data.frame(
  content_id = content_id,
  date = date_iso,
  impressions = impressions,
  likes = likes,
  shares = shares,
  clicks = clicks,
  comments = comments,
  stringsAsFactors = FALSE
)
df <- df[!duplicated(df[, c("content_id", "date")]), ]

# 5. Insert (replace if exists: delete then insert, or use INSERT OR REPLACE)
for (i in seq_len(nrow(df))) {
  r <- df[i, ]
  dbExecute(conn, "INSERT OR REPLACE INTO fact_post_performance_daily (content_id, date, impressions, likes, shares, clicks, comments) VALUES (?, ?, ?, ?, ?, ?, ?)",
    params = list(r$content_id, r$date, r$impressions, r$likes, r$shares, r$clicks, r$comments))
}

dbDisconnect(conn)
message("Loaded ", nrow(df), " engagement rows into fact_post_performance_daily.")
# Optional: use message() instead of print for consistency
