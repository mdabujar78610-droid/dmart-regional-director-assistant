# Data Quality Report

## Dataset shapes

| Dataset | Rows | Columns |
|---|---:|---:|
| Raw daily | 453 | 9 |
| Clean daily | 450 | 15 |
| Inventory | 40 | 6 |
| Feedback | 200 | 6 |

## Column data types and missing values

### Raw daily

| Column | Type | Missing | Non-missing |
|---|---|---:|---:|
| date | date (ISO-8601 string) | 0 | 453 |
| store_id | string/category | 0 | 453 |
| store | string/category | 0 | 453 |
| footfall | float | 4 | 449 |
| revenue_inr | float | 0 | 453 |
| daily_target_inr | integer | 0 | 453 |
| marketing_spend_inr | integer | 0 | 453 |
| stockout_hours | float | 0 | 453 |
| discount_pct | float | 0 | 453 |

### Clean daily

| Column | Type | Missing | Non-missing |
|---|---|---:|---:|
| date | date (ISO-8601 string) | 0 | 450 |
| store_id | string/category | 0 | 450 |
| store | string/category | 0 | 450 |
| footfall | float | 0 | 450 |
| revenue_inr | float | 0 | 450 |
| daily_target_inr | integer | 0 | 450 |
| marketing_spend_inr | integer | 0 | 450 |
| stockout_hours | float | 0 | 450 |
| discount_pct | float | 0 | 450 |
| revenue_per_footfall | float | 0 | 450 |
| marketing_efficiency | float | 0 | 450 |
| achievement_pct | float | 0 | 450 |
| shortfall_inr | float | 0 | 450 |
| weekend_flag | string/category | 0 | 450 |
| performance_band | string/category | 0 | 450 |

### Inventory

| Column | Type | Missing | Non-missing |
|---|---|---:|---:|
| store_id | string/category | 0 | 40 |
| store | string/category | 0 | 40 |
| product_id | string/category | 0 | 40 |
| product | string/category | 0 | 40 |
| stock_units | integer | 0 | 40 |
| reorder_threshold | integer | 0 | 40 |

### Feedback

| Column | Type | Missing | Non-missing |
|---|---|---:|---:|
| feedback_id | string/category | 0 | 200 |
| store_id | string/category | 0 | 200 |
| store | string/category | 0 | 200 |
| date | date (ISO-8601 string) | 0 | 200 |
| rating | float | 12 | 188 |
| theme | string/category | 0 | 200 |

## Descriptive statistics

### Raw daily

| Column | Count | Missing | Min | Q1 | Median | Mean | Q3 | Max | IQR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| footfall | 449 | 4 | -150.000 | 1,811.000 | 2,047.000 | 2,044.298 | 2,266.000 | 9,800.000 | 455.000 |
| revenue_inr | 453 | 0 | 502,132.140 | 739,468.620 | 857,707.170 | 861,941.581 | 978,884.090 | 1,290,280.660 | 239,415.470 |
| daily_target_inr | 453 | 0 | 850,000.000 | 900,000.000 | 950,000.000 | 940,066.225 | 950,000.000 | 1,050,000.000 | 50,000.000 |
| marketing_spend_inr | 453 | 0 | 21,232.000 | 38,594.000 | 45,414.000 | 45,273.185 | 52,063.000 | 72,267.000 | 13,469.000 |
| stockout_hours | 453 | 0 | 0.000 | 1.800 | 2.800 | 2.739 | 3.700 | 6.800 | 1.900 |
| discount_pct | 453 | 0 | 3.000 | 5.200 | 7.300 | 7.383 | 9.600 | 12.000 | 4.400 |

### Clean daily

