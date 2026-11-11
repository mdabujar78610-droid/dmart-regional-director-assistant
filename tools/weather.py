"""Historical weather adapter with deterministic offline stub and Open-Meteo live mode."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4866),
    "Bengaluru": (12.9716, 77.5946),
    "Ahmedabad": (23.0225, 72.5714),
}


def _error(message: str) -> dict:
    return {"ok": False, "error": message}


def _validate(city: str, day: str):
    canonical = next((name for name in CITY_COORDINATES if name.casefold() == str(city).casefold()), None)
    if canonical is None:
        return None, _error(f"unsupported city: {city}")
    try:
        # fromisoformat alone accepts some non-canonical forms; enforce exact ISO grammar.
        import re
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(day)):
            raise ValueError
        parsed = date.fromisoformat(day)
    except (TypeError, ValueError):
        return None, _error(f"invalid date: {day}")
    return (canonical, parsed), None


def get_weather(city: str, date: str) -> dict:
    """Return historical daily weather for one supported store city and ISO date."""
    validated, error = _validate(city, date)
    if error:
        return error
    canonical, parsed = validated
    mode = os.getenv("WEATHER_MODE", "stub").strip().lower() or "stub"
    if mode == "stub":
        doy = parsed.timetuple().tm_yday
        n = len(canonical)
        return {
            "ok": True, "city": canonical, "date": parsed.isoformat(), "mode": "stub",
            "temperature_c": float(20 + (n + doy) % 15),
            "humidity_pct": float(40 + (3 * n + doy) % 50),
            "wind_kmh": float(5 + doy % 10),
            "rain_mm": 6.5 if doy % 4 == 0 else 0.0,
        }
    if mode != "live":
        return _error(f"unsupported WEATHER_MODE: {mode}")

    latitude, longitude = CITY_COORDINATES[canonical]
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": parsed.isoformat(),
        "end_date": parsed.isoformat(),
        "timezone": "Asia/Kolkata",
        "daily": "temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_max,precipitation_sum",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "DMart-Regional-Director-Assistant/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                return _error(f"Open-Meteo returned HTTP {response.status}")
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            return _error("Open-Meteo response was not a JSON object")
        daily = payload.get("daily", {})
        fields = {
            "temperature_c": "temperature_2m_mean",
            "humidity_pct": "relative_humidity_2m_mean",
            "wind_kmh": "wind_speed_10m_max",
            "rain_mm": "precipitation_sum",
        }
        values = {}
        for output, source in fields.items():
            series = daily.get(source)
            if not isinstance(series, list) or not series or series[0] is None:
                return _error(f"Open-Meteo response missing {source}")
            values[output] = float(series[0])
        return {"ok": True, "city": canonical, "date": parsed.isoformat(), "mode": "live", **values}
    except urllib.error.HTTPError as exc:
        return _error(f"Open-Meteo HTTP error: {exc.code}")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return _error(f"Open-Meteo request failed: {type(exc).__name__}: {exc}")
