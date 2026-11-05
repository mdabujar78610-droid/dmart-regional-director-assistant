"""Acceptance checks for Part A. Run: python scripts/run_acceptance.py"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, ANALYSIS = ROOT / "data", ROOT / "analysis"
errors = []
def check(ok, message):
    if not bool(ok): errors.append(message)
def close(actual, expected, tol=0.01):
    return abs(float(actual) - expected) <= tol

required = [DATA/"store_daily.csv", DATA/"inventory.csv", DATA/"feedback.csv",
            DATA/"store_daily_clean.csv", ANALYSIS/"cleaning_log.csv",
            ANALYSIS/"data_quality_report.md", ANALYSIS/"findings.md",
            ANALYSIS/"executive_summary.md"]
for p in required:
    check(p.exists(), f"Missing {p.relative_to(ROOT)}")

if not errors:
    raw = pd.read_csv(DATA/"store_daily.csv")
    inventory = pd.read_csv(DATA/"inventory.csv")
    feedback = pd.read_csv(DATA/"feedback.csv")
    clean = pd.read_csv(DATA/"store_daily_clean.csv")
    log = pd.read_csv(ANALYSIS/"cleaning_log.csv")

    check(raw.shape == (453, 9), f"Raw daily shape {raw.shape}; expected (453, 9)")
    check(raw.duplicated().sum() == 3, "Raw daily data should contain 3 exact duplicate rows")
    check(raw.footfall.isna().sum() == 4, "Raw daily data should contain 4 missing footfall values")
    check(raw.footfall.min() == -150, "Raw minimum footfall should be -150")
    check(raw.footfall.max() == 9800, "Raw maximum footfall should be 9800")
    check(inventory.shape == (40, 6), f"Inventory shape {inventory.shape}; expected (40, 6)")
    check(((inventory.stock_units < inventory.reorder_threshold).sum()) == 14, "Expected 14 inventory rows below reorder threshold")
    check(feedback.shape == (200, 6), f"Feedback shape {feedback.shape}; expected (200, 6)")
    check(feedback.rating.isna().sum() == 12, "Expected 12 missing feedback ratings")

    check(len(clean) == 450, f"Cleaned row count {len(clean)}; expected 450")
    check(not clean.isna().any().any(), "Cleaned data contains missing values")
    check((clean.footfall >= 0).all(), "Cleaned data contains negative footfall")
    expected_features = {"revenue_per_footfall", "marketing_efficiency", "achievement_pct",
                         "shortfall_inr", "weekend_flag", "performance_band"}
    check(expected_features.issubset(clean.columns), "One or more six required derived features are missing")

    check((log.rule == "negative_to_missing").sum() == 1, "Expected one negative_to_missing log row")
    check((log.rule == "iqr_cap").sum() == 2, "Expected two iqr_cap log rows")
    check((log.rule == "median_impute").sum() == 5, "Expected five median_impute log rows")
    neg = log[log.rule == "negative_to_missing"]
    check(len(neg) == 1 and neg.iloc[0].store == "Hyderabad" and neg.iloc[0].date == "2026-04-21" and close(neg.iloc[0].old_footfall, -150), "Negative-footfall log entry mismatch")
    caps = log[log.rule == "iqr_cap"].set_index(["store", "date"])
    for key, old, new in [(("Ahmedabad", "2026-05-26"), 9800, 2281.38),
                          (("Mumbai", "2026-04-09"), 6100, 2986.00)]:
        check(key in caps.index, f"Missing IQR cap log entry {key}")
        if key in caps.index:
            check(close(caps.loc[key, "old_footfall"], old), f"Wrong old value in IQR log {key}")
            check(close(caps.loc[key, "new_footfall"], new, 1.0), f"Wrong capped value in IQR log {key}")
    imputes = log[log.rule == "median_impute"].set_index(["store", "date"])
    expected_imputes = [(("Mumbai", "2026-04-30"), 2386.0),
                        (("Pune", "2026-04-12"), 1509.5),
                        (("Pune", "2026-05-17"), 1509.5),
                        (("Hyderabad", "2026-04-21"), 2216.0),
                        (("Bengaluru", "2026-06-10"), 2065.0)]
    for key, value in expected_imputes:
        check(key in imputes.index, f"Missing median-imputation log entry {key}")
        if key in imputes.index:
            check(close(imputes.loc[key, "new_footfall"], value), f"Wrong imputed value for {key}")

    pune = clean[(clean.store == "Pune") & (clean.date == "2026-05-16")]
    check(len(pune) == 1, "Pune 2026-05-16 row not found exactly once")
    if len(pune) == 1:
        row = pune.iloc[0]
        check(close(row.achievement_pct, 74.59) and row.performance_band == "Poor" and row.weekend_flag == "Yes", "Pune 2026-05-16 feature check failed")
        check(close(row.revenue_per_footfall, 396.77) and close(row.marketing_efficiency, 18.12), "Pune 2026-05-16 ratio check failed")
    mumbai = clean[(clean.store == "Mumbai") & (clean.date == "2026-05-21")]
    check(len(mumbai) == 1, "Mumbai 2026-05-21 row not found exactly once")
    if len(mumbai) == 1:
        row = mumbai.iloc[0]
        check(close(row.achievement_pct, 107.99) and row.performance_band == "Excellent" and row.weekend_flag == "No", "Mumbai 2026-05-21 feature check failed")

if errors:
    print("PART A ACCEPTANCE CHECKS FAILED")
    for error in errors: print(f"- {error}")
    raise SystemExit(1)
print("PART A ACCEPTANCE CHECKS PASSED")
