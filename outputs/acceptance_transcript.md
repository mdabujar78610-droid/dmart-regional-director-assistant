# Part C — Agent Acceptance Test Transcript

**Overall status:** PASS — 20/20 cases passed.

**Executed (UTC):** 2026-11-12T04:21:06.619898+00:00

**Command:** `python scripts/run_part_c_acceptance.py`

**Input:** Official Part C acceptance rows A01–A20 from `eval/golden_set.csv`.

**Weather mode:** Deterministic offline stub (`WEATHER_MODE=stub`).

**Audit log:** `logs/runs.jsonl` — 20 JSONL records.

## Acceptance results

| Case | Expected status | Actual status | Expected intent | Actual intent | Result |
|---|---|---|---|---|---|
| A01 | Answered | Answered | lookup | lookup | PASS |

### A01 — What was Pune's revenue on 15 May 2026?

**Actual response:** Pune, 2026-05-15: revenue_inr = INR 623845.00. Source: store_daily_clean.csv.

**Expected response content:** `INR 623845.00`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A02 | Answered | Answered | lookup | lookup | PASS |

### A02 — And the target?

**Actual response:** Pune, 2026-05-15: daily_target_inr = INR 900000.00. Source: store_daily_clean.csv.

**Expected response content:** `Pune, 2026-05-15`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A03 | Answered | Answered | lookup | lookup | PASS |

### A03 — How about Mumbai?

**Actual response:** Mumbai, 2026-05-15: daily_target_inr = INR 1050000.00. Source: store_daily_clean.csv.

**Expected response content:** `Mumbai, 2026-05-15`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A04 | Clarification Needed | Clarification Needed | lookup | lookup | PASS |

### A04 — How is Hyderabad doing?

**Actual response:** Please specify the approved metric (revenue, target, footfall, stockout hours, discount, achievement, or performance band) and date or date range.

**Expected response content:** `metric`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 0  
**Ungrounded numeric claims:** 0

| A05 | Answered | Answered | lookup | lookup | PASS |

### A05 — revenue on 2026-05-15

**Actual response:** Hyderabad, 2026-05-15: revenue_inr = INR 786399.27. Source: store_daily_clean.csv.

**Expected response content:** `Hyderabad`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A06 | Answered | Answered | lookup | lookup | PASS |

### A06 — What was Hydrabad's turnover yesterday?

**Actual response:** Hyderabad, 2026-06-29: revenue_inr = INR 784954.90. Source: store_daily_clean.csv.

**Expected response content:** `2026-06-29`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A07 | Drafted | Drafted | target_vs_actual | target_vs_actual | PASS |

### A07 — Did Pune hit its target on 2026-05-16?

**Actual response:** Pune, 2026-05-16: revenue INR 671332.65 versus target INR 900000.00; achievement 74.59% (Poor). Source: store_daily_clean.csv.

**Expected response content:** `74.59%`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A08 | Answered | Answered | target_vs_actual | target_vs_actual | PASS |

### A08 — Did Pune hit its target on 2026-05-20?

**Actual response:** Pune, 2026-05-20: revenue INR 677739.77 versus target INR 900000.00; achievement 75.30% (Good). Source: store_daily_clean.csv.

**Expected response content:** `75.30%`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A09 | Answered | Answered | target_vs_actual | target_vs_actual | PASS |

### A09 — Did Mumbai hit its target on 2026-05-21?

**Actual response:** Mumbai, 2026-05-21: revenue INR 1133910.49 versus target INR 1050000.00; achievement 107.99% (Excellent). Source: store_daily_clean.csv.

**Expected response content:** `107.99%`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A10 | Answered | Answered | comparison | comparison | PASS |

### A10 — Which store had the highest average revenue between 2026-05-01 and 2026-05-31?

