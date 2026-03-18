# Phase 3 Task 1: Next-7-day channel clicks — baseline backtest (same logic as Python).
# Run from project root: Rscript r/phase3_task1_clicks_forecast.R

library(DBI)
library(RSQLite)

project_root <- getwd()
if (basename(project_root) == "r") project_root <- dirname(project_root)
db <- file.path(project_root, "warehouse", "brightwave.sqlite")
out_dir <- file.path(project_root, "reports", "phase-3")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

conn <- dbConnect(RSQLite::SQLite(), db)
df <- dbGetQuery(conn, "
  SELECT date, SUM(clicks) AS clicks
  FROM fact_post_performance_daily
  GROUP BY date ORDER BY date
")
dbDisconnect(conn)

if (nrow(df) == 0) {
  message("No engagement data.")
  quit(save = "no")
}

df$date <- as.Date(df$date)
dmin <- min(df$date)
dmax <- max(df$date)
all_dates <- seq(dmin, dmax, by = "day")
by_date <- setNames(df$clicks, as.character(df$date))
clicks_vec <- sapply(as.character(all_dates), function(d) {
  v <- by_date[[d]]
  if (is.null(v)) 0L else as.integer(v)
})
series <- data.frame(date = all_dates, channel_clicks = as.integer(clicks_vec))
write.csv(series, file.path(out_dir, "task1_clicks_daily_series.csv"), row.names = FALSE)

n <- nrow(series)
if (n < 14) {
  first7 <- sum(series$channel_clicks[1:7])
  start_next <- series$date[7] + 1
  actual_next <- 0L
  for (i in 0:6) {
    d <- as.character(start_next + i)
    actual_next <- actual_next + ifelse(d %in% names(by_date), by_date[[d]], 0L)
  }
  pred_a <- first7
  pred_b <- 7L * series$channel_clicks[7]
  m <- data.frame(
    metric = c("A", "B", "actual", "mae_A", "mae_B", "note"),
    detail = c(
      "predict_next_7d_equals_prev_7d_sum",
      "predict_next_7d_equals_7x_last_day_clicks",
      "next_7d_channel_clicks_sum",
      "abs(pred_A - actual)",
      "abs(pred_B - actual)",
      "sparse_sample_see_docs"
    ),
    value = c(pred_a, pred_b, actual_next, abs(pred_a - actual_next), abs(pred_b - actual_next), 1)
  )
  write.csv(m, file.path(out_dir, "task1_clicks_backtest_metrics.csv"), row.names = FALSE)
  message("Wrote task1_clicks_* to ", out_dir)
  quit(save = "no")
}

# Rolling (14+ days)
preds_a <- preds_b <- actuals <- integer(0)
for (i in 8:(n - 7)) {
  prev7 <- sum(series$channel_clicks[(i - 7):(i - 1)])
  next7 <- sum(series$channel_clicks[i:(i + 6)])
  preds_a <- c(preds_a, prev7)
  preds_b <- c(preds_b, 7L * series$channel_clicks[i - 1])
  actuals <- c(actuals, next7)
}
mae_a <- mean(abs(preds_a - actuals))
mae_b <- mean(abs(preds_b - actuals))
m <- data.frame(
  metric = c("n_eval_points", "mae_baseline_A", "mae_baseline_B"),
  detail = c("rolling_windows", "prev7_sum", "7x_yesterday"),
  value = c(length(actuals), round(mae_a, 4), round(mae_b, 4))
)
write.csv(m, file.path(out_dir, "task1_clicks_backtest_metrics.csv"), row.names = FALSE)
message("Wrote task1_clicks_backtest_metrics.csv (", length(actuals), " points)")
