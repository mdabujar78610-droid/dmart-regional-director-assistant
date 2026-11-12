# Part D Release Gate

## Decision

**NOT YET VALIDATED** — the committed evaluation artifacts are historical and do not prove the current committed code. The latest code changes must be tested from a clean checkout before a GO decision can be made.

## Required validation

Run these commands from the repository root:

```bash
python scripts/run_acceptance.py
python scripts/run_agent_tests.py
python -m pytest -q --junitxml=pytest-results.xml
python -m eval.run_eval
```

Then inspect the newly generated `eval/eval_results.csv`, `eval/eval_runs.jsonl`, `eval/eval_summary.md`, and this release gate. Confirm that the report corresponds to the code being assessed.

## Release conditions

| Condition | Required result |
|---|---|
| Required safety, ambiguity, and context categories | Every case passes |
| Overall golden-set pass rate | At least 90% |
| Ungrounded numerical claims | 0 |
| Token-budget violations | 0 |
| Part A acceptance | Pass |
| Agent acceptance | Pass |
| Pytest | 0 failures and 0 errors |

A failed, missing, or stale result means **NO-GO**. Do not manually change this decision to GO. The evaluation builder may publish GO only from freshly generated, passing results.

## Historical evidence (not current release proof)

The previously committed 37/37 result is retained as historical evidence only. It must not be represented as validation of the current code. The weather audit records and implementation were not yet consistent with the required external-tool audit contract when the historical run was produced.

## Scope

The release decision applies only to the synthetic assignment datasets and the code/configuration tested in the corresponding run. Any subsequent code, prompt, dataset, or golden-set change requires a new complete validation run.
