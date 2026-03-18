"""
Build portfolio static site: chart PNGs + project01.html + project01-details.html.

Run from project root:
  py python/build_portfolio_site.py

Requires: matplotlib (and optionally pandas; uses csv if needed).
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports" / "phase-3"
SITE = ROOT / "site"
ASSETS = SITE / "assets"


def read_csv_dicts(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ensure_style():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "font.family": "sans-serif",
        }
    )


def fig_content_clicks(rows):
    labels = [r["content_id"] + "\n" + (r["theme"][:18] + "…" if len(r.get("theme", "")) > 18 else r.get("theme", "")) for r in rows]
    clicks = [int(r["clicks"]) for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(labels[::-1], clicks[::-1], color="#1a365d")
    ax.set_xlabel("Total clicks (sample period)")
    ax.set_title("Content engagement by piece")
    plt.tight_layout()
    fig.savefig(ASSETS / "fig_content_clicks.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig_revenue_by_type(path):
    rows = read_csv_dicts(path)
    types = [r["revenue_type"] for r in rows]
    vals = [float(r["total_revenue"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#2c5282", "#3182ce", "#63b3ed"]
    ax.pie(vals, labels=types, autopct="%1.1f%%", colors=colors[: len(types)], startangle=90)
    ax.set_title("Revenue mix by type ($)")
    plt.tight_layout()
    fig.savefig(ASSETS / "fig_revenue_by_type.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig_newsletter(path):
    rows = read_csv_dicts(path)
    dates = [r["date"] for r in rows]
    open_rate = [float(r["open_rate"]) * 100 for r in rows]
    ctr = [float(r["ctr"]) * 100 for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(dates, open_rate, "o-", label="Open rate %", color="#1a365d")
    ax.plot(dates, ctr, "s--", label="CTR %", color="#c05621")
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=45, ha="right")
    ax.set_ylabel("Percent")
    ax.set_title("Newsletter engagement trend")
    ax.legend()
    plt.tight_layout()
    fig.savefig(ASSETS / "fig_newsletter_trend.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig_budget_rules(path):
    rows = read_csv_dicts(path)
    rules = []
    vals = []
    for r in rows:
        if r["rule"] in ("equal_split", "prop_prior_clicks", "efficiency_weighted"):
            rules.append(r["rule"].replace("_", " ").title())
            vals.append(float(r["total_simulated_or_actual_clicks"]))
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(rules))
    ax.bar(x, vals, color=["#4a5568", "#2b6cb0", "#2f855a"])
    ax.set_xticks(x)
    ax.set_xticklabels(["Equal split", "Prop. prior clicks", "Efficiency wtd."], rotation=15, ha="right")
    ax.set_ylabel("Total simulated clicks (eval weeks)")
    ax.set_title("Budget allocation rules — simulated outcome")
    plt.tight_layout()
    fig.savefig(ASSETS / "fig_budget_allocation.png", dpi=150, bbox_inches="tight")
    plt.close()


def fig_task1_actual_vs_pred():
    """Simple bar: actual next-7d channel clicks vs baselines."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    names = ["Baseline A\n(prev 7d sum)", "Baseline B\n(7× last day)", "Actual\nnext 7d"]
    vals = [4515, 4746, 1126]
    colors = ["#718096", "#a0aec0", "#1a365d"]
    ax.bar(names, vals, color=colors)
    ax.set_ylabel("Clicks")
    ax.set_title("Task 1 — channel clicks (teaching sample)")
    plt.tight_layout()
    fig.savefig(ASSETS / "fig_task1_backtest.png", dpi=150, bbox_inches="tight")
    plt.close()


