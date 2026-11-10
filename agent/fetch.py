"""Read-only SQLite access with a strict metric allowlist."""
from pathlib import Path
import sqlite3
import pandas as pd

APPROVED = {
 'store_daily': {'revenue_inr','daily_target_inr','footfall','stockout_hours','discount_pct','achievement_pct','performance_band'},
 'inventory': {'stock_units','reorder_threshold'},
 'feedback': {'rating','theme'}
}
DIMS = {'store','store_id','date','product','product_id'}
FILES = {'store_daily':'store_daily_clean.csv','inventory':'inventory.csv','feedback':'feedback.csv'}

class ValidationError(ValueError): pass
class DataAccessError(RuntimeError): pass

def validate(table, fields):
    if table not in APPROVED:
        raise ValidationError('Unapproved dataset.')
    bad = set(fields) - APPROVED[table] - DIMS
    if bad:
        raise ValidationError('Unapproved field(s): ' + ', '.join(sorted(bad)))

def connect(data_dir='data'):
    con = sqlite3.connect(':memory:')
    for table, filename in FILES.items():
        path = Path(data_dir) / filename
        if not path.exists():
            con.close()
            raise FileNotFoundError('Required dataset missing: ' + str(path))
        df = pd.read_csv(path)
        required = {'store','store_id'} | APPROVED[table]
        if table == 'store_daily':
            required.add('date')
        if table == 'inventory':
            required |= {'product','product_id'}
        missing = required - set(df.columns)
        if missing:
            con.close()
            raise ValidationError(filename + ' missing columns: ' + str(sorted(missing)))
        df.to_sql(table, con, index=False, if_exists='replace')
    con.execute('PRAGMA query_only = ON')
    return con

def safe_query(con, sql, params, table, fields):
    validate(table, fields)
    try:
        return pd.read_sql_query(sql, con, params=params)
    except sqlite3.Error as exc:
        raise DataAccessError(str(exc)) from exc

def fetch_one(con, store, day, metric, simulate_failures=0):
    validate('store_daily', ['store','date',metric])
    if metric not in APPROVED['store_daily']:
        raise ValidationError('Metric not approved for daily data.')
    for attempt in range(1, 4):
        if attempt <= simulate_failures:
            continue
        try:
            row = con.execute('SELECT "' + metric + '" FROM store_daily WHERE store=? AND date=?',
                              (store, day)).fetchone()
            return (row[0] if row else None), attempt
        except sqlite3.OperationalError as exc:
            if attempt == 3:
                raise DataAccessError(str(exc)) from exc
    raise DataAccessError('Maximum three attempts reached.')

def fetch_target(con, store, day, simulate_failures=0):
    fields = ['revenue_inr','daily_target_inr','achievement_pct','performance_band']
    validate('store_daily', fields + ['store','date'])
    for attempt in range(1, 4):
        if attempt <= simulate_failures:
            continue
        try:
            row = con.execute('SELECT revenue_inr,daily_target_inr,achievement_pct,performance_band '
                              'FROM store_daily WHERE store=? AND date=?', (store, day)).fetchone()
            return (dict(zip(fields, row)) if row else None), attempt
        except sqlite3.OperationalError as exc:
            if attempt == 3:
                raise DataAccessError(str(exc)) from exc
    raise DataAccessError('Maximum three attempts reached.')
