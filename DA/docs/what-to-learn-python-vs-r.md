# What to learn from doing the same load in Python and R

We implement each pipeline (engagement, campaign spend, revenue) in **both** Python and R. Here’s what to notice so it actually teaches you something.

---

## 1. The pipeline is the same in both languages

In every script we do the same steps:

| Step | What it means |
|------|----------------|
| **Connect** | Open the SQLite database. |
| **Init** | Run schema + seed SQL so dimensions exist. |
| **Read** | Load the raw file (JSON or CSV). |
| **Clean** | Normalize dates, coerce types, handle missing/empty, optional FKs. |
| **Dedupe** (if needed) | One row per business key. |
| **Insert** | Write rows into the fact table. |

The **logic** doesn’t change with the language. If you can describe the pipeline in plain English, you can implement it in either language. That’s the main takeaway: **data loading is a repeatable recipe**, not magic.

---

## 2. Different syntax, same ideas

| Idea | Python | R |
|------|--------|---|
| **“Use this or that” (null coalesce)** | `x or y`, or `(r.get("date") or r.get("dt"))` | `x %\|\|% y` or custom `%||%` |
| **“Do this for every row”** | `for r in rows:` + dict access `r["key"]` | `vapply(events, function(e) ..., type)` or loop |
| **“Parse this date”** | `re.match(...)` or `datetime.strptime` | `as.Date(s, format = "%m/%d/%Y")` then `format(..., "%Y-%m-%d")` |
| **“Coerce to number, or missing”** | `try: return int(x)` / `float(x)` | `as.numeric(x)` (gives NA if invalid) |
| **“Empty string → null for DB”** | `s.strip() or None` | `if (nchar(s) == 0) NA_character_` |
| **Run a SQL file** | Read file, `conn.executescript(sql)` | Read file, split on `;`, `dbExecute(conn, stmt)` for each |

So when you read the Python script and then the R script for the **same** source, focus on: “Where do we read? Where do we clean? Where do we insert?” The mapping from “idea” to “syntax” is what you’re learning.

---

## 3. Structural differences that matter

- **Python:** You often work with **lists of dicts** (or lists of objects). One row = one dict; you loop and use `row["column"]`.
- **R:** You often work with a **data frame** (one table in memory). You use columns: `df$date`, `df[, "amount"]`, or vectorized functions over columns.

In our R loaders we sometimes build vectors with `vapply(...)` and then combine them into a data frame or loop by index. In Python we build a list of dicts and loop. **Same inputs and outputs**, different in-memory shape.

- **JSON in Python:** `json.load()` → nested dicts/lists; use `.get("key")` and handle missing keys.
- **JSON in R:** `jsonlite::read_json()` → nested lists; use `x$key` (missing key = `NULL`). We use `%||%` to turn NULL into a default.

---

## 4. What to do when you sit down to learn

1. **Pick one source** (e.g. revenue).
2. **Read the Python script** start to finish. Label in your head: “this is read,” “this is clean,” “this is insert.”
3. **Read the R script** for the same source. Find the **same** read / clean / insert sections.
4. **Compare one idea at a time:** e.g. “How does Python normalize the date? How does R do it?” Then “How does Python handle missing `campaign_id`? How does R?”
5. **Run both** from the project root and confirm the same row counts and same data in the warehouse.

You’re not learning “Python” and “R” in the abstract. You’re learning **one pipeline** in two forms so you can:
- Join a team that uses either language and still know what the code is doing.
- Port a pipeline from one language to the other later.
- Decide which language you prefer for “read → clean → insert” and use it confidently.

---

## 5. When to use which (in the real world)

- **Python:** Very common for pipelines, ML, and “one script that does everything.” Good when the rest of the stack is Python.
- **R:** Very common for stats, reporting (R Markdown/Quarto), and teams that live in R. Good when the rest of the stack is R.

In this project we do **both** so you see the same design in two syntaxes. In a job you’ll usually use one primary language; the point is that the **design** (schema, grain, cleaning steps) is what matters most, and that’s language-agnostic.
