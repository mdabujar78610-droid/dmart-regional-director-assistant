"""DMart agent: understand -> fetch -> answer, with auditable JSONL logs."""
import json, os, re, time, uuid
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from .understand import understand, STORES, DATE_MIN, DATE_MAX
from .fetch import connect, sql_query, run_query, FetchError
from .answer import answer_result, money, round2

TABLE = "store_daily_clean"
METRIC_FIELDS = {"revenue_inr","daily_target_inr","footfall","stockout_hours","discount_pct","achievement_pct","performance_band"}

def audit_numeric_claims(answer, grounded_values, confidence=None):
    """Count numeric claims not traceable to returned values or explicit policy metadata.

    Dates are identifiers, not numeric claims. Confidence/threshold figures are
    deterministic routing metadata, not business-data claims. All other numeric
    values must match a value in the handler's grounded_values payload.
    """
    import math

    allowed = []
    def collect(value):
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            if math.isfinite(float(value)):
                allowed.append(float(value))
        elif isinstance(value, dict):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, (list, tuple)):
            for nested in value:
                collect(nested)

    collect(grounded_values or {})
    claims = []
    date_spans = [m.span() for m in re.finditer(r"\\b\\d{4}-\\d{2}-\\d{2}\\b", answer)]
    for match in re.finditer(r"(?<![A-Za-z])[-+]?\\d+(?:,\\d{3})*(?:\\.\\d+)?", answer):
        start, end = match.span()
        if any(left <= start < right for left, right in date_spans):
            continue

        # Do not count pack-size notation (e.g. Amul Milk 1L) as a KPI.
        suffix = answer[end:end + 3]
        if re.match(r"(?i)^(?:l|kg|g)\\b", suffix):
            continue

        # Confidence and the configured confidence floor are routing metadata.
        context = answer[max(0, start - 35):min(len(answer), end + 35)].casefold()
        if "confidence" in context or "minimum is" in context:
            continue

        raw = match.group(0).replace(",", "")
        value = float(raw)
        if not any(abs(value - candidate) <= max(0.011, abs(candidate) * 1e-9)
                   for candidate in allowed):
            claims.append(raw)
    return len(claims), claims


