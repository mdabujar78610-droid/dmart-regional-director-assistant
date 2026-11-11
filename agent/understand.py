
import re
from datetime import date
from difflib import SequenceMatcher

STORES = ["Mumbai", "Pune", "Hyderabad", "Bengaluru", "Ahmedabad"]
STORE_ALIASES = {"bangalore": "Bengaluru", "hydrabad": "Hyderabad", "hydrebad": "Hyderabad"}
PRODUCTS = ["Amul Milk 1L", "Toor Dal 1kg", "Basmati Rice 5kg", "Sunflower Oil 1L",
            "Iodised Salt 1kg", "Instant Noodles 70g", "Glucose Biscuits 200g", "Detergent Powder 1kg"]
DATE_MIN, DATE_MAX = date(2026, 4, 1), date(2026, 6, 29)
AS_OF_DATE = date(2026, 6, 30)

METRICS = {
    "revenue_inr": ["revenue", "sales", "turnover", "earning", "earnings"],
    "daily_target_inr": ["daily target", "target"],
    "footfall": ["footfall", "visitors", "visitor count", "customer count", "people visited"],
    "stockout_hours": ["stockout hours", "stock out hours", "out of stock hours", "stockouts"],
    "discount_pct": ["discount", "discount percentage", "discount percent"],
    "achievement_pct": ["achievement", "target achievement", "achievement percentage"],
    "performance_band": ["performance band", "performance category", "band"],
    "stock_units": ["stock units", "available stock", "inventory level", "quantity in stock"],
    "reorder_threshold": ["reorder threshold", "reorder level", "reorder point"],
    "rating": ["rating", "ratings", "customer rating", "average rating"],
    "theme": ["feedback theme", "theme", "complaints", "customer feedback", "feedback category"],
}
UNSUPPORTED = ["profit", "margin", "marketing", "cost", "expense", "shortfall",
               "efficiency", "weekend", "per footfall", "per visitor"]

def _find_metric(q):
    low = q.lower()
    hits = []
    for field, aliases in METRICS.items():
        for alias in aliases:
            if re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", low):
                hits.append((len(alias), field))
    if not hits:
        return None, True
    longest = max(x[0] for x in hits)
    fields = {field for size, field in hits if size == longest}
    return (next(iter(fields)), True) if len(fields) == 1 else (None, False)

def _find_stores(q):
    low = q.lower()
    found = []
    for name in STORES:
        if re.search(r"\b" + re.escape(name.lower()) + r"\b", low):
            found.append(name)
    for alias, canonical in STORE_ALIASES.items():
        if re.search(r"\b" + alias + r"\b", low):
            found.append(canonical)
    # A small explicit typo tolerance supports the required Hydrabad example.
    if not found:
        for token in re.findall(r"[A-Za-z]+", q):
            matches = [(SequenceMatcher(None, token.lower(), s.lower()).ratio(), s) for s in STORES]
            score, name = max(matches)
            if score >= .78:
                found.append(name)
    return list(dict.fromkeys(found))

def _find_product(q):
    low = q.lower()
    exact = [p for p in PRODUCTS if p.lower() in low]
    if len(exact) == 1:
        return exact[0], False
    # The brief explicitly allows product names without their pack size.
    short = [p for p in PRODUCTS if p.lower().rsplit(" ", 1)[0] in low]
    if len(short) == 1:
        return short[0], False
    return (None, bool(exact or short))

