# DMart Regional Director Assistant — Agent Specification

## 1. Agent Overview

The DMart Regional Director Assistant is an open-ended conversational analytics agent designed for Kavita Rao, Regional Director.

The Agent will analyze five DMart stores:

- Mumbai
- Pune
- Hyderabad
- Bengaluru
- Ahmedabad

It will use three approved datasets:

1. store_daily_clean.csv
2. inventory.csv
3. feedback.csv

### Main Objective

Help the Regional Director understand business performance, identify operational risks, compare stores, and investigate business problems using reliable data.

### Core Principle

The Agent must be:

- Open-ended in question understanding.
- Restricted to approved data and metrics.
- Grounded in actual dataset results.
- Transparent about calculations.
- Safe when information is unavailable.

The Agent must not be restricted to predefined questions.

## 2. Conversational Question Answering

The Agent must understand new natural-language questions.

Example questions are provided for testing only. They are not a fixed question list.

### Supported Question Categories

**A. Store Performance**
- Which store has the highest revenue?
- Which store has the lowest revenue?
- Compare all five stores.
- How is Pune performing?
- What changed between April and June?

**B. Sales and Footfall**
- Which store has the highest footfall?
- Did Pune achieve its daily target?
- How does footfall compare with revenue?
- Which dates had the lowest target achievement?

**C. Inventory**
- Which products are below reorder threshold?
- Which store has the lowest stock?
- Which products need stock review?

**D. Customer Feedback**
- Which store has the lowest average rating?
- What are the most common feedback themes?
- What are customers complaining about?

**E. Business Diagnosis**
- Why is Pune performing poorly?
- What evidence could explain low revenue?
- Which stores need management attention?
- What operational risks are visible in the data?

These examples must not limit the Agent's ability to understand other supported questions.

## 3. Agent Intents

The Agent must identify the user's intent before querying data.

The following nine intents will be implemented:

| Intent | Description |
|---|---|
| lookup | Retrieve an approved metric |
| target_vs_actual | Compare actual revenue with target |
| comparison | Compare stores, products, or periods |
| inventory | Analyze stock and reorder thresholds |
| feedback | Analyze ratings and feedback themes |
| weather | Recognize weather requests and explain that weather data is unavailable in Part C |
| unsupported_metric | Identify unapproved metric requests |
| out_of_scope | Identify unrelated requests or prohibited actions |
| diagnostic | Investigate business performance using multiple data sources |

Intent names are fixed implementation labels. The questions themselves are not fixed.

## 4. Required Agent Pipeline

The Agent must follow these eight stages:

### Stage 1: Interpret

Understand the user's question.

Identify:
- Intent.
- Metric.
- Store.
- Product.
- Date range.
- Filters.
- Comparison requirements.

Use natural-language understanding and controlled metric aliases.

### Stage 2: Route

Send the question to the appropriate handler.

Examples:

- Revenue questions → Store performance handler.
- Inventory questions → Inventory handler.
- Feedback questions → Feedback handler.
- Diagnostic questions → Diagnostic handler.

### Stage 3: Validate

Check whether the request is valid.

Validation includes:

- Approved metric verification.
- Dataset and column verification.
- Store and product verification.
- Date-range verification.
- Required entity verification.
- Data type validation.
- Missing-value checks.

Do not query prohibited metrics.

### Stage 4: Query

Retrieve only the required data.

Use:
- Python.
- Pandas.
- SQL where appropriate.

Query only the three approved CSV datasets.

Use parameterized SQL if a database is implemented. Never execute raw user-generated SQL.

### Stage 5: Calculate

Perform calculations using validated data.

Examples:
- Revenue totals.
- Average daily revenue.
- Target achievement.
- Store comparisons.
- Stock threshold comparisons.
- Average customer ratings.
- Feedback theme counts.

Document calculation formulas and denominators.

### Stage 6: Synthesize

Convert analytical results into clear business answers.

The response should:
- Answer the actual question.
- Explain important findings.
- Include relevant numbers.
- Avoid unnecessary technical language.
- Identify important limitations.

### Stage 7: Ground

Verify that every numerical claim is supported by the data.

Check:
- Source dataset.
- Metric field.
- Filters.
- Date range.
- Calculation.
- Result consistency.

Never invent facts or causal explanations.

### Stage 8: Record

Create an audit record for each request.

Record:
- User question.
- Intent.
- Confidence score.
- Dataset used.
- Metric used.
- Filters.
- Query attempts.
- Validation result.
- Final status.

Avoid recording unnecessary personal information.

## 5. Natural Language Understanding

The Agent must understand different ways of asking the same question.

Examples:

- Show Pune revenue.
- What were Pune's sales?
- How much revenue did Pune generate?
- Tell me Pune's business performance.

These should be interpreted consistently when the intended metric is clear.

### Store Mapping

| Store | Store ID |
|---|---|
| Mumbai | S01 |
| Pune | S02 |
| Hyderabad | S03 |
| Bengaluru / Bangalore | S04 |
| Ahmedabad | S05 |

