"""Part A data and report acceptance checks. Run from the repository root."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, ANALYSIS = ROOT / "data", ROOT / "analysis"
errors = []


def check(condition, message):
    if isinstance(condition, pd.Series):
        condition = condition.all()
    if not bool(condition):
        errors.append(message)


def close(actual, expected, tolerance=0.01):
    difference = actual - expected
    if hasattr(difference, "abs"):
        return difference.abs().le(tolerance)
    return abs(float(difference)) <= tolerance


required_paths = [
    DATA / "store_daily.csv", DATA / "inventory.csv", DATA / "feedback.csv",
    DATA / "store_daily_clean.csv", ANALYSIS / "cleaning_log.csv",
    ANALYSIS / "data_quality_report.md", ANALYSIS / "findings.md",
    ANALYSIS / "executive_summary.md",
]
for path in required_paths:
    check(path.is_file(), f"Missing required file: {path.relative_to(ROOT)}")


def read_csv(path, label):
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        errors.append(f"Could not read {label}: {exc}")
        return None


raw = read_csv(DATA / "store_daily.csv", "raw daily data")
inventory = read_csv(DATA / "inventory.csv", "inventory")
feedback = read_csv(DATA / "feedback.csv", "feedback")
clean = read_csv(DATA / "store_daily_clean.csv", "cleaned daily data")
log = read_csv(ANALYSIS / "cleaning_log.csv", "cleaning log")

if raw is not None:
    check(raw.shape == (453, 9), f"Raw daily shape is {raw.shape}; expected (453, 9)")
    check(int(raw.duplicated().sum()) == 3, "Expected three exact raw daily duplicates")
    footfall = pd.to_numeric(raw["footfall"], errors="coerce")
    check(int(footfall.isna().sum()) == 4, "Expected four missing raw footfall values")
    check(int((footfall < 0).sum()) == 1, "Expected one negative raw footfall value")
    check(float(footfall.min()) == -150, "Raw minimum footfall should be -150")
    check(float(footfall.max()) == 9800, "Raw maximum footfall should be 9800")

if inventory is not None:
    check(inventory.shape == (40, 6), f"Inventory shape is {inventory.shape}; expected (40, 6)")
    check(int((inventory.stock_units < inventory.reorder_threshold).sum()) == 14,
          "Expected 14 inventory rows below reorder threshold")

if feedback is not None:
    check(feedback.shape == (200, 6), f"Feedback shape is {feedback.shape}; expected (200, 6)")
    check(int(feedback.rating.isna().sum()) == 12, "Expected 12 missing feedback ratings")

if clean is not None:
    check(clean.shape == (450, 15), f"Cleaned shape is {clean.shape}; expected (450, 15)")
    check(not clean.isna().any().any(), "Cleaned daily data contains missing values")
    check((clean.footfall >= 0).all(), "Cleaned daily data contains negative footfall")
    expected_features = {
        "revenue_per_footfall", "marketing_efficiency", "achievement_pct",
        "shortfall_inr", "weekend_flag", "performance_band",
    }
    check(expected_features.issubset(clean.columns), "One or more derived columns are missing")
    check(close(clean.revenue_per_footfall, clean.revenue_inr / clean.footfall).all(),
          "Revenue-per-footfall values do not match source columns")
    check(close(clean.marketing_efficiency, clean.revenue_inr / clean.marketing_spend_inr).all(),
          "Marketing-efficiency values do not match source columns")
    expected_achievement = clean.revenue_inr / clean.daily_target_inr * 100
    check(close(clean.achievement_pct, expected_achievement).all(),
          "Achievement percentages do not match source columns")
    check(close(clean.shortfall_inr, clean.daily_target_inr - clean.revenue_inr).all(),
          "Shortfall values do not match source columns")
    expected_weekend = pd.to_datetime(clean.date).dt.day_of_week.ge(5).map(
        {True: "Yes", False: "No"}
    )
    check((clean.weekend_flag == expected_weekend).all(), "Weekend flags do not match dates")
    expected_band = expected_achievement.ge(100).map({True: "Excellent", False: ""})
    expected_band = expected_band.mask(expected_achievement.ge(75) & expected_achievement.lt(100), "Good")
    expected_band = expected_band.mask(expected_achievement.lt(75), "Poor")
    check((clean.performance_band == expected_band).all(), "Performance bands do not match achievement")

if log is not None:
    check(
        list(log.columns) == ["store", "date", "old_footfall", "new_footfall", "rule"],
        f"Cleaning log columns are {list(log.columns)}; expected the five assignment columns",
    )
    rules = log["rule"].value_counts().to_dict()
    check(len(log) == 8, f"Expected 8 cleaning-change rows; found {len(log)}")
    check(rules.get("negative_to_missing", 0) == 1, "Expected one negative-to-missing row")
    check(rules.get("iqr_cap", 0) == 2, "Expected two IQR cap rows")
    check(rules.get("median_impute", 0) == 5, "Expected five median-imputation rows")
    negative = log[log.rule == "negative_to_missing"]
    check(len(negative) == 1 and negative.iloc[0].store == "Hyderabad"
          and negative.iloc[0]["date"] == "2026-04-21"
          and close(negative.iloc[0].old_footfall, -150),
          "Negative-footfall log entry mismatch")
    caps = log[log.rule == "iqr_cap"].set_index(["store", "date"])
    for key, old_value, new_value in [
        (("Ahmedabad", "2026-05-26"), 9800, 2281.38),
        (("Mumbai", "2026-04-09"), 6100, 2986.00),
    ]:
        check(key in caps.index, f"Missing IQR cap log entry {key}")
        if key in caps.index:
            check(close(caps.loc[key, "old_footfall"], old_value), f"Wrong original outlier for {key}")
            check(close(caps.loc[key, "new_footfall"], new_value), f"Wrong capped value for {key}")
    imputes = log[log.rule == "median_impute"].set_index(["store", "date"])
    for key, value in [
        (("Mumbai", "2026-04-30"), 2386.0),
        (("Pune", "2026-04-12"), 1509.5),
        (("Pune", "2026-05-17"), 1509.5),
        (("Hyderabad", "2026-04-21"), 2216.0),
        (("Bengaluru", "2026-06-10"), 2065.0),
    ]:
        check(key in imputes.index, f"Missing median-imputation entry {key}")
        if key in imputes.index:
            check(close(imputes.loc[key, "new_footfall"], value), f"Wrong median imputation for {key}")

if clean is not None:
    pune = clean[(clean.store == "Pune") & (clean.date == "2026-05-16")]
    check(len(pune) == 1, "Pune 2026-05-16 row should occur exactly once")
    if len(pune) == 1:
        row = pune.iloc[0]
        check(close(row.achievement_pct, 74.59) and row.performance_band == "Poor"
              and row.weekend_flag == "Yes", "Pune 2026-05-16 feature check failed")
        check(close(row.revenue_per_footfall, 396.77)
              and close(row.marketing_efficiency, 18.12), "Pune 2026-05-16 ratio check failed")
    mumbai = clean[(clean.store == "Mumbai") & (clean.date == "2026-05-21")]
    check(len(mumbai) == 1, "Mumbai 2026-05-21 row should occur exactly once")
    if len(mumbai) == 1:
        row = mumbai.iloc[0]
        check(close(row.achievement_pct, 107.99) and row.performance_band == "Excellent"
              and row.weekend_flag == "No", "Mumbai 2026-05-21 feature check failed")

findings_path = ANALYSIS / "findings.md"
if findings_path.is_file():
    findings = findings_path.read_text(encoding="utf-8")
    for phrase in (
        "## Store performance", "## Verified premise checks", "## Correlations",
        "Pune has the lowest mean daily revenue",
        "Hyderabad has the highest mean stockout hours",
        "Pune does not have the highest mean stockout hours",
        "do not establish that stockouts caused",
    ):
        check(phrase.lower() in findings.lower(), f"Findings report missing: {phrase}")

quality_path = ANALYSIS / "data_quality_report.md"
if quality_path.is_file():
    quality = quality_path.read_text(encoding="utf-8")
    for phrase in ("Column data types and missing values", "Descriptive statistics",
                   "Raw daily source checks", "Per-store raw footfall IQR bounds and outlier rows",
                   "Q1", "Q3", "Median", "IQR", "marketing_spend_inr"):
        check(phrase.lower() in quality.lower(), f"Data quality report missing: {phrase}")

summary_path = ANALYSIS / "executive_summary.md"
if summary_path.is_file():
    words = len(summary_path.read_text(encoding="utf-8").split())
    check(words <= 250, f"Executive summary has {words} words; maximum is 250")

if errors:
    print("PART A ACCEPTANCE CHECKS FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("PART A ACCEPTANCE CHECKS PASSED")
print(f"Validated {len(required_paths)} files, raw/clean shapes, cleaning audit, derived fields, and reports.")
