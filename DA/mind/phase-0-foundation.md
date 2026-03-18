# Phase 0: Foundation

## Current phase
**Phase 0** — Foundation (scope, story, structure). No teaching quizzes yet.

---

## Fictional company: BrightWave Media

**BrightWave Media** is a fictional brand/content publisher that:

- Publishes content across multiple channels (blog, newsletter, social platforms).
- Monetizes via affiliate links, sponsorships, and paid newsletter subscriptions.
- Runs paid campaigns to grow reach and conversions.
- Wants to use data to decide what to publish, when, and how much to spend on promotion.

This context matches the Upwork role: combining multiple “public”/operational sources (platform exports, ad dashboards, affiliate reports, newsletter tool) into structured datasets to evaluate predictive models and improve decisions.

---

## Business KPIs (portfolio piece)

We will design the benchmark so these can be answered or approximated:

| KPI / question | Type | How we support it |
|----------------|------|--------------------|
| Revenue per post (by theme, channel, time) | Descriptive / reporting | Clean fact tables (post performance + revenue events) |
| Cost per acquired subscriber | Efficiency | Campaign spend + subscription events, join by campaign |
| Engagement trend (likes, shares, clicks) over time | Descriptive / trend | Daily post-performance facts, time series |
| Next-week engagement or revenue bucket (high/med/low) | Predictive | Backtest: baseline vs. model on historical splits |
| Budget allocation (which campaigns/channels to fund) | Decision / optimization | Evaluation framework: compare rule-based vs. model-guided allocation |

---

## Success criteria for the portfolio piece

1. **Demonstrates the job description**
   - Artifacts map clearly to: collecting/structuring from multiple sources, historical snapshots, schema design, backtests, pattern-finding, evaluation framework.

2. **Web-friendly**
   - All deliverables viewable or downloadable from a static site: CSV, Markdown, HTML reports, notebooks (as HTML), SQLite + schema + CSV extracts.

3. **Realistic but safe**
   - Synthetic data only; 100+ records per core entity; obviously fake names/contacts; no re-identification risk; patterns plausible for social/content publishing.

4. **Teaching-ready**
   - Explanations of data and pipelines; same analytical tasks shown in Python and R; space for quizzes and “what you learned” after teaching blocks.

5. **Reproducible**
   - Fixed seeds for synthetic data; clear pipeline steps (raw → intermediate → warehouse); documented evaluation protocol.

---

## Definitions (for AI/context)

- **Benchmark dataset**: A structured, research-grade dataset built from messy sources, used to test analytical frameworks and predictive systems.
- **Backtest**: Running a model or rule on historical data (time-based split) and comparing outputs to actual outcomes.
- **Grain**: The level of detail of a table (e.g., one row per post per day).
- **Portfolio piece**: A self-contained project that showcases skills for the Upwork-style role; static-site friendly.
