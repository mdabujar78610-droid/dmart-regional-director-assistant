# Analysis Findings

## Project
DMart Regional Director Assistant — Part A

## Analysis Scope
The analysis uses the cleaned `data/store_daily_clean.csv` dataset containing 450 daily records across five stores.

## Store Performance

| Store | Total revenue (INR) | Average achievement | Average stockout hours | Poor-performance days |
|---|---:|---:|---:|---:|
| Mumbai | 95,793,443.95 | 101.37% | 1.93 | 0 |
| Bengaluru | 83,795,910.89 | 98.01% | 2.38 | 0 |
| Hyderabad | 80,390,970.85 | 94.02% | 3.85 | 0 |
| Ahmedabad | 70,438,262.88 | 92.08% | 3.19 | 1 |
| Pune | 57,272,269.78 | 70.71% | 2.32 | 70 |

## Key Findings

1. **Mumbai leads revenue performance.** It recorded the highest total revenue (approximately INR 9.58 crore) and the highest average target achievement at 101.37%.
2. **Pune is the main performance concern.** Its average target achievement was 70.71%, and it recorded 70 poor-performance days out of 90.
3. **Hyderabad has the highest average stockout duration.** Its average was 3.85 hours, compared with 1.93 hours in Mumbai.
4. **Revenue and footfall move strongly together in this generated dataset.** The overall Pearson correlation reported by the analysis script is 0.918.
5. **The overall revenue-stockout relationship is weak and negative.** The reported correlation is -0.152.
6. **Pune-specific correlations:** revenue vs. stockout hours = -0.254; revenue vs. footfall = 0.735.

## Interpretation and Limitations
- Correlation does not establish causation. These results do not prove that stockouts caused a change in revenue.
- The data is synthetically generated with a fixed random seed for practice and reproducibility.
- The current analysis script does not analyze inventory or customer feedback. Those datasets need separate analysis before making complete store-level recommendations.
