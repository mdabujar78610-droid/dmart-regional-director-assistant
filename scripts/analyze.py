"""Generate data-quality, findings, and executive reports from committed CSVs."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, ANALYSIS = ROOT / "data", ROOT / "analysis"
FILES = {
    "Raw daily": DATA / "store_daily.csv",
    "Clean daily": DATA / "store_daily_clean.csv",
    "Inventory": DATA / "inventory.csv",
    "Feedback": DATA / "feedback.csv",
}


def dtype(series):
    if pd.api.types.is_integer_dtype(series): return "integer"
    if pd.api.types.is_float_dtype(series): return "float"
    if series.name == "date": return "date (ISO-8601 string)"
    return "string/category"


def generate_quality(frames):
    lines = [
        "# Data Quality Report", "",
        "## Dataset shapes", "",
        "| Dataset | Rows | Columns |", "|---|---:|---:|",
    ]
    for name, df in frames.items():
        lines.append(f"| {name} | {len(df)} | {len(df.columns)} |")
    lines += ["", "## Column data types and missing values", ""]
    for name, df in frames.items():
        lines += [f"### {name}", "", "| Column | Type | Missing | Non-missing |",
                  "|---|---|---:|---:|"]
        for col in df.columns:
            missing = int(df[col].isna().sum())
            lines.append(f"| {col} | {dtype(df[col])} | {missing} | {len(df)-missing} |")
        lines.append("")
    lines += ["## Descriptive statistics", ""]
    for name, df in frames.items():
        numeric = df.select_dtypes(include="number")
        lines += [f"### {name}", "",
                  "| Column | Count | Missing | Min | Q1 | Median | Mean | Q3 | Max | IQR |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for col in numeric.columns:
            s = numeric[col].dropna()
            if s.empty:
                vals = ["—"] * 7
                count = 0
            else:
                q1, q3 = s.quantile(.25), s.quantile(.75)
                vals = [f"{s.min():,.3f}", f"{q1:,.3f}", f"{s.median():,.3f}",
                        f"{s.mean():,.3f}", f"{q3:,.3f}", f"{s.max():,.3f}",
                        f"{q3-q1:,.3f}"]
                count = len(s)
            lines.append(f"| {col} | {count} | {int(numeric[col].isna().sum())} | " +
                         " | ".join(vals) + " |")
        lines.append("")
    raw = frames["Raw daily"]
    clean = frames["Clean daily"]
    inv = frames["Inventory"]
    fb = frames["Feedback"]

    # Assignment-required raw-source inspection and store-specific IQR audit.
    raw_footfall = pd.to_numeric(raw["footfall"], errors="coerce")
    dedup = raw.drop_duplicates(keep="first").copy()
    dedup["footfall"] = pd.to_numeric(dedup["footfall"], errors="coerce")
    dedup.loc[dedup["footfall"] < 0, "footfall"] = pd.NA
    lines += [
        "## Raw daily source checks", "",
        f"- Raw shape: {raw.shape[0]} rows × {raw.shape[1]} columns.",
        f"- Exact duplicate rows: {int(raw.duplicated().sum())}.",
        f"- Raw footfall minimum: {raw_footfall.min():,.0f}; maximum: {raw_footfall.max():,.0f}.",
        "",
        "| Column | Data type | Null count |",
        "|---|---|---:|",
    ]
    for col in raw.columns:
        lines.append(f"| {col} | {raw[col].dtype} | {int(raw[col].isna().sum())} |")
    lines += [
        "", "## Per-store raw footfall IQR bounds and outlier rows", "",
        "Bounds use raw daily data after exact duplicate removal and treating negative footfall as missing. "
        "Q1 and Q3 use linear interpolation; IQR = Q3 - Q1; bounds are Q1 - 1.5*IQR and Q3 + 1.5*IQR.",
        "",
        "| Store | Q1 | Q3 | IQR | Lower bound | Upper bound | Outlier rows |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for store in sorted(dedup["store"].dropna().unique()):
        group = dedup[dedup["store"] == store]
        values = group["footfall"].dropna()
        q1 = float(values.quantile(0.25, interpolation="linear"))
        q3 = float(values.quantile(0.75, interpolation="linear"))
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = group[group["footfall"].notna() & (
            (group["footfall"] < lower) | (group["footfall"] > upper)
        )]
        details = []
        for row in outliers.itertuples():
            side = "below" if row.footfall < lower else "above"
            details.append(f"{row.store} {row.date}: {row.footfall:g} ({side})")
        detail = "; ".join(details) if details else "None"
        lines.append(
            f"| {store} | {q1:.2f} | {q3:.2f} | {iqr:.2f} | "
            f"{lower:.2f} | {upper:.2f} | {detail} |"
        )
    lines += [
        "",
        "Only observations outside the store-specific bounds are listed. "
        "Raw source values are retained unchanged; these bounds inform the separate cleaning step.",
        "",
    ]
    raw_footfall = pd.to_numeric(raw["footfall"], errors="coerce")
    log_path = ANALYSIS / "cleaning_log.csv"
    log = pd.read_csv(log_path) if log_path.exists() else pd.DataFrame()
    lines += [
        "## Cleaning reconciliation", "",
        f"- Raw daily: {len(raw)} rows; {len(raw.columns)} columns; {int(raw.duplicated().sum())} exact duplicates.",
        f"- Raw missing footfall: {int(raw_footfall.isna().sum())}; negative footfall: {int((raw_footfall < 0).sum())}.",
        f"- Clean daily: {len(clean)} rows; {len(clean.columns)} columns; missing cells: {int(clean.isna().sum().sum())}.",
        f"- Inventory: {len(inv)} rows; {int((inv.stock_units < inv.reorder_threshold).sum())} records below threshold.",
        f"- Feedback: {len(fb)} rows; missing ratings: {int(fb.rating.isna().sum())}.",
        f"- Cleaning log rows: {len(log)}.",
        "",
        "Numeric statistics use non-missing values. Quartiles use pandas linear interpolation; IQR = Q3 − Q1.",
        "Date values are ISO-8601 strings in the CSVs. Inventory is an undated snapshot. Missing feedback ratings are not imputed.",
        "The marketing_spend_inr column is documented as a source field but is prohibited from agent calculations and responses.",
        "Raw source CSVs must remain unchanged.", "",
    ]
    (ANALYSIS / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")


def generate_findings(df):
    required = {"store", "date", "revenue_inr", "daily_target_inr", "footfall",
                "stockout_hours", "achievement_pct", "performance_band"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    rows = []
    for store, g in df.groupby("store"):
        rows.append({
            "store": store, "mean_revenue": g.revenue_inr.mean(),
            "mean_footfall": g.footfall.mean(),
            "mean_stockout": g.stockout_hours.mean(),
            "revenue_per_footfall": g.revenue_inr.sum()/g.footfall.sum(),
            "mean_achievement": g.achievement_pct.mean(),
            "poor_days": int((g.performance_band == "Poor").sum()),
        })
    summary = pd.DataFrame(rows)
    revenue_rank = summary.sort_values("mean_revenue")
    stockout_rank = summary.sort_values("mean_stockout", ascending=False)
    pune = summary.loc[summary.store == "Pune"].iloc[0]
    hyd = summary.loc[summary.store == "Hyderabad"].iloc[0]
    if revenue_rank.iloc[0].store != "Pune":
        raise AssertionError("Pune is not the lowest mean-revenue store.")
    if stockout_rank.iloc[0].store != "Hyderabad":
        raise AssertionError("Hyderabad is not the highest mean-stockout store.")
    if stockout_rank.iloc[0].store == "Pune":
        raise AssertionError("Pune must not be the highest mean-stockout store.")
    corr_stockout = df.revenue_inr.corr(df.stockout_hours)
    corr_footfall = df.revenue_inr.corr(df.footfall)
    raw_daily = pd.read_csv(DATA / "store_daily.csv")
    raw_daily = raw_daily.drop_duplicates(keep="first").copy()
    raw_daily["footfall"] = pd.to_numeric(raw_daily["footfall"], errors="coerce")
    raw_daily.loc[raw_daily["footfall"] < 0, "footfall"] = pd.NA
    raw_baseline = raw_daily.dropna(subset=["footfall"])
    raw_corr_footfall = raw_baseline["revenue_inr"].corr(raw_baseline["footfall"])
    pooled = {
        "mean_revenue": df.revenue_inr.mean(),
        "mean_footfall": df.footfall.mean(),
        "mean_stockout": df.stockout_hours.mean(),
        "revenue_per_footfall": df.revenue_inr.sum() / df.footfall.sum(),
        "mean_achievement": df.achievement_pct.mean(),
        "poor_days": int((df.performance_band == "Poor").sum()),
    }
    lines = [
        "# Analysis Findings", "",
        f"## Store performance ({len(df)} cleaned store-days)", "",
        "| Store | Mean daily revenue (INR) | Mean footfall | Mean stockout hours | Revenue / footfall (INR) | Mean achievement (%) | Poor days |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary.sort_values("store").itertuples():
        lines.append(f"| {r.store} | {r.mean_revenue:,.2f} | {r.mean_footfall:,.2f} | "
                     f"{r.mean_stockout:.2f} | {r.revenue_per_footfall:.2f} | "
                     f"{r.mean_achievement:.2f} | {r.poor_days} |")
    lines.append(
        f"| **All stores** | {pooled['mean_revenue']:,.2f} | {pooled['mean_footfall']:,.2f} | "
        f"{pooled['mean_stockout']:.2f} | {pooled['revenue_per_footfall']:.2f} | "
        f"{pooled['mean_achievement']:.2f} | {pooled['poor_days']} |"
    )
    lines += ["", "## Verified premise checks", "",
              "- Pune has the lowest mean daily revenue.",
              "- Hyderabad has the highest mean stockout hours.",
              "- Pune does not have the highest mean stockout hours.",
              "- These observations do not establish that stockouts caused Pune's lower revenue.",
              "", "## Store ranking", "",
              "Mean revenue, lowest to highest: " + "; ".join(
                  f"{r.store}: INR {r.mean_revenue:,.2f}" for r in revenue_rank.itertuples()),
              "",
              "Mean stockout hours, highest to lowest: " + "; ".join(
                  f"{r.store}: {r.mean_stockout:.2f}" for r in stockout_rank.itertuples()),
              "", "## Correlations", "",
              "| Scope | Revenue vs stockout hours | Revenue vs footfall |",
              "|---|---:|---:|",
              f"| All stores ({len(df)} rows) | {corr_stockout:.3f} | {corr_footfall:.3f} |",
              f"| Pune ({len(df[df.store == 'Pune'])} rows) | "
              f"{df.loc[df.store == 'Pune', 'revenue_inr'].corr(df.loc[df.store == 'Pune', 'stockout_hours']):.3f} | "
              f"{df.loc[df.store == 'Pune', 'revenue_inr'].corr(df.loc[df.store == 'Pune', 'footfall']):.3f} |",
              f"| Raw deduplicated non-missing footfall ({len(raw_baseline)} rows) | — | {raw_corr_footfall:.3f} |",
              "", "Correlation describes association and does not prove causation.",
              "", "## Facts", "",
              f"- **Fact 1:** Pune mean daily revenue is INR {pune.mean_revenue:,.2f}, the lowest of the five stores.",
              f"- **Fact 2:** Pune has {int(pune.poor_days)} Poor-performance days out of 90.",
              f"- **Fact 3:** Pune mean stockout duration is {pune.mean_stockout:.2f} hours; Hyderabad is highest at {hyd.mean_stockout:.2f} hours.",
              f"- **Fact 4:** Cleaned revenue-footfall correlation is {corr_footfall:.3f}; raw deduplicated non-missing baseline is {raw_corr_footfall:.3f}.",
              "", "## Insights", "",
              "- **Insight 1:** Pune is fourth of five stores by mean stockout hours, so it does not have the most stockout time.",
              "- **Insight 2:** Footfall and revenue move together in this dataset, but association alone does not establish a cause.",
              "", "## Hypotheses (unconfirmed)", "",
              "- **Hypothesis 1 (unconfirmed):** Local demand or catchment differences may reduce Pune visits; test using catchment demographics, competitor locations, hourly traffic and campaign reach.",
              "- **Hypothesis 2 (unconfirmed):** Assortment, pricing or execution may affect conversion or basket value; test using SKU-level sales and availability, price/promotion history, conversion, basket size and store-level feedback.",
              "", "## Limitations", "",
              "- The datasets are synthetic, observational, and cover one 90-day period.",
              "- Inventory is an undated snapshot, not historical stock availability.",
              "- SKU-level sales, conversion, basket size, local demand, and competitor data are not supplied.",
              "- Potential explanations are hypotheses requiring additional evidence.", ""]
    (ANALYSIS / "findings.md").write_text("\n".join(lines), encoding="utf-8")
    return summary, pune, hyd, corr_stockout, corr_footfall


def generate_executive(summary, pune, hyd, corr_stockout, corr_footfall):
    df = pd.read_csv(DATA / "store_daily_clean.csv")
    by_revenue = summary.sort_values("mean_revenue")
    next_low = float(by_revenue.iloc[1].mean_revenue)
    top = float(by_revenue.iloc[-1].mean_revenue)
    p_rev = float(pune.mean_revenue)
    pct_next = (next_low-p_rev)/next_low*100
    pct_top = (top-p_rev)/top*100
    p_stock = float(pune.mean_stockout)
    h_stock = float(hyd.mean_stockout)
    stock_gap = (h_stock-p_stock)/h_stock*100
    report = f"""# Executive Summary