| Column | Count | Missing | Min | Q1 | Median | Mean | Q3 | Max | IQR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| footfall | 450 | 0 | 1,293.000 | 1,805.000 | 2,047.500 | 2,023.588 | 2,265.000 | 2,986.000 | 460.000 |
| revenue_inr | 450 | 0 | 502,132.140 | 739,604.965 | 857,389.795 | 861,535.241 | 975,895.275 | 1,290,280.660 | 236,290.310 |
| daily_target_inr | 450 | 0 | 850,000.000 | 900,000.000 | 950,000.000 | 940,000.000 | 950,000.000 | 1,050,000.000 | 50,000.000 |
| marketing_spend_inr | 450 | 0 | 21,232.000 | 38,989.500 | 45,422.500 | 45,335.804 | 52,066.000 | 72,267.000 | 13,076.500 |
| stockout_hours | 450 | 0 | 0.000 | 1.800 | 2.750 | 2.737 | 3.700 | 6.800 | 1.900 |
| discount_pct | 450 | 0 | 3.000 | 5.200 | 7.300 | 7.390 | 9.600 | 12.000 | 4.400 |
| revenue_per_footfall | 450 | 0 | 292.610 | 404.905 | 424.190 | 425.137 | 447.002 | 511.200 | 42.098 |
| marketing_efficiency | 450 | 0 | 11.260 | 16.782 | 19.130 | 19.478 | 21.633 | 37.310 | 4.850 |
| achievement_pct | 450 | 0 | 55.790 | 82.278 | 93.165 | 91.237 | 100.480 | 122.880 | 18.203 |
| shortfall_inr | 450 | 0 | -240,280.660 | -4,601.302 | 62,943.360 | 78,464.759 | 161,541.495 | 397,867.860 | 166,142.797 |

### Inventory

| Column | Count | Missing | Min | Q1 | Median | Mean | Q3 | Max | IQR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| stock_units | 40 | 0 | 33.000 | 74.000 | 179.000 | 175.550 | 241.000 | 389.000 | 167.000 |
| reorder_threshold | 40 | 0 | 64.000 | 79.750 | 100.000 | 100.925 | 128.250 | 144.000 | 48.500 |

### Feedback

| Column | Count | Missing | Min | Q1 | Median | Mean | Q3 | Max | IQR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rating | 188 | 12 | 1.000 | 3.000 | 4.000 | 3.473 | 4.250 | 5.000 | 1.250 |

## Raw daily source checks

- Raw shape: 453 rows × 9 columns.
- Exact duplicate rows: 3.
- Raw footfall minimum: -150; maximum: 9,800.

| Column | Data type | Null count |
|---|---|---:|
| date | str | 0 |
| store_id | str | 0 |
| store | str | 0 |
| footfall | float64 | 4 |
| revenue_inr | float64 | 0 |
| daily_target_inr | int64 | 0 |
| marketing_spend_inr | int64 | 0 |
| stockout_hours | float64 | 0 |
| discount_pct | float64 | 0 |

## Per-store raw footfall IQR bounds and outlier rows

Bounds use raw daily data after exact duplicate removal and treating negative footfall as missing. Q1 and Q3 use linear interpolation; IQR = Q3 - Q1; bounds are Q1 - 1.5*IQR and Q3 + 1.5*IQR.

| Store | Q1 | Q3 | IQR | Lower bound | Upper bound | Outlier rows |
|---|---:|---:|---:|---:|---:|---|
| Ahmedabad | 1844.50 | 2019.25 | 174.75 | 1582.38 | 2281.38 | Ahmedabad 2026-05-26: 9800 (above) |
| Bengaluru | 1952.00 | 2211.00 | 259.00 | 1563.50 | 2599.50 | None |
| Hyderabad | 2053.00 | 2356.00 | 303.00 | 1598.50 | 2810.50 | None |
| Mumbai | 2246.00 | 2542.00 | 296.00 | 1802.00 | 2986.00 | Mumbai 2026-04-09: 6100 (above) |
| Pune | 1434.00 | 1593.50 | 159.50 | 1194.75 | 1832.75 | None |

Only observations outside the store-specific bounds are listed. Raw source values are retained unchanged; these bounds inform the separate cleaning step.

## Cleaning reconciliation

- Raw daily: 453 rows; 9 columns; 3 exact duplicates.
- Raw missing footfall: 4; negative footfall: 1.
- Clean daily: 450 rows; 15 columns; missing cells: 0.
- Inventory: 40 rows; 14 records below threshold.
- Feedback: 200 rows; missing ratings: 12.
- Cleaning log rows: 8.

Numeric statistics use non-missing values. Quartiles use pandas linear interpolation; IQR = Q3 − Q1.
Date values are ISO-8601 strings in the CSVs. Inventory is an undated snapshot. Missing feedback ratings are not imputed.
The marketing_spend_inr column is documented as a source field but is prohibited from agent calculations and responses.
Raw source CSVs must remain unchanged.
