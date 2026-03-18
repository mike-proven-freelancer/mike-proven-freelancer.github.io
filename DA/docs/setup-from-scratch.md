# Development environment setup from scratch

Use this when you’re on a **new machine**, **reinstalled Windows**, or **forgot how you set things up**. Follow in order; each section ends with a **Check** so you know it worked.

**Workspace:** This project lives on `D:\` (e.g. `D:\Dual-Storage\Shared-AI\DA`). R and Python can be installed on `C:\`; they run scripts on D: just fine.

---

## 1. Install Python

1. Download: https://www.python.org/downloads/ (or Windows Store).
2. Run the installer. **Check “Add Python to PATH”** if the option appears.
3. **Check:** Open a **new** terminal (PowerShell or CMD) and run:
   ```powershell
   py --version
   ```
   You should see something like `Python 3.12.x` or `Python 3.13.x`.  
   If you get “open from Store” or nothing, use `py` instead of `python` in this project.

### Optional: notebooks and charts (Phase 3 / portfolio)

You do **not** put these on PATH. Run **once** in a terminal (from any folder):

```powershell
py -m pip install pandas matplotlib seaborn jupyter
```

That installs Python **libraries** into your Python install. After that, use **Jupyter** via Cursor/VS Code (“Create Jupyter Notebook”) or run `py -m jupyter lab` from the project folder.

---

## 2. Install R

1. Download R for Windows: https://cran.r-project.org/bin/windows/base/
2. Run the installer. Default options are fine.
3. **Optional:** Install RStudio: https://posit.co/download/rstudio-desktop/ (uses the R you just installed).
4. **Important:** Close and reopen Cursor (or at least **reload the window**: `Ctrl+Shift+P` → “Developer: Reload Window”). Then open a **new** terminal.
5. **Check:**
   ```powershell
   Rscript --version
   ```
   You should see e.g. `Rscript (R) version 4.x.x`.  
   If you get “not recognized”, add R to PATH:
   - Win → “environment variables” → Edit the system environment variables.
   - User variables → **Path** → Edit → New → add: `C:\Program Files\R\R-4.5.3\bin\x64` (use your R version folder name).
   - OK, then **close and reopen Cursor** and try again.

---

## 3. Install R packages (for this project)

Run **once** after R is installed. From project root in PowerShell:

```powershell
cd D:\Dual-Storage\Shared-AI\DA
Rscript -e "install.packages(c('DBI','RSQLite','jsonlite'), repos='https://cloud.r-project.org')"
```

Or in **RStudio**: open R Console and run:

```r
install.packages(c("DBI", "RSQLite", "jsonlite"), repos = "https://cloud.r-project.org")
```

**Check:** Run the R load script:

```powershell
Rscript r/load_engagement_to_warehouse.R
```

You should see: `Loaded 9 engagement rows into fact_post_performance_daily.`

---

## 4. Check Python (project scripts)

From project root:

```powershell
py python/load_engagement_to_warehouse.py
```

You should see: `Loaded 9 engagement rows into fact_post_performance_daily.`

---

## 5. SQLite (no separate install)

The project uses SQLite **inside** Python (`sqlite3`) and R (`RSQLite`). You don’t need to install SQLite yourself. Optional: install a **SQLite extension** in Cursor so you can open `warehouse/brightwave.sqlite` and run queries in the editor (see Extensions below).

---

## 6. Cursor / VS Code extensions (recommended)

These give you syntax highlighting, running code from the editor, and viewing the SQLite DB. The project has a **recommended extensions** list: when you open the repo in Cursor, you may see a prompt to install them. If not:

1. Press **Ctrl+Shift+X** (Extensions).
2. Install these (search by name or ID):

| What to search | Extension ID | Purpose |
|----------------|--------------|--------|
| **Python** | `ms-python.python` | Run/debug Python, Jupyter, linting |
| **R** | `REditorSupport.r` | Run R, syntax, R LSP |
| **SQLite** | `alexcvzz.vscode-sqlite` | Open `.sqlite` files, run queries |

**Check:** Open `warehouse/brightwave.sqlite` in the editor (with SQLite extension) and you should see tables. Open a `.py` or `.R` file and you should get language support.

---

## 7. Quick reference: run from project root

Always `cd` to the project root first (e.g. `D:\Dual-Storage\Shared-AI\DA`), then:

```powershell
# Python: load engagement into warehouse
py python/load_engagement_to_warehouse.py

# R: same load
Rscript r/load_engagement_to_warehouse.R
```

---

## If something breaks later

- **R not found again:** New terminal might not have PATH. Reload window (`Ctrl+Shift+P` → Reload Window) or add R to User PATH (step 2).
- **“No package called 'DBI'”:** Run the R package install again (step 3).
- **Python opens Store:** Use `py` instead of `python` for all commands in this project.

More detail and troubleshooting: [environment-setup.md](environment-setup.md).
