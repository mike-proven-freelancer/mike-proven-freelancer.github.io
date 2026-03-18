# Phase 2: Data generation (reference)

Design notes for creating **synthetic, messy raw data** for BrightWave Media (finance-focused content) and loading it into the clean warehouse.

---

## Themes and scope (Phase 2)

- **Finance focus** (user choice): content around money and business.
- Example themes we will use in titles and tagging:
  - Personal Finance
  - Budgeting & Saving
  - Investing Basics
  - Retirement Planning
  - Small Business & Side Hustles
  - FinTech & Digital Banking
- Time range: as per data spec (24 months).
- Scale target: ≥100 rows per core dimension; thousands of rows in fact tables over time.

---

## Raw sources we will generate

These live under `raw/` and intentionally contain **messiness** (missing values, duplicates, mixed formats, etc.).

- **Platform engagement export** (`raw/api/engagement_*.json` / `raw/vendor/engagement_*.csv`)
  - Daily or per-post metrics: impressions, clicks, likes, shares, comments.
  - Some numbers as strings, some missing fields, mixed date formats.

- **Ad dashboard export** (`raw/vendor/campaign_spend_*.csv`)
  - Campaign-level daily spend, impressions, clicks.
  - Header changes between files (schema drift), extra footer rows, occasional empty cells.

- **Revenue report** (`raw/api/revenue_*.json`)
  - Event-level revenue: affiliate, sponsorship, subscription.
  - Nested JSON, optional `content_id` or `campaign_id`, some malformed entries.

- **Newsletter export** (`raw/vendor/newsletter_*.tsv`)
  - Sends, opens, clicks, unsubscribes.
  - Mixed delimiters/encodings, odd date formats.

- **Campaign notes** (`raw/notes/campaign_*.md`)
  - Human-written notes like \"boosted investing series in Q2; strong CTR but low conversions\".
  - Used later to show how unstructured text can be linked to campaigns/themes.

- **Logs** (`raw/logs/events_*.log`)
  - Timestamped events (e.g. content view, click, error).
  - Includes duplicates, partial/corrupt lines.

---

## Messiness level (chosen: \"very messy\")

We will inject:

- Missing values in key metrics and optional fields.
- Duplicated rows in exports and repeated log lines.
- Numbers stored as strings, and mixed date formats (ISO + MM/DD/YYYY).
- Column name changes between file versions (e.g. `clicks` vs `click_count`).
- Extra header/footer rows and comments in CSV-like files.
- Encoding quirks (simulated in text) and mixed delimiters (CSV + TSV).
- Nested JSON arrays/objects that require flattening.
- Truncated / malformed log lines.

---

## Generation notes (to follow as we implement)

- Use fixed random seeds so the synthetic data is reproducible.
- Start with **small samples** for teaching, then scale up to full size.
- Map all raw fields back to the warehouse schema (`schema.sql`) via documented transforms.
- Ensure no real people or real identifiers appear anywhere.

**Initial raw files created:** `raw/api/engagement_2024q1.json`, `raw/api/revenue_2024q1.json`, `raw/vendor/campaign_spend_2024q1.csv`, `raw/vendor/campaign_spend_2024q2.csv` (schema drift), `raw/vendor/newsletter_2024q1.tsv`, `raw/notes/campaign_q2_push.md`, `raw/logs/events_2024q1_sample.log`. See `docs/raw-files-guide.md`.

**Load status:** All four tabular sources are loaded into the warehouse (engagement → fact_post_performance_daily, campaign spend → fact_campaign_spend_daily, revenue → fact_revenue_events, newsletter → fact_newsletter_daily). Python and R loaders for each. Notes and logs are not loaded as tables; optional for Phase 3. See `docs/loading-one-source.md` and `docs/phase-2-complete-phase-3-next.md`.

Checklist to keep in mind:

- [ ] ≥100 rows per core dimension table (`dim_*`).
- [ ] Thousands of fact rows over 24 months.
- [ ] Finance themes present in content titles and tags.
- [ ] Messiness types from `docs/data-spec.md` represented across raw sources.
- [ ] All synthetic, no re-identification risk.
