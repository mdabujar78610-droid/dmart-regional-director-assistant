# DMart Regional Director Assistant

**Store Diagnosis and a Grounded Conversational Analytics Agent**

## 1. Project overview

The DMart Regional Director Assistant is a read-only, grounded conversational analytics project for a regional director overseeing five synthetic DMart practice stores: Mumbai (S01), Pune (S02), Hyderabad (S03), Bengaluru (S04), and Ahmedabad (S05).

The project investigates store performance, tests the premise that Pune's lower average revenue is explained by stockouts, and implements a deterministic conversational agent that answers supported business questions from approved datasets.

**Data provenance:** All CSV files are synthetic assignment data. They are not actual DMart or Avenue Supermarts operational records.

## 2. Project scope

The repository combines the four assignment parts into one project:

| Part | Project work | Main deliverables |
|---|---|---|
| **A — Data Foundation and Analysis** | Generate and inspect source datasets, clean daily data, document data quality, analyze store performance, and test the Pune stockout premise. | `data/`, `scripts/generate_data.py`, `scripts/clean_data.py`, `scripts/analyze.py`, `analysis/`, Part A acceptance output. |
| **B — Agent Specification** | Define the business requirements, data context, approved metrics, intents, pipeline, validation, safety rules, and acceptance criteria. | `docs/requirement.md`, `docs/data_context.md`, `docs/agent_spec.md`. |
| **C — Conversational Analytics Agent** | Interpret natural-language questions, route supported intents, validate requests, retrieve approved data, calculate and ground answers, and record request traces. | `agent/`, `logs/runs.jsonl`, `outputs/acceptance_transcript.md`. |
| **D — Weather and Evaluation** | Provide historical weather through an offline stub or optional live adapter, evaluate the golden set, and maintain the release decision. | `tools/weather.py`, `tests/weather_tool_tests.md`, `eval/`, `docs/release_gate.md`. |

## 3. Repository structure

The folders are organized by project responsibility, not by assignment-part labels. The conversational agent implementation is kept in `agent/`.

```text
dmart-regional-director-assistant/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── store_daily.csv
│   ├── store_daily_clean.csv
│   ├── inventory.csv
│   └── feedback.csv
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
│   ├── handover.md
│   └── release_gate.md
├── agent/
│   ├── understand.py
│   ├── fetch.py
│   ├── answer.py
│   └── run_agent.py
├── tools/
│   └── weather.py
├── tests/
│   ├── test_agent.py
│   └── weather_tool_tests.md
├── outputs/
│   └── acceptance_transcript.md
├── logs/
│   └── runs.jsonl
└── eval/
    ├── golden_set.csv
    ├── golden_set_derivation.md
    ├── run_eval.py
    ├── build_reports.py
    ├── eval_results.csv
    ├── eval_runs.jsonl
    └── eval_summary.md
```

## 4. Datasets

| Dataset | Rows | Grain / purpose |
|---|---:|---|
| `data/store_daily.csv` | 453 | Raw daily store records; includes three exact duplicate rows and injected data-quality issues. |
| `data/store_daily_clean.csv` | 450 | Cleaned daily store data; one row per store per date, with six Part A derived columns. |
| `data/inventory.csv` | 40 | Store-product inventory snapshot; undated. |
| `data/feedback.csv` | 200 | Individual customer feedback records; missing ratings are retained. |

The daily reporting period is **1 April 2026 through 29 June 2026** (90 days across five stores).

### Data-cleaning rules

- Preserve the raw source CSV files.
- Remove exact duplicate daily rows, retaining the first occurrence, and record removals in `analysis/cleaning_log.csv`.
- Convert negative footfall to missing rather than zero.
- Apply the documented two-sided, store-specific 1.5 × IQR rule and cap outliers at the applicable bound.
- Impute missing daily footfall with the median for the same store.
- Keep missing customer ratings missing; do not impute them.

## 5. Main business finding

Pune has the lowest mean daily revenue among the five stores. However, Pune does **not** have the highest mean stockout duration: Hyderabad has the highest average stockout hours, while Pune ranks fourth. The available evidence therefore does not support the claim that Pune has the lowest revenue because it has the most stockouts.

The analysis also reports revenue-footfall and revenue-stockout associations. Correlation is descriptive and does not establish causation. The available datasets do not prove the cause of Pune's lower revenue.

See `analysis/findings.md`, `analysis/data_quality_report.md`, and `analysis/executive_summary.md` for the detailed analysis and supporting figures.

## 6. Agent data boundaries

The agent uses the three approved datasets:

- `data/store_daily_clean.csv`
- `data/inventory.csv`
- `data/feedback.csv`

It may report or calculate using exactly these 11 approved fields:

| Dataset | Approved fields |
|---|---|
| Daily store performance | `revenue_inr`, `daily_target_inr`, `footfall`, `stockout_hours`, `discount_pct`, `achievement_pct`, `performance_band` |
| Inventory snapshot | `stock_units`, `reorder_threshold` |
| Customer feedback | `rating`, `theme` |

