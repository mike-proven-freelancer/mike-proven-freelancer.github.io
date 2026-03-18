# Environment setup for data analytics (DA project)

**New machine or “how do I set this up again?”** → Use **[setup-from-scratch.md](setup-from-scratch.md)** for a full step-by-step checklist (Python, R, R packages, extensions, checks).

This page is a **quick reference** and **troubleshooting** supplement.

---

## What you need installed

| Tool | Purpose in this project | How to check |
|------|-------------------------|--------------|
| **Python** | Load raw → warehouse, analysis, notebooks | `py --version` (Windows) or `python3 --version` |
| **R** | Same loads + analysis in R; Quarto reports | `Rscript --version` (after install, may need PATH) |
| **SQLite** | Database for the warehouse | No separate install needed: Python has `sqlite3` built in; R uses `RSQLite`. Optional: [sqlite.org](https://sqlite.org/download.html) CLI for ad-hoc queries. |

---

## Current status (as of setup)

- **Python**: Use the **py launcher**: `py python/load_engagement_to_warehouse.py` from project root. If `python` opens the Store, use `py` instead.
- **R**: Install from [CRAN](https://cran.r-project.org/) (Windows: “Install R for the first time”). After install, R may not be on PATH until you **reload the workspace** or restart Cursor (see below). Workspace on **D:\** is fine; R can be installed on **C:\** and will run scripts in your D: project.
- **SQLite**: The project runs without a standalone SQLite CLI; Python/R talk to `warehouse/brightwave.sqlite` via libraries.

---

## R installed but “not found” (Windows)

If you installed R (and maybe RStudio) but the terminal says `Rscript` or `R` is not recognized:

1. **R is likely installed** (e.g. `C:\Program Files\R\R-4.5.3\bin\x64\`). The installer sometimes doesn’t add it to PATH, or the terminal was opened *before* install and still has the old PATH.
2. **Reload the workspace** so the integrated terminal gets a fresh environment:
   - **Cursor**: `Ctrl+Shift+P` → “Developer: Reload Window” (or close and reopen Cursor).
   - Then open a **new** terminal and try: `Rscript --version`.
3. **If it still fails**, add R to your **User** PATH manually:
   - Windows Settings → System → About → Advanced system settings → Environment Variables.
   - Under “User variables”, select **Path** → Edit → New → add: `C:\Program Files\R\R-4.5.3\bin\x64` (adjust version if yours is different).
   - OK out, then **reload Cursor** and open a new terminal.
4. **Temporary workaround** (no reload): run R by full path from project root:
   ```powershell
   & "C:\Program Files\R\R-4.5.3\bin\x64\Rscript.exe" r/load_engagement_to_warehouse.R
   ```
   Replace `R-4.5.3` with your version if different.

5. **If you see “there is no package called 'DBI'”**: R is running but the required packages aren’t installed. In RStudio (or R GUI) run: `install.packages(c("DBI", "RSQLite", "jsonlite"), repos = "https://cloud.r-project.org")`. Then run the load script again.

---

## Cursor / VS Code extensions (recommended)

The project has **recommended extensions** in `.vscode/extensions.json`. When you open this repo, Cursor may prompt you to install them. If not, open Extensions (`Ctrl+Shift+X`) and install:

| Extension | ID | What it does |
|-----------|-----|----------------|
| **Python** (Microsoft) | `ms-python.python` | Run/debug Python, Jupyter, linting |
| **R** (REditorSupport) | `REditorSupport.r` | Run R, syntax, R LSP |
| **SQLite** (alexcvzz) | `alexcvzz.vscode-sqlite` | Open `.sqlite` files, run queries in editor |

They are **not** required for scripts to run from the terminal, but they make editing and browsing the DB much easier.

---

## First-time R setup (if not installed)

See **[setup-from-scratch.md](setup-from-scratch.md)** section 2 (Install R) and section 3 (R packages). Summary: install R from CRAN → reload Cursor → install packages (`DBI`, `RSQLite`, `jsonlite`) → run `Rscript r/load_engagement_to_warehouse.R`.

---

## Run from project root

All commands assume your current directory is the project root (`DA/`):

```bash
# Python load (engagement → warehouse)
py python/load_engagement_to_warehouse.py

# R load (after R is installed)
Rscript r/load_engagement_to_warehouse.R
```
