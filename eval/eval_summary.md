# Part D Evaluation Summary

Golden-set cases: 37  
Passed: 37/37 (100.00%)

## Cost

| Measure | Result |
|---|---:|
| Mean estimated tokens per case | 20.68 |
| Maximum estimated tokens | 39 |
| Total tool calls | 24 |
| Budget-exceeded cases | 0 |

## Latency

| Measure | Result |
|---|---:|
| Mean latency | 0.765 ms |
| 90th percentile latency (linear interpolation) | 1.663 ms |
| Maximum latency | 3.248 ms |

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

## Reproducibility notes

- The evaluation runner forces `WEATHER_MODE=stub` and writes one JSONL record per golden-set case to `eval/eval_runs.jsonl`.
- `eval/eval_results.csv` is the source for cost, latency, quality and budget metrics.
- Non-answer INR scanning uses `eval/eval_runs.jsonl` because `answer_text` is not a column in `eval_results.csv`.
