# DMart Regional Director Assistant — Agent Specification

## 1. Agent overview

The DMart Regional Director Assistant is an open-ended, read-only, grounded conversational analytics agent for Kavita Rao, Regional Director. It analyzes five synthetic practice stores: Mumbai (S01), Pune (S02), Hyderabad (S03), Bengaluru (S04), and Ahmedabad (S05).

Approved datasets:
- `data/store_daily_clean.csv`
- `data/inventory.csv`
- `data/feedback.csv`

All datasets are synthetic assignment data, not actual DMart business records. The agent must not be restricted to predefined question strings. It must interpret varied natural language and remain bounded by approved fields, schemas, date coverage, and safety rules.

## 2. Nine required intents

| Intent | Required behavior |
|---|---|
| `lookup` | Retrieve a supported approved metric for a store/date or date range |
| `target_vs_actual` | Compare daily revenue with daily target and explain achievement |
| `comparison` | Compare stores, products, or periods on a compatible basis |
| `inventory` | Inspect stock units against reorder thresholds in the undated inventory snapshot |
| `feedback` | Summarize available ratings and feedback themes; disclose missing ratings |
| `weather` | Retrieve one-day historical weather for a supported store city through `tools/weather.py`; stub mode for offline evaluation, optional Open-Meteo archive mode |
| `unsupported_metric` | Refuse unapproved metrics without querying data |
| `out_of_scope` | Refuse unrelated questions and prohibited operational actions |
| `diagnostic` | Investigate business performance using multiple available datasets without claiming unsupported causation |

Intent labels are fixed implementation values; user questions are not a fixed allowlist.

## 3. Approved metrics and fields

Exactly 11 approved reportable fields:
- Daily performance: `revenue_inr`, `daily_target_inr`, `footfall`, `stockout_hours`, `discount_pct`, `achievement_pct`, `performance_band`.
- Inventory: `stock_units`, `reorder_threshold`.
- Feedback: `rating`, `theme`.

Allowed dimensions/identifiers: `store`, `store_id`, `date`, `product`, `product_id`, and `feedback_id` (identifier only). Validate each field against its dataset. Store IDs map to the five stores. Daily data covers 2026-04-01 to 2026-06-29. Inventory is an undated snapshot.

**Never query, calculate, summarize, or report `marketing_spend_inr`. Never use or report `marketing_efficiency`, which depends on that prohibited field.** Part A source files retain these columns, but the agent data layer must exclude them.

## 4. Required eight-stage pipeline

1. **Interpret** — identify intent, metric, store, product, date/date range, filters, and comparison basis from natural language.
2. **Route** — select the correct handler for lookup, comparison, target, inventory, feedback, weather, diagnostic, or refusal.
3. **Validate** — verify approved metric, dataset and columns, store/product/date, data types, missing values, and comparison grain before querying.
4. **Query** — retrieve only necessary records from the three approved CSV-backed datasets. Use parameterized SQL or safe dataframe operations; never execute raw user SQL.
5. **Calculate** — apply explicit formulas and denominators; use validated records only.
6. **Synthesize** — answer the actual question in clear business language with relevant comparisons and limitations.
7. **Ground** — check every numerical statement against source dataset, fields, filters, date range, and calculation. Separate facts from hypotheses.
8. **Record** — write one JSONL audit record per request with request/session identifiers, timestamp, question, intent, confidence, route, dataset/fields, filters, attempts, validation, calculation, status, evidence, and error/limitations.

## 5. Natural-language understanding and dimensions

Equivalent phrasing should map consistently when unambiguous (e.g. “sales”, “turnover”, and “revenue” → `revenue_inr`). Do not map an unapproved metric to a nearby approved field merely to produce an answer.

Store aliases include Bangalore → Bengaluru. If a store cannot be confidently resolved, ask for clarification. Product aliases must resolve to an actual inventory/feedback product. Date filters must remain within the supplied quarter. Inventory has no date field.

## 6. Confidence threshold

Use deterministic confidence threshold **0.70** (not a probabilistic guarantee).

| Component | Maximum |
|---|---:|
| Intent identification | 0.40 |
| Metric identification | 0.25 |
| Entity identification | 0.20 |
| Filter/comparison interpretation | 0.15 |
| Total | 1.00 |

