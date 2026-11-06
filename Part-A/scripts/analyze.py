"""Part A store performance analysis. Writes analysis/findings.md."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
CLEAN_PATH = DATA / "store_daily_clean.csv"
RAW_PATH = DATA / "store_daily.csv"

if not CLEAN_PATH.exists():
    raise FileNotFoundError("Missing Part-A/data/store_daily_clean.csv; run python Part-A/scripts/clean_data.py first")
if not RAW_PATH.exists():
    raise FileNotFoundError("Missing Part-A/data/store_daily.csv; run python Part-A/scripts/generate_data.py first")

df = pd.read_csv(CLEAN_PATH)
required = {"store", "date", "revenue_inr", "footfall", "stockout_hours",
            "achievement_pct", "performance_band"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Cleaned dataset is missing required columns: {sorted(missing)}")

rows = []
for store, group in df.groupby("store"):
    rows.append({
        "store": store,
        "mean_daily_revenue_inr": group["revenue_inr"].mean(),
        "mean_footfall": group["footfall"].mean(),
        "mean_stockout_hours": group["stockout_hours"].mean(),
        "revenue_per_footfall": group["revenue_inr"].sum() / group["footfall"].sum(),
        "mean_achievement_pct": group["achievement_pct"].mean(),
        "poor_days": int((group["performance_band"] == "Poor").sum()),
    })
summary = pd.DataFrame(rows).sort_values("store")
all_row = {
    "store": "All stores",
    "mean_daily_revenue_inr": df["revenue_inr"].mean(),
    "mean_footfall": df["footfall"].mean(),
    "mean_stockout_hours": df["stockout_hours"].mean(),
    "revenue_per_footfall": df["revenue_inr"].sum() / df["footfall"].sum(),
    "mean_achievement_pct": df["achievement_pct"].mean(),
    "poor_days": int((df["performance_band"] == "Poor").sum()),
}
summary = pd.concat([summary, pd.DataFrame([all_row])], ignore_index=True)

ranked = summary[summary["store"] != "All stores"].sort_values(
    "mean_stockout_hours", ascending=False
)
all_stockout_corr = df["revenue_inr"].corr(df["stockout_hours"])
all_footfall_corr = df["revenue_inr"].corr(df["footfall"])
pune = df[df["store"] == "Pune"]
pune_stockout_corr = pune["revenue_inr"].corr(pune["stockout_hours"])
pune_footfall_corr = pune["revenue_inr"].corr(pune["footfall"])

raw = pd.read_csv(RAW_PATH).drop_duplicates(keep="first")
raw_baseline = raw.loc[raw["footfall"].notna(), ["revenue_inr", "footfall"]]
raw_footfall_corr = raw_baseline["revenue_inr"].corr(raw_baseline["footfall"])

def money(value):
    return f"{value:,.2f}"

def number(value):
    return f"{value:,.2f}"

lines = [
    "# Analysis Findings",
    "",
    f"## Store performance (cleaned {len(df)} store-days)",
    "",
    "| Store | Mean daily revenue (INR) | Mean footfall | Mean stockout hours | Revenue / footfall (INR) | Mean achievement (%) | Poor days |",
    "|---|---:|---:|---:|---:|---:|---:|",
]
for _, row in summary.iterrows():
    lines.append(
        f"| {row['store']} | {money(row['mean_daily_revenue_inr'])} | "
        f"{number(row['mean_footfall'])} | {number(row['mean_stockout_hours'])} | "
        f"{number(row['revenue_per_footfall'])} | {number(row['mean_achievement_pct'])} | "
        f"{int(row['poor_days'])} |"
    )

rank_text = ", ".join(
    f"{row['store']} {row['mean_stockout_hours']:.2f}"
    for _, row in ranked.iterrows()
)
pune_row = summary[summary["store"] == "Pune"].iloc[0]
hyderabad_row = summary[summary["store"] == "Hyderabad"].iloc[0]
lines += [
    "",
    "## Premise test: Is Pune the lowest-revenue store because of stockouts?",
    "",
    f"Mean stockout hours ranked highest to lowest: {rank_text}. "
    f"Pune ranks fourth of five, below the all-store mean of {all_row['mean_stockout_hours']:.2f} hours. "
    "The claim that Pune is the lowest-revenue store because it has the most stockouts is "
    "**not supported by these data**. Pune has the lowest mean daily revenue and "
    f"{int(pune_row['poor_days'])} Poor days, but it does not have the highest mean stockout hours.",
    "",
    "## Correlations",
    "",
    "| Scope | Revenue vs stockout hours | Revenue vs footfall |",
    "|---|---:|---:|",
    f"| All stores ({len(df)} cleaned rows) | {all_stockout_corr:.3f} | {all_footfall_corr:.3f} |",
    f"| Pune only | {pune_stockout_corr:.3f} | {pune_footfall_corr:.3f} |",
    f"| Raw daily data, deduplicated and non-missing footfall ({len(raw_baseline)} rows; negatives and extremes retained) | — | {raw_footfall_corr:.3f} |",
    "",
    "The raw baseline correlation uses deduplicated raw data, excludes missing footfall only, "
    "and retains negative and extreme values. Correlation describes association; it does not establish causation.",
    "",
    "## Facts",
    "",
    f"- **Fact 1:** Pune's mean daily revenue is INR {money(pune_row['mean_daily_revenue_inr'])}, the lowest of the five stores.",
    f"- **Fact 2:** Pune records {int(pune_row['poor_days'])} Poor days; all other stores combined record "
    f"{int(summary.loc[summary['store'].isin(['Ahmedabad', 'Bengaluru', 'Hyderabad', 'Mumbai']), 'poor_days'].sum())}.",
    f"- **Fact 3:** Pune's mean stockout duration is {pune_row['mean_stockout_hours']:.2f} hours, "
    f"versus {hyderabad_row['mean_stockout_hours']:.2f} hours in Hyderabad.",
    f"- **Fact 4:** Revenue-footfall correlation is {all_footfall_corr:.3f} across cleaned store-days, "
    f"compared with {raw_footfall_corr:.3f} in the raw deduplicated non-missing baseline.",
    "",
    "## Insights",
    "",
    "- **Insight 1:** Pune's weak performance is not explained by having the most stockout hours; it ranks fourth on that measure.",
    "- **Insight 2:** Footfall is strongly associated with revenue in the cleaned data, but this association alone cannot explain why Pune has lower traffic or prove a causal mechanism.",
    "",
    "## Hypotheses (unconfirmed)",
    "",
    "- **Hypothesis 1 — Pune demand or catchment differences may reduce visits.** Unconfirmed; test with catchment demographics, local competition, store location, customer counts by hour, and local campaign reach.",
    "- **Hypothesis 2 — Pune's assortment, pricing, or execution may reduce conversion or basket value.** Unconfirmed; test with SKU-level sales, availability and stockout-by-SKU, prices, basket size, conversion rate, promotion history, and customer feedback by store.",
    "",
]
ANALYSIS.mkdir(exist_ok=True)
output_path = ANALYSIS / "findings.md"
output_path.write_text("\n".join(lines), encoding="utf-8")

print(summary.to_string(index=False, float_format=lambda value: f"{value:.2f}"))
print("\nStockout ranking (highest first):")
print(ranked[["store", "mean_stockout_hours"]].to_string(index=False))
print("\nCorrelations:")
print(f"All stores revenue-stockout: {all_stockout_corr:.3f}")
print(f"All stores revenue-footfall: {all_footfall_corr:.3f}")
print(f"Pune revenue-stockout: {pune_stockout_corr:.3f}")
print(f"Pune revenue-footfall: {pune_footfall_corr:.3f}")
print(f"Raw deduplicated revenue-footfall correlation: {raw_footfall_corr:.3f}")
print("Wrote Part-A/analysis/findings.md")