**Dataset:** Synthetic DMart practice data  
**Period:** 1 April–29 June 2026  
**Author:** Mohammad Abuzar  
**Coverage:** 450 cleaned store-days across five stores

## Headline finding

Pune has the lowest mean daily revenue. The premise that it is lowest because it has the most stockout hours is not supported.

## Magnitude

Pune averages INR {p_rev:,.2f} per day, {pct_next:.1f}% below the next-lowest store and {pct_top:.1f}% below Mumbai. Pune averages {p_stock:.2f} stockout hours; Hyderabad is highest at {h_stock:.2f} hours. Pune has 70 Poor days out of 90.

## What is and is not driving the finding

Pune ranks fourth of five for mean stockout hours. Revenue-stockout correlation is {corr_stockout:.3f}; revenue-footfall correlation is {corr_footfall:.3f}. These associations do not prove causation. Inventory is an undated snapshot.

## Supporting facts

- Pune mean achievement is {pune.mean_achievement:.2f}%; all-store mean is {summary.mean_achievement.mean():.2f}%.
- Pune revenue per footfall is INR {pune.revenue_per_footfall:.2f}.
- Pune-only revenue-footfall correlation is {df.loc[df.store == 'Pune', 'revenue_inr'].corr(df.loc[df.store == 'Pune', 'footfall']):.3f}.

## Open hypotheses and data needed

Unconfirmed: demand/catchment differences and assortment, pricing or conversion issues. Test with catchment and competitor data, hourly visits, SKU-level sales and availability, price/promotion history, conversion, basket size and feedback.

## Recommendation

**Owner:** Pune Store Manager with Regional Merchandising Lead. **Action:** complete a 14-day SKU availability, pricing and conversion audit against Mumbai and Bengaluru. **Timeline:** deliver a corrective-action plan within 21 days.
"""
    if len(report.split()) > 250:
        raise AssertionError("Executive summary exceeds 250 words.")
    (ANALYSIS / "executive_summary.md").write_text(report, encoding="utf-8")


def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    frames = {}
    for name, path in FILES.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing {path.relative_to(ROOT)}")
        frames[name] = pd.read_csv(path)
    generate_quality(frames)
    summary, pune, hyd, c1, c2 = generate_findings(frames["Clean daily"])
    generate_executive(summary, pune, hyd, c1, c2)
    print("Generated data_quality_report.md, findings.md, and executive_summary.md")
    print("Verified: Pune lowest mean revenue; Hyderabad highest mean stockout hours; Pune is not highest.")


if __name__ == "__main__":
    main()
