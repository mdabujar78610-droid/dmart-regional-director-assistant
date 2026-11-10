"""Response formatters that identify source fields and avoid invented values."""
def money(value): return 'INR {:,.2f}'.format(float(value))
def lookup(value,parsed,source):
    if value is None: return 'Safe Failure','No matching record was found.',{},[]
    metric=parsed['metric']; display=money(value) if metric=='revenue_inr' else str(value) if metric in ('performance_band','theme') else '{:,.2f}'.format(float(value))
    label=metric.replace('_',' ')
    return 'Answered', '{} on {}: {} = {}. Source: {} field {}.'.format(parsed['store'],parsed['date'],label,display,source,metric),{metric:value},[{'source':source,'fields':[metric]}]
def target(data,parsed):
    if not data: return 'Safe Failure','No matching store/date record was found.',{},[]
    rev=float(data['revenue_inr']); tgt=float(data['daily_target_inr']); gap=rev-tgt
    msg='{} on {}: actual revenue {}, target {}, achievement {:.2f}% ({}); actual minus target {}. Source: store_daily_clean.csv fields revenue_inr, daily_target_inr, achievement_pct, performance_band.'.format(parsed['store'],parsed['date'],money(rev),money(tgt),float(data['achievement_pct']),data['performance_band'],money(gap))
    return 'Answered',msg,data,[{'source':'store_daily_clean.csv','fields':['revenue_inr','daily_target_inr','achievement_pct','performance_band']}]
