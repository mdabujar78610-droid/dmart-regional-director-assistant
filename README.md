# DMart Regional Director Assistant

A data-driven retail diagnosis and grounded conversational analytics project for five synthetic DMart practice stores: Mumbai, Pune, Hyderabad, Bengaluru and Ahmedabad.

The project examines Pune's lower average daily revenue and implements a read-only conversational analytics agent. Every reported business number must be traceable to approved fields in the supplied datasets. **All datasets are synthetic practice data, not actual DMart business records.**

## Repository structure

```text
dmart-regional-director-assistant/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── store_daily.csv
│   ├── inventory.csv
│   ├── feedback.csv
│   └── store_daily_clean.csv
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── analyze.py
│   ├── run_acceptance.py
│   └── run_agent_tests.py
├── analysis/
│   ├── data_quality_report.md
│   ├── cleaning_log.csv
│   ├── findings.md
│   └── executive_summary.md
├── docs/
│   ├── requirement.md
│   ├── data_context.md
│   ├── agent_spec.md
│   └── release_gate.md
├── agent/
│   ├── __init__.py
│   ├── understand.py
│   ├── fetch.py
│   ├── answer.py
│   └── run_agent.py
├── tools/
│   ├── __init__.py
│   └── weather.py
├── tests/
│   ├── test_agent.py
│   └── weather_tool_tests.md
├── outputs/
│   └── acceptance_transcript.md
├── logs/
│   └── runs.jsonl
└── eval/
    ├── __init__.py
    ├── golden_set.csv
    ├── golden_set_derivation.md
    ├── run_eval.py
    ├── build_reports.py
    ├── eval_results.csv
    ├── eval_runs.jsonl
    └── eval_summary.md
```

## Setup

Requirements: Python 3.9 or later, pandas and numpy.

```bash
python -m pip install -r requirements.txt
```

## Run the project

Run commands from the repository root.

### Part A — Data generation, cleaning and analysis

Run these in order:

```bash
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/analyze.py
python scripts/run_acceptance.py
```

The generator is seeded and deterministic. It creates synthetic source data; the cleaning script writes a separate cleaned dataset and an audit log. Do not manually edit the generated raw CSV files.

### Part C — Conversational analytics agent

```bash
python scripts/run_agent_tests.py
python -m agent.run_agent
```

The agent uses a local in-memory SQLite data layer and the approved cleaned daily, inventory and feedback datasets. Each request is recorded in `logs/runs.jsonl`. The agent is read-only: it does not execute store operations or modify source data.

### Part D — Weather tool and evaluation

The weather adapter supports deterministic offline stub mode and optional Open-Meteo historical weather mode. Offline evaluation forces stub mode.

```bash
python -m eval.run_eval
```

This runs the committed golden set and regenerates:
- `eval/eval_results.csv`
- `eval/eval_runs.jsonl`
- `eval/eval_summary.md`
- `docs/release_gate.md`

## Project findings

The cleaned daily dataset contains 450 store-days covering 1 April 2026 through 29 June 2026. Pune has the lowest mean daily revenue among the five stores, but the available data do not show that Pune has the highest mean stockout duration. The stockout explanation is therefore not supported by this evidence. Correlation and co-occurrence do not establish causation.

See:
- `analysis/data_quality_report.md`
- `analysis/cleaning_log.csv`
- `analysis/findings.md`
- `analysis/executive_summary.md`

## Agent scope and safeguards

The agent can answer supported questions about store revenue, targets, footfall, stockout hours, discounts, achievement, performance bands, inventory thresholds and customer feedback.

It must:
- Use only the approved datasets and approved reportable metrics.
- Never query or report `marketing_spend_inr`.
- Validate stores, dates, products, fields and data availability.
- Ask for clarification when material information is ambiguous.
- Ground numerical claims in source records and disclose limitations.
- Treat inventory as an undated snapshot.
- Avoid causal claims that the data cannot establish.
- Remain read-only and refuse prohibited operational actions.

See `docs/requirement.md`, `docs/data_context.md` and `docs/agent_spec.md` for the detailed specification.

## Evaluation evidence

The committed golden set contains 37 cases. The currently committed evaluation artifacts report 37/37 passing cases; rerun `python -m eval.run_eval` after any code, dataset, specification or golden-set change before relying on the release decision in `docs/release_gate.md`.

## Limitations

- The datasets are synthetic and must not be represented as actual DMart operational records.
- The reporting period is limited to 2026-04-01 through 2026-06-29.
- The analysis is descriptive and observational; it cannot prove why revenue differs between stores.
- Inventory is an undated snapshot and must not be interpreted as historical inventory.
- The agent is a bounded, deterministic analytics assistant, not an autonomous store-operations system.
