# DMart Regional Director Assistant

A data-driven retail diagnosis and grounded conversational analytics project for five synthetic DMart practice stores: Mumbai, Pune, Hyderabad, Bengaluru and Ahmedabad.

The project tests the claim that Pune's lowest average daily revenue is caused by stockouts, then specifies a conversational assistant whose numerical answers must be traceable to approved data fields. All project datasets are synthetic practice data, not real DMart business records.

## Repository layout

```text
dmart-regional-director-assistant/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── store_daily.csv
│   ├── store_daily_clean.csv
│   ├── inventory.csv
│   └── feedback.csv
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── analyze.py
│   └── run_acceptance.py
├── analysis/
│   ├── data_quality_report.md
│   ├── cleaning_log.csv
│   ├── findings.md
│   └── executive_summary.md
├── docs/
│   ├── requirement.md
│   ├── data_context.md
│   ├── agent_spec.md
│   └── release_gate.md             # Part D deliverable; to be added
├── agent/                          # Part C deliverables; to be added
├── tools/                          # Part D weather tool; to be added
├── tests/                          # Part D weather tests; to be added
├── outputs/                        # Part C acceptance transcript; to be added
├── logs/                            # Part C run log; to be added
└── eval/                            # Part D evaluation; to be added
```

Part A and Part B are committed now. Part C and Part D are not yet implemented; their folders and files will be added as those stages are completed. The repository uses the required single `main` branch and one public repository.

## Setup and offline path

Requirements: Python 3.9 or later, pandas and numpy. The Part A workflow is fully local and requires no account, API key, hosted database or hosted app.

From the repository root:

```bash
python -m pip install -r requirements.txt
```

Run the Part A scripts in this order:

1. Generate the three raw synthetic datasets:

   ```bash
   python scripts/generate_data.py
   ```

2. Clean the daily data, write the cleaned dataset and cleaning log:

   ```bash
   python scripts/clean_data.py
   ```

3. Produce the store diagnosis and findings:

   ```bash
   python scripts/analyze.py
   ```

4. Run the Part A acceptance checks:

   ```bash
   python scripts/run_acceptance.py
   ```

The generator is seeded and deterministic. Do not manually edit the three raw CSV files after generation. The cleaning script writes a separate cleaned file and an audit log. The Part C specification requires a local SQLite data layer; no hosted database is needed. Part D specifies a deterministic stub weather mode for offline evaluation.

## Part A — Data foundation and premise test

The cleaning process removes exact duplicate rows, converts impossible negative footfall to missing, caps extreme high footfall using store-level IQR bounds, and imputes missing footfall using each store's median. The cleaned daily dataset contains 450 store-days. The analysis finds that Pune has the lowest mean daily revenue but does not have the highest mean stockout duration; therefore, these data do not support the claim that Pune is the lowest-revenue store because it has the most stockouts. Correlation is not evidence of causation.

See `analysis/data_quality_report.md`, `analysis/cleaning_log.csv`, `analysis/findings.md` and `analysis/executive_summary.md` for the committed evidence.

## Part B — Agent specification

- `docs/requirement.md`: business goals, scope, approved metrics and prohibited actions.
- `docs/data_context.md`: dataset schemas, quality facts, relationships and supported questions.
- `docs/agent_spec.md`: conversational pipeline, intents, grounding, statuses, retries and acceptance criteria.

## Rounding method

For reported averages, retain full precision during aggregation and round only the final displayed value to two decimal places using standard half-up rounding where a rounded currency or percentage value is required.

## Known limitations

- The data is synthetic and covers 2026-04-01 through 2026-06-29; it must not be represented as actual DMart operational data.
- The analysis is descriptive and observational. It cannot establish that stockouts, footfall, marketing or another factor caused revenue differences.
- Part A is implemented and validated by a local acceptance script and GitHub Actions workflow. The conversational agent, weather integration, evaluation suite and release decision are specified by the assignment but are not yet implemented in this repository.
- The Part B specification is a design document; it does not itself demonstrate a working agent.

## Prioritised Iteration-2 backlog

1. **Store trend and period-over-period questions**
   - Input: a store, approved metric and two comparable date ranges.
   - Output: period values, absolute and percentage change, plus source evidence.
   - Success: results reconcile to the cleaned rows and every reported number is grounded.
   - Failure: ask for missing dates or return a safe failure for unsupported metrics or out-of-range dates.

2. **Multi-turn follow-up depth**
   - Input: a follow-up question referring to a previously resolved store, metric or period.
   - Output: an answer that reuses only unambiguous session context and records the context used.
   - Success: required entities are carried forward consistently without silently filling unresolved named stores or dates.
   - Failure: request clarification whenever the reference is ambiguous or conflicts with the current question.

3. **Richer diagnostic evidence**
   - Input: a supported business question plus an explicitly selected comparison dimension such as product, store or period.
   - Output: a bounded diagnostic breakdown with evidence and clearly labelled hypotheses.
   - Success: every figure comes from approved fields and no association is stated as a cause.
   - Failure: refuse unsupported dimensions, missing data or causal conclusions not established by the data.