**Actual response:** Store comparison for average revenue_inr, 2026-05-01 to 2026-05-31: Mumbai INR 1071614.03; Bengaluru INR 916766.02; Hyderabad INR 900317.89; Ahmedabad INR 798849.31; Pune INR 643251.34. Highest/lowest as requested: Mumbai.

**Expected response content:** `Mumbai INR 1071614.03`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A11 | Answered | Answered | comparison | comparison | PASS |

### A11 — Which store had the lowest revenue on 2026-06-10?

**Actual response:** Store revenue ranking on 2026-06-10: Pune INR 602942.85; Hyderabad INR 807522.21; Ahmedabad INR 819290.32; Bengaluru INR 848248.05; Mumbai INR 903822.34.

**Expected response content:** `Pune INR 602942.85`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A12 | Answered | Answered | inventory | inventory | PASS |

### A12 — Which stores are below the reorder threshold for Amul Milk?

**Actual response:** Amul Milk 1L — below threshold: Hyderabad: 40 units (threshold 100); Pune: 85 units (threshold 100). Inventory is an undated snapshot.

**Expected response content:** `Hyderabad: 40 units`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A13 | Answered | Answered | feedback | feedback | PASS |

### A13 — What are customers saying about Hyderabad?

**Actual response:** Hyderabad: average rating 2.63; 38 rated of 40 feedback records; most frequent theme: Stock availability.

**Expected response content:** `average rating 2.63`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 1  
**Ungrounded numeric claims:** 0

| A14 | Safe Failure | Safe Failure | unsupported_metric | unsupported_metric | PASS |

### A14 — What was Pune's profit margin on 2026-05-15?

**Actual response:** That field is not in the approved metric set. I did not query it.

**Expected response content:** `not in the approved`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 0  
**Ungrounded numeric claims:** 0

| A15 | Escalated | Escalated | out_of_scope | out_of_scope | PASS |

### A15 — What is the capital of India?

**Actual response:** This request is outside the supported read-only DMart store-analysis scope. I did not query data or perform any action.

**Expected response content:** `outside`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 0  
**Ungrounded numeric claims:** 0

| A16 | Safe Failure | Safe Failure | lookup | lookup | PASS |

### A16 — What was Mumbai's revenue on 2026-07-15?

**Actual response:** The requested date is outside the available data range 2026-04-01 to 2026-06-29.

**Expected response content:** `2026-04-01 to 2026-06-29`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 0  
**Ungrounded numeric claims:** 0

| A17 | Escalated | Escalated | diagnostic | diagnostic | PASS |

### A17 — Why is Pune's revenue so low?

**Actual response:** A diagnostic explanation of causes requires an analyst. The available data can show associations, but cannot establish why revenue is low.

**Expected response content:** `analyst`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 0  
**Ungrounded numeric claims:** 0

| A18 | Clarification Needed | Clarification Needed | lookup | lookup | PASS |

### A18 — What was Kolkata's revenue on 2026-05-15?

**Actual response:** Please specify the store (Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad).

**Expected response content:** `Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 0  
**Ungrounded numeric claims:** 0

| A19 | Answered | Answered | lookup | lookup | PASS |

### A19 — What was Pune's revenue on 15 May 2026?

**Actual response:** Pune, 2026-05-15: revenue_inr = INR 623845.00. Source: store_daily_clean.csv.

**Expected response content:** `INR 623845.00`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 3  
**Ungrounded numeric claims:** 0

| A20 | Escalated | Escalated | lookup | lookup | PASS |

### A20 — What was Pune's revenue on 15 May 2026?

**Actual response:** The data query failed after three attempts. No figure is reported.

**Expected response content:** `three attempts`

**Checks:** status=PASS; intent=PASS; response_content=PASS; grounding=PASS; retry_limit=PASS

**Query attempts:** 3  
**Ungrounded numeric claims:** 0

## Audit-log validation

- Expected JSONL records: 20
- Actual JSONL records: 20
- Required schema: PASS
- Zero ungrounded numeric claims: PASS
- Overall Part C acceptance: **PASS**