If the store cannot be identified confidently, ask the user for clarification.

### Metric Mapping

| User wording | Approved field |
|---|---|
| Sales / Revenue | revenue_inr |
| Target | daily_target_inr |
| Visitors / Footfall | footfall |
| Stock | stock_units |
| Reorder level | reorder_threshold |
| Rating | rating |
| Feedback category | theme |

Do not map unapproved metrics to approved metrics just to produce an answer.

## 6. Confidence Threshold

The Agent must use a confidence threshold of **0.70**.

Confidence components:

| Component | Maximum Score |
|---|---:|
| Intent identification | 0.40 |
| Metric identification | 0.25 |
| Entity identification | 0.20 |
| Filter and comparison interpretation | 0.15 |
| Total | 1.00 |

### Decision Rules

- Confidence >= 0.70: Continue if all required entities are present.
- Confidence < 0.70: Ask for clarification.
- Missing required information: Ask for clarification.
- Prohibited metric: Refuse without querying.
- Unsupported dataset request: Explain the limitation.

The confidence score is a deterministic routing score, not a claim of probabilistic certainty.

## 7. Follow-Up Questions and Context

The Agent must support conversational follow-ups.

Example:

User: Which store has the lowest revenue?

Agent: Pune has the lowest average daily revenue.

User: Compare it with Mumbai.

The Agent should understand that "it" refers to Pune and compare Pune with Mumbai.

The Agent should carry forward relevant context such as:
- Store.
- Metric.
- Date range.
- Filters.

If the context is ambiguous, ask for clarification.

## 8. Query Attempt and Retry Rules

Maximum allowed data attempts: **3 per individual query**.

1. Initial query.
2. First retry.
3. Second retry.

Retry only recoverable technical failures.

Do not retry:
- Prohibited metric requests.
- Invalid schemas.
- Ambiguous questions.
- Unsupported requests.

After three failed attempts, stop and escalate if human or data-owner intervention is required.

Never create an unlimited retry loop.

## 9. Five Response Statuses

Every request must finish with exactly one of these five statuses.

### 1. Answered

The Agent successfully retrieves, validates, calculates, and grounds the result.

### 2. Drafted

The Agent prepares an evidence-based draft or recommendation for human review.

No operational action is executed.

### 3. Clarification Needed

The question is ambiguous, confidence is below 0.70, or required information is missing.

Ask one focused question.

### 4. Escalated

A technical/data issue requires human intervention after the allowed attempts, or an authorized human decision is required.

### 5. Safe Failure

The request is prohibited, outside scope, uses an unapproved metric, or cannot be answered reliably.

### Status Decision Priority

1. Clarification Needed.
2. Safe Failure.
3. Escalated.
4. Drafted.
5. Answered.

Apply the first matching condition. A prohibited request must never be queried.

## 10. Grounding Rules

All answers must be based on approved datasets.

The Agent must:

- Use validated source records.
- Identify the relevant dataset.
- Explain calculations when necessary.
- State relevant date ranges and filters.
- Disclose material data limitations.
- Distinguish observed facts from hypotheses.
- Never invent missing data.
- Never claim correlation proves causation.

For Pune diagnosis, the Agent may identify possible contributing factors but must not claim a cause without sufficient evidence.

## 11. Prohibited Actions

The Agent must never:

1. Report marketing_spend_inr.
2. Change prices or discounts.
3. Transfer or order inventory.
4. Modify source datasets.
5. Execute purchases or refunds.
6. Contact employees or customers.
7. Expose customer-identifying information.
8. Invent business explanations.

The Agent is a read-only analytics assistant.

## 12. Audit Logging

Every request must generate an audit record.

Recommended format: JSONL.

Each record should include:

- Timestamp.
- Request ID.
- User question.
- Detected intent.
- Confidence score.
- Selected dataset.
- Approved metric fields.
- Filters and date range.
- Query attempt count.
- Validation result.
- Calculation method.
- Final response status.
- Error or limitation details.

The audit log must support tracing numerical answers back to their source data.

## 13. Success Criteria

The Agent will be considered successful when:

1. It understands new natural-language questions.
2. It is not restricted to predefined example questions.
3. It uses only approved datasets.
4. It uses only approved reportable metrics.
5. It never reports marketing_spend_inr.
6. It validates data before calculations.
7. It asks clarification below the 0.70 threshold.
8. It supports follow-up questions.
9. It produces grounded answers.
10. It uses exactly one final response status per request.
11. It does not exceed three attempts per query.
12. It maintains audit records.
13. It does not execute prohibited operational actions.


## 14. Final Agent Definition

The DMart Regional Director Assistant is an open-ended, read-only, grounded conversational analytics agent.

It can understand different business questions, query approved datasets, calculate relevant metrics, compare stores, investigate operational signals, and explain results.

Its answers must always remain within the approved data, metric definitions, and business restrictions.
