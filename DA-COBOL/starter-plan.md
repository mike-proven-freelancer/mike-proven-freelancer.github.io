# DA-COBOL Starter Plan

## Goal

Build a fictional bank sample in COBOL, export transactions to CSV, and analyze spending with Python for a portfolio story (legacy-style generation + modern analytics).

## Project layout (current)

```text
DA-COBOL/
  README.md
  starter-plan.md
  requirements.txt
  cobol/
    hello.cob
    bank_main.cob
  data/
    transactions.csv
  analysis/
    spending_analysis.py
  images/
    charts/
      spend_by_category.png
      spend_by_merchant.png
```

## Phase 2 — COBOL (done for this slice)

- Transaction types: deposit, withdrawal, purchase (with merchant/category in CSV).
- Output: `data/transactions.csv` (fixed-width fields, comma-separated; no header row).

## Phase 3 — Analytics (done for this slice)

- Load CSV in pandas; strip COBOL padding.
- Summarize outflows (purchases + withdrawals) by category and merchant.
- Optional bar charts in `images/charts/`.

## Portfolio

- Site: `project02.html`, `project02-details.html`, `blog02.html` (repo root).
- Optional: terminal screenshot of compile/run, COBOL source snippet, charts in README or pages.

## Milestones

- [x] GnuCOBOL installed; hello compiles.
- [x] `bank_main.cob` produces `transactions.csv`.
- [x] `spending_analysis.py` runs; charts generated.
- [x] Portfolio pages + this README.
