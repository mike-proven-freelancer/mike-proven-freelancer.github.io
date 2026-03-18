# Load newsletter TSV into fact_newsletter_daily.
# Tab-separated; mixed date formats; skip footer.
# Run from project root: Rscript r/load_newsletter_to_warehouse.R

library(DBI)
library(RSQLite)

project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
raw_newsletter <- file.path(project_root, "raw", "vendor", "newsletter_2024q1.tsv")
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

safe_int <- function(x) {
  if (is.null(x)) return(NA_integer_)
  if (is.character(x) && trimws(x) %in% c("", "null", "NULL")) return(NA_integer_)
  as.integer(round(as.numeric(x)))
}

# ---- Main ----

dir.create(dirname(warehouse_db), recursive = TRUE, showWarnings = FALSE)
conn <- dbConnect(RSQLite::SQLite(), warehouse_db)

run_sql_file(conn, schema_sql)
run_sql_file(conn, seed_sql)
run_sql_file(conn, seed_campaigns_sql)

d <- read.delim(raw_newsletter, stringsAsFactors = FALSE)
d$date <- vapply(d$Date.Sent, normalize_date, character(1))
d <- d[!is.na(d$date), , drop = FALSE]

# Coerce to integer; NA -> 0
d$recipients   <- as.integer(round(as.numeric(d$Recipients)))
d$sends        <- as.integer(round(as.numeric(d$Sends)))
d$opens        <- as.integer(round(as.numeric(d$Opens)))
d$clicks       <- as.integer(round(as.numeric(d$Clicks)))
d$unsubscribes <- as.integer(round(as.numeric(d$Unsubscribes)))
d$bounces      <- as.integer(round(as.numeric(d$Bounces)))
d$recipients[is.na(d$recipients)]   <- 0L
d$sends[is.na(d$sends)]            <- 0L
d$opens[is.na(d$opens)]           <- 0L
d$clicks[is.na(d$clicks)]         <- 0L
d$unsubscribes[is.na(d$unsubscribes)] <- 0L
d$bounces[is.na(d$bounces)]       <- 0L

for (i in seq_len(nrow(d))) {
  dbExecute(conn,
    "INSERT OR REPLACE INTO fact_newsletter_daily (date, recipients, sends, opens, clicks, unsubscribes, bounces) VALUES (?, ?, ?, ?, ?, ?, ?)",
    params = list(d$date[i], d$recipients[i], d$sends[i], d$opens[i], d$clicks[i], d$unsubscribes[i], d$bounces[i]))
}

dbDisconnect(conn)
message("Loaded ", nrow(d), " newsletter rows into fact_newsletter_daily.")