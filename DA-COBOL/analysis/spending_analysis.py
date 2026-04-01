"""
Load COBOL-generated transactions.csv (no header), clean padded fields,
and summarize spending for portfolio screenshots.

Run from repo root:
  python DA-COBOL/analysis/spending_analysis.py

Or from DA-COBOL:
  python analysis/spending_analysis.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Optional charts (saves PNGs for README / portfolio)
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

COLS = [
    "txn_id",
    "account_id",
    "txn_date",
    "txn_type",
    "amount",
    "balance_after",
    "merchant",
    "category",
]

STRING_COLS = [
    "account_id",
    "txn_date",
    "txn_type",
    "merchant",
    "category",
]


def default_csv_path() -> Path:
    here = Path(__file__).resolve().parent
    return here.parent / "data" / "transactions.csv"


def load_transactions(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        csv_path,
        header=None,
        names=COLS,
        dtype=str,
        encoding="utf-8",
        skip_blank_lines=True,
    )
    for c in STRING_COLS:
        df[c] = df[c].str.strip()
    df["txn_id"] = df["txn_id"].str.strip().astype(int)
    df["amount"] = pd.to_numeric(df["amount"].str.replace(",", "", regex=False))
    df["balance_after"] = pd.to_numeric(df["balance_after"].str.replace(",", "", regex=False))
    df["txn_date"] = pd.to_datetime(df["txn_date"], format="%Y-%m-%d")
    return df


def spending_subset(df: pd.DataFrame) -> pd.DataFrame:
    """Outflows used for habit-style analysis (exclude pure deposits)."""
    mask = df["txn_type"].isin(["PURCHASE", "WITHDRAWAL"])
    return df.loc[mask].copy()


def print_summary(df: pd.DataFrame, spend: pd.DataFrame) -> None:
    print("=== All transactions ===")
    print(df.to_string(index=False))
    print()

    print("=== Spending rows (PURCHASE + WITHDRAWAL) ===")
    if spend.empty:
        print("(none)")
    else:
        print(spend[["txn_id", "txn_type", "amount", "merchant", "category"]].to_string(index=False))
    print()

    total_out = spend["amount"].sum()
    print(f"Total outflows (purchases + withdrawals): {total_out:,.2f}")
    print()

    by_cat = spend.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    print("=== Spend by category (outflows only) ===")
    print(by_cat.to_string(index=False))
    print()

    by_merch = spend.groupby("merchant", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    print("=== Spend by merchant (outflows only) ===")
    print(by_merch.to_string(index=False))


def save_charts(spend: pd.DataFrame, out_dir: Path) -> None:
    if plt is None:
        print("matplotlib not installed; skipping chart PNGs. pip install matplotlib")
        return
    out_dir.mkdir(parents=True, exist_ok=True)

    if spend.empty:
        return

    by_cat = spend.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    by_cat.plot(kind="bar", ax=ax, color="#2563eb")
    ax.set_title("Outflows by category")
    ax.set_ylabel("Amount")
    ax.set_xlabel("Category")
    fig.tight_layout()
    p1 = out_dir / "spend_by_category.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    print(f"Wrote {p1}")

    by_m = spend.groupby("merchant")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    by_m.plot(kind="barh", ax=ax, color="#0d9488")
    ax.set_title("Outflows by merchant")
    ax.set_xlabel("Amount")
    fig.tight_layout()
    p2 = out_dir / "spend_by_merchant.png"
    fig.savefig(p2, dpi=120)
    plt.close(fig)
    print(f"Wrote {p2}")


def main() -> int:
    csv_path = default_csv_path()
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1]).resolve()

    if not csv_path.is_file():
        print(f"Missing CSV: {csv_path}", file=sys.stderr)
        return 1

    df = load_transactions(csv_path)
    spend = spending_subset(df)
    print_summary(df, spend)

    charts_dir = Path(__file__).resolve().parent.parent / "images" / "charts"
    save_charts(spend, charts_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
