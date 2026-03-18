# Dataset specification: BrightWave Media benchmark

Structured dataset design for the portfolio project. Supports business KPIs and evaluation/backtesting.

---

## Time span and scope

- **Time range**: 24 months of synthetic history (e.g. 2023-01-01 through 2024-12-31).
- **Grain for time series**: Daily for performance and spend; event-level for revenue.
- **Minimum scale**: 100+ rows per core dimension table; daily facts will yield thousands of rows.

---

## Entities and dimensions

| Entity | Table | Grain | Key columns (conceptual) | Purpose |
|--------|--------|--------|---------------------------|---------|
| Account | `dim_account` | One row per account | `account_id`, name, created_at, region | Brand/publisher identity. |
| Channel | `dim_channel` | One row per channel | `channel_id`, name, platform (blog, newsletter, social_X), created_at | Where content is published. |
| Creator | `dim_creator` | One row per creator | `creator_id`, display_name, role, joined_at | Content author / brand persona. |
| Content | `dim_content` | One row per content piece | `content_id`, title, theme, content_type, channel_id, creator_id, published_at | Individual posts/articles. |

---

## Fact tables

| Table | Grain | Key columns (conceptual) | Purpose |
|-------|--------|---------------------------|---------|
| `fact_post_performance_daily` | One row per content per day | `content_id`, `date`, impressions, likes, shares, clicks, comments | Engagement metrics for backtest and reporting. |
| `fact_campaign_spend_daily` | One row per campaign per day | `campaign_id`, `date`, spend, impressions, clicks | Paid promotion; join to posts via bridge. |
| `fact_revenue_events` | One row per revenue event | `event_id`, `content_id` (nullable), `campaign_id` (nullable), `date`, amount, type (affiliate, sponsorship, subscription) | Revenue attribution and KPIs. |

---

## Bridge and campaigns

| Table | Grain | Purpose |
|-------|--------|---------|
| `dim_campaign` | One row per campaign | `campaign_id`, name, channel_id, start_date, end_date, objective. |
| `bridge_post_campaign` | One row per (content, campaign) | Links which content was promoted by which campaign (many-to-many). |

---

## Relationships (ER summary)

```
dim_account ──┬── dim_channel (account owns channels)
              └── dim_creator (account employs creators)

dim_channel ──┬── dim_content (content published on channel)
              └── dim_campaign (campaigns run on channel)

dim_creator ───── dim_content (creator authors content)

dim_content ──┬── fact_post_performance_daily (content_id, date)
              ├── fact_revenue_events (content_id, e.g. affiliate)
              └── bridge_post_campaign ── dim_campaign

dim_campaign ──┬── fact_campaign_spend_daily (campaign_id, date)
               ├── fact_revenue_events (campaign_id, e.g. subscription drive)
               └── bridge_post_campaign
```

---

## Required messiness and anomalies (raw layer)

We will generate clean target tables but **produce raw inputs** that mimic real-world problems. Pipelines will demonstrate cleaning and reconciliation.

| Anomaly type | Where we emulate it | Teaching point |
|--------------|--------------------|----------------|
| Missing values | API JSON with absent keys; CSV with empty cells | Imputation, defaults, or explicit “unknown”. |
| Duplicates | Logs with repeated events; CSV with duplicate rows | Deduplication and keys. |
| Inconsistent types | JSON numbers as strings; mixed date formats (ISO vs MM/DD/YYYY) | Parsing and type coercion. |
| Schema drift | Two “export” versions with different column names or order | Mapping and versioned schemas. |
| Merged/extra headers | Excel with merged cells; footnotes in last rows | Skip rows, clean headers. |
| Nested structure | JSON with arrays and objects | Flattening and one-to-many extracts. |
| Partial/corrupt lines | Log files with truncated or malformed lines | Log parsing, validation, discard or flag. |
| Multiple delimiters / encodings | TSV vs CSV; UTF-8 vs Latin-1 | Encoding and delimiter detection. |

---

## “Public sources” we emulate (Phase 1 alignment)

| Source | Format | Content | Raw path (example) |
|--------|--------|---------|--------------------|
| Platform export (engagement) | JSON or CSV | Post-level or daily rollups | `raw/api/engagement_*.json` or `raw/vendor/engagement_*.csv` |
| Ad dashboard export | CSV or Excel | Campaign daily spend/impressions | `raw/vendor/campaign_spend_*.xlsx` |
| Affiliate / revenue report | JSON or CSV | Revenue events by type | `raw/api/revenue_*.json` |
| Newsletter tool export | CSV or TSV | Subscriptions, sends, opens | `raw/vendor/newsletter_*.tsv` |
| Internal campaign notes | Markdown | Unstructured notes to parse | `raw/notes/campaign_*.md` |
| Logs (optional) | .log / .txt | Event stream with timestamps | `raw/logs/events_*.log` |

---

## Primary keys and uniqueness

- **dim_account**: `account_id` (PK).
- **dim_channel**: `channel_id` (PK); `account_id` (FK).
- **dim_creator**: `creator_id` (PK); `account_id` (FK).
- **dim_content**: `content_id` (PK); `channel_id`, `creator_id` (FK).
- **dim_campaign**: `campaign_id` (PK); `channel_id` (FK).
- **fact_post_performance_daily**: composite (content_id, date) — unique per content per day.
- **fact_campaign_spend_daily**: composite (campaign_id, date).
- **fact_revenue_events**: `event_id` (PK); optional FKs to content_id, campaign_id.
- **bridge_post_campaign**: composite (content_id, campaign_id).

All IDs are synthetic (UUIDs or integer surrogates); no real person identifiers.
