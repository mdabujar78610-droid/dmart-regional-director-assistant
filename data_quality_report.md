# Data Quality Report

## Project
DMart Regional Director Assistant — Part A

## Dataset Scope
This report reviews the three generated datasets and documents the cleaning performed on `store_daily.csv`.

| Dataset | Rows | Columns | Quality observations |
|---|---:|---:|---|
| `store_daily.csv` | 453 | 9 | 3 exact duplicate rows, 4 missing footfall values, 1 negative footfall value, 2 high footfall outliers capped |
| `inventory.csv` | 40 | 6 | No missing values found; 14 product-store records are below their reorder threshold |
| `feedback.csv` | 200 | 6 | 12 missing customer ratings; other fields have no missing values |

## Store Daily Cleaning

The cleaning process was applied to `store_daily.csv`.

| Check / action | Result |
|---|---:|
| Original rows | 453 |
| Exact duplicate rows removed | 3 |
| Rows after duplicate removal | 450 |
| Negative footfall values changed to missing | 1 |
| High footfall outliers capped using store-wise IQR upper bounds | 2 |
| Missing footfall values filled using store-wise median | 5 |
| Final cleaned rows | 450 |
| Missing values in cleaned dataset | 0 |

### Cleaning Rules
1. Exact duplicate rows were removed, keeping the first occurrence.
2. Negative footfall values were treated as missing.
3. IQR bounds were calculated separately for each store. Values above the upper bound were capped at that bound.
4. Missing footfall values were imputed using the median footfall for the corresponding store.
5. The cleaning actions were recorded in `analysis/cleaning_log.csv`.

## Derived Columns
The cleaned store-level daily dataset includes:
- `revenue_per_footfall`
- `marketing_efficiency`
- `achievement_pct`
- `shortfall_inr`
- `weekend_flag`
- `performance_band`

## Important Scope Notes
- The current cleaning notebook cleans `store_daily.csv`; it loads the inventory and feedback datasets but does not clean them.
- The 12 missing ratings in `feedback.csv` remain unresolved in the current workflow.
- The 14 inventory records below reorder threshold are a stock-monitoring observation, not a data-cleaning error.
- The generated datasets are synthetic practice data, not actual DMart operational records.
