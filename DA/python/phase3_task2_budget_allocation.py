"""
Phase 3 Task 2: Budget allocation backtest (two campaigns).

Uses prior-week clicks-per-dollar efficiency; allocates weekly budget W (actual total spend that week).

Run: py python/phase3_task2_budget_allocation.py
"""

import csv
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB = PROJECT_ROOT / "warehouse" / "brightwave.sqlite"
OUT = PROJECT_ROOT / "reports" / "phase-3"
EPS = 1e-6


def iso_week(d):
    y, w, _ = d.isocalendar()
    return (y, w)


def monday_of_iso_week(year, week):
    # Monday of ISO week
    jan4 = datetime(year, 1, 4).date()
    return jan4 + timedelta(weeks=week - 1) - timedelta(days=jan4.weekday())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT campaign_id, date, spend, clicks FROM fact_campaign_spend_daily"
    ).fetchall()
    conn.close()

    # (year, week) -> campaign -> {spend, clicks}
    agg = defaultdict(lambda: defaultdict(lambda: {"spend": 0.0, "clicks": 0}))
    for cid, ds, sp, cl in rows:
        d = datetime.strptime(ds, "%Y-%m-%d").date()
        yw = iso_week(d)
        agg[yw][cid]["spend"] += float(sp or 0)
        agg[yw][cid]["clicks"] += int(cl or 0)

    campaigns = sorted({cid for yw in agg for cid in agg[yw]})
    weeks = sorted(agg.keys())

    detail = []
    for i in range(1, len(weeks)):
        prev, cur = weeks[i - 1], weeks[i]
        W = sum(agg[cur][c]["spend"] for c in campaigns)
        if W < EPS:
            continue
        e = {}
        cl_prev = {}
        for c in campaigns:
            sp = max(agg[prev][c]["spend"], EPS)
            e[c] = agg[prev][c]["clicks"] / sp
            cl_prev[c] = agg[prev][c]["clicks"]
        tot_cl = sum(cl_prev.values()) or EPS

        # Equal split
        sim_equal = sum((W / len(campaigns)) * e[c] for c in campaigns)

        # Proportional to prior clicks
        sim_prop = sum((W * cl_prev[c] / tot_cl) * e[c] for c in campaigns)

        # Efficiency-weighted (normalize e)
        esum = sum(e[c] for c in campaigns) or EPS
        sim_eff = sum((W * e[c] / esum) * e[c] for c in campaigns)

        act_clicks = sum(agg[cur][c]["clicks"] for c in campaigns)

        y, w = cur
        detail.append(
            {
                "week_year": y,
                "week_iso": w,
                "week_start": monday_of_iso_week(y, w).isoformat(),
                "budget_W": round(W, 2),
                "actual_clicks_week": act_clicks,
                "sim_equal_split": round(sim_equal, 2),
                "sim_prop_prior_clicks": round(sim_prop, 2),
                "sim_efficiency_weighted": round(sim_eff, 2),
            }
        )

    path_detail = OUT / "task2_budget_allocation_by_week.csv"
    with open(path_detail, "w", newline="", encoding="utf-8") as f:
        if detail:
            w = csv.DictWriter(f, fieldnames=list(detail[0].keys()))
            w.writeheader()
            w.writerows(detail)

    # Summary: sum of simulated clicks across weeks (higher better under model)
    sums = defaultdict(float)
    for r in detail:
        sums["equal"] += r["sim_equal_split"]
        sums["prop_clicks"] += r["sim_prop_prior_clicks"]
        sums["efficiency"] += r["sim_efficiency_weighted"]
        sums["actual"] += r["actual_clicks_week"]

    best = max(
        [("equal_split", sums["equal"]), ("prop_prior_clicks", sums["prop_clicks"]), ("efficiency_weighted", sums["efficiency"])],
        key=lambda x: x[1],
    )
    path_sum = OUT / "task2_budget_allocation_summary.csv"
    with open(path_sum, "w", newline="", encoding="utf-8") as f:
        cw = csv.writer(f)
        cw.writerow(["rule", "total_simulated_or_actual_clicks", "notes"])
        cw.writerow(["equal_split", round(sums["equal"], 2), "sum over eval weeks"])
        cw.writerow(["prop_prior_clicks", round(sums["prop_clicks"], 2), "sum over eval weeks"])
        cw.writerow(["efficiency_weighted", round(sums["efficiency"], 2), "sum over eval weeks"])
        cw.writerow(["actual_total_clicks", round(sums["actual"], 2), "observed clicks those weeks (not simulated)"])
        cw.writerow(["best_rule_simulated", best[0], f"total={round(best[1], 2)}"])

    print(f"Wrote {path_detail} ({len(detail)} rows), {path_sum}")
    print(f"Best rule (simulated total clicks): {best[0]} = {best[1]:.2f}")


if __name__ == "__main__":
    main()
