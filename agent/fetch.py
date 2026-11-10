
from pathlib import Path
import sqlite3
import pandas as pd

TABLE_FILES = {
    "store_daily_clean": "store_daily_clean.csv",
    "inventory": "inventory.csv",
    "feedback": "feedback.csv",
}
APPROVED = {
    "store_daily_clean": {"revenue_inr", "daily_target_inr", "footfall", "stockout_hours",
                          "discount_pct", "achievement_pct", "performance_band"},
    "inventory": {"stock_units", "reorder_threshold"},
    "feedback": {"rating", "theme"},
}
DIMENSIONS = {"store", "store_id", "date", "product", "product_id", "feedback_id"}
REQUIRED = {
    "store_daily_clean": {"store", "store_id", "date"} | APPROVED["store_daily_clean"],
    "inventory": {"store", "store_id", "product", "product_id"} | APPROVED["inventory"],
    "feedback": {"store", "store_id", "date", "feedback_id"} | APPROVED["feedback"],
}

class FetchError(RuntimeError):
    pass

def connect(data_dir="data"):
    root = Path(data_dir)
    if not root.exists():
        raise FetchError(f"Data directory not found: {root}")
    con = sqlite3.connect(":memory:")
    for table, filename in TABLE_FILES.items():
        path = root / filename
        if not path.is_file():
            con.close()
            raise FetchError(f"Required dataset missing: {path}")
        df = pd.read_csv(path)
        missing = REQUIRED[table] - set(df.columns)
        if missing:
            con.close()
            raise FetchError(f"{filename} is missing required columns: {sorted(missing)}")
        df = df.loc[:, sorted(REQUIRED[table])].copy()
        if df.empty:
            con.close()
            raise FetchError(f"{filename} contains no records")
        if "date" in df:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        for col in APPROVED[table] - {"performance_band", "theme"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.to_sql(table, con, index=False, if_exists="fail")
    return con

def validate(table, selected):
    if table not in APPROVED:
        raise FetchError(f"Unapproved dataset: {table}")
    invalid = set(selected) - APPROVED[table] - DIMENSIONS
    if invalid:
        raise FetchError(f"Unapproved column(s): {sorted(invalid)}")
    return True

def sql_query(con, sql, params=(), table=None, selected=()):
    if table is None:
        raise FetchError("Dataset must be declared")
    validate(table, selected)
    if not isinstance(params, (tuple, list)):
        raise FetchError("SQL parameters must be positional values")
    return pd.read_sql_query(sql, con, params=tuple(params))

def run_query(query_fn, max_attempts=3, simulate_failures=0):
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3")
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            if attempts <= simulate_failures:
                raise sqlite3.OperationalError("simulated temporary database failure")
            return query_fn(), attempts
        except (FetchError, ValueError, TypeError):
            raise
        except (sqlite3.OperationalError, TimeoutError, ConnectionError):
            if attempts == max_attempts:
                raise
    raise RuntimeError("Query attempts exhausted")
