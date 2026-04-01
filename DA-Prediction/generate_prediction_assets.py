from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BrandConfig:
    name: str
    base_inventory: float
    base_sell_through: float
    trend_inventory: float
    seasonality_strength: float
    noise_inventory: float
    noise_sales: float


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CHART_DIR = ROOT / "images" / "charts"


def build_month_index(periods: int = 36) -> pd.DatetimeIndex:
    today = date.today()
    current_month = pd.Timestamp(today.year, today.month, 1)
    return pd.date_range(end=current_month, periods=periods, freq="MS")


def generate_brand_frame(months: pd.DatetimeIndex, cfg: BrandConfig, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(months))
    seasonal = 1 + cfg.seasonality_strength * np.sin((2 * np.pi * idx / 12) - 0.8)
    trend = 1 + cfg.trend_inventory * idx
    inventory = cfg.base_inventory * seasonal * trend + rng.normal(0, cfg.noise_inventory, len(months))

    # Add occasional shocks to make data realistic and imperfect.
    shock_positions = [7, 14, 25, 31]
    for p in shock_positions:
        if p < len(months):
            inventory[p] = inventory[p] * rng.uniform(0.86, 1.16)

    inventory = np.maximum(inventory, cfg.base_inventory * 0.4)

    sell_through = cfg.base_sell_through + 0.045 * np.sin((2 * np.pi * idx / 12) + 0.35)
    sell_through += rng.normal(0, 0.028, len(months))
    sell_through = np.clip(sell_through, 0.38, 0.92)

    sales = inventory * sell_through + rng.normal(0, cfg.noise_sales, len(months))
    sales = np.clip(sales, inventory * 0.34, inventory * 0.96)

    return pd.DataFrame(
        {
            f"{cfg.name}_inventory": np.round(inventory, 2),
            f"{cfg.name}_sales": np.round(sales, 2),
        },
        index=months,
    )


def add_metrics(df: pd.DataFrame, brands: list[str]) -> pd.DataFrame:
    out = df.copy()
    for brand in brands:
        inv_col = f"{brand}_inventory"
        sales_col = f"{brand}_sales"
        pct_col = f"{brand}_pct_sold"
        out[pct_col] = (out[sales_col] / out[inv_col]) * 100

        out[f"{brand}_pct_sold_mom_change_pp"] = out[pct_col].diff()
        out[f"{brand}_pct_sold_yoy_change_pp"] = out[pct_col].diff(12)
        out[f"{brand}_inventory_mom_change_pct"] = out[inv_col].pct_change() * 100
        out[f"{brand}_inventory_yoy_change_pct"] = out[inv_col].pct_change(12) * 100
        out[f"{brand}_sales_mom_change_pct"] = out[sales_col].pct_change() * 100
        out[f"{brand}_sales_yoy_change_pct"] = out[sales_col].pct_change(12) * 100

    inventory_cols = [f"{b}_inventory" for b in brands]
    sales_cols = [f"{b}_sales" for b in brands]
    out["total_inventory"] = out[inventory_cols].sum(axis=1)
    out["total_sales"] = out[sales_cols].sum(axis=1)
    out["total_pct_sold"] = (out["total_sales"] / out["total_inventory"]) * 100
    out["total_pct_sold_mom_change_pp"] = out["total_pct_sold"].diff()
    out["total_pct_sold_yoy_change_pp"] = out["total_pct_sold"].diff(12)
    out["total_inventory_mom_change_pct"] = out["total_inventory"].pct_change() * 100
    out["total_inventory_yoy_change_pct"] = out["total_inventory"].pct_change(12) * 100
    out["total_sales_mom_change_pct"] = out["total_sales"].pct_change() * 100
    out["total_sales_yoy_change_pct"] = out["total_sales"].pct_change(12) * 100

    return out.round(2)


def build_forecast(df: pd.DataFrame) -> pd.DataFrame:
    latest_month = df.index.max()
    future_months = pd.date_range(start=latest_month + pd.offsets.MonthBegin(1), periods=2, freq="MS")

    recent_yoy = df["total_sales_yoy_change_pct"].tail(12).dropna()
    avg_yoy = recent_yoy.mean() if not recent_yoy.empty else 0.0
    recent_sell_through = df["total_pct_sold"].tail(6).mean()

    last_sales = df["total_sales"].iloc[-1]
    forecast_sales = []
    for step in range(2):
        growth_factor = 1 + (avg_yoy / 100.0) * (0.65 + 0.1 * step)
        if step == 0:
            next_sales = last_sales * growth_factor
        else:
            next_sales = forecast_sales[-1] * growth_factor
        forecast_sales.append(next_sales)

    base_df = pd.DataFrame({"month": future_months, "forecast_total_sales": np.round(forecast_sales, 2)})
    base_df["implied_inventory_order"] = np.round(base_df["forecast_total_sales"] / (recent_sell_through / 100.0), 2)
    base_df["low_case_sales_minus_10pct"] = np.round(base_df["forecast_total_sales"] * 0.9, 2)
    base_df["high_case_sales_plus_8pct"] = np.round(base_df["forecast_total_sales"] * 1.08, 2)
    return base_df


