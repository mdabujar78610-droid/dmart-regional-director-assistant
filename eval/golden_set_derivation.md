# Golden Set Derivation Notes

The following expected figures were calculated from the committed source CSVs, independently of the agent's answer text.

## C01 — Hyderabad revenue, 2026-06-29

- Pandas expression: `df.loc[(df.store == "Hyderabad") & (df.date == "2026-06-29"), "revenue_inr"].iloc[0]`
- Source: `data/store_daily_clean.csv`
- Result: `784954.90` (raw value `784954.9`, formatted to two decimal places).

## C02 — Pune sales, 2026-05-15

- Pandas expression: `df.loc[(df.store == "Pune") & (df.date == "2026-05-15"), "revenue_inr"].iloc[0]`
- Source: `data/store_daily_clean.csv`
- Result: `623845.00` (raw value `623845.0`, formatted to two decimal places).

## C08 and C10 — Session setup lookup

- Pandas expression: `df.loc[(df.store == "Pune") & (df.date == "2026-05-15"), "revenue_inr"].iloc[0]`
- Source: `data/store_daily_clean.csv`
- Result: `623845.00`. These setup turns establish Pune and the date in their respective sessions; the following unresolved-store/date tests verify that unresolved named entities are not silently filled from context.

## R01 — Full-period reconciliation

- Pandas expression: `df.groupby("store").revenue_inr.mean().sort_values()`
- Source: `data/store_daily_clean.csv`, all 450 rows from 2026-04-01 through 2026-06-29.
- Results, rounded to two decimal places:
  - Pune: `636358.55`
  - Ahmedabad: `782647.37`
  - Hyderabad: `893233.01`
  - Bengaluru: `931065.68`
  - Mumbai: `1064371.60`

The agent's SQL `AVG(revenue_inr)` values are displayed using the same two-decimal currency format. `agent.answer.round2` uses decimal `ROUND_HALF_UP` for the final two-decimal conversion.
