# Raw data (messy synthetic sources)

Phase 2 synthetic files (finance-focused, intentionally messy). See `docs/raw-files-guide.md` for what each file contains and how it maps to the warehouse.

- **api/** — `engagement_2024q1.json`, `revenue_2024q1.json` (nested JSON, mixed types, missing keys)
- **vendor/** — `campaign_spend_2024q1.csv`, `campaign_spend_2024q2.csv` (schema drift between files), `newsletter_2024q1.tsv`
- **notes/** — `campaign_q2_push.md` (unstructured)
- **logs/** — `events_2024q1_sample.log` (duplicates, corrupt lines)
- **drops/** — Optional zipped vendor drops (not yet added)
