# Analysis Findings

## Store performance (cleaned 450 store-days)

| Store | Mean daily revenue (INR) | Mean footfall | Mean stockout hours | Revenue / footfall (INR) | Mean achievement (%) | Poor days |
|---|---:|---:|---:|---:|---:|---:|
| Ahmedabad | 782,647.37 | 1,922.59 | 3.19 | 407.08 | 92.08 | 1 |
| Bengaluru | 931,065.68 | 2,076.86 | 2.38 | 448.31 | 98.01 | 0 |
| Hyderabad | 893,233.01 | 2,209.51 | 3.85 | 404.27 | 94.02 | 0 |
| Mumbai | 1,064,371.60 | 2,391.27 | 1.93 | 445.11 | 101.37 | 0 |
| Pune | 636,358.55 | 1,517.71 | 2.32 | 419.29 | 70.71 | 70 |
| **All stores** | **861,535.24** | **2,023.59** | **2.74** | **425.75** | **91.24** | **71** |

## Premise test: Is Pune the lowest-revenue store because of stockouts?
Mean stockout hours ranked highest to lowest: Hyderabad 3.85, Ahmedabad 3.19, Bengaluru 2.38, Pune 2.32, Mumbai 1.93. Pune ranks fourth of five, below the all-store mean of 2.74 hours. The claim that Pune is the lowest-revenue store because it has the most stockouts is **not supported by these data**. Pune has the lowest mean daily revenue and 70 Poor days, but it does not have the highest mean stockout hours.

## Correlations
| Scope | Revenue vs stockout hours | Revenue vs footfall |
|---|---:|---:|
| All stores (450 cleaned rows) | -0.152 | 0.918 |
| Pune only | -0.254 | 0.735 |
| Raw daily data, deduplicated and non-missing footfall (446 rows; negatives and extremes retained) | — | 0.548 |

The raw baseline correlation uses the deduplicated raw data, excludes missing footfall only, and retains negative and extreme values. Correlation describes association; it does not establish causation.

## Facts
- **Fact 1:** Pune's mean daily revenue is INR 636,358.55, the lowest of the five stores.
- **Fact 2:** Pune records 70 Poor days; all other stores combined record one.
- **Fact 3:** Pune's mean stockout duration is 2.32 hours, versus 3.85 hours in Hyderabad.
- **Fact 4:** Revenue-footfall correlation is 0.918 across cleaned store-days, compared with 0.548 in the raw deduplicated non-missing baseline.

## Insights
- **Insight 1:** Pune's weak performance is not explained by having the most stockout hours; it ranks fourth on that measure.
- **Insight 2:** Footfall is strongly associated with revenue in the cleaned data, but this association alone cannot explain why Pune has lower traffic or prove a causal mechanism.

## Hypotheses (unconfirmed)
- **Hypothesis 1 — Pune demand or catchment differences may reduce visits.** Unconfirmed; test with catchment demographics, local competition, store location, customer counts by hour, and local campaign reach.
- **Hypothesis 2 — Pune's assortment, pricing, or execution may reduce conversion or basket value.** Unconfirmed; test with SKU-level sales, availability and stockout-by-SKU, prices, basket size, conversion rate, promotion history, and customer feedback by store.
