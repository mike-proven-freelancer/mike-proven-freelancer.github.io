# Repository structure and web-friendly artifacts

## Folder layout

```
DA/
├── mind/                    # Phase state, tasks, glossary, decisions (for AI)
├── raw/                     # Messy synthetic source files (as-delivered)
│   ├── api/                 # API-like JSON exports
│   ├── logs/                # Log files (.log, .txt)
│   ├── vendor/              # Excel, TSV, vendor CSVs
│   ├── notes/               # Human docs (campaign notes, etc.)
│   └── drops/               # Zipped vendor drops (optional)
├── intermediate/            # Cleaned/standardized extracts (CSV, Parquet optional)
├── warehouse/               # SQLite DB + final CSV table exports
├── python/                  # Jupyter notebooks + scripts
├── r/                       # Quarto/R Markdown notebooks
├── reports/                 # Rendered HTML (Quarto + notebook exports)
├── docs/                    # Markdown narrative, data dictionaries
└── site/                    # Copy of web-friendly outputs for static portfolio
```

## Web-friendly artifacts (what we publish)

| Artifact type | Format | Location | Purpose |
|---------------|--------|----------|---------|
| Datasets | `.csv` | `warehouse/*.csv`, optionally `site/data/` | Primary tabular data; viewable in browser or downloadable. |
| Data samples | `.json` | `raw/api/` or `docs/samples/` | Small samples to show nested/API-like structure. |
| Documentation | `.md` | `docs/` | Project narrative, data dictionaries, how-to. |
| Reports | `.html` | `reports/` and/or `site/reports/` | Rendered Quarto and Jupyter HTML. |
| Notebooks (source) | `.ipynb`, `.qmd` | `python/`, `r/` | Reproducible analysis; not always viewable on all static hosts. |
| Notebooks (rendered) | `.html` | `reports/`, `site/` | Same content as HTML for browser viewing. |
| Database | `.sqlite` | `warehouse/` | Single file; link for download or use in-browser SQL tools if desired. |
| Schema | `.sql` | `warehouse/schema.sql`, `docs/` | DDL for transparency and reuse. |
| CSV extracts | `.csv` | `warehouse/` or `site/data/` | Key tables exported for those who cannot open SQLite. |

## Messy raw formats we emulate (teaching / realism)

| Format | Path pattern | Intent |
|--------|--------------|--------|
| API-like JSON | `raw/api/*.json` | Nested fields, missing keys, inconsistent types. |
| Logs | `raw/logs/*.log`, `*.txt` | Timestamps, duplicates, partial lines. |
| CSV variants | `raw/vendor/*.csv`, `*.tsv` | Delimiters, encodings, mixed date formats. |
| Excel | `raw/vendor/*.xlsx` | Merged headers, multiple sheets, footnotes. |
| Human docs | `raw/notes/*.md` | Unstructured campaign notes to be parsed. |
| Zipped drops | `raw/drops/*.zip` | Simulated vendor delivery. |

## Static site copy (`site/`)

For portfolio deployment, we will (in pipeline or script):

- Copy or symlink: `reports/*.html` → `site/reports/`
- Copy: `warehouse/*.csv`, `schema.sql`, optionally `*.sqlite` → `site/data/`
- Copy: `docs/*.md` (or rendered HTML) → `site/docs/` as needed

All file types above are browser-friendly (CSV download, HTML view, MD often rendered by static generators).
