# Phase 3 Task 2: Budget allocation backtest (same logic as Python).
# Run: Rscript r/phase3_task2_budget_allocation.R

library(DBI)
library(RSQLite)

project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
db <- file.path(project_root, "warehouse", "brightwave.sqlite")
out_dir <- file.path(project_root, "reports", "phase-3")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
EPS <- 1e-6

conn <- dbConnect(RSQLite::SQLite(), db)
df <- dbGetQuery(conn, "SELECT campaign_id, date, spend, clicks FROM fact_campaign_spend_daily")
dbDisconnect(conn)

df$date <- as.Date(df$date)
df$yw <- paste(strftime(df$date, "%G"), strftime(df$date, "%V"), sep = "-W")

agg <- aggregate(
  cbind(spend, clicks) ~ campaign_id + yw,
  data = df,
  FUN = sum
)

campaigns <- sort(unique(agg$campaign_id))
weeks <- sort(unique(agg$yw))

get_sc <- function(yw, cid) {
  r <- agg[agg$yw == yw & agg$campaign_id == cid, ]
  if (nrow(r) == 0) return(c(0, 0))
  c(as.numeric(r$spend), as.integer(r$clicks))
}

detail <- list()
for (i in seq_along(weeks)[-1]) {
  prev <- weeks[i - 1]
  cur <- weeks[i]
  W <- sum(sapply(campaigns, function(c) get_sc(cur, c)[1]))
  if (W < EPS) next
  e <- cl_prev <- numeric(length(campaigns))
  names(e) <- names(cl_prev) <- campaigns
  for (j in seq_along(campaigns)) {
    c <- campaigns[j]
    sp <- max(get_sc(prev, c)[1], EPS)
    e[c] <- get_sc(prev, c)[2] / sp
    cl_prev[c] <- get_sc(prev, c)[2]
  }
  tot_cl <- sum(cl_prev)
  if (tot_cl < EPS) tot_cl <- EPS

  sim_equal <- sum((W / length(campaigns)) * e[campaigns])
  sim_prop <- sum((W * cl_prev[campaigns] / tot_cl) * e[campaigns])
  esum <- sum(e[campaigns])
  if (esum < EPS) esum <- EPS
  sim_eff <- sum((W * e[campaigns] / esum) * e[campaigns])

  act <- sum(sapply(campaigns, function(c) get_sc(cur, c)[2]))

  yw_parts <- strsplit(cur, "-W")[[1]]
  y <- as.integer(yw_parts[1])
  w <- as.integer(yw_parts[2])
  jan4 <- as.Date(paste0(y, "-01-04"))
  mon <- jan4 - as.integer(strftime(jan4, "%u")) + 1 + 7 * (w - 1)

  detail[[length(detail) + 1]] <- data.frame(
    week_year = y,
    week_iso = w,
    week_start = format(mon, "%Y-%m-%d"),
    budget_W = round(W, 2),
    actual_clicks_week = act,
    sim_equal_split = round(sim_equal, 2),
    sim_prop_prior_clicks = round(sim_prop, 2),
    sim_efficiency_weighted = round(sim_eff, 2),
    stringsAsFactors = FALSE
  )
}

dmat <- do.call(rbind, detail)
write.csv(dmat, file.path(out_dir, "task2_budget_allocation_by_week.csv"), row.names = FALSE)

s_eq <- sum(dmat$sim_equal_split)
s_pr <- sum(dmat$sim_prop_prior_clicks)
s_ef <- sum(dmat$sim_efficiency_weighted)
s_ac <- sum(dmat$actual_clicks_week)
best <- which.max(c(s_eq, s_pr, s_ef))
best_name <- c("equal_split", "prop_prior_clicks", "efficiency_weighted")[best]
best_val <- c(s_eq, s_pr, s_ef)[best]

sm <- data.frame(
  rule = c(
    "equal_split", "prop_prior_clicks", "efficiency_weighted",
    "actual_total_clicks", "best_rule_simulated"
  ),
  total_simulated_or_actual_clicks = c(
    round(s_eq, 2), round(s_pr, 2), round(s_ef, 2), round(s_ac, 2),
    best_name
  ),
  notes = c(
    "sum over eval weeks", "sum over eval weeks", "sum over eval weeks",
    "observed clicks those weeks (not simulated)",
    paste0("total=", round(best_val, 2))
  ),
  stringsAsFactors = FALSE
)
write.csv(sm, file.path(out_dir, "task2_budget_allocation_summary.csv"), row.names = FALSE)

message("Wrote task2_budget_allocation_*.csv; best simulated rule: ", best_name, " = ", round(best_val, 2))
