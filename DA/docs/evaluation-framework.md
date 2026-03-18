# Evaluation framework and backtesting protocol

Aligned to the Upwork role: *“Running backtests and comparing model outputs to historical outcomes”* and *“Improving evaluation frameworks over time.”*

---

## Evaluation tasks (portfolio scope)

We will implement **two** evaluation tasks on the BrightWave benchmark:

### Task 1: Next-period engagement / revenue prediction

- **Target**: Predict next 7-day engagement (e.g. total clicks or likes per content) or revenue bucket (e.g. high / medium / low).
- **Grain**: Per content or per channel, depending on business question.
- **Use**: Compare baseline vs. model; document in notebook and short report.

### Task 2: Budget allocation (decision model)

- **Target**: Given a fixed weekly budget, allocate spend across campaigns (or channels) to maximize a business KPI (e.g. expected revenue or subscriptions).
- **Baseline**: Simple rule (e.g. equal split, or proportional to last week’s performance).
- **Model**: Lightweight decision aid (e.g. model-predicted “value” per campaign used to allocate budget).
- **Use**: Backtest on historical windows; compare baseline vs. model allocation by simulated outcome (e.g. total revenue in holdout period).

---

## Backtesting protocol

### Time-based split

- **Training window**: e.g. first 18 months of the 24-month history.
- **Validation** (optional): next 3 months for tuning.
- **Test / holdout**: last 3 months; no model retraining on this period; all metrics reported on holdout only.

No future leakage: features only use data available up to the prediction date.

### Task 1 (forecasting) — steps

1. For each date in the test window, train (or use rolling training) on past data only.
2. Predict next 7-day engagement or revenue bucket for each content/channel.
3. Compare predictions to actuals; compute metrics (see below).
4. Repeat for baseline and for model(s).

### Task 2 (budget allocation) — steps

1. For each week in the test window, use only past data to:
   - Run baseline rule → allocation vector.
   - Run model (e.g. predicted value per campaign) → allocation vector.
2. Simulate outcome: apply each allocation to “actual” campaign performance in that week (from fact tables).
3. Compare total KPI (e.g. revenue or conversions) under baseline vs. model allocation.

---

## Baselines

| Task | Baseline | Description |
|------|----------|-------------|
| Forecasting | Moving average | Past 7-day or 28-day average engagement/revenue for that content or channel. |
| Forecasting | Last period | Previous 7-day value as prediction. |
| Budget allocation | Equal split | Allocate budget equally across campaigns (or channels). |
| Budget allocation | Proportional to last week | Allocate in proportion to last week’s spend or performance. |

---

## Models (lightweight, portfolio-appropriate)

- **Forecasting**: e.g. Ridge/Lasso regression on lagged features and simple calendar features; or a small tree-based model (e.g. one sklearn GradientBoosting or RandomForest). No deep learning required.
- **Budget allocation**: Use predicted “value” (e.g. expected revenue or engagement) from a small model per campaign; allocate budget in proportion to predicted value (or similar rule). Compare to baseline allocation.

---

## Metrics

| Task | Metrics | Notes |
|------|---------|--------|
| Forecasting (numeric) | MAE, RMSE | For continuous targets (e.g. next 7-day clicks). |
| Forecasting (bucket) | Accuracy, F1 (macro), AUC if binary | For high/med/low revenue bucket. |
| Budget allocation | Business KPI on holdout | e.g. Total revenue or total conversions in test period under baseline vs. model allocation; report lift or difference. |

All metrics reported on the **same holdout period**; document in notebooks and in a one-page summary table (baseline vs. model).

---

## Comparison and reporting

- **Notebooks**: Python and R notebooks that run the full pipeline (load data → train → predict → evaluate).
- **Output**: A small results table (e.g. CSV or Markdown) and a short narrative in `docs/` or `reports/`: what was tried, what improved, and what a data analyst would do next to improve the framework.

This document defines the evaluation framework; implementation happens in Phase 3 (analysis) using data built in Phase 2.