def write_project01_html():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>BrightWave Media — Data Analytics Portfolio (Project 01)</title>
  <style>
    :root { --ink:#1a202c; --muted:#4a5568; --accent:#2b6cb0; --bg:#f7fafc; }
    * { box-sizing: border-box; }
    body { font-family: system-ui, Segoe UI, Roboto, sans-serif; color: var(--ink); background: var(--bg); margin: 0; line-height: 1.6; }
    header { background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); color: #fff; padding: 2.5rem 1.5rem; text-align: center; }
    header h1 { margin: 0 0 0.5rem; font-size: 1.75rem; }
    header p { margin: 0; opacity: 0.9; max-width: 640px; margin-inline: auto; }
    nav { background: #fff; border-bottom: 1px solid #e2e8f0; padding: 0.75rem 1rem; text-align: center; }
    nav a { color: var(--accent); margin: 0 1rem; font-weight: 600; }
    main { max-width: 920px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }
    section { background: #fff; border-radius: 8px; padding: 1.5rem 1.75rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
    h2 { color: #1a365d; margin-top: 0; font-size: 1.25rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }
    h3 { color: var(--muted); font-size: 1rem; margin: 1.25rem 0 0.5rem; }
    .figure { margin: 1rem 0; text-align: center; }
    .figure img { max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #e2e8f0; }
    .figure figcaption { font-size: 0.85rem; color: var(--muted); margin-top: 0.5rem; }
    .action-plan { background: #ebf8ff; border-left: 4px solid var(--accent); padding: 1rem 1.25rem; }
    .action-plan ol { margin: 0.5rem 0 0 1.25rem; }
    .action-plan li { margin: 0.5rem 0; }
    footer { text-align: center; padding: 2rem; color: var(--muted); font-size: 0.9rem; }
    footer a { color: var(--accent); }
  </style>
</head>
<body>
  <header>
    <h1>BrightWave Media — Analytics &amp; Decisions</h1>
    <p>Synthetic benchmark project: messy multi-source data → SQLite warehouse → KPIs, forecasts, and budget backtests. <strong>Project 01</strong> portfolio summary.</p>
  </header>
  <nav>
    <a href="#overview">Overview</a>
    <a href="#visuals">Visuals</a>
    <a href="#tasks">Analysis</a>
    <a href="#action">Action plan</a>
    <a href="project01-details.html">Data &amp; details →</a>
  </nav>
  <main>
    <section id="overview">
      <h2>Overview</h2>
      <p>This project mirrors an analyst role: <strong>ingest messy exports</strong> (JSON, CSV, TSV), <strong>load into a dimensional warehouse</strong>, then run <strong>engagement and revenue KPIs</strong>, a <strong>next-period clicks baseline</strong> (Task&nbsp;1), and a <strong>budget allocation backtest</strong> (Task&nbsp;2). All data is synthetic and safe for a public portfolio.</p>
      <p><a href="project01-details.html">Open the data &amp; methodology page</a> for file locations, schema, and how to reproduce results.</p>
    </section>

    <section id="visuals">
      <h2>Key visuals</h2>

      <h3>Content performance</h3>
      <figure class="figure">
        <img src="assets/fig_content_clicks.png" alt="Bar chart of clicks by content" />
        <figcaption>Total clicks by content piece in the loaded sample — retirement and budgeting themes lead.</figcaption>
      </figure>

      <h3>Revenue mix</h3>
      <figure class="figure">
        <img src="assets/fig_revenue_by_type.png" alt="Revenue by type pie chart" />
        <figcaption>Sponsorship and affiliate drive most revenue in this slice; subscriptions appear as smaller ticket events.</figcaption>
      </figure>

      <h3>Newsletter trend</h3>
      <figure class="figure">
        <img src="assets/fig_newsletter_trend.png" alt="Newsletter open rate and CTR over time" />
        <figcaption>Open rate and email CTR improve steadily — list hygiene and creative tests should continue.</figcaption>
      </figure>
    </section>

    <section id="tasks">
      <h2>Analysis highlights</h2>

      <h3>Task 1 — Next-period engagement (clicks)</h3>
      <p>Channel-level baseline forecast (teaching sample with sparse daily rows). Two simple baselines vs. actual “next week” sum.</p>
      <figure class="figure">
        <img src="assets/fig_task1_backtest.png" alt="Task 1 backtest bars" />
        <figcaption>Baselines overshoot when the following week has fewer active days in the sample — documented in the repo.</figcaption>
      </figure>

      <h3>Task 2 — Budget allocation</h3>
      <p>Compared allocating weekly spend across campaigns using <strong>equal split</strong>, <strong>proportional to prior-week clicks</strong>, and <strong>efficiency-weighted</strong> splits under a linear clicks-per-dollar model.</p>
      <figure class="figure">
        <img src="assets/fig_budget_allocation.png" alt="Budget allocation rule comparison" />
        <figcaption>Proportional-to-prior-clicks yielded the highest total simulated clicks across evaluation weeks in this benchmark.</figcaption>
      </figure>
    </section>

    <section id="action">
      <h2>Action plan</h2>
      <div class="action-plan">
        <ol>
          <li><strong>Content:</strong> Prioritize themes and titles similar to top click-getters (e.g. retirement, budgeting) for the next content calendar; A/B test headlines on FinTech and investing pieces to lift CTR.</li>
          <li><strong>Revenue:</strong> Protect sponsorship pipeline; grow affiliate placements on high-traffic posts. Tie subscription campaigns to <strong>CAMP-Q1-SUB</strong>-style programs and track cost per sub vs. LTV.</li>
          <li><strong>Newsletter:</strong> Maintain send quality — open rate and CTR are trending up; monitor unsubscribes and bounces; segment finance topics for relevance.</li>
          <li><strong>Paid spend:</strong> Pilot shifting budget toward last week’s stronger click performers before moving to full efficiency-weighted rules; validate with holdout weeks as more daily data arrives.</li>
          <li><strong>Data:</strong> Expand daily fact tables (more days per content/campaign) so per-content forecasts and allocation backtests stabilize; keep pipelines in Python and R for auditability.</li>
          <li><strong>Portfolio:</strong> Publish this page plus linked artifacts on GitHub Pages or your static host; point recruiters to <code>project01-details.html</code> for reproducibility.</li>
        </ol>
      </div>
    </section>
  </main>
  <footer>
    <p>Synthetic data · Educational portfolio · <a href="project01-details.html">Data &amp; details</a></p>
  </footer>
</body>
</html>
"""
    (SITE / "project01.html").write_text(html, encoding="utf-8")


def write_details_html():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Project 01 — Data &amp; methodology</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #1a202c; }
    h1 { color: #1a365d; }
    a { color: #2b6cb0; }
    code { background: #edf2f7; padding: 0.1rem 0.35rem; border-radius: 4px; }
    ul { padding-left: 1.25rem; }
    .back { margin-bottom: 1.5rem; }
  </style>
</head>
<body>
  <p class="back"><a href="project01.html">← Back to Project 01 main page</a></p>
  <h1>Data, files &amp; methodology</h1>
  <p>Paths are relative to the repository root (folder <code>DA/</code>). On GitHub, use the file browser from your repo.</p>

  <h2>Main narrative</h2>
  <ul>
    <li><a href="project01.html"><strong>project01.html</strong></a> — visuals and action plan</li>
  </ul>

  <h2>Warehouse &amp; schema</h2>
  <ul>
    <li><code>warehouse/brightwave.sqlite</code> — SQLite database (open with DB Browser, VS Code SQLite extension, or Python/R)</li>
    <li><code>warehouse/schema.sql</code> — table definitions</li>
    <li><code>warehouse/seed_dimensions.sql</code>, <code>seed_campaigns.sql</code> — dimension seeds</li>
  </ul>

  <h2>Raw sources (messy)</h2>
  <ul>
    <li><code>raw/api/</code> — engagement &amp; revenue JSON</li>
    <li><code>raw/vendor/</code> — campaign spend CSV, newsletter TSV</li>
    <li><code>raw/notes/</code>, <code>raw/logs/</code> — notes &amp; sample logs</li>
    <li><code>docs/raw-files-guide.md</code> — what each file contains</li>
  </ul>

  <h2>Phase 3 outputs (CSVs &amp; figures)</h2>
  <ul>
    <li><code>reports/phase-3/</code> — KPI extracts, Task 1 &amp; 2 metrics, revenue summaries</li>
    <li><code>site/assets/</code> — chart PNGs used on the main page</li>
  </ul>

  <h2>Documentation</h2>
  <ul>
    <li><code>docs/project-overview.md</code> — project story</li>
    <li><code>docs/evaluation-framework.md</code> — Task 1 &amp; 2 definitions</li>
    <li><code>docs/phase3-task1-clicks-backtest.md</code>, <code>docs/phase3-task2-budget-allocation.md</code></li>
    <li><code>docs/setup-from-scratch.md</code> — environment setup</li>
  </ul>

  <h2>Reproduce</h2>
  <ol>
    <li>Load warehouse: run <code>py python/load_*_to_warehouse.py</code> (or R equivalents) from repo root.</li>
    <li>KPIs: <code>py python/phase3_eda_kpis.py</code></li>
    <li>Task 1: <code>py python/phase3_task1_clicks_forecast.py</code></li>
    <li>Task 2: <code>py python/phase3_task2_budget_allocation.py</code></li>
    <li>This site: <code>py python/build_portfolio_site.py</code></li>
  </ol>

  <p><a href="project01.html">← Back to Project 01</a></p>
</body>
</html>
"""
    (SITE / "project01-details.html").write_text(html, encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    ensure_style()

    kpi_content = REPORTS / "kpi_content_performance.csv"
    kpi_news = REPORTS / "kpi_newsletter_daily.csv"
    rev_type = REPORTS / "revenue_by_type.csv"
    task2_sum = REPORTS / "task2_budget_allocation_summary.csv"

    if kpi_content.exists():
        rows = read_csv_dicts(kpi_content)
        rows.sort(key=lambda r: int(r["clicks"]), reverse=True)
        fig_content_clicks(rows)
    if rev_type.exists():
        fig_revenue_by_type(rev_type)
    if kpi_news.exists():
        fig_newsletter(kpi_news)
    if task2_sum.exists():
        fig_budget_rules(task2_sum)
    fig_task1_actual_vs_pred()

    write_project01_html()
    write_details_html()

    print("Built:", SITE / "project01.html")
    print("Built:", SITE / "project01-details.html")
    print("Assets:", ASSETS)


if __name__ == "__main__":
    main()
