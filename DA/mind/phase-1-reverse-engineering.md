# Phase 1: Reverse engineering the job description

## What “reverse engineering” means here

Translate each responsibility and scope item from the Upwork posting into **concrete portfolio deliverables**: which datasets, pipelines, schemas, and experiments we will build so the portfolio clearly demonstrates the same work.

---

## Responsibility → artifact mapping

| Job responsibility | Portfolio artifact / deliverable | Phase 1 task |
|--------------------|---------------------------------|--------------|
| **Collecting and structuring datasets from public sources** | Multiple “source” formats in `raw/` (API JSON, logs, Excel, CSV, notes); pipeline that ingests and normalizes into `intermediate/` and `warehouse/`. | Define which “public sources” we emulate (platform export, ad dashboard, affiliate report, newsletter tool); list raw file types and naming. |
| **Reconstructing historical information snapshots** | Time-bounded raw extracts + fact tables with `date` (e.g. daily post performance, daily campaign spend). Documentation of “as-of” logic. | Specify time range and grain (e.g. one row per post per day); document how we simulate historical snapshots in synthetic data. |
| **Designing data schemas for analytical models** | `warehouse/schema.sql`; dimension and fact tables; data dictionary in `docs/`. | Draft full schema (tables, columns, keys, grain); align to business questions and evaluation tasks. |
| **Running backtests and comparing model outputs to historical outcomes** | Notebooks (Python + R) that train on past window, predict next period, compare to actuals; metrics (MAE, RMSE, AUC, etc.); short report. | Define backtest protocol: train/test split (time-based), baselines, one or two models, metrics, and comparison table. |
| **Identifying patterns across structured datasets** | EDA notebooks and reports; summary tables and visuals (e.g. engagement by theme/channel, revenue by campaign). | List analytical questions and required joins; ensure schema supports them. |
| **Improving evaluation frameworks over time** | Documented evaluation framework: what we measure, how we split data, how we compare models; `docs/evaluation-framework.md`. | Write evaluation design (see phase-1-eval-design). |

---

## Project scope (initial) → deliverables

| Scope item | Deliverable |
|------------|-------------|
| **Help design and structure a benchmark dataset** | Dataset specification (`mind/` or `docs/`), schema, and synthetic data generation spec (entities, relationships, grain, anomalies). |
| **Build data pipelines and schemas** | Scripts/notebooks: raw → intermediate → warehouse; `schema.sql`; optional DAG or README describing pipeline steps. |
| **Assist with model evaluation experiments** | Backtest notebooks (Python + R), metrics, and a one-page summary of baseline vs. model performance. |

---

## Phase 1 task list (reverse engineering)

- [x] Map each responsibility to an artifact (this document).
- [x] **Data spec**: Draft dataset specification (entities, schema, grains, relationships, time span, required messiness/anomalies) — see `docs/data-spec.md` and `warehouse/schema.sql`.
- [x] **Source emulation**: Defined in `docs/data-spec.md` (Platform export, Ad dashboard, Affiliate report, Newsletter tool, Notes, Logs) and `mind/artifacts-and-structure.md`.
- [x] **Evaluation design**: Backtest and evaluation protocol — see `docs/evaluation-framework.md`.
- [x] **Docs**: Project narrative and job mapping in `docs/project-overview.md`.

Completion of these yields a clear design so Phase 2 (synthetic data build) and Phase 3 (analysis and action plan) can proceed without ambiguity.
