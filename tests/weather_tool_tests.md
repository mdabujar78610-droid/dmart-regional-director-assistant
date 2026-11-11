# Weather Tool Test Record

Run from the repository root with `WEATHER_MODE=stub` (PowerShell: `$env:WEATHER_MODE='stub'`; macOS/Linux: `WEATHER_MODE=stub`). These are pasted outputs from `tools.weather.get_weather`.

```python
from tools.weather import get_weather

print(get_weather('Mumbai', '2026-05-15'))
print(get_weather('Pune', '2026-05-16'))
print(get_weather('Hyderabad', '2026-04-01'))
print(get_weather('Kolkata', '2026-05-15'))
print(get_weather('Mumbai', '15-05-2026'))
print(get_weather('Ahmedabad', '2026-05-15'))
```

## Captured outputs

```text
{'ok': True, 'city': 'Mumbai', 'date': '2026-05-15', 'mode': 'stub', 'temperature_c': 26.0, 'humidity_pct': 43.0, 'wind_kmh': 10.0, 'rain_mm': 0.0}
{'ok': True, 'city': 'Pune', 'date': '2026-05-16', 'mode': 'stub', 'temperature_c': 25.0, 'humidity_pct': 88.0, 'wind_kmh': 11.0, 'rain_mm': 6.5}
{'ok': True, 'city': 'Hyderabad', 'date': '2026-04-01', 'mode': 'stub', 'temperature_c': 30.0, 'humidity_pct': 58.0, 'wind_kmh': 6.0, 'rain_mm': 0.0}
{'ok': False, 'error': 'unsupported city: Kolkata'}
{'ok': False, 'error': 'invalid date: 15-05-2026'}
{'ok': True, 'city': 'Ahmedabad', 'date': '2026-05-15', 'mode': 'stub', 'temperature_c': 29.0, 'humidity_pct': 52.0, 'wind_kmh': 10.0, 'rain_mm': 0.0}
```

All six cases return a dictionary. Invalid inputs return structured errors without raising exceptions.
