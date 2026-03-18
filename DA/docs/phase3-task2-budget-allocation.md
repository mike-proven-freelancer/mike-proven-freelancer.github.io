# Phase 3 Task 2: Budget allocation backtest

## Goal

Given a **weekly budget** (we use that week’s **actual total spend** as \(W\)), compare how different **allocation rules** would perform if **clicks scaled linearly** with spend using the **previous week’s clicks-per-dollar** efficiency per campaign.

This matches the evaluation doc idea: *baseline vs. model-guided allocation*, simulated on historical windows.

## Campaigns

- `CAMP-Q1-PUSH` — content push  
- `CAMP-Q1-SUB` — subscription drive  

## Rules compared

| Rule | Allocation |
|------|------------|
| **Equal split** | Each campaign gets \(W/2\). |
| **Proportional to prior-week clicks** | Share of \(W\) ∝ prior week’s clicks per campaign. |
| **Efficiency-weighted (model-style)** | Share of \(W\) ∝ prior week’s **clicks / spend** (then renormalize). |

## Expected clicks (simulation)

For campaign \(c\), prior-week efficiency \(e_c = \text{clicks}_{c,t-1} / \max(\text{spend}_{c,t-1}, \varepsilon)\).

Allocated spend \(s_c\) sums to \(W\). Simulated clicks:

\[
\widehat{\text{clicks}} = \sum_c s_c \cdot e_c
\]

## Caveats

- **Linear scaling** is a teaching simplification.  
- If calendar weeks are **missing** between two batches of data, “prior week” is the **last week present in the data** before the current week (may be several weeks earlier).  
- Compare rules by **total simulated clicks** across evaluation weeks (higher = better under this model).

## Scripts

- `python/phase3_task2_budget_allocation.py`  
- `r/phase3_task2_budget_allocation.R`  

Outputs: `reports/phase-3/task2_budget_allocation_by_week.csv`, `task2_budget_allocation_summary.csv`