class Agent:
    def __init__(self, data_dir="data", log_path=None):
        self.con = connect(data_dir)
        self.contexts = {}
        self.log_path = Path(log_path or os.getenv("AGENT_LOG_PATH","logs/runs.jsonl"))
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._attempts = []
        self._route = "none"
        self._executed = None
        self._tool_calls = 0
        self._tools_called = []

    def _query(self, sql, params, table, fields, failures=0):
        self._route = "sql"
        self._tool_calls += 1
        self._tools_called.append("sqlite_query")
        self._executed = sql
        try:
            result, attempts = run_query(lambda: sql_query(self.con, sql, params, table, fields), 3, failures)
        except Exception:
            self._attempts.append(3)
            raise
        self._attempts.append(attempts)
        return result

    def _python_daily(self, store, day, failures=0):
        self._route = "python"
        self._tool_calls += 1
        self._tools_called.append("daily_lookup")
        self._executed = "daily_lookup(store, date) using approved dataframe columns"
        from .fetch import validate
        validate(TABLE, ["date", "store", "revenue_inr", "daily_target_inr", "footfall", "stockout_hours", "discount_pct", "achievement_pct", "performance_band"])
        def work():
            df = pd.read_sql_query(
                "SELECT date, store, revenue_inr, daily_target_inr, footfall, stockout_hours, discount_pct, achievement_pct, performance_band FROM store_daily_clean WHERE store=? AND date=?",
                self.con, params=(store, day))
            if df.empty: raise LookupError("No row")
            return df.iloc[0]
        # run_query retries operational errors; simulated errors follow same cap.
        from .fetch import run_query
        try:
            row, attempts = run_query(work, 3, failures)
        except Exception:
            self._attempts.append(3)
            raise
        self._attempts.append(attempts)
        return row

    def _base(self, p):
        if p.get("date"):
            return "date = ?", [p["date"]], p["date"]
        dr = p.get("date_range") or [DATE_MIN.isoformat(), DATE_MAX.isoformat()]
        return "date BETWEEN ? AND ?", list(dr), f"{dr[0]} to {dr[1]}"

    def _clarify(self, p):
        missing = p.get("required_entities", [])
        parts = []
        if "store" in missing: parts.append("store (Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad)")
        if "metric" in missing: parts.append("approved metric (revenue, target, footfall, stockout hours, discount, achievement, or performance band)")
        if "product" in missing: parts.append("product")
        if "date" in missing or "date_range" in missing: parts.append("date or date range")
        if p.get("intent") == "weather":
            questions = []
            if "store" in missing: questions.append("Which store city (Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad)?")
            if "date" in missing or "date_range" in missing: questions.append("Which single date in the available period?")
            return " ".join(questions) or "Please clarify the weather request."
        return "Please specify the " + " and ".join(parts) + "."

    def _handle(self, q, p, failures):
        intent, store, metric = p["intent"], p.get("store"), p.get("metric")
        if intent == "unsupported_metric":
            return answer_result("Safe Failure", "That field is not in the approved metric set. I did not query it.")
        if intent == "out_of_scope":
            return answer_result("Escalated", "This request is outside the read-only DMart store-analysis scope and requires a human assistant.")
        if intent == "diagnostic":
            return answer_result("Escalated", "A diagnostic explanation of causes requires an analyst. The available data can show associations, but cannot establish why revenue is low.")
        if p.get("out_of_range"):
            return answer_result("Safe Failure", f"The requested date is outside the available data range {DATE_MIN} to {DATE_MAX}.")
        if p.get("required_entities") or p["confidence"] < .70:
            return answer_result("Clarification Needed", self._clarify(p), limitations=[f"Interpretation confidence {p['confidence']:.2f}; minimum is 0.70."])
        if intent == "weather":
            if not store or not p.get("date"):
                return answer_result("Clarification Needed",
                    "Please specify one supported store city (Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad) and one date in the available period.")
            from tools.weather import get_weather
            weather = get_weather(store, p["date"])
            if not weather.get("ok"):
                return answer_result("Safe Failure", f"Weather lookup unavailable: {weather.get('error', 'unknown error')}.")
            values = {key: weather[key] for key in ("temperature_c", "humidity_pct", "wind_kmh", "rain_mm")}
            evidence = [{"dataset": "Open-Meteo archive API" if weather["mode"] == "live" else "deterministic weather stub",
                         "fields": list(values), "filters": {"city": store, "date": p["date"]}}]
            body = (f"{store}, {p['date']}: temperature {values['temperature_c']:.1f} °C; "
                    f"humidity {values['humidity_pct']:.1f}%; wind {values['wind_kmh']:.1f} km/h; "
                    f"rainfall {values['rain_mm']:.1f} mm. Weather mode: {weather['mode']}.")
            return answer_result("Answered", body, values, evidence,
                                 "Daily weather values returned by tools.weather.get_weather")
        if intent == "lookup":
            if p.get("date"):
                row = self._python_daily(store, p["date"], failures)
                val = row[metric]
                if pd.isna(val): return answer_result("Safe Failure", "No non-missing value exists for the selected store, metric and date.")
                formatted = money(val) if metric.endswith("_inr") else f"{float(val):.2f}"
                body = f"{store}, {p['date']}: {metric} = {formatted}. Source: store_daily_clean.csv."
                grounded = {metric: float(val)}
                evidence = [{"dataset":"store_daily_clean.csv","fields":[metric,"store","date"],"filters":{"store":store,"date":p["date"]}}]
                if re.search(r"\b(weather|rain|temperature|humidity|hot|cold)\b", q, re.I):
                    from tools.weather import get_weather
                    weather = get_weather(store, p["date"])
                    if weather.get("ok"):
                        weather_values = {key: weather[key] for key in ("temperature_c", "humidity_pct", "wind_kmh", "rain_mm")}
                        grounded.update(weather_values)
                        evidence.append({"dataset": "Open-Meteo archive API" if weather["mode"] == "live" else "deterministic weather stub",
                                         "fields": list(weather_values), "filters": {"city": store, "date": p["date"]}})
                        body += (f" Weather: temperature {weather_values['temperature_c']:.1f} °C; "
                                 f"humidity {weather_values['humidity_pct']:.1f}%; wind {weather_values['wind_kmh']:.1f} km/h; "
                                 f"rainfall {weather_values['rain_mm']:.1f} mm (mode: {weather['mode']}).")
                    else:
                        body += f" Weather unavailable: {weather.get('error', 'unknown error')}."
                return answer_result("Answered", body, grounded, evidence,
                    "Direct one-store, one-date Python lookup; optional daily weather tool lookup")
            clause, params, period = self._base(p)
            if metric == "performance_band":
                sql = f"SELECT performance_band, COUNT(*) AS n FROM {TABLE} WHERE {clause} AND store=? GROUP BY performance_band ORDER BY performance_band"
                df = self._query(sql, params+[store], TABLE, [metric,"store","date"], failures)
                values = {str(r.performance_band):int(r.n) for r in df.itertuples()}
                body = "; ".join(f"{k}: {v}" for k,v in values.items())
                return answer_result("Answered", f"{store}, {period}: performance bands — {body}. Source: store_daily_clean.csv.", values,
                    [{"dataset":"store_daily_clean.csv","fields":[metric,"store","date"],"filters":{"store":store,"period":period}}], "COUNT grouped by performance_band")
            sql = f"SELECT AVG({metric}) AS value, COUNT({metric}) AS n FROM {TABLE} WHERE {clause} AND store=?"
            df = self._query(sql, params+[store], TABLE, [metric,"store","date"], failures)
            if int(df.iloc[0]["n"]) == 0: return answer_result("Safe Failure","No records support these filters.")
            val = float(df.iloc[0]["value"])
            fmt = money(val) if metric.endswith("_inr") else f"{val:.2f}"
            return answer_result("Answered", f"{store}, {period}: average {metric} = {fmt} (n={int(df.iloc[0]['n'])}). Source: store_daily_clean.csv.",
                {metric:round2(val),"valid_records":int(df.iloc[0]["n"])}, [{"dataset":"store_daily_clean.csv","fields":[metric,"store","date"],"filters":{"store":store,"period":period}}],
                f"AVG({metric}) excluding null values")

        if intent == "target_vs_actual":
            row = self._python_daily(store, p["date"], failures)
            rev, target, achievement = float(row.revenue_inr), float(row.daily_target_inr), float(row.achievement_pct)
            band = str(row.performance_band)
            status = "Drafted" if achievement < 75 else "Answered"
            return answer_result(status, f"{store}, {p['date']}: revenue {money(rev)} versus target {money(target)}; achievement {achievement:.2f}% ({band}). Source: store_daily_clean.csv.",
                {"revenue_inr":round2(rev),"daily_target_inr":round2(target),"achievement_pct":round2(achievement),"performance_band":band},
                [{"dataset":"store_daily_clean.csv","fields":["revenue_inr","daily_target_inr","achievement_pct","performance_band","store","date"],"filters":{"store":store,"date":p["date"]}}],
                "Direct daily row retrieval; achievement and performance band taken from approved supplied fields")

        if intent == "comparison":
            clause, params, period = self._base(p)
            if p.get("date"):
                sql = f"SELECT store, AVG(revenue_inr) AS value, COUNT(revenue_inr) AS n FROM {TABLE} WHERE {clause} GROUP BY store ORDER BY value ASC, store ASC"
                # Requested date ranking: direction from wording.
                if "highest" in q.lower(): sql = sql.replace("ASC, store ASC","DESC, store ASC")
                df = self._query(sql, params, TABLE, ["store","date","revenue_inr"], failures)
                rows = [f"{r.store} {money(r.value)}" for r in df.itertuples()]
                vals = {str(r.store):round2(r.value) for r in df.itertuples()}
                return answer_result("Answered", f"Store revenue ranking on {period}: " + "; ".join(rows) + ".", vals,
                    [{"dataset":"store_daily_clean.csv","fields":["store","date","revenue_inr"],"filters":{"date":period}}], "Daily revenue grouped by store and sorted")
            sql = f"SELECT store, AVG({metric}) AS value, COUNT({metric}) AS n FROM {TABLE} WHERE {clause} GROUP BY store ORDER BY value DESC, store ASC"
            df = self._query(sql, params, TABLE, ["store","date",metric], failures)
            if any(x in q.lower() for x in ["lowest","least","worst"]):
                df = df.sort_values(["value","store"],ascending=[True,True])
            vals = {str(r.store):round2(r.value) for r in df.itertuples()}
            rows = [f"{r.store} {money(r.value) if metric.endswith('_inr') else f'{r.value:.2f}'}" for r in df.itertuples()]
            winner = str(df.iloc[0]["store"])
            return answer_result("Answered", f"Store comparison for average {metric}, {period}: " + "; ".join(rows) + f". Highest/lowest as requested: {winner}.",
                vals, [{"dataset":"store_daily_clean.csv","fields":["store","date",metric],"filters":{"period":period}}], f"GROUP BY store; AVG({metric}); nulls excluded")

        if intent == "inventory":
            sql = "SELECT store, product, stock_units, reorder_threshold FROM inventory WHERE product=? ORDER BY store"
            df = self._query(sql, [p["product"]], "inventory", ["store","product","stock_units","reorder_threshold"], failures)
            if df.empty: return answer_result("Safe Failure","No inventory records match that product.")
            below = df[df.stock_units < df.reorder_threshold]
            rows = [f"{r.store}: {int(r.stock_units)} units (threshold {int(r.reorder_threshold)})" for r in below.itertuples()]
            values = {str(r.store):{"stock_units":int(r.stock_units),"reorder_threshold":int(r.reorder_threshold)} for r in below.itertuples()}
            body = "; ".join(rows) if rows else "No stores are below the reorder threshold"
            return answer_result("Answered", f"{p['product']} — below threshold: {body}. Inventory is an undated snapshot.",
                values, [{"dataset":"inventory.csv","fields":["store","product","stock_units","reorder_threshold"],"filters":{"product":p["product"]}}], "Rows where stock_units < reorder_threshold")

        if intent == "feedback":
            sql = "SELECT AVG(rating) AS avg_rating, COUNT(rating) AS rated, COUNT(*) AS total FROM feedback WHERE store=?"
            df = self._query(sql,[store],"feedback",["store","rating","date"],failures)
            themes = self._query("SELECT theme, COUNT(*) AS n FROM feedback WHERE store=? GROUP BY theme ORDER BY n DESC, theme ASC",
                                 [store],"feedback",["store","theme","date"],failures)
            r = df.iloc[0]
            common = str(themes.iloc[0]["theme"]) if not themes.empty else "Unavailable"
            return answer_result("Answered", f"{store}: average rating {float(r.avg_rating):.2f}; {int(r.rated)} rated of {int(r.total)} feedback records; most frequent theme: {common}.",
                {"average_rating":round2(r.avg_rating),"rated_records":int(r.rated),"total_records":int(r.total),"most_frequent_theme":common},
                [{"dataset":"feedback.csv","fields":["rating","theme","store"],"filters":{"store":store}}], "AVG(rating) excluding nulls; COUNT(rating); theme frequency by COUNT(*)")
        return answer_result("Safe Failure","The request could not be mapped to a supported analysis.")

    def handle(self, question, session_id="default", user_id="u1", simulate_failures=0):
        started = time.perf_counter()
        self._attempts, self._route, self._executed, self._tool_calls = [], "none", None, 0
        self._tools_called = []
        ctx = self.contexts.setdefault(session_id,{})
        p = understand(question,ctx)
        try:
            result = self._handle(question,p,simulate_failures)
        except LookupError:
            result = answer_result("Safe Failure","No record exists for the selected store and date.")
        except Exception as exc:
            if self._route != "none" and self._attempts and max(self._attempts) >= 3:
                result = answer_result("Escalated","The data query failed after three attempts. No figure is reported.")
            elif self._route != "none" and simulate_failures >= 3:
                self._attempts.append(3)
                result = answer_result("Escalated","The data query failed after three attempts. No figure is reported.")
            else:
                result = answer_result("Safe Failure",f"The request could not be completed safely: {type(exc).__name__}.")
        # Persist resolved entities even after a clarification, so a user can supply
        # only the missing field in the next turn. Unresolved names/dates are never stored.
        if not p.get("unresolved_store"):
            for key in ("store","metric","date","date_range","product"):
                if p.get(key) is not None: ctx[key] = p[key]
        elapsed = (time.perf_counter()-started)*1000
        answer = result["answer_text"]
        tokens = len((question + " " + answer).split())
        ungrounded_count, ungrounded_claims = audit_numeric_claims(
            answer, result["grounded_values"], p.get("confidence"))
        log = {
            "run_id":str(uuid.uuid4()), "user_id":user_id, "session_id":session_id,
            "timestamp":datetime.now(timezone.utc).isoformat(), "question":question,
            "intent":p["intent"], "confidence":p["confidence"], "route":self._route,
            "executed":self._executed, "attempts":max(self._attempts,default=0),
            "tools_called":self._tools_called[:], "status":result["status"], "answer_text":answer,
            "evidence":result["evidence"], "grounded_values":result["grounded_values"],
            "latency_ms":round(elapsed,3), "tokens_est":tokens, "tool_calls":self._tool_calls,
            "ungrounded_numbers":ungrounded_count, "ungrounded_claims":ungrounded_claims,
            "budget_exceeded":tokens>150,
        }
        # Resolve the environment override for every invocation, not only at construction.
        active_log_path = Path(os.getenv("AGENT_LOG_PATH", str(self.log_path)))
        active_log_path.parent.mkdir(parents=True, exist_ok=True)
        with active_log_path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(log,ensure_ascii=False,default=str)+"\n")
        return {"final_status":result["status"],"status":result["status"],"intent":p["intent"],
                "confidence":p["confidence"],"answer_text":answer,"grounded_values":result["grounded_values"],
                "evidence":result["evidence"],"attempts":log["attempts"],"individual_query_attempts":self._attempts[:],
                "route":self._route,"tool_calls":self._tool_calls,
                "ungrounded_numbers":ungrounded_count,"ungrounded_claims":ungrounded_claims}
