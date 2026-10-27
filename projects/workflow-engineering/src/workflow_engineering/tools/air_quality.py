"""Air quality integration for travel safety workflows."""

import time
from dataclasses import dataclass

import httpx

from workflow_engineering.config import get_external_api_settings
from workflow_engineering.tools.location import Location, resolve_location


@dataclass(frozen=True)
class AirQualityResult:
    """Air quality information relevant to a travel decision."""

    destination: str
    travel_date: str
    us_aqi: int
    pm2_5: float
    pm10: float

def get_air_quality(
    location: Location,
    travel_date: str,
) -> dict:
    """Retrieve air quality data for a location and travel date."""
    settings = get_external_api_settings()

    start = time.perf_counter()
    response = httpx.get(
        settings.open_meteo_air_quality_url,
        params={
            "latitude": location.latitude,
            "longitude": location.longitude,
            "start_date": travel_date,
            "end_date": travel_date,
            "hourly": "us_aqi,pm2_5,pm10",
            "timezone": "auto",
        },
        timeout=settings.timeout_seconds,
    )

    response.raise_for_status()

    elapsed = time.perf_counter() - start

    print(
        f"[TIMING] Open-Meteo air-quality API: "
        f"{elapsed:.2f}s"
    )

    return response.json()


def check_air_quality(
    destination: str,
    travel_date: str,
) -> AirQualityResult:
    """Get travel-relevant air quality information for a destination."""
    location = resolve_location(destination)
    payload = get_air_quality(location, travel_date)

    hourly = payload["hourly"]

    aqi_values = [
        value
        for value in hourly["us_aqi"]
        if value is not None
    ]

    if not aqi_values:
        raise RuntimeError(
            f"No air quality data available for "
            f"{destination} on {travel_date}."
        )

    max_aqi = max(aqi_values)
    max_aqi_index = hourly["us_aqi"].index(max_aqi)

    return AirQualityResult(
        destination=location.name,
        travel_date=travel_date,
        us_aqi=max_aqi,
        pm2_5=hourly["pm2_5"][max_aqi_index],
        pm10=hourly["pm10"][max_aqi_index],
    )