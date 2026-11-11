# Part D Release Gate

## Decision

**GO** — all four required conditions pass in the currently committed evaluation artifacts.

| Condition | Measured value | Result |
|---|---|---|
| 1. Required safety, ambiguity and context categories pass | 12/12 cases pass across unsupported_metric, out_of_scope, out_of_range_date, injection, ambiguity, unresolved_store and unresolved_date | PASS |
| 2. Overall pass rate is at least 90% | 37/37 = 100.00% (threshold 90%) | PASS |
| 3. Total ungrounded numbers equals zero | 0 | PASS |
| 4. No case exceeds the token budget | 0 budget-exceeded cases | PASS |

## Failed cases

None. All golden-set cases passed their expected status, intent and required-content checks.

## Scope and evidence

- Golden set: 37 cases (`eval/golden_set.csv`).
- Evaluation output: `eval/eval_results.csv` (37 passed, 0 failed).
- Per-case answer and audit records: `eval/eval_runs.jsonl` (37 records).
- Summary metrics: `eval/eval_summary.md`.
- The category-level gate includes every case in unsupported_metric, out_of_scope, out_of_range_date, injection, ambiguity, unresolved_store and unresolved_date.

The release decision is based on the committed evaluation artifacts. Any future code, dataset, specification or golden-set change requires rerunning the evaluation before relying on this decision.
