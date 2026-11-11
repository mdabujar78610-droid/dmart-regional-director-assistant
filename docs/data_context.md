# DMart Regional Director Assistant — Data Context

## 1. Provenance, stores, and reporting period

All CSV files are synthetic assignment data, not actual DMart operational records.

| Store ID | Store |
|---|---|
| S01 | Mumbai |
| S02 | Pune |
| S03 | Hyderabad |
| S04 | Bengaluru |
| S05 | Ahmedabad |

Daily reporting period: **2026-04-01 through 2026-06-29** (90 calendar days). Inventory is an undated snapshot.

## 2. Dataset inventory

| File | Rows | Columns | Grain |
|---|---:|---:|---|
| data/store_daily.csv (raw) | 453 | 9 | Store-day, includes 3 injected exact duplicates |
| data/store_daily_clean.csv | 450 | 15 | Unique store-day plus six derived analysis columns |
| data/inventory.csv | 40 | 6 | Store-product snapshot |
| data/feedback.csv | 200 | 6 | Individual feedback record |

## 3. Actual column schemas and semantic data types

Types below describe the CSV values and their intended pandas-compatible representation. CSV has no native type system; date columns are ISO-8601 strings on disk and should be parsed as dates for filtering.

### 3.1 data/store_daily.csv — raw daily source (453 × 9)

| Column | Semantic type | Description |
|---|---|---|
| date | date (ISO-8601 string in CSV) | Business date |
| store_id | string identifier | Store code |
| store | string/category | Store name |
| footfall | integer or missing | Visitor count; contains injected invalid/missing/extreme values |
| revenue_inr | float | Daily revenue in INR |
| daily_target_inr | integer | Daily target in INR |
| marketing_spend_inr | integer | Synthetic field retained in source; prohibited for agent use |
| stockout_hours | float | Daily stockout duration |
| discount_pct | float | Discount percentage |

Raw quality facts: 453 rows, 9 columns; 3 exact duplicate records; 4 blank footfall cells; one negative footfall value (-150); injected extreme high footfall values 6,100 and 9,800. Do not edit the raw file during cleaning.

### 3.2 data/store_daily_clean.csv — cleaned daily data (450 × 15)

| Column | Semantic type | Description |
|---|---|---|
| date | date (ISO-8601 string in CSV) | Business date |
| store_id | string identifier | Store code |
| store | string/category | Store name |
| footfall | float/integer-valued | Cleaned visitor count; store-median imputation and IQR capping may produce fractional values |
| revenue_inr | float | Daily revenue in INR |
| daily_target_inr | integer | Daily target in INR |
| marketing_spend_inr | integer | Retained from source for reproducibility; prohibited for agent use |
| stockout_hours | float | Daily stockout duration |
| discount_pct | float | Discount percentage |
| revenue_per_footfall | float | Part A analysis-only ratio; not an approved agent metric |
| marketing_efficiency | float | Part A-only derived field that depends on prohibited marketing spend; agent must never use or report it |
| achievement_pct | float | Revenue divided by daily target × 100 |
| shortfall_inr | float | Daily target minus revenue; Part A analysis-only |
| weekend_flag | category/string | Yes for Saturday/Sunday, otherwise No; Part A analysis-only |
| performance_band | category/string | Excellent (achievement ≥100%), Good (≥75% and <100%), Poor (<75%) |

### 3.3 data/inventory.csv — inventory snapshot (40 × 6)

| Column | Semantic type | Description |
|---|---|---|
| store_id | string identifier | Store code |
| store | string/category | Store name |
| product_id | string identifier | Product code |
| product | string/category | Product name |
| stock_units | integer | Available stock units |
| reorder_threshold | integer | Reorder threshold in units |

This dataset has no date column. Never describe it as historical or join it to a daily period as though it were time-aligned.

### 3.4 data/feedback.csv — customer feedback (200 × 6)

| Column | Semantic type | Description |
|---|---|---|
| feedback_id | string identifier | Feedback record code |
| store_id | string identifier | Store code |
| store | string/category | Store name |
| date | date (ISO-8601 string in CSV) | Feedback date within the quarter |
| rating | integer or missing | Customer rating; 12 missing values are retained |
| theme | category/string | Feedback theme |

Feedback rows represent individual records. Rating averages must use non-missing ratings and disclose rated/total counts.

## 4. Approved metric set and dimensions

Exactly 11 approved reportable fields:
1. `revenue_inr`
2. `daily_target_inr`
3. `footfall`
4. `stockout_hours`
5. `discount_pct`
6. `achievement_pct`
7. `performance_band`
8. `stock_units`
9. `reorder_threshold`
10. `rating`
11. `theme`

Allowed dimensions/identifiers: `store`, `store_id`, `date`, `product`, `product_id`, and `feedback_id` (feedback identifier only). These may filter, group, or label but are not additional metrics.

**Prohibited:** `marketing_spend_inr` and dependent `marketing_efficiency`. They must not be used by the agent, even though the fields exist in the Part A files. Part A may document the source schema and derived column for transparency, but must not include those values in the conversational analytics path.

## 5. Cleaning record and data-quality rules

Part A cleaning must:
- Remove three exact duplicate store-day rows, retaining the first copy.
- Convert the single negative footfall value to missing before outlier treatment.
- Apply store-specific two-sided IQR bounds: lower = Q1 − 1.5×IQR; upper = Q3 + 1.5×IQR. Cap values below the lower bound to the lower bound and above the upper bound to the upper bound; log every change.
- Impute missing daily footfall with that store's median and log each imputation.
- Preserve the 12 missing feedback ratings; do not impute them.
- Keep raw source files unchanged.

Expected daily cleaning counts from the current synthetic generator: 453 raw rows → 450 cleaned rows; 3 duplicates removed; 4 blank footfall values plus 1 negative footfall treated as missing; 5 total store-median imputations. Two high footfall values are known injected outliers; verify whether either lower-bound outliers exist from the data rather than assuming the count.

## 6. Verified business findings to regenerate

The current assignment findings to test against the actual cleaned CSV are:
- Pune has the lowest mean daily revenue.
- Hyderabad has the highest mean stockout hours.
- Pune does not have the highest mean stockout hours.

The previous analysis reported Pune mean daily revenue INR 636,358.55, Pune mean stockout hours 2.32, and Hyderabad mean stockout hours 3.85. Treat these as prior values to reconcile against regenerated outputs, not hard-coded truths. Never claim stockouts caused Pune's lower revenue.

## 7. Relationships and safe joins

- Daily grain: store + date.
- Inventory grain: store + product.
- Feedback grain: feedback_id / individual feedback record.
- Validate store identifiers and row counts before joining.
- Aggregate to compatible grains before joining.
- Prevent many-to-many row multiplication.
- Analyze datasets separately when a safe join cannot be demonstrated.

## 8. Analysis rules

Use the full available period when no daily date filter is specified. Clearly label totals, means, medians, counts, percentages, and denominators. Use non-missing ratings for rating averages and disclose rated/total counts. Do not impute missing ratings. Never treat inventory as dated. Do not claim correlation proves causation. Disclose data cleaning adjustments when relevant.
