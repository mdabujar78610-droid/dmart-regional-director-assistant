# Data Quality Report

## Dataset scope
Part A daily store data covers 1 April–29 June 2026. The raw daily file contains 453 rows and 9 columns. It has 3 exact duplicate rows, 4 missing footfall values, and one invalid negative footfall value (-150). The maximum raw footfall is 9,800. The raw inventory file contains 40 rows × 6 columns, including 14 product-store records below their reorder threshold. The feedback file contains 200 rows × 6 columns, including 12 missing ratings.

## Decisions
1. **Exact duplicates — remove duplicates, keep the first occurrence.** Exact repeated records add no new information and would double-count a store-day. Keeping the first preserves one original observation; keeping the last would be arbitrary because the rows are identical. The raw source remains unchanged.
2. **Negative footfall — convert to missing, not zero.** A negative customer count is impossible and is not evidence that zero customers visited. Treating it as missing avoids inventing a valid zero. The raw source remains unchanged.
3. **Extreme footfall — cap using store-specific IQR upper bounds, rather than deleting rows.** Store traffic levels differ, so a pooled threshold would be inappropriate. Capping retains the affected store-days and other valid fields while limiting the influence of extreme values. The raw source remains unchanged.
4. **Missing footfall — impute the median for the same store, rather than the mean.** Store-specific medians reflect each store's typical traffic and are less sensitive to outliers than means. The raw source remains unchanged.

## IQR bounds
Bounds were calculated per store after duplicate removal and treating negative footfall as missing.

| Store | Lower bound | Upper bound |
|---|---:|---:|
| Ahmedabad | 1,582.38 | 2,281.38 |
| Bengaluru | 1,563.50 | 2,599.50 |
| Hyderabad | 1,598.50 | 2,810.50 |
| Mumbai | 1,802.00 | 2,986.00 |
| Pune | 1,194.75 | 1,832.75 |

Two raw observations exceeded their store's upper bound: Mumbai (6,100) and Ahmedabad (9,800). No rows were deleted for being extreme.

## Cleaning outcome
The cleaned daily dataset contains 450 rows, with no missing values and no negative footfall. The cleaning log records 1 negative-to-missing treatment, 2 IQR caps, and 5 store-median imputations (the negative value is subsequently imputed). Six derived fields are included: `revenue_per_footfall`, `marketing_efficiency`, `achievement_pct`, `shortfall_inr`, `weekend_flag`, and `performance_band`.

## Reproducibility
Run from the repository root:
```bash
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/run_acceptance.py
```
The generator recreates the synthetic raw datasets. Do not manually edit raw files; cleaning writes separate processed outputs.
