# Analysis Findings

## Store performance (450 cleaned store-days)

| Store | Mean daily revenue (INR) | Mean footfall | Mean stockout hours | Revenue / footfall (INR) | Mean achievement (%) | Poor days |
|---|---:|---:|---:|---:|---:|---:|
| Ahmedabad | 782,647.37 | 1,922.59 | 3.19 | 407.08 | 92.08 | 1 |
| Bengaluru | 931,065.68 | 2,076.86 | 2.38 | 448.31 | 98.01 | 0 |
| Hyderabad | 893,233.01 | 2,209.51 | 3.85 | 404.27 | 94.02 | 0 |
| Mumbai | 1,064,371.60 | 2,391.27 | 1.93 | 445.11 | 101.37 | 0 |
| Pune | 636,358.55 | 1,517.71 | 2.32 | 419.29 | 70.71 | 70 |
| **All stores** | 861,535.24 | 2,023.59 | 2.74 | 425.75 | 91.24 | 71 |

## Verified premise checks

- Pune has the lowest mean daily revenue.
- Hyderabad has the highest mean stockout hours.
- Pune does not have the highest mean stockout hours.
- These observations do not establish that stockouts caused Pune's lower revenue.

## Store ranking

Mean revenue, lowest to highest: Pune: INR 636,358.55; Ahmedabad: INR 782,647.37; Hyderabad: INR 893,233.01; Bengaluru: INR 931,065.68; Mumbai: INR 1,064,371.60

Mean stockout hours, highest to lowest: Hyderabad: 3.85; Ahmedabad: 3.19; Bengaluru: 2.38; Pune: 2.32; Mumbai: 1.93

## Correlations

| Scope | Revenue vs stockout hours | Revenue vs footfall |
|---|---:|---:|
| All stores (450 rows) | -0.152 | 0.918 |
| Pune (90 rows) | -0.254 | 0.735 |
| Raw deduplicated non-missing footfall (445 rows) | — | 0.565 |

Correlation describes association and does not prove causation.

## Facts

- **Fact 1:** Pune mean daily revenue is INR 636,358.55, the lowest of the five stores.
- **Fact 2:** Pune has 70 Poor-performance days out of 90.
- **Fact 3:** Pune mean stockout duration is 2.32 hours; Hyderabad is highest at 3.85 hours.
- **Fact 4:** Cleaned revenue-footfall correlation is 0.918; raw deduplicated non-missing baseline is 0.565.

## Insights

- **Insight 1:** Pune is fourth of five stores by mean stockout hours, so it does not have the most stockout time.
- **Insight 2:** Footfall and revenue move together in this dataset, but association alone does not establish a cause.

## Hypotheses (unconfirmed)

- **Hypothesis 1 (unconfirmed):** Local demand or catchment differences may reduce Pune visits; test using catchment demographics, competitor locations, hourly traffic and campaign reach.
- **Hypothesis 2 (unconfirmed):** Assortment, pricing or execution may affect conversion or basket value; test using SKU-level sales and availability, price/promotion history, conversion, basket size and store-level feedback.

## Limitations

- The datasets are synthetic, observational, and cover one 90-day period.
- Inventory is an undated snapshot, not historical stock availability.
- SKU-level sales, conversion, basket size, local demand, and competitor data are not supplied.
- Potential explanations are hypotheses requiring additional evidence.
