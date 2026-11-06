# DMart Regional Director Assistant — Data Context

## 1. Project Overview

This document describes the datasets used by the DMart Regional Director Assistant.

The AI Agent will analyze three prepared datasets to help Kavita Rao, Regional Director, understand store performance, inventory conditions, and customer feedback.

The datasets are synthetic assignment data and must not be presented as actual DMart business records.

### Stores Covered

| Store ID | Store Name |
|---|---|
| S01 | Mumbai |
| S02 | Pune |
| S03 | Hyderabad |
| S04 | Bengaluru |
| S05 | Ahmedabad |

### Reporting Period

1 April 2026 to 29 June 2026.

## 2. Dataset Overview

The project uses three datasets:

| Dataset | Rows | Purpose |
|---|---:|---|
| store_daily_clean.csv | 450 | Daily store performance |
| inventory.csv | 40 | Product stock and reorder information |
| feedback.csv | 200 | Customer ratings and feedback themes |

### 2.1 store_daily_clean.csv

**Purpose:** Analyze daily store performance.

Expected columns:

| Column | Data Type | Description |
|---|---|---|
| store | String | Store name |
| store_id | String | Store identifier |
| date | Date | Business date |
| revenue_inr | Numeric | Daily revenue in INR |
| daily_target_inr | Numeric | Daily revenue target |
| footfall | Numeric | Number of visitors |
| stockout_hours | Numeric | Stockout duration in hours |
| discount_pct | Numeric | Discount percentage |
| achievement_pct | Numeric | Target achievement percentage |
| performance_band | Category | Performance classification |

**Prepared row count:** 450

**Date range:** 2026-04-01 to 2026-06-29.

Supported analysis:
- Revenue analysis.
- Daily target achievement.
- Store comparisons.
- Footfall analysis.
- Discount analysis.
- Performance trends.
- Pune performance diagnosis.

### 2.2 inventory.csv

**Purpose:** Analyze inventory and stock availability.

Expected columns:

| Column | Data Type | Description |
|---|---|---|
| store | String | Store name |
| store_id | String | Store identifier |
| product | String | Product name |
| product_id | String | Product identifier |
| stock_units | Numeric | Available stock |
| reorder_threshold | Numeric | Minimum reorder level |

**Prepared row count:** 40.

Important:
- This dataset has no confirmed date column.
- Treat it as an undated inventory snapshot.
- Do not use it to claim historical stock levels.

Supported analysis:
- Products below reorder threshold.
- Store-wise stock comparison.
- Products requiring stock review.
- Inventory risk identification.

### 2.3 feedback.csv

**Purpose:** Analyze customer feedback and satisfaction.

Expected columns:

| Column | Data Type | Description |
|---|---|---|
| store | String | Store name |
| store_id | String | Store identifier |
| date | Date | Feedback date, if present |
| product | String | Product name, if present |
| product_id | String | Product identifier, if present |
| rating | Numeric | Customer rating |
| theme | Category | Feedback theme |

**Prepared row count:** 200.

**Expected reporting period:** 2026-04-01 to 2026-06-29, where date information is available.

Supported analysis:
- Customer rating summaries.
- Common feedback themes.
- Store-wise customer feedback.
- Customer satisfaction comparisons.

## 3. Data Cleaning Summary (Part A)

The following cleaning operations were reported in Part A:

1. Removed 3 duplicate daily records.
2. Handled 5 missing footfall values through imputation.
3. Capped 2 extreme values.
4. Treated negative footfall values as missing before cleaning.
5. Prepared the three datasets for analysis.

### Data Quality Rules

The Agent must:

- Never treat missing values as zero.
- Identify imputed values when relevant.
- Disclose capped or adjusted values when they affect an answer.
- Check actual CSV files before analysis.
- Validate missing values, duplicate records, and data types.
- Never invent missing business information.

The cleaning summary does not guarantee that every column in every dataset is complete.

## 4. Dataset Relationships

The datasets can be connected through store identifiers when their mappings are verified.

Dataset grain:

- store_daily_clean.csv: Store and date.
- inventory.csv: Store and product.
- feedback.csv: Individual feedback record.

### Join Rules

Before joining datasets, the Agent must:

1. Verify the store identifiers.
2. Check the grain of each dataset.
3. Avoid duplicate rows caused by many-to-many joins.
4. Aggregate data to compatible levels where necessary.
5. Validate row counts and metric totals after joining.

If a safe join is not possible, analyze datasets separately.

## 5. Approved Metrics

The Agent is allowed to report and calculate using only these 11 approved metric fields:

1. revenue_inr
2. daily_target_inr
3. footfall
4. stockout_hours
5. discount_pct
6. achievement_pct
7. performance_band
8. stock_units
9. reorder_threshold
10. rating
11. theme

### Dimension and Identifier Fields

These fields may be used for filtering, grouping, and identification:

- store
- store_id
- date
- product
- product_id

They are not additional reportable metrics.

### Prohibited Metric

`marketing_spend_inr`

The Agent must never query, calculate, estimate, or report this field.

## 6. Data Analysis Rules

1. Use the full available date range when the user does not specify a period.
2. Apply consistent filters when comparing stores.
3. Clearly distinguish totals, averages, counts, and percentages.
4. Do not divide by zero.
5. Do not silently remove relevant missing records.
6. Do not invent historical inventory information.
7. Use only columns actually present in the selected CSV file.
8. Validate data before calculations.

## 7. Pune Store Diagnosis

Pune is identified in the assignment as having the lowest average daily revenue among the five stores.

The Agent should investigate this using available evidence from:

- Revenue.
- Daily targets.
- Footfall.
- Stockout hours.
- Discounts.
- Inventory.
- Customer ratings.
- Feedback themes.

The Agent must distinguish:

- Observed facts.
- Calculated results.
- Possible explanations.
- Unsupported conclusions.

For example, low inventory and low revenue occurring together do not automatically prove that inventory caused the revenue decline.

## 8. Open-Ended Conversational Analytics

The Agent must support natural-language questions rather than a fixed list of questions.

Users may ask new questions about the five stores, datasets, approved metrics, and business performance.

The Agent should understand different phrasings, follow-up questions, comparisons, and diagnostic requests.

However, all answers must remain within the approved datasets and metric restrictions.

If information is unavailable, the Agent must explain the limitation rather than inventing an answer.

