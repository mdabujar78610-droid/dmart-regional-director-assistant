# Executive Summary

## DMart Regional Director Assistant — Part A

This project builds a reproducible retail analytics workflow using three synthetic datasets: daily store performance, inventory, and customer feedback. The workflow generates the datasets, cleans daily store data, creates performance metrics, and compares results across five stores.

### Work Completed
- Generated 90 days of daily store data for five stores, along with inventory and customer feedback datasets.
- Removed three exact duplicate daily records.
- Treated one negative footfall value as missing, capped two high footfall outliers using store-wise IQR bounds, and imputed five missing footfall values using store-wise medians.
- Produced a cleaned dataset of 450 rows with no remaining missing values in the cleaned store-daily table.
- Created revenue, marketing-efficiency, target-achievement, shortfall, weekend, and performance-band metrics.
- Analyzed store performance and correlations between revenue, footfall, and stockout hours.

### Business-Level Observations
- Mumbai was the strongest store in the current analysis, with approximately INR 9.58 crore total revenue and 101.37% average target achievement.
- Pune requires the closest performance review: average target achievement was 70.71%, with 70 poor-performance days.
- Hyderabad had the highest average stockout duration at 3.85 hours.
- Overall revenue-footfall correlation was strong and positive (0.918), while revenue-stockout correlation was weak and negative (-0.152).

### Recommended Next Steps
1. Complete a separate inventory analysis, prioritizing the 14 product-store records below reorder threshold.
2. Analyze customer feedback themes and ratings, including a documented treatment for the 12 missing ratings.
3. Investigate Pune's low target achievement using daily trends, footfall, discounts, marketing spend, and stockout patterns.
4. Create charts or a dashboard to communicate store comparisons and key findings.
5. Add a conversational assistant layer only after the underlying metrics and recommendations are validated.

### Important Note
All datasets in this project are synthetic practice data. The findings demonstrate an analytical workflow and should not be presented as actual DMart business results. The current analysis shows associations, not proof of cause and effect.
