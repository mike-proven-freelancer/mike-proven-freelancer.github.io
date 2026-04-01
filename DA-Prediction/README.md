# DA-Prediction

This folder holds all non-HTML code and data for Project 03.

## Goal

Create a single-source monthly dataset (36 rows, one row per month) for three brands and derive:

- inventory and sales by brand (`a_brand`, `b_brand`, `c_brand`)
- `% sold` by brand and total
- month-over-month (MoM) changes
- year-over-year (YoY, same-month-last-year) changes
- a simple 2-month forecast with scenario bounds

## Files

- `prediction-plan.md` - original planning notes
- `generate_prediction_assets.py` - pandas + numpy generator and metric builder
- `requirements.txt` - Python dependencies
- `data/inventory_sales_source.xlsx` - primary dataset for the project
- `data/inventory_sales_source.csv` - CSV mirror of the XLSX source
- `data/forecast_2_months.csv` - simple 2-month projection
- `data/insights.json` - key values used for write-up/reference
- `images/charts/*.png` - generated figures used by portfolio pages

## Run

From repo root:

```powershell
py -m pip install -r DA-Prediction\requirements.txt
py DA-Prediction\generate_prediction_assets.py
```

## Notes

- Data is synthetic but intentionally messy and realistic (seasonality, trend, random noise, occasional shocks).
- Current month is dynamic based on run date, and the script always emits the latest 36-month window.
