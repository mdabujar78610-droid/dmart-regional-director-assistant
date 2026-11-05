# DMart Regional Director Assistant

A reproducible retail analytics project that prepares synthetic store data and tests the claim: **“Pune is the lowest-revenue store because of stockouts.”**

## Part A — Data foundation and premise test

Part A builds a trustworthy daily-store dataset, documents cleaning decisions, and tests the premise before any causal claim is made.

### Repository structure
```text
.
├── data/
│   ├── store_daily.csv
│   ├── inventory.csv
│   ├── feedback.csv
│   └── store_daily_clean.csv
├── analysis/
│   ├── data_quality_report.md
│   ├── cleaning_log.csv
│   ├── findings.md
│   └── executive_summary.md
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── analyze.py
│   └── run_acceptance.py
├── requirements.txt
└── .gitignore
```

### Setup and run
Python 3.10 or later is recommended.

```bash
python -m pip install -r requirements.txt
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/analyze.py
python scripts/run_acceptance.py
```

Run commands from the repository root. The seeded generator is supplied for the assignment and should not be modified. It recreates the synthetic raw datasets in `data/`. Do not edit raw CSVs manually; cleaning writes a separate processed file and an auditable log.

### Cleaning approach
- Remove exact duplicate daily records, keeping the first.
- Convert negative footfall to missing.
- Cap extreme footfall using per-store IQR upper bounds.
- Impute missing footfall using the relevant store's median.
- Derive revenue per footfall, marketing efficiency, achievement percentage, shortfall, weekend flag and performance band.

### Initial premise-test result
Pune has the lowest mean daily revenue (INR 636,358.55), but averages 2.32 stockout hours—fourth-highest among five stores. Hyderabad is highest at 3.85 hours. The data therefore do not support the claim that Pune is lowest because it has the most stockouts. Correlation is not causation.

See [data quality report](analysis/data_quality_report.md), [findings](analysis/findings.md), [executive summary](analysis/executive_summary.md), and [cleaning log](analysis/cleaning_log.csv).

**Scope:** Part A only. Later assignment parts are intentionally not included yet.
