# Phase 3: Analysis and insights (reference)

Placeholder. After Phase 2 data exists:

- Run pipelines: raw → intermediate → warehouse.
- EDA and KPI reporting (Python + R).
- Execute evaluation tasks per docs/evaluation-framework.md (backtests, baselines, models, metrics).
- Produce business action plan: how to use the data to increase revenue and/or decrease expenses.
- Portfolio-ready writeup and rendered reports.

---

## Phase 3 started (status)

Phase 3 has started. First pass EDA/KPI extracts are generated in **both** Python and R.

### Outputs

- **Python script**: `python/phase3_eda_kpis.py`
- **R script**: `r/phase3_eda_kpis.R`
- **Output folder**: `reports/phase-3/`
  - `kpi_content_performance.csv`
  - `kpi_campaign_spend.csv`
  - `kpi_revenue_by_type.csv`
  - `kpi_revenue_attribution.csv`
  - `kpi_newsletter_daily.csv`

### Warehouse row counts (sanity check)

- `dim_account`: 1
- `dim_channel`: 1
- `dim_creator`: 2
- `dim_content`: 5
- `dim_campaign`: 2
- `fact_post_performance_daily`: 9
- `fact_campaign_spend_daily`: 28
- `fact_revenue_events`: 12
- `fact_newsletter_daily`: 13

### Task 1 started (clicks → engagement)

- User chose **next-7-day clicks** first (engagement path), then revenue source analysis.
- **Scripts:** `python/phase3_task1_clicks_forecast.py`, `r/phase3_task1_clicks_forecast.R`
- **Outputs:** `reports/phase-3/task1_clicks_daily_series.csv`, `task1_clicks_backtest_metrics.csv`
- **Note:** Sample is sparse; backtest is **channel-level** daily clicks (see `docs/phase3-task1-clicks-backtest.md`).

### Revenue sources (what’s working)

- **Scripts:** `python/phase3_revenue_sources.py`, `r/phase3_revenue_sources.R`
- **Outputs:** `revenue_by_type.csv`, `revenue_top_content.csv`, `revenue_by_campaign_attribution.csv`

### Task 2 (budget allocation)

- **Scripts:** `python/phase3_task2_budget_allocation.py`, `r/phase3_task2_budget_allocation.R`
- **Docs:** `docs/phase3-task2-budget-allocation.md`
- **Outputs:** `reports/phase-3/task2_budget_allocation_by_week.csv`, `task2_budget_allocation_summary.csv`
- Compares **equal split** vs **proportional to prior-week clicks** vs **efficiency-weighted** allocation under a linear clicks-per-dollar model.

### Portfolio (wrapped)

- **Main:** `site/project01.html` — visuals + action plan on one page.
- **Details:** `site/project01-details.html` — data paths, methodology, reproduce steps.
- **Build:** `py python/build_portfolio_site.py` regenerates `site/assets/*.png` and both HTML files.

### Optional later

- More daily rows for stronger forecasts; Quarto deep-dive; GitHub Pages deploy.
