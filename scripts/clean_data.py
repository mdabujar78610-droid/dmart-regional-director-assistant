"""Clean Part A daily store data. Run from the repository root."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
DATA.mkdir(exist_ok=True)
ANALYSIS.mkdir(exist_ok=True)

daily_path = DATA / "store_daily.csv"
if not daily_path.exists():
    raise FileNotFoundError(f"Missing {daily_path}; run python scripts/generate_data.py first")
df = pd.read_csv(daily_path)
original_rows = len(df)
df = df.drop_duplicates(keep="first").reset_index(drop=True)
duplicates_removed = original_rows - len(df)
log_rows = []

negative = df["footfall"] < 0
for _, row in df.loc[negative].iterrows():
    log_rows.append({"store": row["store"], "date": row["date"], "old_footfall": row["footfall"], "new_footfall": "", "rule": "negative_to_missing"})
df.loc[negative, "footfall"] = np.nan

stores = df["store"].unique()
bounds = {}
for store in stores:
    mask = df["store"] == store
    values = df.loc[mask, "footfall"].dropna()
    q1, q3 = values.quantile(.25), values.quantile(.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    bounds[store] = (lower, upper)
    cap_mask = mask & (df["footfall"] > upper)
    for idx in df.index[cap_mask]:
        old = df.at[idx, "footfall"]
        capped = float(Decimal(str(upper)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        df.at[idx, "footfall"] = capped
        log_rows.append({"store": store, "date": df.at[idx, "date"], "old_footfall": old, "new_footfall": capped, "rule": "iqr_cap"})

for store in stores:
    mask = df["store"] == store
    median = df.loc[mask, "footfall"].median()
    missing = mask & df["footfall"].isna()
    for idx in df.index[missing]:
        log_rows.append({"store": store, "date": df.at[idx, "date"], "old_footfall": "", "new_footfall": median, "rule": "median_impute"})
        df.at[idx, "footfall"] = median

df["revenue_per_footfall"] = (df["revenue_inr"] / df["footfall"]).round(2)
df["marketing_efficiency"] = (df["revenue_inr"] / df["marketing_spend_inr"]).round(2)
df["achievement_pct"] = (df["revenue_inr"] / df["daily_target_inr"] * 100).round(2)
df["shortfall_inr"] = (df["daily_target_inr"] - df["revenue_inr"]).round(2)
df["weekend_flag"] = np.where(pd.to_datetime(df["date"]).dt.dayofweek >= 5, "Yes", "No")
df["performance_band"] = np.select([df["achievement_pct"] >= 100, df["achievement_pct"] >= 75], ["Excellent", "Good"], default="Poor")

df.to_csv(DATA / "store_daily_clean.csv", index=False)
pd.DataFrame(log_rows, columns=["store", "date", "old_footfall", "new_footfall", "rule"]).to_csv(ANALYSIS / "cleaning_log.csv", index=False)
print(f"Rows: {original_rows} -> {len(df)}; duplicates removed: {duplicates_removed}")
print("IQR bounds:", bounds)
print("Wrote data/store_daily_clean.csv and analysis/cleaning_log.csv")
