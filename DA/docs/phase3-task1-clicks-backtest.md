# Phase 3 Task 1: Next-7-day clicks (baseline backtest)

## What you chose

- **Goal:** Support **engagement** (clicks) first — higher engagement often supports revenue later.
- **Then:** Understand **revenue sources** (what’s working / selling best) — see `phase3_revenue_sources.py` outputs in `reports/phase-3/`.

## Why we use channel-level clicks here

The teaching warehouse has **sparse** post-level daily rows (one or two days per content in the sample). A strict **per-content** rolling 7-day backtest needs many consecutive days per content.

So Task 1 uses **channel-level daily clicks**: sum of clicks across all content on each calendar day for dates that appear in `fact_post_performance_daily`, then **fill missing calendar days with 0** between min and max date so “weeks” are defined on the calendar.

## Baselines (no ML required)

| Baseline | Rule |
|----------|------|
| **A** | Next 7 days total clicks ≈ **previous 7 days** total (weekly persistence). |
| **B** | Next 7 days total ≈ **7 × last day’s** channel clicks. |

## With the current small sample

You may get **one** evaluation point (first calendar week vs next week). That’s enough to show the **pattern** of backtesting; a larger synthetic history would produce many rolling windows and more stable MAE.

## Scripts

- Python: `python/phase3_task1_clicks_forecast.py` → `reports/phase-3/task1_clicks_daily_series.csv`, `task1_clicks_backtest_metrics.csv`
- R: `r/phase3_task1_clicks_forecast.R` (same logic)

## Next steps (optional)

- Add more daily rows per `content_id` in the warehouse → rerun for **per-content** forecasts.
- Add a simple model (e.g. ridge on lags) and compare MAE to baselines on the same splits.
