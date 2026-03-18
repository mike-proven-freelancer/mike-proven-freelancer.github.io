# Newbie guide: What the job wanted and what we did (Phase 0 & 1)

A plain-English summary for learning.

---

## What the job description actually wanted

The Upwork role was for someone who:

1. **Gets messy data from lots of places** — spreadsheets, APIs, exports, logs — and turns it into one organized system so analysts and models can use it.
2. **Builds “historical snapshots”** — so you can ask questions like “what did we know on this date?” and run tests as if you were in the past.
3. **Designs how data is stored** — which tables, which columns, how they link — so reporting and prediction make sense.
4. **Tests predictions fairly** — by running models on past data only and comparing “what the model said” to “what actually happened” (that’s a backtest).
5. **Finds patterns** — e.g. which content or campaigns perform better — by joining and summarizing the structured data.
6. **Keeps improving how we evaluate** — clear rules for how we measure success and compare different approaches.

So the job is **not** “train one fancy AI model on clean data.” It’s **“take messy real-world data, structure it, and use it to evaluate and improve decision-making.”**

---

## How we’re achieving it (in one sentence)

We’re building a **fake-but-realistic** version of that job: a fictional company (BrightWave Media), fake data that looks like real exports and logs, a real schema and pipeline, and real backtests — so your portfolio shows you can do exactly what the job asked for.

---

## What “reverse engineering” meant here

**Reverse engineering** here meant: **start from the job ad and work backward to a concrete plan.**

- We took each bullet (e.g. “Collecting and structuring datasets from public sources”) and asked: *“What would we actually build to prove we can do that?”*
- Answer: raw files in many formats → a pipeline → a clean warehouse. So we **designed** that pipeline and warehouse (Phase 1) before creating any data (Phase 2).

So we didn’t copy their code or data. We **translated their words into a clear list of deliverables** (tables, pipelines, backtests, docs) and then designed our project to match that list. That translation step is what we call “reverse engineering” the job description.

---

## What happened in Phase 0 (foundation)

We locked in the **story and rules** so everything else has a clear purpose:

- **Who:** A fictional brand/content publisher (BrightWave Media) that does blogs, newsletters, social, campaigns, affiliate, sponsorships, subscriptions.
- **Why:** So we have “multiple public-like sources” (platform exports, ad dashboards, affiliate reports, newsletter data) — just like the job said.
- **What we’ll answer:** Business questions (revenue per post, cost per subscriber, next-week engagement, where to put budget).
- **How we’ll deliver:** Everything viewable or downloadable on a static website (CSV, Markdown, HTML reports, SQLite, etc.).
- **Rules:** Synthetic data only, 100+ records per main entity, obviously fake names, no real people.

We also defined the **folder structure** (raw → intermediate → warehouse, plus python/, r/, reports/, docs/, site/) and **what “web-friendly” means** for each artifact.

---

## What happened in Phase 1 (reverse engineering / design)

We turned the job’s responsibilities into a **concrete design** — no data yet, just blueprints:

1. **Responsibility → deliverable table**  
   Each job bullet was mapped to something we will build (e.g. “Running backtests” → Python and R notebooks that run backtests and a short report).

2. **Data specification**  
   We wrote down:
   - Which **entities** exist (accounts, channels, creators, content, campaigns).
   - Which **tables** (dimensions like `dim_content`, facts like `fact_post_performance_daily`).
   - **Grain** (e.g. one row per post per day).
   - **Time span** (e.g. 24 months).
   - What **messiness** we’ll add on purpose in the raw data (missing values, duplicates, mixed date formats, etc.) so we can show cleaning and reconciliation.

3. **Schema**  
   We created the actual SQL: `warehouse/schema.sql` with all tables and keys. So when we generate data in Phase 2, we know exactly what to fill.

4. **“Public sources” we’ll emulate**  
   We listed where each type of messy input will live (e.g. platform export → `raw/api/` or `raw/vendor/`, ad dashboard → Excel in `raw/vendor/`, etc.).

5. **Evaluation framework**  
   We defined how we’ll backtest: two tasks (next-period prediction + budget allocation), time-based train/test split, baselines (e.g. moving average, equal split), simple models, and metrics (MAE, RMSE, business KPI). So in Phase 3 we just execute this plan.

6. **Project overview**  
   We added a short doc that explains the project and maps it to the job description for portfolio visitors.

**Phase 1 is “design only.”** Phase 2 creates the messy raw data and loads the warehouse. Phase 3 runs the pipelines, analysis, and backtests and writes the action plan.

For **how we decided what tables and columns to have** when the job wasn’t explicit, see [how-we-designed-the-schema.md](how-we-designed-the-schema.md).

---

## Quick recap

| Phase | What we did |
|-------|-------------|
| **Phase 0** | Chose the story (BrightWave Media), KPIs, success criteria, folder structure, and web-friendly artifact list. |
| **Phase 1** | Reverse engineered the job into deliverables; wrote data spec, schema, source list, and evaluation framework; no data built yet. |
| **Phase 2** (next) | Generate synthetic messy data and load it into the warehouse. |
| **Phase 3** | Run pipelines, EDA, backtests, and produce the business action plan and reports. |
