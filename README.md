# DMart Regional Director Assistant

A data-driven retail analytics and grounded conversational AI project built around a five-store DMart assignment. The repository is organized by assignment part so that the data foundation and business documentation are easy to review.

> **Data note:** The supplied datasets are synthetic assignment data, not actual DMart business records.

## Project structure

```text
dmart-regional-director-assistant/
├── Part-A/
│   ├── data/
│   │   ├── store_daily.csv
│   │   ├── store_daily_clean.csv
│   │   ├── inventory.csv
│   │   └── feedback.csv
│   ├── scripts/
│   │   ├── generate_data.py
│   │   ├── clean_data.py
│   │   ├── analyze.py
│   │   └── run_acceptance.py
│   └── analysis/
│       ├── cleaning_log.csv
│       ├── data_quality_report.md
│       ├── findings.md
│       └── executive_summary.md
├── Part-B/
│   └── docs/
│       ├── requirement.md
│       ├── data_context.md
│       └── agent_spec.md
├── .github/
│   └── workflows/
│       └── part-a-validation.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Part A — Data foundation and analysis

Part A prepares the daily store dataset, records cleaning decisions, checks data quality, and evaluates the claim that Pune's lower revenue is caused by stockouts.

### Run Part A

Run these commands from the repository root:

```bash
python -m pip install -r requirements.txt
python Part-A/scripts/generate_data.py
python Part-A/scripts/clean_data.py
python Part-A/scripts/analyze.py
python Part-A/scripts/run_acceptance.py
```

The generator recreates the synthetic raw CSV files. The cleaning script writes a separate cleaned daily dataset and an audit log. The analysis and acceptance scripts produce and validate the reports.

### Key finding

The current Part A analysis finds that Pune has the lowest mean daily revenue, but it does not have the highest average stockout duration. The available evidence therefore does not support the claim that Pune is the lowest-revenue store because it has the most stockouts. Correlation is not proof of causation.

## Part B — Business requirements and agent design

Part B documents the intended open-ended, grounded conversational analytics agent.

- **requirement.md** — business purpose, scope, approved metrics, and restrictions.
- **data_context.md** — datasets, field meanings, data quality, and relationships.
- **agent_spec.md** — conversational behavior, processing pipeline, validation, grounding, and audit rules.

The example questions are illustrative, not a fixed allowlist. The agent must understand new business questions while answering only when the approved data supports them.

## Part C and Part D

Part C implementation and Part D evaluation folders will be added when those assignment stages begin. No unimplemented agent or test code is claimed here.

## Technology

- Python
- Pandas
- CSV-based data preparation and analysis
- GitHub Actions for Part A validation

## Repository scope

This repository currently contains the Part A data foundation and Part B documentation.