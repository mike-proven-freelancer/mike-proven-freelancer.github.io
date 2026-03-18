"""
Phase 3 Task 1: Next-7-day clicks (engagement) — baseline backtest.

Teaching sample is sparse (one row per content on different days), so we aggregate
to **channel-level daily clicks** (BrightWave blog), build a contiguous date range,
and compare:
  - Baseline A: next 7 days total ≈ previous 7 days total (weekly persistence)
  - Baseline B: next 7 days total ≈ 7 × last observed daily clicks

Writes reports/phase-3/task1_clicks_backtest_metrics.csv and task1_clicks_daily_series.csv

Run: py python/phase3_task1_clicks_forecast.py
"""

import csv
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
OUT = PROJECT_ROOT / "reports" / "phase-3"


def parse_d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT date, SUM(clicks) AS clicks FROM fact_post_performance_daily GROUP BY date ORDER BY date"
    ).fetchall()
    conn.close()

    if not rows:
        print("No engagement data.")
        return

    by_date = {parse_d(d): int(c) for d, c in rows}
    d_min, d_max = min(by_date), max(by_date)
    # Contiguous calendar days (missing = 0 clicks that day)
    series = []
    d = d_min
    while d <= d_max:
        series.append((d.isoformat(), by_date.get(d, 0)))
        d += timedelta(days=1)

    with open(OUT / "task1_clicks_daily_series.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "channel_clicks"])
        w.writerows(series)

    n = len(series)
    if n < 14:
        # Single evaluation: first 7 days vs next 7 days (within range, pad tail with 0)
        first7 = sum(c for _, c in series[:7])
        # "Next" 7 calendar days after first week
        start_next = parse_d(series[6][0]) + timedelta(days=1)
        actual_next = 0
        for i in range(7):
            day = start_next + timedelta(days=i)
            actual_next += by_date.get(day, 0)
        pred_a = first7
        last_day = series[6][1] if len(series) >= 7 else series[-1][1]
        pred_b = 7 * last_day

        metrics = [
            ("baseline", "description", "value"),
            ("A", "predict_next_7d_equals_prev_7d_sum", pred_a),
            ("B", "predict_next_7d_equals_7x_last_day_clicks", pred_b),
            ("actual", "next_7d_channel_clicks_sum", actual_next),
            ("mae_A", "abs(pred_A - actual)", abs(pred_a - actual_next)),
            ("mae_B", "abs(pred_B - actual)", abs(pred_b - actual_next)),
            ("note", "sparse_sample_see_docs", 1),
        ]
        with open(OUT / "task1_clicks_backtest_metrics.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["metric", "detail", "value"])
            for row in metrics:
                w.writerow(row)
        print(f"Wrote {OUT / 'task1_clicks_daily_series.csv'} and task1_clicks_backtest_metrics.csv")
        print("See docs/phase3-task1-clicks-backtest.md for interpretation.")
        return

    # If we ever have 14+ days: rolling one-step weekly forecast
    preds_a, preds_b, actuals = [], [], []
    for i in range(7, n - 7):
        prev7 = sum(c for _, c in series[i - 7 : i])
        next7 = sum(c for _, c in series[i : i + 7])
        preds_a.append(prev7)
        preds_b.append(7 * series[i - 1][1])
        actuals.append(next7)
    mae_a = sum(abs(a - b) for a, b in zip(preds_a, actuals)) / len(actuals)
    mae_b = sum(abs(a - b) for a, b in zip(preds_b, actuals)) / len(actuals)
    with open(OUT / "task1_clicks_backtest_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "detail", "value"])
        w.writerow(["n_eval_points", "rolling_windows", len(actuals)])
        w.writerow(["mae_baseline_A", "prev7_sum", round(mae_a, 4)])
        w.writerow(["mae_baseline_B", "7x_yesterday", round(mae_b, 4)])
    print(f"Wrote metrics for {len(actuals)} evaluation points.")


if __name__ == "__main__":
    main()
