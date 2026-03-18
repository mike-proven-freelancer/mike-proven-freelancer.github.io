# Site (static portfolio)

## Main page

- **`project01.html`** — Charts, analysis summary, and **action plan** on one page.
- **`project01-details.html`** — Links to warehouse, raw data, docs, CSV outputs, and how to reproduce.

## Regenerate

From repo root (after Phase 3 CSVs exist under `reports/phase-3/`):

```bash
py python/build_portfolio_site.py
```

This refreshes `assets/*.png` and both HTML files.

## View locally

Open `site/project01.html` in a browser (double-click or “Open with Live Server”).

## Deploy (e.g. GitHub Pages)

Option A: Publish the **whole repo** and set Pages to `/site` or move these files into `docs/`.

Option B: Copy `site/` contents (including `assets/`) to your Pages branch; keep links on **details** page working by mirroring `reports/`, `docs/`, `warehouse/` or updating URLs to raw GitHub links.
