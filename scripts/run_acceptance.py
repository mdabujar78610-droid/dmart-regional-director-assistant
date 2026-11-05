"""Acceptance checks for Part A. Run: python scripts/run_acceptance.py"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, ANALYSIS = ROOT / "data", ROOT / "analysis"
errors = []
def check(condition, message):
    if not condition: errors.append(message)

required = [DATA/"store_daily.csv", DATA/"inventory.csv", DATA/"feedback.csv", DATA/"store_daily_clean.csv", ANALYSIS/"cleaning_log.csv"]
for p in required: check(p.exists(), f"Missing {p.relative_to(ROOT)}")
if not errors:
    raw = pd.read_csv(DATA/"store_daily.csv")
    inv = pd.read_csv(DATA/"inventory.csv")
    feedback = pd.read_csv(DATA/"feedback.csv")
    clean = pd.read_csv(DATA/"store_daily_clean.csv")
    log = pd.read_csv(ANALYSIS/"cleaning_log.csv")
    check(raw.shape == (453, 9), f"Raw daily shape is {raw.shape}, expected (453, 9)")
    check(len(inv) == 40 and inv.shape[1] == 6, "Inventory must be 40 x 6")
    check(len(feedback) == 200 and feedback.shape[1] == 6, "Feedback must be 200 x 6")
    check(len(clean) == 450, f"Cleaned rows {len(clean)}, expected 450")
    check(not clean.isna().any().any(), "Cleaned data contains missing values")
    check((clean.footfall >= 0).all(), "Cleaned data contains negative footfall")
    features = {"revenue_per_footfall","marketing_efficiency","achievement_pct","shortfall_inr","weekend_flag","performance_band"}
    check(features.issubset(clean.columns), f"Missing feature columns: {sorted(features-set(clean.columns))}")
    check((log.rule == "negative_to_missing").sum() == 1, "Expected one negative_to_missing log row")
    check((log.rule == "iqr_cap").sum() == 2, "Expected two iqr_cap log rows")
    check((log.rule == "median_impute").sum() == 5, "Expected five median_impute log rows")
    pune = clean[(clean.store=="Pune") & (clean.date=="2026-05-16")]
    check(len(pune)==1 and round(float(pune.iloc[0].achievement_pct),2)==74.59 and pune.iloc[0].performance_band=="Poor" and pune.iloc[0].weekend_flag=="Yes", "Pune 2026-05-16 acceptance row failed")
    mum = clean[(clean.store=="Mumbai") & (clean.date=="2026-05-21")]
    check(len(mum)==1 and round(float(mum.iloc[0].achievement_pct),2)==107.99 and mum.iloc[0].performance_band=="Excellent" and mum.iloc[0].weekend_flag=="No", "Mumbai 2026-05-21 acceptance row failed")
if errors:
    print("PART A FAILED")
    print("\n".join(f"- {e}" for e in errors))
    raise SystemExit(1)
print("PART A DATA ACCEPTANCE CHECKS PASSED")
