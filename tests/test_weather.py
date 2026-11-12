"""Rubric checks for deterministic stub values and structured weather errors."""

import os

from tools.weather import get_weather


def test_required_weather_stub_values(monkeypatch):
    monkeypatch.setenv("WEATHER_MODE", "stub")
    cases = [
        ("Mumbai", "2026-05-15", 26.0, 43.0, 10.0, 0.0),
        ("Pune", "2026-05-16", 25.0, 88.0, 11.0, 6.5),
        ("Hyderabad", "2026-04-01", 30.0, 58.0, 6.0, 0.0),
    ]
    for city, day, temperature, humidity, wind, rain in cases:
        result = get_weather(city, day)
        assert result["ok"] is True
        assert result["mode"] == "stub"
        assert result["city"] == city
        assert result["date"] == day
        assert result["temperature_c"] == temperature
        assert result["humidity_pct"] == humidity
        assert result["wind_kmh"] == wind
        assert result["rain_mm"] == rain


def test_weather_rejects_unsupported_city_without_raising(monkeypatch):
    monkeypatch.setenv("WEATHER_MODE", "stub")
    result = get_weather("Patna", "2026-05-15")
    assert result["ok"] is False
    assert "unsupported city: Patna" in result["error"]


def test_weather_rejects_invalid_iso_dates_without_raising(monkeypatch):
    monkeypatch.setenv("WEATHER_MODE", "stub")
    for day in ("2026-5-15", "2026-02-30", "15-05-2026"):
        result = get_weather("Mumbai", day)
        assert result["ok"] is False
        assert day in result["error"]
