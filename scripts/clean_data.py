"""Clean synthetic daily data without modifying the raw source CSV.

Run from the repository root:
    python scripts/clean_data.py
"""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
RAW_PATH = DATA / "store_daily.csv"
CLEAN_PATH = DATA / "store_daily_clean.csv"
LOG_PATH = ANALYSIS / "cleaning_log.csv"

LOG_COLUMNS = ["store", "date", "old_footfall", "new_footfall", "rule"]


def rounded(value):
    return float(
        Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def main():
    if not RAW_PATH.is_file():
        raise FileNotFoundError(
            f"Missing {RAW_PATH}; run python scripts/generate_data.py first"
        )

    DATA.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RAW_PATH)
    original_rows = len(df)
    log_rows = []

    required = {
        "date", "store_id", "store", "footfall", "revenue_inr",
        "daily_target_inr", "marketing_spend_inr", "stockout_hours",
        "discount_pct",
    }
    missing_columns = required - set(df.columns)
    if missing_columns:
        raise ValueError(f"Raw daily data is missing columns: {sorted(missing_columns)}")

    # Record each exact duplicate before removing it; retain the first copy.
    duplicate_mask = df.duplicated(keep="first")
    df = df.loc[~duplicate_mask].copy().reset_index(drop=True)
    duplicates_removed = original_rows - len(df)

    df["footfall"] = pd.to_numeric(df["footfall"], errors="coerce")
    negative_mask = df["footfall"] < 0
    for _, row in df.loc[negative_mask].iterrows():
        log_rows.append({
            "operation": "invalid_value_to_missing",
            "store": row["store"],
            "date": row["date"],
            "column": "footfall",
            "old_value": row["footfall"],
            "new_value": "",
            "old_footfall": row["footfall"],
            "new_footfall": "",
            "rule": "negative_to_missing",
            "details": "Negative footfall is invalid; treated as missing, not zero.",
        })
    df.loc[negative_mask, "footfall"] = np.nan

    # Apply the two-sided 1.5*IQR rule independently within each store.
    bounds = {}
    for store in sorted(df["store"].dropna().unique()):
        store_mask = df["store"] == store
        valid = df.loc[store_mask, "footfall"].dropna()
        if valid.empty:
            raise ValueError(f"No valid footfall values remain for store {store}.")
        q1 = float(valid.quantile(0.25))
        q3 = float(valid.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        bounds[store] = {"q1": q1, "q3": q3, "iqr": iqr,
                         "lower": lower, "upper": upper}

        for side, mask in (
            ("lower", store_mask & (df["footfall"] < lower)),
            ("upper", store_mask & (df["footfall"] > upper)),
        ):
            for idx in df.index[mask]:
                old = float(df.at[idx, "footfall"])
                new = rounded(lower if side == "lower" else upper)
                df.at[idx, "footfall"] = new
                log_rows.append({
                    "operation": "cap_outlier",
                    "store": store,
                    "date": df.at[idx, "date"],
                    "column": "footfall",
                    "old_value": old,
                    "new_value": new,
                    "old_footfall": old,
                    "new_footfall": new,
                    "rule": "iqr_cap",
                    "details": (
                        f"Two-sided IQR rule; capped to {side} bound. "
                        f"Lower bound {lower:.4f}; upper bound {upper:.4f}."
                    ),
                })

    # Impute all missing footfall (including the invalid negative) by store median.
    for store in sorted(df["store"].dropna().unique()):
        store_mask = df["store"] == store
        median = float(df.loc[store_mask, "footfall"].median())
        missing_mask = store_mask & df["footfall"].isna()
        for idx in df.index[missing_mask]:
            log_rows.append({
                "operation": "impute_missing",
                "store": store,
                "date": df.at[idx, "date"],
                "column": "footfall",
                "old_value": "",
                "new_value": median,
                "old_footfall": "",
                "new_footfall": median,
                "rule": "median_impute",
                "details": "Missing footfall filled with the median for the same store.",
            })
            df.at[idx, "footfall"] = median

    if df["footfall"].isna().any() or (df["footfall"] < 0).any():
        raise AssertionError("Footfall cleaning left missing or negative values.")

    derived = {
        "revenue_per_footfall": (
            "revenue_inr / footfall; rounded to 2 decimal places"
        ),
        "marketing_efficiency": (
            "revenue_inr / marketing_spend_inr; rounded to 2 decimal places; "
            "Part A only and prohibited from agent use"
        ),
        "achievement_pct": (
            "revenue_inr / daily_target_inr * 100; rounded to 2 decimal places"
        ),
        "shortfall_inr": (
            "daily_target_inr - revenue_inr; rounded to 2 decimal places"
        ),
        "weekend_flag": "Yes when date is Saturday or Sunday; otherwise No",
        "performance_band": (
            "Excellent when achievement_pct >= 100; Good when >= 75; "
            "otherwise Poor"
        ),
    }
    df["revenue_per_footfall"] = (
        df["revenue_inr"] / df["footfall"]
    ).round(2)
    df["marketing_efficiency"] = (
        df["revenue_inr"] / df["marketing_spend_inr"]
    ).round(2)
    df["achievement_pct"] = (
        df["revenue_inr"] / df["daily_target_inr"] * 100
    ).round(2)
    df["shortfall_inr"] = (
        df["daily_target_inr"] - df["revenue_inr"]
    ).round(2)
    df["weekend_flag"] = np.where(
        pd.to_datetime(df["date"]).dt.day_of_week >= 5, "Yes", "No"
    )
    df["performance_band"] = np.select(
        [df["achievement_pct"] >= 100, df["achievement_pct"] >= 75],
        ["Excellent", "Good"],
        default="Poor",
    )

    df.to_csv(CLEAN_PATH, index=False)
    pd.DataFrame(log_rows, columns=LOG_COLUMNS).to_csv(LOG_PATH, index=False)

    print(f"Raw rows: {original_rows}; duplicate rows removed: {duplicates_removed}")
    print(f"Cleaned shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print("Two-sided IQR bounds by store:")
    for store, values in bounds.items():
        print(
            f"  {store}: lower={values['lower']:.2f}, "
            f"upper={values['upper']:.2f}"
        )
    print(f"Cleaning operations logged: {len(log_rows)}")
    print(f"Wrote {CLEAN_PATH.relative_to(ROOT)} and {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