Store, date, product, and record identifiers may be used as dimensions or filters, not as additional metrics.

**Prohibited:** `marketing_spend_inr` and `marketing_efficiency`. The source files retain the marketing-spend column for the assignment's data exercise, but the conversational agent must never query, calculate, summarize, or report it or any dependent metric. Part A-only derived fields such as `revenue_per_footfall`, `shortfall_inr`, and `weekend_flag` are not approved agent metrics.

## 7. Conversational agent behaviour

The agent is deterministic and read-only. It supports nine required intents:

1. `lookup`
2. `target_vs_actual`
3. `comparison`
4. `inventory`
5. `feedback`
6. `weather`
7. `unsupported_metric`
8. `out_of_scope`
9. `diagnostic`

Its required processing pipeline is **Interpret → Route → Validate → Query → Calculate → Synthesize → Ground → Record**.

Key controls defined in `docs/agent_spec.md` include:

- Deterministic confidence threshold of **0.70**; ask one focused clarification when confidence is lower or required details are ambiguous.
- Validate approved metrics, schema, entities, date range, and data sufficiency before querying.
- Use safe parameterized queries or bounded dataframe operations; never execute raw user SQL.
- Maximum of **three query attempts** (one initial attempt and at most two retries), retrying only recoverable technical failures.
- Ground numerical statements in retrieved evidence and write an auditable JSONL request record.
- Return exactly one documented status: **Answered**, **Drafted**, **Clarification Needed**, **Escalated**, or **Safe Failure**.
- Do not perform store operations, modify source data, or claim unsupported causation.

## 8. Setup

**Requirements:** Python 3.9 or later, plus the packages listed in `requirements.txt`. SQLite is included with Python.

Run from the repository root:

```bash
python -m pip install -r requirements.txt
```

The default project workflow is designed to run locally. The deterministic agent mode and weather stub do not require an API key or hosted database.

## 9. Run the project

### Data generation, cleaning, and analysis

Run these commands in order when reproducing the data workflow:

```bash
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/analyze.py
python scripts/run_acceptance.py
```

The generator recreates the seeded synthetic source datasets. The cleaning script writes a separate cleaned dataset and cleaning log; it does not edit the raw files. The analysis script regenerates the data-quality report, findings, and executive summary.

### Run the conversational agent

```bash
python scripts/run_agent_tests.py
python -m agent.run_agent
```

The agent uses local data access, including an in-memory SQLite layer for supported query paths. Each request is recorded in `logs/runs.jsonl`.

### Run automated tests and golden-set evaluation

```bash
python -m pytest -q
python -m eval.run_eval
```

The evaluation runner uses deterministic offline weather stub mode and regenerates the evaluation result files and release-gate report. Review the generated files in `eval/` and `docs/release_gate.md` after execution.

## 10. Weather configuration

`tools/weather.py` supports:

- **Stub mode:** deterministic offline values for the five supported store cities; used for reproducible evaluation.
- **Live mode:** optional historical weather requests through the Open-Meteo archive service. This mode requires network access and is not required for the offline workflow.

## 11. Evaluation and release status

The committed `eval/eval_summary.md` contains the recorded results for the 37-case golden set. However, the current `docs/release_gate.md` is marked **NOT YET VALIDATED** because relevant agent, weather-routing, and numeric-audit code changed after those evaluation artifacts were generated.

Therefore, historical evaluation results must not be presented as validation of the current code. Run the agent tests, pytest, and golden-set evaluation again; inspect the newly generated results and release gate before declaring the current version release-ready.

## 12. Known limitations

- All data is synthetic and covers only the stated 90-day reporting period.
- The analysis is observational and cannot prove the cause of differences in store performance.
- Inventory is an undated snapshot, not historical stock availability.
- SKU-level sales, conversion, basket size, catchment, competitor, and hourly demand data are not supplied.
- The assistant is a bounded analytics tool; it does not autonomously change store operations.
- Live weather depends on an external service; offline evaluation uses deterministic stub data.

## 13. Iteration-2 backlog

| Priority | Planned enhancement | Required safeguards |
|---|---|---|
| **P1 — Store and metric trends** | Support trend questions for approved metrics over validated date ranges. | Reconcile every period value to approved source rows; clarify ambiguous filters and reject unsupported metrics or dates. |
| **P2 — Multi-turn follow-ups** | Expand follow-up context for store, metric, date range, product, and filters. | Reuse only unambiguous context; never silently replace an explicitly named but unresolved entity. |
| **P3 — Dated inventory history** | Add dated stock movement or daily inventory data for historical availability analysis. | Validate date coverage and data grain; do not infer historical stock levels from the current undated snapshot. |

## 14. Project documentation

- [Project requirements](docs/requirement.md)
- [Data context and schemas](docs/data_context.md)
- [Agent specification](docs/agent_spec.md)
- [Handover notes](docs/handover.md)
- [Release gate](docs/release_gate.md)
- [Data-quality report](analysis/data_quality_report.md)
- [Analysis findings](analysis/findings.md)
- [Executive summary](analysis/executive_summary.md)
