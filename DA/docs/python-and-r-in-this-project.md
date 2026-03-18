# What R is, and how we use Python and R in this project

## What is R?

**R** is a programming language built for **statistics, data manipulation, and visualization**. It’s been around for decades and is widely used in research, biostatistics, economics, and data analysis.

- **Typical uses:** Cleaning and reshaping data (e.g. with the tidyverse: dplyr, tidyr), running statistical models, making plots (e.g. ggplot2), and writing reports (R Markdown, Quarto) that mix text, code, and outputs.
- **Strengths:** Very concise syntax for “do this by group” or “filter then summarize”; lots of packages for specific statistical methods; publication-quality graphics; reproducible reports (one file → HTML/PDF).
- **Compared to Python:** Python is more general-purpose and dominates in ML pipelines and production systems. R is often the tool of choice when the main job is “analyze this dataset, run some models, and write a report.” Many teams use **both**: Python for ingestion and ML, R for stats and reporting (or the other way around).

In this project we use **both** so you can see the same workflow in two languages and learn when each is handy.

---

## Can R load data into SQLite?

**Yes.** R can:

- Connect to SQLite (and other databases) using packages like **DBI** and **RSQLite**.
- Run SQL (CREATE TABLE, INSERT, SELECT, etc.) and read query results into R data frames.
- Read and write CSV, JSON, Excel, and other file formats.

So **loading** (read raw → clean → insert into warehouse) is something we do in **both** Python and R. We’ll load the same source (e.g. engagement JSON) with Python first, then with R, so you can compare the steps and the code.

---

## How we use Python and R in this project

| Task | Python | R |
|------|--------|---|
| **Load raw data into the warehouse** | Yes — scripts (or notebooks) that read raw files, clean, and insert into SQLite. | Yes — same. We do the first source (engagement) in both so you can learn both. |
| **Run the pipeline** (init DB, seed dimensions, load each source) | Yes. | Yes — same pipeline, same schema, same result. |
| **Phase 3: analysis, backtests, reports** | Yes — notebooks, models, visualizations. | Yes — same analyses and reports (e.g. Quarto), so you see both languages. |

So we don’t “save R for Phase 3.” We use R for loading too. If a client or job asks for “Python and data analysis libraries,” showing the same ETL and analysis in both Python and R is a strong portfolio piece.

---

## Summary

- **Loading** = code (Python or R) that reads raw data, cleans/normalizes it, and inserts it into the warehouse (SQLite) in the right tables and columns.
- **R** can do that. We’ll do the first source (engagement → `fact_post_performance_daily`) in Python, then again in R, with comments so you can compare.
- **R** is also used later for analysis and reporting; we’ll keep doing key tasks in both languages where it helps you learn.
