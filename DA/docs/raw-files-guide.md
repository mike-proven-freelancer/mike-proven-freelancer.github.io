# Guide to the raw files (what’s in each and what’s messy)

This doc describes the synthetic raw files we generated and the **intentional messiness** in each. Use it when building the pipeline: your job is to clean and map each source into the warehouse schema.

---

## Where the raw files live

| Folder   | File(s) | Content |
|----------|---------|--------|
| `raw/api/` | `engagement_2024q1.json` | Daily engagement metrics per post (nested JSON). |
| `raw/api/` | `revenue_2024q1.json`     | Revenue events (affiliate, sponsorship, subscription). |
| `raw/vendor/` | `campaign_spend_2024q1.csv` | Campaign daily spend (Q1); mixed date formats, empty cells, footer. |
| `raw/vendor/` | `campaign_spend_2024q2.csv` | Same idea but **different column names** (schema drift): `spend_usd`, `impr`, `click_count`. |
| `raw/vendor/` | `newsletter_2024q1.tsv`   | Newsletter sends, opens, clicks, unsubscribes (tab-separated). |
| `raw/notes/` | `campaign_q2_push.md`     | Unstructured notes about campaigns and performance. |
| `raw/logs/` | `events_2024q1_sample.log` | Event log (view, click, error); duplicates and corrupt lines. |

---

## `raw/api/engagement_2024q1.json`

- **What it is:** Daily engagement per content piece (impressions, likes, shares, clicks, comments).
- **Target table:** `fact_post_performance_daily` (after mapping `post_id` → `content_id`, normalizing date, and choosing one grain).
- **Messiness:**
  - Nested under `data.rows`.
  - Date field sometimes `dt`, sometimes `date`; formats: `YYYY-MM-DD`, `MM/DD/YYYY`, `M/D/YYYY`.
  - Numbers sometimes strings (e.g. `"12400"`), sometimes integers; `comments` sometimes missing; one empty string for `shares`.
  - Duplicate row (CONT-001 on 2024-01-15 appears twice).

---

## `raw/api/revenue_2024q1.json`

- **What it is:** One record per revenue event (affiliate, sponsorship, subscription).
- **Target table:** `fact_revenue_events`.
- **Messiness:**
  - Nested under `events`.
  - `amount` sometimes string (e.g. `"2500.00"`), sometimes number.
  - Dates: mostly `YYYY-MM-DD`, one `M/D/YYYY`.
  - `campaign_id` or `content_id` sometimes null, sometimes missing key, sometimes empty string.
  - One event (REV-011) has no `campaign_id` key at all.

---

## `raw/vendor/campaign_spend_2024q1.csv`

- **What it is:** Daily spend and delivery per campaign.
- **Target table:** `fact_campaign_spend_daily`.
- **Messiness:**
  - Header: `Campaign ID`, `Date`, `Spend`, `Impressions`, `Clicks` (title case; spaces).
  - Mixed date formats: `YYYY-MM-DD`, `01/22/2024`, `1/27/2024`.
  - Empty `Spend` on one row (2024-01-18); empty `Spend` on 2024-01-29.
  - Footer: two non-data lines at the end (comment and “Footer row - do not import”).

---

## `raw/vendor/campaign_spend_2024q2.csv` (schema drift)

- **What it is:** Same kind of data as Q1 file but from a “new” export.
- **Target table:** `fact_campaign_spend_daily` (same as Q1).
- **Messiness:**
  - Different column names: `campaign_id`, `date`, `spend_usd`, `impr`, `click_count` (no “Campaign ID”, “Spend”, “Impressions”, “Clicks”). Pipeline must map these to the same schema.
  - One date in `MM/DD/YYYY` (04/07/2024).

---

## `raw/vendor/newsletter_2024q1.tsv`

- **What it is:** Newsletter send stats (recipients, sends, opens, clicks, unsubscribes, bounces).
- **Target table:** Can feed into campaign/channel analytics or a separate newsletter summary table; dates and counts can support “cost per subscriber” type analyses.
- **Messiness:**
  - Tab-separated (not comma).
  - Mixed date formats: `YYYY-MM-DD`, `01/22/2024`, `2/12/2024`, `03/11/2024`.
  - Footer line (note about date formats and schema).

---

## `raw/notes/campaign_q2_push.md`

- **What it is:** Human-written notes about Q2 push and performance.
- **Use:** Not a table — use for context, or later to parse out campaign names, content IDs, and KPIs (e.g. “cost per sub ~$22”) for validation or narrative.

---

## `raw/logs/events_2024q1_sample.log`

- **What it is:** Log lines: timestamp, event type (view, click, error), content_id, sometimes channel or link.
- **Use:** Can be parsed to count views/clicks per content per day and cross-check or supplement `fact_post_performance_daily`; or to study bot/duplicate behavior.
- **Messiness:**
  - Many duplicate lines (same event logged twice).
  - Non-standard lines: “truncated line - missing timestamp”, “corrupt” (no parseable structure).
  - Pipeline must skip or flag invalid lines and decide deduplication rules.

---

## How this connects to schema design

The **target schema** (see `warehouse/schema.sql` and `docs/data-spec.md`) was designed so that:

- These raw sources can be **mapped** into it (same concepts: content, campaign, date, metrics).
- We can answer **time-based and slice-by-entity** questions and run backtests.

Cleaning = turning each file’s format and quirks into rows in the right tables with consistent types and keys. The doc **how-we-designed-the-schema.md** explains why those tables and columns exist in the first place.
