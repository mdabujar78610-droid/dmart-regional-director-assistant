# Part D Release Gate

## Decision

**GO** — all four assignment release conditions pass.

| Condition | Measured value | Result |
|---|---|---|
| 1. All cases in required safety/ambiguity/context categories pass | 12/12 cases pass across: unsupported_metric, out_of_scope, out_of_range_date, injection, ambiguity, unresolved_store, unresolved_date | PASS |
| 2. Overall pass rate is at least 90% | 37/37 = 100.00% (threshold 90%) | PASS |
| 3. Total ungrounded numbers equals zero | 0 | PASS |
| 4. No case exceeds the token budget | 0 budget-exceeded cases | PASS |

## Test evidence (informational; not an additional release condition)

- Pytest: 5 tests; 0 failures; 0 errors; report present=True; PASS.

## Failed cases

None. All golden-set cases passed their expected status, intent and required-content checks.

## Scope and evidence

- Golden set: 37 cases (`eval/golden_set.csv`).
- Evaluation output: `eval/eval_results.csv` (37 passed, 0 failed).
- Per-case answer and audit records: `eval/eval_runs.jsonl` (37 lines).
- Summary metrics: `eval/eval_summary.md`.
- The category-level gate includes every case in unsupported_metric, out_of_scope, out_of_range_date, injection, ambiguity, unresolved_store and unresolved_date.
- Pytest results are supplementary test evidence and are not an additional release condition beyond the four assignment rules.

The release decision is computed from the recorded evaluation values above. Any future code, prompt, dataset or golden-set change requires rerunning the evaluation before relying on this decision.
