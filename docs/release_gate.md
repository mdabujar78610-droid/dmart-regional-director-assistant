# Part D Release Gate

## Decision

**NOT YET VALIDATED** — the agent, weather-routing, and numeric-audit code has changed since the committed evaluation artifacts were generated. The previous 37/37 result is historical evidence only and must not be treated as validation of the current code.

| Condition | Required result | Current state |
|---|---|---|
| Safety, ambiguity and context categories | All required cases pass | Pending fresh evaluation |
| Overall golden-set pass rate | At least 90% | Pending fresh evaluation |
| Ungrounded numeric claims | 0 | Pending fresh evaluation |
| Token budget | No case exceeds the configured budget | Pending fresh evaluation |
| Agent acceptance tests | All 20 acceptance cases pass under pytest | Pending execution |

## Required validation

Run these commands from the repository root after installing `requirements.txt`:

```bash
python -m pytest -q
python -m eval.run_eval
```

Then review the newly generated `eval/eval_results.csv`, `eval/eval_runs.jsonl`, and `eval/eval_summary.md`. Confirm that the summary matches the current code and that every required safety/context category passes before changing this decision to **GO**.

## Scope and evidence

- Golden set: 37 cases in `eval/golden_set.csv`.
- The previously committed evaluation artifacts reported 37/37 passing cases, but predate the latest code changes.
- Raw source datasets must remain unchanged.
- The release decision must be regenerated after any code, dataset, specification, or golden-set change.
