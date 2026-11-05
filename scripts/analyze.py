"""Part A store performance analysis and premise test."""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
df = pd.read_csv(DATA / "store_daily_clean.csv")
required = {"revenue_inr", "footfall", "stockout_hours", "achievement_pct", "performance_band"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Cleaned dataset missing columns: {sorted(missing)}")

rows = []
for store, g in df.groupby("store"):
    rows.append({
        "store": store,
        "mean_daily_revenue_inr": g.revenue_inr.mean(),
        "mean_footfall": g.footfall.mean(),
        "mean_stockout_hours": g.stockout_hours.mean(),
        "revenue_per_footfall": g.revenue_inr.sum() / g.footfall.sum(),
        "mean_achievement_pct": g.achievement_pct.mean(),
        "poor_days": (g.performance_band == "Poor").sum(),
    })
summary = pd.DataFrame(rows).sort_values("store")
all_row = {
    "store": "All stores",
    "mean_daily_revenue_inr": df.revenue_inr.mean(),
    "mean_footfall": df.footfall.mean(),
    "mean_stockout_hours": df.stockout_hours.mean(),
    "revenue_per_footfall": df.revenue_inr.sum() / df.footfall.sum(),
    "mean_achievement_pct": df.achievement_pct.mean(),
    "poor_days": (df.performance_band == "Poor").sum(),
}
summary = pd.concat([summary, pd.DataFrame([all_row])], ignore_index=True)
ranked = summary[summary.store != "All stores"].sort_values("mean_stockout_hours", ascending=False)
print(summary.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
print("\nStockout ranking (highest first):")
print(ranked[["store", "mean_stockout_hours"]].to_string(index=False))
print("\nCorrelations:")
print("All stores revenue-stockout:", df.revenue_inr.corr(df.stockout_hours))
print("All stores revenue-footfall:", df.revenue_inr.corr(df.footfall))
pune = df[df.store == "Pune"]
print("Pune revenue-stockout:", pune.revenue_inr.corr(pune.stockout_hours))
print("Pune revenue-footfall:", pune.revenue_inr.corr(pune.footfall))

# Raw-data baseline: deduplicate, exclude missing footfall, retain negatives and extremes.
raw = pd.read_csv(DATA / "store_daily.csv").drop_duplicates(keep="first")
baseline = raw.loc[raw.footfall.notna(), ["revenue_inr", "footfall"]]
print("Raw deduplicated revenue-footfall correlation:", baseline.revenue_inr.corr(baseline.footfall))
