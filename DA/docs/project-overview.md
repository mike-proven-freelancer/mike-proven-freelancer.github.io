# BrightWave Media benchmark — project overview

Portfolio project demonstrating data science and research analyst work for **predictive modeling and dataset development** (aligned to an Upwork-style role).

## What this project does

- **Designs and structures a benchmark dataset** from multiple “public-source-like” inputs (platform exports, ad dashboards, affiliate reports, newsletter data, notes).
- **Builds pipelines and schemas** that turn messy raw data into a research-grade SQLite warehouse and CSV exports.
- **Runs backtests** comparing baseline rules to simple predictive models (forecasting and budget allocation) and documents the evaluation framework.

The fictional context is **BrightWave Media**, a brand/content publisher that monetizes via affiliate, sponsorships, and subscriptions. All data is synthetic; no real people or identities.

## How it maps to the job description

| Job requirement | Where we show it |
|-----------------|------------------|
| Collecting and structuring datasets from public sources | Multiple raw formats in `raw/`; pipeline to `warehouse/`. |
| Reconstructing historical information snapshots | Time-bounded fact tables (daily performance, spend, revenue). |
| Designing data schemas for analytical models | `warehouse/schema.sql` and [data-spec.md](data-spec.md). |
| Running backtests and comparing to historical outcomes | [evaluation-framework.md](evaluation-framework.md); notebooks in Phase 3. |
| Identifying patterns across structured datasets | EDA and KPI reports (Phase 3). |
| Improving evaluation frameworks | Documented protocol, baselines, metrics, and comparison process. |

## Repository layout

- **raw/** — Messy synthetic sources (JSON, CSV, Excel, logs, notes).
- **intermediate/** — Cleaned extracts.
- **warehouse/** — SQLite database, schema, and CSV exports.
- **python/**, **r/** — Analysis and pipeline notebooks (Python and R).
- **reports/** — Rendered HTML reports.
- **docs/** — Data spec, evaluation framework, and this overview.

All outputs are web-friendly (CSV, Markdown, HTML) for use on a static portfolio site.
