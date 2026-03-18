# Loading raw sources into the warehouse

**Why we do each load in both Python and R:** See [what-to-learn-python-vs-r.md](what-to-learn-python-vs-r.md) for what to notice when comparing the two scripts.

---

## What “loading” means

**Loading** = code that:

1. Reads raw data from a file (here: `raw/api/engagement_2024q1.json`).
2. Cleans and normalizes it (parse dates, coerce types, handle missing values, dedupe).
3. Writes the result into the warehouse (SQLite) in the right table and columns.

So we’re not moving files by hand — we’re using **Python or R** to “comb through” the data and insert **records** into the warehouse. Both languages can do this; we do the same load in both so you can compare.

---

## Why we need dimension rows first

The fact table `fact_post_performance_daily` has a foreign key: `content_id` must exist in `dim_content`. So before we insert engagement rows we need:

1. Create the database and tables (`schema.sql`).
2. Insert minimal **dimension** rows so CONT-001 … CONT-005 exist (`seed_dimensions.sql`).
3. Then insert the **fact** rows from the engagement JSON.

The Python and R scripts do (1) and (2) first, then (3).

---

## What the scripts do (same logic in both)

1. **Init** — Connect to `warehouse/brightwave.sqlite`, run `schema.sql`, then `seed_dimensions.sql`.
2. **Read** — Load `raw/api/engagement_2024q1.json` and get the list of rows (under `data.rows`).
3. **Clean**
   - Map `post_id` → `content_id`.
   - Take date from `dt` or `date`; normalize to `YYYY-MM-DD` (handle `01/16/2024` and `1/20/2024`).
   - Coerce impressions, likes, shares, clicks, comments to integers; treat missing or empty as 0.
4. **Dedupe** — Keep one row per (content_id, date); drop duplicates (we had one duplicate in the raw file).
5. **Insert** — `INSERT OR REPLACE` into `fact_post_performance_daily` so re-running the script doesn’t fail.

---

## How to run

**Python** (from project root `DA/`):

```bash
python python/load_engagement_to_warehouse.py
```

On Windows you may need `py` instead of `python`. You should see: `Loaded 9 engagement rows into fact_post_performance_daily.`

**R** (from project root `DA/`):

```r
# Install once: install.packages(c("DBI", "RSQLite", "jsonlite"))
source("r/load_engagement_to_warehouse.R")
```

Or from the shell: `Rscript r/load_engagement_to_warehouse.R`

You should see: `Loaded 9 engagement rows into fact_post_performance_daily.`

---

## Files involved

| File | Role |
|-----|------|
| `warehouse/schema.sql` | Creates all tables. |
| `warehouse/seed_dimensions.sql` | Inserts one account, one channel, two creators, five content rows (CONT-001 … CONT-005). |
| `raw/api/engagement_2024q1.json` | Raw engagement data (messy). |
| `python/load_engagement_to_warehouse.py` | Python: init + load engagement. |
| `r/load_engagement_to_warehouse.R` | R: same init + load engagement. |
| `warehouse/brightwave.sqlite` | The database file (created/updated by the scripts). |

---

## Second source: campaign spend CSV → fact_campaign_spend_daily

We load **two** raw files (schema drift: different column names between Q1 and Q2):

| Raw file | Columns (messy) | Cleaned to |
|----------|-----------------|------------|
| `raw/vendor/campaign_spend_2024q1.csv` | Campaign ID, Date, Spend, Impressions, Clicks | campaign_id, date, spend, impressions, clicks |
| `raw/vendor/campaign_spend_2024q2.csv` | campaign_id, date, spend_usd, impr, click_count | same |

**Steps (same in Python and R):** Run schema + `seed_dimensions.sql` + **`seed_campaigns.sql`** (so CAMP-Q1-PUSH and CAMP-Q1-SUB exist in `dim_campaign`). Read both CSVs; map Q2 column names to the same schema; normalize dates (YYYY-MM-DD); skip footer lines; empty Spend → 0; dedupe by (campaign_id, date); insert into `fact_campaign_spend_daily`.

**How to run**

```bash
# Python (from project root)
py python/load_campaign_spend_to_warehouse.py

# R (from project root)
Rscript r/load_campaign_spend_to_warehouse.R
```

Expected: `Loaded 28 campaign spend rows into fact_campaign_spend_daily.`

**Files added**

| File | Role |
|------|------|
| `warehouse/seed_campaigns.sql` | Inserts CAMP-Q1-PUSH, CAMP-Q1-SUB into `dim_campaign`. |
| `python/load_campaign_spend_to_warehouse.py` | Python: init + load both campaign spend CSVs. |
| `r/load_campaign_spend_to_warehouse.R` | R: same. |

---

## Third source: revenue JSON → fact_revenue_events

**Raw file:** `raw/api/revenue_2024q1.json` — events under `events`; each has `id`, `type`, `amount`, `date`, optional `content_id` and `campaign_id`.

**Messiness:** amount sometimes string; dates mixed (YYYY-MM-DD and M/D/YYYY); `content_id`/`campaign_id` can be null, missing key (e.g. REV-011 has no `campaign_id`), or empty string. We normalize dates, coerce amount to real, and store NULL for missing/empty FKs.

**Steps (same in Python and R):** Run schema + seed_dimensions + seed_campaigns; read JSON; for each event: normalize date, safe_float(amount), optional_id(content_id/campaign_id); insert into `fact_revenue_events`.

**How to run**

```bash
py python/load_revenue_to_warehouse.py
Rscript r/load_revenue_to_warehouse.R
```

Expected: `Loaded 12 revenue events into fact_revenue_events.`

**Files:** `python/load_revenue_to_warehouse.py`, `r/load_revenue_to_warehouse.R`

---

## Fourth source: newsletter TSV → fact_newsletter_daily

**Raw file:** `raw/vendor/newsletter_2024q1.tsv` (tab-separated). Columns: Date Sent, Recipients, Sends, Opens, Clicks, Unsubscribes, Bounces. Footer line skipped; dates normalized to YYYY-MM-DD.

**Schema:** Added `fact_newsletter_daily` (date PK, recipients, sends, opens, clicks, unsubscribes, bounces).

**How to run:** `py python/load_newsletter_to_warehouse.py` and `Rscript r/load_newsletter_to_warehouse.R`. Expected: `Loaded 13 newsletter rows into fact_newsletter_daily.`

---

## What’s loaded (all tabular raw sources)

| Source | Table | Rows |
|--------|--------|------|
| Engagement JSON | fact_post_performance_daily | 9 |
| Campaign spend (Q1 + Q2 CSV) | fact_campaign_spend_daily | 28 |
| Revenue JSON | fact_revenue_events | 12 |
| Newsletter TSV | fact_newsletter_daily | 13 |

**Not loaded as tables:** `raw/notes/campaign_q2_push.md` (unstructured text for context/narrative). `raw/logs/events_2024q1_sample.log` (optional: can be parsed in Phase 3 for analysis or validation). **What to learn from Python vs R:** see [what-to-learn-python-vs-r.md](what-to-learn-python-vs-r.md).
