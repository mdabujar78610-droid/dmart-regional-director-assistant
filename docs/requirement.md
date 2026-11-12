# DMart Regional Director Assistant — Requirements

## 1. Project purpose and data provenance

Build an open-ended, read-only, grounded conversational analytics assistant for Kavita Rao, Regional Director, across five synthetic DMart practice stores. The assistant must understand varied natural-language questions but answer only within the approved datasets, fields, calculations, and safety rules.

All supplied datasets are synthetic assignment data. They are not actual DMart or Avenue Supermarts operational records.

## 2. Intended outcome

Deliver a reproducible, read-only analytics assistant that helps the regional director investigate store performance. The deliverable includes a traceable data-quality workflow, verified analysis, explicit agent specification, deterministic offline tests, auditable request logs, and a release decision based on fresh test evidence.

## 3. Stakeholder and stores

- Primary user: Kavita Rao, Regional Director.
- Business scenario: DMart regional operations.
- Stores: Mumbai (S01), Pune (S02), Hyderabad (S03), Bengaluru (S04), Ahmedabad (S05).

## 3. Approved datasets and grain

| Dataset | Expected rows | Grain | Date coverage |
|---|---:|---|---|
| data/store_daily_clean.csv | 450 | One store per calendar day | 2026-04-01 through 2026-06-29 |
| data/inventory.csv | 40 | One store-product snapshot | Undated snapshot |
| data/feedback.csv | 200 | One feedback record | Dates fall within the reporting quarter |

Raw source data is data/store_daily.csv (453 rows before cleaning). Do not modify raw source CSVs. The generator may recreate them deterministically only when explicitly running the documented data-generation workflow.

## 4. Exactly 11 approved reportable metrics/fields

The agent may report or calculate using only these 11 approved metric fields:

| # | Field | Dataset | Meaning |
|---:|---|---|---|
| 1 | revenue_inr | store_daily_clean.csv | Daily store revenue in INR |
| 2 | daily_target_inr | store_daily_clean.csv | Daily revenue target in INR |
| 3 | footfall | store_daily_clean.csv | Daily visitor count |
| 4 | stockout_hours | store_daily_clean.csv | Recorded daily stockout duration in hours |
| 5 | discount_pct | store_daily_clean.csv | Recorded discount percentage |
| 6 | achievement_pct | store_daily_clean.csv | Revenue target achievement percentage |
| 7 | performance_band | store_daily_clean.csv | Performance classification |
| 8 | stock_units | inventory.csv | Available stock units in the inventory snapshot |
| 9 | reorder_threshold | inventory.csv | Reorder threshold in units |
| 10 | rating | feedback.csv | Customer rating; missing ratings remain missing |
| 11 | theme | feedback.csv | Customer feedback theme/category |

No additional field is an approved reportable metric. Identifiers and dimensions may only identify, filter, group, sort, or label records.

**Explicit exclusion:** `marketing_spend_inr` is present in the raw and cleaned daily CSV for the assignment's data-generation/cleaning exercise. It is prohibited from all agent queries, calculations, summaries, grounded values, and responses. Do not use `marketing_efficiency` because it depends on the prohibited field. Never reveal, estimate, infer, or calculate marketing spend or marketing efficiency.

Other Part A derived columns (`revenue_per_footfall`, `shortfall_inr`, `weekend_flag`) are analysis-only and are not among the 11 approved agent metrics. The agent must use the approved source fields and documented formulas only.

## 5. Allowed dimensions, identifiers, and filters

Allowed dimensions/identifiers:
- `store`, `store_id`
- `date` (daily and feedback datasets only)
- `product`, `product_id` (inventory and feedback where present)
- `feedback_id` (feedback record identifier only)

Allowed store values are the five stores listed in Section 2. Allowed date filters must fall within 2026-04-01 to 2026-06-29. Date filters may be a single date or an inclusive range. Inventory has no date field and must always be described as an undated snapshot. Product filters must match available product records. Apply identical date/store filters when comparing like-for-like daily records. Do not treat identifiers as metrics.

## 6. Scope

The assistant may answer supported store-performance, target-vs-actual, footfall, stockout, discount, performance-band, inventory-threshold, customer-rating, feedback-theme, comparison, and evidence-based diagnostic questions. It may summarize records and suggest human review, but it cannot execute business operations.

Examples it should answer when the required data and filters are present:
- “Which store had the lowest mean daily revenue during the reporting period?”
- “Compare Pune and Mumbai revenue for May 2026.”
- “Did Pune meet its daily target on 2026-05-16?”
- “Which stores have Amul Milk below reorder threshold?”
- “What feedback themes were most common in Hyderabad?”