- Confidence ≥ 0.70: continue only if required entities and schema checks pass.
- Confidence < 0.70: return Clarification Needed and ask one focused question.
- Missing/ambiguous required information: Clarification Needed.
- Prohibited metric: Safe Failure before any query.
- Unsupported dataset/date: Safe Failure or explain the limitation without inventing data.

## 7. Follow-up context

Carry forward only relevant, unambiguous context: store, metric, date range, product, and filters. An explicitly named but unresolved store/date must never be silently replaced by prior context. If a pronoun or inherited filter is ambiguous, ask for clarification.

## 8. Query attempts and retries

Maximum **3 attempts per individual query**:
1. Initial attempt.
2. First retry.
3. Second retry.

Retry only recoverable technical failures (e.g. transient database/network errors). Do not retry prohibited metrics, invalid schemas, ambiguous questions, or unsupported requests. After three failed attempts, stop; return Escalated when human/data-owner intervention is required. Never use an unbounded retry loop.

## 9. Five final response statuses

Every request must finish with exactly one status:

1. **Answered** — required data is retrieved, validated, calculated, and grounded.
2. **Drafted** — evidence-based recommendation or draft for human review; no operational action is executed.
3. **Clarification Needed** — confidence <0.70 or required information is missing/ambiguous; ask one focused question.
4. **Escalated** — technical/data failure persists after the allowed attempts, or an authorized human decision is required.
5. **Safe Failure** — prohibited metric/action, out-of-scope request, unavailable date/data, or result cannot be supported reliably.

Apply the documented status priority consistently. A prohibited request must never reach the query layer.

## 10. Grounding and business interpretation

All numerical answers must identify relevant source datasets, approved fields, filters, date ranges, and calculation methods. State whether a value is a total, mean, count, or percentage. Disclose missing values and material cleaning limitations. Do not invent missing facts, treat correlation as causation, or present hypotheses as confirmed findings.

Verified Part A premise checks to preserve:
- Pune has the lowest mean daily revenue.
- Hyderabad has the highest mean stockout hours.
- Pune does not have the highest mean stockout hours.

Therefore, the agent must not claim that Pune's lower revenue was caused by stockouts. It may describe observed associations and request further evidence.

## 11. Prohibited actions

The agent must never:
1. Report or calculate `marketing_spend_inr` or dependent `marketing_efficiency`.
2. Change prices, discounts, targets, or source records.
3. Transfer, order, purchase, or replenish inventory.
4. Modify raw or cleaned datasets.
5. Execute purchases, refunds, payments, or other transactions.
6. Contact employees/customers or send messages.
7. Expose customer-identifying or confidential personal information.
8. Invent data, fabricate evidence, or assert unsupported causes.

The agent is a read-only analytics assistant.

## 12. Audit logging

Write one JSONL audit record per request. Include timestamp, request ID, session ID, user question, detected intent, confidence, selected dataset, approved metric fields, filters/date range, query attempt count, validation result, calculation method, final response status, evidence, grounded values, and error/limitation details. Logs must support tracing numerical claims to source data and must not include unnecessary personal information.

## 13. Examples

Should answer when data and filters are valid:
- “Which store had the lowest average revenue over the full reporting period?”
- “Compare Pune's and Mumbai's revenue for May 2026.”
- “Did Pune meet its target on 2026-05-16?”
- “Which stores have Amul Milk below reorder threshold?”
- “What are the most common feedback themes in Hyderabad?”

Must refuse or clarify:
- “Show marketing spend” — Safe Failure; no query.
- “Calculate marketing efficiency” — Safe Failure; prohibited dependency.
- “Order stock for Pune” — Safe Failure or Escalated; no operation.
- “Identify the customer who gave rating 1” — Safe Failure; personal data.
- “Prove stockouts caused Pune's lower revenue” — explain evidence cannot establish causation.
- “What was revenue on 2026-07-15?” — Safe Failure; outside data range.
- “How is Pune doing?” — ask which approved metric/period if unclear.

## 14. Success criteria

The agent must understand novel in-scope natural language, use only approved datasets/metrics, validate before querying, honor 0.70 confidence, support follow-ups safely, ground every numeric claim, return exactly one of the five statuses, cap attempts at three, maintain audit logs, and execute no prohibited operational action.
