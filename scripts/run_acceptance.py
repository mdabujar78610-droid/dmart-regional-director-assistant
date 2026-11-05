"""Validate Part A source data, cleaned output, logs and written reports."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, ANALYSIS = ROOT / "data", ROOT / "analysis"
errors = []

def check(condition, message):
    if not bool(condition):
        errors.append(message)

def close(actual, expected, tolerance=0.01):
    return abs(float(actual) - expected) <= tolerance

required_paths = [
    DATA / "store_daily.csv", DATA / "inventory.csv", DATA / "feedback.csv",
    DATA / "store_daily_clean.csv", ANALYSIS / "cleaning_log.csv",
    ANALYSIS / "data_quality_report.md", ANALYSIS / "findings.md",
    ANALYSIS / "executive_summary.md",
]
for path in required_paths:
    check(path.is_file(), f"Missing required file: {path.relative_to(ROOT)}")

def read_csv_if_present(path, label):
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        errors.append(f"Could not read {label}: {exc}")
        return None

raw = read_csv_if_present(DATA / "store_daily.csv", "raw daily data")
inventory = read_csv_if_present(DATA / "inventory.csv", "inventory data")
feedback = read_csv_if_present(DATA / "feedback.csv", "feedback data")
clean = read_csv_if_present(DATA / "store_daily_clean.csv", "cleaned daily data")
log = read_csv_if_present(ANALYSIS / "cleaning_log.csv", "cleaning log")

if raw is not None:
    check(raw.shape == (453, 9), f"Raw daily shape is {raw.shape}; expected (453, 9)")
    check(raw.duplicated().sum() == 3, "Raw daily data should contain 3 exact duplicate rows")
    check(raw["footfall"].isna().sum() == 4, "Raw daily data should contain 4 missing footfall values")
    check(raw["footfall"].min() == -150, "Raw minimum footfall should be -150")
    check(raw["footfall"].max() == 9800, "Raw maximum footfall should be 9800")

if inventory is not None:
    check(inventory.shape == (40, 6), f"Inventory shape is {inventory.shape}; expected (40, 6)")
    check((inventory["stock_units"] < inventory["reorder_threshold"]).sum() == 14,
          "Expected 14 inventory rows below reorder threshold")

if feedback is not None:
    check(feedback.shape == (200, 6), f"Feedback shape is {feedback.shape}; expected (200, 6)")
    check(feedback["rating"].isna().sum() == 12, "Expected 12 missing feedback ratings")

if clean is not None:
    check(len(clean) == 450, f"Cleaned row count is {len(clean)}; expected 450")
    check(not clean.isna().any().any(), "Cleaned data contains missing values")
    check((clean["footfall"] >= 0).all(), "Cleaned data contains negative footfall")
    expected_features = {
        "revenue_per_footfall", "marketing_efficiency", "achievement_pct",
        "shortfall_inr", "weekend_flag", "performance_band",
    }
    check(expected_features.issubset(clean.columns), "One or more required derived features are missing")
    if {"revenue_inr", "footfall", "marketing_spend_inr", "daily_target_inr", "date"}.issubset(clean.columns):
        check(close(clean["revenue_per_footfall"], clean["revenue_inr"] / clean["footfall"]).all(), 
              "Revenue-per-footfall values do not match source columns")
        check(close(clean["marketing_efficiency"], clean["revenue_inr"] / clean["marketing_spend_inr"]).all(),
              "Marketing-efficiency values do not match source columns")
        expected_achievement = clean["revenue_inr"] / clean["daily_target_inr"] * 100
        check(close(clean["achievement_pct"], expected_achievement).all(),
              "Achievement percentages do not match source columns")
        expected_weekend = pd.to_datetime(clean["date"]).dt.dayofweek.ge(5).map({True: "Yes", False: "No"})
        check((clean["weekend_flag"] == expected_weekend).all(), "Weekend flags do not match dates")
        expected_band = expected_achievement.ge(100).map({True: "Excellent", False: ""})
        expected_band = expected_band.mask(expected_achievement.between(75, 100, inclusive="left"), "Good")
        expected_band = expected_band.mask(expected_achievement.lt(75), "Poor")
        check((clean["performance_band"] == expected_band).all(), "Performance bands do not match achievement percentages")

if log is not None:
    check((log["rule"] == "negative_to_missing").sum() == 1, "Expected one negative_to_missing log row")
    check((log["rule"] == "iqr_cap").sum() == 2, "Expected two iqr_cap log rows")
    check((log["rule"] == "median_impute").sum() == 5, "Expected five median_impute log rows")
    negative = log[log["rule"] == "negative_to_missing"]
    check(len(negative) == 1 and negative.iloc[0]["store"] == "Hyderabad"
          and negative.iloc[0]["date"] == "2026-04-21"
          and close(negative.iloc[0]["old_footfall"], -150),
          "Negative-footfall log entry mismatch")
    caps = log[log["rule"] == "iqr_cap"].set_index(["store", "date"])
    expected_caps = [
        (("Ahmedabad", "2026-05-26"), 9800, 2281.38),
        (("Mumbai", "2026-04-09"), 6100, 2986.00),
    ]
    for key, old_value, new_value in expected_caps:
        check(key in caps.index, f"Missing IQR cap log entry {key}")
        if key in caps.index:
            check(close(caps.loc[key, "old_footfall"], old_value), f"Wrong old IQR value for {key}")
            check(close(caps.loc[key, "new_footfall"], new_value, 1.0), f"Wrong capped value for {key}")
    imputes = log[log["rule"] == "median_impute"].set_index(["store", "date"])
    expected_imputes = [
        (("Mumbai", "2026-04-30"), 2386.0),
        (("Pune", "2026-04-12"), 1509.5),
        (("Pune", "2026-05-17"), 1509.5),
        (("Hyderabad", "2026-04-21"), 2216.0),
        (("Bengaluru", "2026-06-10"), 2065.0),
    ]
    for key, value in expected_imputes:
        check(key in imputes.index, f"Missing median-imputation log entry {key}")
        if key in imputes.index:
            check(close(imputes.loc[key, "new_footfall"], value), f"Wrong imputed value for {key}")

if clean is not None and {"store", "date"}.issubset(clean.columns):
    pune = clean[(clean["store"] == "Pune") & (clean["date"] == "2026-05-16")]
    check(len(pune) == 1, "Pune 2026-05-16 row not found exactly once")
    if len(pune) == 1:
        row = pune.iloc[0]
        check(close(row["achievement_pct"], 74.59) and row["performance_band"] == "Poor"
              and row["weekend_flag"] == "Yes", "Pune 2026-05-16 feature check failed")
        check(close(row["revenue_per_footfall"], 396.77)
              and close(row["marketing_efficiency"], 18.12), "Pune 2026-05-16 ratio check failed")
    mumbai = clean[(clean["store"] == "Mumbai") & (clean["date"] == "2026-05-21")]
    check(len(mumbai) == 1, "Mumbai 2026-05-21 row not found exactly once")
    if len(mumbai) == 1:
        row = mumbai.iloc[0]
        check(close(row["achievement_pct"], 107.99) and row["performance_band"] == "Excellent"
              and row["weekend_flag"] == "No", "Mumbai 2026-05-21 feature check failed")

findings_path = ANALYSIS / "findings.md"
if findings_path.is_file():
    findings = findings_path.read_text(encoding="utf-8")
    check("Premise test" in findings and "not supported by these data" in findings,
          "Findings report is missing the premise-test conclusion")
    check("## Store performance" in findings and "## Correlations" in findings,
          "Findings report is missing required analysis sections")

summary_path = ANALYSIS / "executive_summary.md"
if summary_path.is_file():
    summary_text = summary_path.read_text(encoding="utf-8")
    word_count = len(summary_text.split())
    check(word_count <= 250, f"Executive summary has {word_count} words; maximum is 250")

if errors:
    print("PART A ACCEPTANCE CHECKS FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("PART A ACCEPTANCE CHECKS PASSED")
print(f"Validated {len(required_paths)} required files and all available data/report checks.")