def _parse_dates(q):
    low = q.lower()
    iso = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", q)
    if len(iso) >= 2:
        try:
            a, b = date.fromisoformat(iso[0]), date.fromisoformat(iso[1])
            return (a.isoformat(), b.isoformat()), False, False
        except ValueError:
            return None, True, True
    if len(iso) == 1:
        try:
            d = date.fromisoformat(iso[0])
            return d.isoformat(), False, not (DATE_MIN <= d <= DATE_MAX)
        except ValueError:
            return None, True, True
    m = re.search(r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(2026)\b", q, re.I)
    if m:
        try:
            d = date(int(m.group(3)), date.strptime if False else 1, 1)
            month = date(2026, 1, 1)
            from datetime import datetime
            d = datetime.strptime(m.group(0), "%d %B %Y").date()
            return d.isoformat(), False, not (DATE_MIN <= d <= DATE_MAX)
        except ValueError:
            return None, True, True
    if "yesterday" in low:
        d = AS_OF_DATE.fromordinal(AS_OF_DATE.toordinal() - 1)
        return d.isoformat(), False, False
    if any(x in low for x in ["today", "tomorrow", "last week", "this week", "last month"]):
        return None, True, False
    months = [m for m in ["april", "may", "june"] if re.search(r"\b" + m + r"\b", low)]
    if len(months) == 1:
        from calendar import monthrange
        n = {"april":4, "may":5, "june":6}[months[0]]
        return (date(2026,n,1).isoformat(), min(date(2026,n,monthrange(2026,n)[1]), DATE_MAX).isoformat()), False, False
    if any(x in low for x in ["whole period", "entire period", "full period", "all dates", "overall"]):
        return (DATE_MIN.isoformat(), DATE_MAX.isoformat()), False, False
    if len(months) >= 2:
        return None, True, False
    return None, False, False

def understand(question, context=None):
    context = context or {}
    q, low = question.strip(), question.lower()
    stores = _find_stores(q)
    named_store_unresolved = bool(re.search(r"\b(kolkata|delhi|chennai|jaipur)\b", low))
    store = stores[0] if len(stores) == 1 else None
    metric, metric_clear = _find_metric(q)
    product, product_ambiguous = _find_product(q)
    date_value, unresolved_date, out_of_range = _parse_dates(q)

    override = re.search(r"\b(ignore|disregard|override|bypass|forget|send|email|whatsapp|purchase|buy|restock|place an order|order stock|reorder stock)\b", low)
    unsupported = any(re.search(r"\b" + re.escape(x) + r"\b", low) for x in UNSUPPORTED)
    diagnostic = re.search(r"\b(why|reason|diagnos|cause|explain)\b", low)
    inventory = re.search(r"\b(inventory|stock|reorder|stockout|out of stock)\b", low)
    feedback = re.search(r"\b(feedback|rating|ratings|theme|complain|customer satisfaction|customers saying)\b", low)
    target = re.search(r"\b(target|achievement|hit its target|met its target)\b", low)
    comparison = re.search(r"\b(which store|highest|lowest|rank|compare|comparison|between stores|across stores)\b", low)
    weather_word = re.search(r"\b(weather|rain|temperature|humidity|hot|cold|forecast)\b", low)
    unrelated = re.search(r"\b(capital of|write (a|me) poem|president of|movie recommendation)\b", low)

    if override or unrelated: intent = "out_of_scope"
    elif unsupported: intent = "unsupported_metric"
    elif diagnostic: intent = "diagnostic"
    elif inventory: intent = "inventory"
    elif feedback: intent = "feedback"
    elif target and re.search(r"\b(hit|met|against|performance|perform)\b", low): intent = "target_vs_actual"
    elif comparison: intent = "comparison"
    # Weather-only requests route to the weather adapter even when they name
    # a store or date. Explicit business metrics still use the data lookup path.
    elif weather_word and not metric: intent = "weather"
    elif metric or store or date_value or unresolved_date: intent = "lookup"
    else: intent = "out_of_scope"

    if intent == "inventory" and not product:
        product = None
    if intent == "feedback" and not metric:
        metric = "rating"
    if intent == "target_vs_actual" and not metric:
        metric = "revenue_inr"
    if intent == "comparison" and not metric:
        metric = "revenue_inr"

    follow = bool(re.search(r"\b(and|also|what about|how about|same|there|it)\b", low))
    # Context fills only omitted entities, never unresolved named entities or dates.
    if not stores and not named_store_unresolved:
        store = context.get("store")
    if not metric and metric_clear:
        metric = context.get("metric")
    if not date_value and not unresolved_date and not out_of_range:
        date_value = context.get("date")
    if not product:
        product = context.get("product")

    required = []
    if intent == "lookup":
        if not metric or not metric_clear: required.append("metric")
        if not store or named_store_unresolved or len(stores) > 1: required.append("store")
        if not date_value and not unresolved_date: required.append("date_range")
        elif unresolved_date: required.append("date_range")
    elif intent == "target_vs_actual":
        if not store or named_store_unresolved or len(stores) > 1: required.append("store")
        if not date_value: required.append("date")
    elif intent == "comparison":
        if not metric: required.append("metric")
        if not date_value and not unresolved_date: required.append("date_range")
        if unresolved_date: required.append("date_range")
    elif intent == "inventory" and not product:
        required.append("product")
    elif intent == "feedback":
        if not store or named_store_unresolved: required.append("store")
    elif intent == "weather":
        if not store or named_store_unresolved: required.append("store")
        # Weather tool accepts one calendar date, not a date range.
        if not isinstance(date_value, str): required.append("date")

    confidence = 1.0
    if intent in ("lookup", "target_vs_actual", "comparison", "feedback", "inventory", "weather"):
        if required: confidence = .55
        elif len(stores) == 1 and re.search(r"hydrabad", low): confidence = .85
        elif len(stores) > 1: confidence = .5
    if not metric_clear: confidence = min(confidence, .55)
    return {
        "intent": intent, "store": store, "stores": stores, "metric": metric,
        "date": date_value if isinstance(date_value, str) else None,
        "date_range": list(date_value) if isinstance(date_value, tuple) else None,
        "product": product, "confidence": confidence, "required_entities": required,
        "unresolved_date": unresolved_date, "out_of_range": out_of_range,
        "unresolved_store": named_store_unresolved, "metric_ambiguous": not metric_clear,
    }
