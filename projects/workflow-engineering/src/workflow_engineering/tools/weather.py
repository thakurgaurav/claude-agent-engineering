"""Weather capabilities backed by the Open-Meteo APIs.

Author:
    Gaurav Thakur
Description: This module provides functionality to resolve a human-readable location name into geographical coordinates (latitude and longitude) using the Open-Meteo Geocoding API. It defines a `Location` dataclass to represent the resolved location and a function `resolve_location` to perform the resolution.
    
"""

import time
from dataclasses import dataclass

import httpx

from workflow_engineering.config import get_external_api_settings
from workflow_engineering.tools.location import Location, resolve_location


@dataclass(frozen=True)
class WeatherResult:
    """Weather information relevant to a travel decision."""

    destination: str
    travel_date: str
    temperature_max_c: float
    temperature_min_c: float
    precipitation_probability_percent: int
    weather_code: int


def check_weather(destination: str, travel_date: str):
    """Get weather information for a destination and travel date."""

    location = resolve_location(destination)
    forecast = get_forecast(location, travel_date)

    daily = forecast["daily"]

    return WeatherResult(
        destination = location.name,
        travel_date = daily["time"][0],
        temperature_max_c=daily["temperature_2m_max"][0],
        temperature_min_c=daily["temperature_2m_min"][0],
        precipitation_probability_percent=(
            daily["precipitation_probability_max"][0]
        ),
        weather_code=daily["weather_code"][0],
    )


def get_forecast(location: Location, travel_date: str) -> dict:
    """Retrieve the daily weather forecast for a location and travel date."""

    settings = get_external_api_settings()

    start = time.perf_counter()

    response = httpx.get(
        settings.open_meteo_forecast_url,
        params={
            "latitude": location.latitude,
            "longitude": location.longitude,
            "start_date": travel_date,
            "end_date": travel_date,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max,"
                "weather_code"
            ),
            "timezone": "auto"

        },
        timeout=settings.timeout_seconds,
    )

    response.raise_for_status()

    elapsed = time.perf_counter() - start

    print(
        f"[TIMING] Open-Meteo weather API: "
        f"{elapsed:.2f}s"
    )

    return response.json()