def create_charts(df: pd.DataFrame, brands: list[str], forecast_df: pd.DataFrame) -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df.index, df["total_inventory"], label="Total inventory", linewidth=2.2)
    ax.plot(df.index, df["total_sales"], label="Total sales", linewidth=2.2)
    ax.set_title("Total Inventory vs Sales (36 months)")
    ax.set_ylabel("Value")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "total_inventory_vs_sales.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    for b in brands:
        ax.plot(df.index, df[f"{b}_pct_sold"], linewidth=2, label=f"{b} % sold")
    ax.set_title("Sell-through Percentage by Brand")
    ax.set_ylabel("% inventory sold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "brand_pct_sold_trends.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.5, 5))
    ax.plot(df.index, df["total_sales"], label="Historical total sales", linewidth=2.1)
    ax.plot(forecast_df["month"], forecast_df["forecast_total_sales"], label="Forecast total sales", linewidth=2.1, marker="o")
    ax.fill_between(
        forecast_df["month"],
        forecast_df["low_case_sales_minus_10pct"],
        forecast_df["high_case_sales_plus_8pct"],
        color="#93c5fd",
        alpha=0.3,
        label="Scenario band",
    )
    ax.set_title("Two-Month Sales Forecast with Scenario Band")
    ax.set_ylabel("Sales value")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "forecast_with_scenario_band.png", dpi=130)
    plt.close(fig)


def build_insights(df: pd.DataFrame, brands: list[str], forecast_df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]
    best_brand = max(brands, key=lambda b: latest[f"{b}_pct_sold"])
    weakest_brand = min(brands, key=lambda b: latest[f"{b}_pct_sold"])
    forecast_serializable = forecast_df.copy()
    forecast_serializable["month"] = forecast_serializable["month"].dt.strftime("%Y-%m")

    insight = {
        "current_month": df.index.max().strftime("%B %Y"),
        "total_inventory": round(float(latest["total_inventory"]), 2),
        "total_sales": round(float(latest["total_sales"]), 2),
        "total_pct_sold": round(float(latest["total_pct_sold"]), 2),
        "best_brand_by_pct_sold": best_brand,
        "best_brand_pct_sold": round(float(latest[f"{best_brand}_pct_sold"]), 2),
        "weakest_brand_by_pct_sold": weakest_brand,
        "weakest_brand_pct_sold": round(float(latest[f"{weakest_brand}_pct_sold"]), 2),
        "average_total_pct_sold_12m": round(float(df["total_pct_sold"].tail(12).mean()), 2),
        "forecast_rows": forecast_serializable.to_dict(orient="records"),
    }
    return insight


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    months = build_month_index(36)
    configs = [
        BrandConfig("a_brand", 142000, 0.64, 0.0044, 0.16, 7200, 3900),
        BrandConfig("b_brand", 108000, 0.60, 0.0032, 0.12, 6200, 3400),
        BrandConfig("c_brand", 92000, 0.57, 0.0024, 0.10, 5800, 3200),
    ]

    brand_frames = [generate_brand_frame(months, cfg, seed=2300 + i * 101) for i, cfg in enumerate(configs)]
    base_df = pd.concat(brand_frames, axis=1)
    full_df = add_metrics(base_df, [cfg.name for cfg in configs])
    full_df = full_df.reset_index(names="month")
    full_df["month"] = full_df["month"].dt.strftime("%Y-%m")

    full_df.to_excel(DATA_DIR / "inventory_sales_source.xlsx", index=False)
    full_df.to_csv(DATA_DIR / "inventory_sales_source.csv", index=False)

    history = full_df.copy()
    history["month"] = pd.to_datetime(history["month"])
    history = history.set_index("month")
    forecast_df = build_forecast(history)
    forecast_df.to_csv(DATA_DIR / "forecast_2_months.csv", index=False)

    create_charts(history, [cfg.name for cfg in configs], forecast_df)
    insights = build_insights(history, [cfg.name for cfg in configs], forecast_df)
    (DATA_DIR / "insights.json").write_text(json.dumps(insights, indent=2), encoding="utf-8")

    print("Generated:")
    print("- DA-Prediction/data/inventory_sales_source.xlsx")
    print("- DA-Prediction/data/inventory_sales_source.csv")
    print("- DA-Prediction/data/forecast_2_months.csv")
    print("- DA-Prediction/data/insights.json")
    print("- DA-Prediction/images/charts/*.png")


if __name__ == "__main__":
    main()