Examples it must refuse or safely limit:
- “What was Pune’s marketing spend?” — prohibited field; do not query.
- “Calculate marketing efficiency.” — depends on prohibited marketing spend.
- “Order 500 units for Pune.” — operational action not permitted.
- “Who submitted this customer rating?” — identifying information is unavailable and prohibited.
- “Prove stockouts caused Pune’s lower revenue.” — causal claim is not established by observational data.
- “Give revenue for July 2026.” — outside the supplied date range.

## 7. Verified Part A findings

The cleaned daily dataset has 450 store-days. Re-generated analysis must verify these findings from the current committed CSVs before publication:
1. Pune has the lowest mean daily revenue among the five stores.
2. Hyderabad has the highest mean stockout hours.
3. Pune does not have the highest mean stockout hours.

Do not claim that stockouts caused Pune's lower revenue. Report associations as associations, identify limitations, and do not infer causation.

## 8. Data quality and calculation rules

- Preserve all raw CSV files unchanged during cleaning and analysis.
- Remove exact duplicate daily records while retaining the first occurrence and log each removed row.
- Convert negative footfall to missing, not zero.
- Apply the two-sided store-specific IQR rule: values below Q1 − 1.5×IQR and above Q3 + 1.5×IQR are outliers. Apply the documented cap treatment to either bound and log every changed record.
- Impute missing daily footfall using the median for the same store; log each imputation.
- Do not silently convert missing values to zero.
- Preserve missing customer ratings; do not impute them.
- Verify derived columns and disclose adjusted values where material.
- State aggregation, denominator, period, filters, and source dataset for numerical claims.
- Avoid division by zero and invalid/many-to-many joins.

## 9. Agent requirements

The agent must implement nine intents: `lookup`, `target_vs_actual`, `comparison`, `inventory`, `feedback`, `weather`, `unsupported_metric`, `out_of_scope`, and `diagnostic`.

It must use a deterministic confidence threshold of **0.70**. Below 0.70, or when a material required entity is missing/ambiguous, ask one focused clarification question before querying.

The agent must use exactly one final response status per request:
1. **Answered** — validated data retrieval/calculation is grounded.
2. **Drafted** — evidence-based draft/recommendation for human review; no action executed.
3. **Clarification Needed** — confidence below 0.70 or required information is missing/ambiguous.
4. **Escalated** — recoverable technical failure remains after retries or authorized human decision is required.
5. **Safe Failure** — prohibited, unsupported, out-of-scope, out-of-range, or unreliable request.

Maximum query attempts: **3 total** (initial attempt plus at most two retries). Retry only recoverable technical errors. Never retry prohibited metrics, invalid schemas, ambiguity, or unsupported requests.

The required eight-stage pipeline is:
1. **Interpret** — identify intent, metric, store/product, date, filters, and comparison.
2. **Route** — dispatch to the appropriate supported handler.
3. **Validate** — verify approved metric, dataset, schema, entity, date, types, and data sufficiency.
4. **Query** — retrieve only required approved records using safe parameterized operations.
5. **Calculate** — calculate with explicit formula, aggregation, and denominator.
6. **Synthesize** — answer clearly and concisely with limitations.
7. **Ground** — verify every numeric claim against returned source evidence.
8. **Record** — append an auditable JSONL record with intent, confidence, source, fields, filters, attempts, validation, status, and limitations.

## 10. Prohibited actions

The agent must never:
1. Query, calculate, or report `marketing_spend_inr` or dependent marketing efficiency.
2. Change prices, discounts, targets, or store records.
3. Transfer, order, purchase, or replenish inventory.
4. Modify raw or cleaned source datasets.
5. Execute purchases, refunds, payments, or other transactions.
6. Contact employees or customers or send messages on the user's behalf.
7. expose customer-identifying or confidential personal information.
8. Invent data, fabricate evidence, or claim causation from correlation.

## 11. Decision boundary

The assistant may retrieve, calculate, compare, summarize, and propose evidence-based next steps for human review. It remains read-only: it cannot change store data, inventory, prices, targets, discounts, or business systems; place orders; contact people; or execute transactions. When evidence is incomplete, ambiguous, outside approved scope, or insufficient to establish causation, it must clarify, safely decline, or escalate rather than guess.

## 12. Acceptance and release

Run actual tests from the repository root. Do not treat committed historical outputs as proof for current code. Re-run data generation only when required, then cleaning, analysis, Part A acceptance, pytest, and the golden-set evaluation. The release gate must reflect freshly generated results and must remain NO-GO / NOT YET VALIDATED if any required condition fails or has not been executed.
