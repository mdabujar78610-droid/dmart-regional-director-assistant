"""Deterministic natural-language parser for the approved DMart analytics scope."""
import re
from datetime import date
from calendar import monthrange

STORES = ('Mumbai', 'Pune', 'Hyderabad', 'Bengaluru', 'Ahmedabad')
ALIASES = {'bangalore': 'Bengaluru', 'hydrabad': 'Hyderabad', 'hydrebad': 'Hyderabad'}
METRICS = {
 'revenue':'revenue_inr','sales':'revenue_inr','turnover':'revenue_inr',
 'daily target':'daily_target_inr','target':'daily_target_inr',
 'footfall':'footfall','visitors':'footfall',
 'stockout hours':'stockout_hours','stockout':'stockout_hours',
 'discount':'discount_pct','achievement':'achievement_pct',
 'performance band':'performance_band','rating':'rating','ratings':'rating',
 'customer rating':'rating','theme':'theme','feedback theme':'theme',
 'stock units':'stock_units','stock':'stock_units','reorder threshold':'reorder_threshold'
}
PROHIBITED = ('marketing_spend_inr','marketing spend','marketing_efficiency',
              'marketing efficiency','profit margin','conversion rate','basket size')
PRODUCTS = ('Amul Milk 1L','Toor Dal 1kg','Basmati Rice 5kg','Sunflower Oil 1L',
            'Iodised Salt 1kg','Instant Noodles 70g','Glucose Biscuits 200g','Detergent Powder 1kg')

def _dates(q):
    found = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', q)
    if len(found) >= 2:
        try:
            a, b = date.fromisoformat(found[0]), date.fromisoformat(found[1])
            if a > b:
                return None, None, 'Start date must not be after end date.'
            return None, (a.isoformat(), b.isoformat()), None
        except ValueError:
            return None, None, 'Please provide valid ISO dates (YYYY-MM-DD).'
    if found:
        try:
            return date.fromisoformat(found[0]).isoformat(), None, None
        except ValueError:
            return None, None, 'Please provide a valid ISO date (YYYY-MM-DD).'
    month_match = re.search(r'\b(april|may|june)\s+2026\b', q)
    if month_match:
        month = {'april': 4, 'may': 5, 'june': 6}[month_match.group(1)]
        return None, ('2026-%02d-01' % month,
                      date(2026, month, monthrange(2026, month)[1]).isoformat()), None
    return None, None, None

def understand(question, context=None):
    context = context or {}
    q = question.strip().lower()
    stores = [s for s in STORES if re.search(r'\b' + re.escape(s.lower()) + r'\b', q)]
    for alias, canonical in ALIASES.items():
        if re.search(r'\b' + alias + r'\b', q) and canonical not in stores:
            stores.append(canonical)
    if not stores and re.search(r'\b(it|that store|same store|there)\b', q) and context.get('store'):
        stores = [context['store']]

    metric = None
    for alias in sorted(METRICS, key=len, reverse=True):
        if re.search(r'\b' + re.escape(alias) + r'\b', q):
            metric = METRICS[alias]
            break
    if not metric and re.search(r'\b(it|same metric|that metric)\b', q):
        metric = context.get('metric')

    product = next((p for p in PRODUCTS if p.lower() in q), None)
    if not product:
        product = next((p for p in PRODUCTS
                        if re.search(r'\b' + re.escape(p.split()[0].lower()) + r'\b', q)), None)

    if any(x in q for x in PROHIBITED):
        intent = 'unsupported_metric'
    elif re.search(r'\b(weather|rain|temperature|humidity|forecast)\b', q):
        intent = 'weather'
    elif any(x in q for x in ('purchase','buy stock','place an order','replenish now',
                              'transfer stock','change price','issue refund','contact staff')):
        intent = 'out_of_scope'
    elif any(x in q for x in ('why','diagnos','possible reason','what explains','evidence for','contributor')):
        intent = 'diagnostic'
    elif any(x in q for x in ('hit its target','achieve its target','met the target',
                              'meet the target','target vs actual','against its target','did it achieve')):
        intent = 'target_vs_actual'
    elif any(x in q for x in ('inventory','reorder','below threshold','stock availability','stock review')):
        intent = 'inventory'
    elif any(x in q for x in ('feedback','customer','complain','complaint','theme','satisfaction','rating')):
        intent = 'feedback'
    elif any(x in q for x in ('compare','comparison','highest','lowest','rank','which store','across stores','all five')):
        intent = 'comparison'
    else:
        intent = 'lookup'

    if intent == 'comparison' and not metric:
        metric = 'revenue_inr'
    if intent == 'target_vs_actual':
        metric = 'revenue_inr'
    if intent == 'inventory' and not metric:
        metric = 'stock_units'
    if intent == 'feedback' and not metric:
        metric = 'rating'

    day, date_range, date_error = _dates(q)
    if not day and not date_range and context.get('date') and re.search(r'\b(it|that date|same date)\b', q):
        day = context['date']

    required = []
    if date_error:
        required.append('valid date')
    if intent in ('lookup','target_vs_actual') and not stores:
        required.append('store')
    if intent == 'lookup' and not metric:
        required.append('approved metric')
    if intent in ('lookup','target_vs_actual') and not day and not date_range:
        required.append('date or date range')
    confidence = (0.40 + (0.25 if metric else 0)
                  + (0.20 if stores or intent in ('comparison','inventory','feedback','diagnostic',
                                                  'weather','unsupported_metric','out_of_scope') else 0)
                  + (0.15 if day or date_range or intent in ('comparison','inventory','feedback','diagnostic',
                                                            'weather','unsupported_metric','out_of_scope') else 0))
    if required:
        confidence = min(confidence, 0.69)
    return {'intent':intent,'stores':stores,'store':stores[0] if len(stores)==1 else None,
            'metric':metric,'product':product,'date':day,'date_range':date_range,
            'date_error':date_error,'required_entities':required,'confidence':round(confidence,2)}
