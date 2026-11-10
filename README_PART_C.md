# Part C — Grounded Conversational Analytics Agent

This implementation adds an extracted, importable `agent/` package to the existing repository. It preserves the original `Agent.zip`, Parts A and B, source CSVs, and the single `main` branch.

## Run from repository root

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m agent.run_agent
```

Required datasets in `data/`: `store_daily_clean.csv`, `inventory.csv`, and `feedback.csv`.

## Guardrails

- Queries use only the approved datasets and metric allowlist from `docs/data_context.md`.
- `marketing_spend_inr` and other unapproved metrics are rejected before query execution.
- SQL user values are parameterized; the agent is read-only.
- Inventory is explicitly treated as an undated snapshot.
- Weather is unavailable in Part C and remains a Part D responsibility.
- Diagnostic summaries are descriptive and do not claim that stockouts caused lower revenue.
- Missing feedback ratings are excluded from averages rather than converted to zero.
- Each request writes one JSONL audit record with one final status.

The interpreter is deterministic and rule-based, so unfamiliar phrasing can still require clarification. This is an honest limitation, not a claim of unrestricted language understanding.
