# Project Handover

**Project:** DMart Regional Director Assistant: Store Diagnosis and a Grounded Conversational Analytics Agent  
**Handover date:** 12 November 2026  
**Repository:** https://github.com/mdabujar78610-droid/dmart-regional-director-assistant

## Project purpose

This repository contains a read-only, deterministic analytics assistant built around synthetic practice data for five stores: Mumbai, Pune, Hyderabad, Bengaluru and Ahmedabad. The datasets are not actual DMart business records.

## Verified baseline

GitHub Actions run [#43142990496](https://github.com/mdabujar78610-droid/dmart-regional-director-assistant/actions/runs/43142990496) completed successfully on baseline commit `445006102bf12eb3c095be6bc5aa2186da65f724` on 12 November 2026.

| Check | Recorded result |
|---|---:|
| Part A cleaning and acceptance | PASS |
| Cleaned daily data | 450 rows × 15 columns |
| Exact duplicate rows removed | 3 |
| Pytest | 2 passed |
| Golden evaluation | 37/37 passed |
| Evaluation release decision on baseline commit only | GO (historical; not applicable to current `main`) |
| GitHub Actions workflow | Success |

The workflow logs also show that analysis reports were regenerated and validation artifacts were uploaded to the Actions run.

## Current release status

The current `main` branch has a recorded **GO** release decision in `docs/release_gate.md`.

Latest verified evidence:
- Evidence commit: `cd522147d4ccf96043690745e77e14fa39224804`.
- Part D GitHub Actions run [#43154923914](https://github.com/mdabujar78610-droid/dmart-regional-director-assistant/actions/runs/43154923914): completed successfully.
- Part A validation workflow run [#43154788967](https://github.com/mdabujar78610-droid/dmart-regional-director-assistant/actions/runs/43154788967): successful.
- Part C acceptance: 20/20 passed.
- Agent acceptance checks: 20/20 passed.
- Pytest: 5 passed, 0 failures.
- Golden-set evaluation: 37/37 passed (100%).
- Required safety, ambiguity, and context categories: 12/12 passed.
- Ungrounded numeric claims: 0.
- Token-budget violations: 0.
- Release decision: **GO**, according to the assignment's four documented release conditions.

The evidence commit updates `docs/release_gate.md`, `eval/eval_results.csv`, `eval/eval_runs.jsonl`, `eval/eval_summary.md`, `logs/runs.jsonl`, and `outputs/acceptance_transcript.md`. The decision applies to the code and evidence tested at that commit; rerun validation after any relevant code, prompt, dataset, or golden-set change.

## Final presentation review

The repository has a responsibility-based folder structure and a root README describing the project, datasets, approved metric boundaries, setup, execution, evaluation, and limitations. Before submission, manually open the README and key evidence files in GitHub to confirm they render as expected. No additional feature work is required by the current recorded release gate.

## Reproduction commands

Run from the repository root after installing dependencies:

```bash
python -m pip install -r requirements.txt
python scripts/clean_data.py
python scripts/analyze.py
python scripts/run_acceptance.py
python scripts/run_agent_tests.py
python -m pytest -q --junitxml=pytest-results.xml
python -m eval.run_eval
```

## Known limitations

- The data is synthetic and covers 1 April 2026 through 29 June 2026.
- Inventory is an undated snapshot.
- Descriptive correlations do not establish causation.
- The agent is deterministic and read-only; it is not an autonomous store-operations system.
