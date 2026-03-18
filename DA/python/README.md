# Python

Jupyter notebooks (`.ipynb`) and scripts for ingest, clean, load, and analysis.
Rendered HTML goes to `reports/`.

## Load engagement into warehouse

From project root:

```bash
python python/load_engagement_to_warehouse.py
```

(Uses `warehouse/schema.sql`, `warehouse/seed_dimensions.sql`, and `raw/api/engagement_2024q1.json`; writes to `warehouse/brightwave.sqlite`.)
