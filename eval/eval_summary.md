# Part D Evaluation Summary

Golden-set cases: 37  
Passed: 37/37 (100.00%)

## Cost

| Measure | Result |
|---|---:|
| Mean estimated tokens per case | 21.30 |
| Maximum estimated tokens | 38 |
| Total tool calls | 24 |
| Budget-exceeded cases | 0 |

## Latency

| Measure | Result |
|---|---:|
| Mean latency | 1.054 ms |
| 90th percentile latency (linear interpolation) | 1.763 ms |
| Maximum latency | 12.973 ms |

## Quality

- Overall pass rate: **100.00% (37/37)**.
- Total `ungrounded_numbers`: **0**.

| Category | Passed | Total |
|---|---:|---:|
| ambiguity | 3 | 3 |
| comparison | 3 | 3 |
| context_setup | 2 | 2 |
| diagnostic | 1 | 1 |
| feedback | 1 | 1 |
| injection | 1 | 1 |
| inventory | 1 | 1 |
| lookup | 5 | 5 |
| out_of_range_date | 2 | 2 |
| out_of_scope | 2 | 2 |
| retry | 2 | 2 |
| synonym | 1 | 1 |
| target_vs_actual | 3 | 3 |
| typo | 2 | 2 |
| unresolved_date | 1 | 1 |
| unresolved_store | 1 | 1 |
| unsupported_metric | 2 | 2 |
| weather | 2 | 2 |
| weather_ignored | 1 | 1 |
| weather_range | 1 | 1 |

## Safety

- Injection + unsupported_metric + out_of_scope pass rate: **5/5 (100.00%)**.
- Non-answer replies containing an INR figure: **0**.
- `.gitignore` lists `.env`: **Yes**.
- Pytest evidence: **5 tests, 0 failures, 0 errors**; report present: **Yes**.

## Reproducibility notes

- The evaluation runner forces `WEATHER_MODE=stub` and writes one JSONL record per golden-set case to `eval/eval_runs.jsonl`.
- `eval/eval_results.csv` is the source for cost, latency, quality and budget metrics.
- Non-answer INR scanning uses `eval/eval_runs.jsonl` because `answer_text` is not a column in `eval_results.csv`.
