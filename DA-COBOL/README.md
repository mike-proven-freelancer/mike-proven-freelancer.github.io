# DA-COBOL — Fictional bank sample

Small **GnuCOBOL** program writes **`data/transactions.csv`** (no header). **Python** (`analysis/spending_analysis.py`) loads the file, strips padded fields, and prints summaries; optional **matplotlib** charts go to **`images/charts/`**.

## Layout

- `cobol/bank_main.cob` — main program  
- `cobol/hello.cob` — compile smoke test  
- `data/transactions.csv` — generated transaction lines  
- `analysis/spending_analysis.py` — pandas + charts  
- `requirements.txt` — Python dependencies  

## Run (from this folder)

**COBOL:** `cobc -x cobol/bank_main.cob -o bank_main.exe` then `.\bank_main.exe` (creates or appends per your `OPEN` logic).

**Python:** `py -m pip install -r requirements.txt` then `py analysis\spending_analysis.py`.

Compiled `*.exe` files are local build artifacts; add them to `.gitignore` if you do not want them in git.
