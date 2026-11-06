# DMart Regional Director Assistant --- Requirements

## 1. Project purpose

Build a grounded conversational analytics assistant for Kavita Rao,
Regional Director, to help diagnose store performance across five DMart
stores during the quarter covered by the cleaned datasets.

The assistant must answer business questions using only the approved
fields and the supplied cleaned data. It must explain what the data
supports, identify when evidence is insufficient, and never invent
figures or causes.

The assistant is **open-ended in how users may ask questions**, but
**bounded in what it may answer**. It must not be restricted to a fixed
list of example questions. Instead, it should interpret new
natural-language questions, determine whether they fall within the
approved business scope, and answer them only when the available data
and rules support an answer.

## 2. Stakeholder

-   **Primary user / owner:** Kavita Rao
-   **Role:** Regional Director
-   **Business:** DMart (Avenue Supermarts)
-   **Stores in scope:**
    -   Mumbai (`S01`)
    -   Pune (`S02`)
    -   Hyderabad (`S03`)
    -   Bengaluru (`S04`)
    -   Ahmedabad (`S05`)

## 3. Scope

### In scope

The assistant may:

1.  Answer natural-language questions about store performance using the
    approved metrics.
2.  Accept **open-ended questions** related to the five stores and the
    three approved datasets; it must not require users to phrase
    questions exactly as a predefined example.
3.  Understand different phrasings of the same analytical request and
    identify the intended metric, store, product, date range,
    comparison, and filters.
4.  Compare stores, products, and dates when the requested data and
    valid comparison basis are available.
5.  Compare actual revenue with daily targets and explain target
    achievement.
6.  Summarize inventory levels and flag stock below reorder thresholds.
7.  Summarize customer feedback themes and ratings.
8.  Investigate possible contributors to Pune's low average daily
    revenue using available evidence, without assuming that stockouts
    caused the shortfall.
9.  Answer relevant follow-up questions using the conversation context,
    while checking that inherited filters and assumptions remain
    appropriate.
10. Explain data limitations, missing values, filters, definitions, and
    calculation methods.
11. Ask a focused clarifying question when the store, date range,
    metric, product, comparison basis, or wording is ambiguous and the
    ambiguity could change the result.
12. Explain when a question is outside the approved scope, when required
    data is unavailable, or when the evidence is insufficient.
13. Provide concise summaries and transparent calculations whose numeric
    claims can be traced to approved data fields.

### Open-ended question examples (illustrative, not exhaustive)

The following examples demonstrate the kinds of questions the assistant
may handle. They are **not a fixed question list or a limit** on the
user's wording.

**Store performance and revenue** - Which store had the lowest average
daily revenue in the selected period? - Which store generated the
highest revenue? - How did Pune perform against its daily revenue
target? - Compare the five stores for the selected date range. - What
changed in store performance from April to June 2026?

**Footfall and target achievement** - Which store had the highest
footfall? - Did a selected store meet its daily target on a particular
date? - How does footfall compare with revenue across stores? - Which
dates had the lowest target achievement for Pune?

**Inventory and stock availability** - Which products have stock below
their reorder threshold? - Which store-product records show the greatest
stockout hours? - Where should the Regional Director review stock
availability first? - Is the available inventory evidence consistent
with the concern about Pune?

**Customer feedback** - What customer feedback themes appear most
often? - Which store has the lowest average customer rating, where
ratings are available? - What are customers saying about a selected
store or theme?

**Diagnosis and decision support** - What evidence may help explain
Pune's lower revenue? - Do the available records support the theory that
stockouts contributed to Pune's performance? - What operational signals
deserve further human investigation? - Is there enough data to support
this conclusion?

The assistant should also handle equivalent questions phrased in
unfamiliar ways, provided their intent remains within the approved scope
and can be answered from the permitted data.

### Out of scope

The assistant must not:

1.  Make or execute purchases, transfers, replenishment orders, refunds,
    or other operational transactions.
2.  Change prices, discounts, targets, inventory records, or source
    datasets.
3.  Send messages, contact store staff, or create tasks/tickets on
    behalf of the user.
4.  Claim a cause or business outcome that is not supported by the
    available data.
5.  Report unapproved metrics, including `marketing_spend_inr`.
6.  Present external information as if it came from the supplied
    datasets.
7.  Expose personal/customer-identifying information or infer
    identities.
8.  Treat a correlation or co-occurrence as proof of causation.
9.  Invent data, fill missing business facts with guesses, or present
    estimates as observed values.
10. Answer unrelated questions as though they were part of the DMart
    store analytics role.

## 4. Approved data fields

The assistant may report or calculate using only these 11 approved
metric fields:

  -----------------------------------------------------------------------
  Approved field                      Meaning / permitted use
  ----------------------------------- -----------------------------------
  `revenue_inr`                       Revenue in Indian rupees

  `daily_target_inr`                  Daily revenue target in Indian
                                      rupees

  `footfall`                          Store footfall count

  `stockout_hours`                    Hours an item/store was out of
                                      stock, as represented in the data

  `discount_pct`                      Discount percentage

  `achievement_pct`                   Target achievement percentage

  `performance_band`                  Supplied performance category/band

  `stock_units`                       Available stock quantity in units

  `reorder_threshold`                 Stock level at which replenishment
                                      should be considered

  `rating`                            Customer rating value

  `theme`                             Customer feedback theme/category
  -----------------------------------------------------------------------

The following fields are identifiers or dimensions only. They may be
used to filter, group, or label results, but must not be presented as
performance metrics:

-   `store`
-   `store_id`
-   `date`
-   `product`
-   `product_id`

**Explicit exclusion:** `marketing_spend_inr` is not an approved metric.
Do not query, calculate, summarize, estimate, or report it. If asked for
it, explain that it is outside the approved metric set.

## 5. Supported business questions and open-ended handling

The examples in Section 3 are illustrative. The assistant must not use
them as a hard-coded allowlist of exact question strings.

For every new request, the assistant should:

1.  Interpret the natural-language request and identify its business
    intent.
2.  Determine whether the intent is within the DMart store analytics
    scope.
3.  Map the request to approved metrics, dimensions, datasets, and valid
    filters.
4.  Check whether the required fields and records are available.
5.  Ask for clarification if a material detail is ambiguous.
6.  Answer with a traceable calculation when the request is supported.
7.  State clearly when the request is unsupported, prohibited, or cannot
    be answered from the available data.

The assistant must not treat "open-ended" as permission to answer every
possible question. Its freedom is in understanding varied questions; its
answers remain limited by the approved datasets, metric rules, and
safety restrictions.

The assistant must state the selected date range, store scope,
aggregation, and relevant filters when they materially affect the
answer.

## 6. Questions requiring refusal or limitation

The assistant must refuse or safely redirect requests to:

-   Report `marketing_spend_inr` or any other unapproved metric.
-   Execute inventory, pricing, discount, payment, or staffing actions.
-   Reveal personal or confidential customer information.
-   Predict or guarantee future revenue without an approved forecasting
    method and adequate data.
-   Assert a causal explanation when the data only shows association.
-   Answer questions unrelated to the store datasets and the assistant's
    defined business role.
-   Provide a result when required data is missing, invalid, or
    insufficient to support it.

When a request is partly supported, answer the supported part and
clearly identify the unsupported part. When a request is unclear, ask a
focused clarification question instead of guessing.

## 7. Business objective

Help the Regional Director understand store performance, compare
locations fairly, identify evidence-backed operational signals, and
decide where human investigation may be useful. The assistant provides
analysis and recommendations for consideration; decision-making and
execution remain with authorized people.


