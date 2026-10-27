"""Configuration for workflow-engineering integrations."""

import os
from dataclasses import dataclass
from typing import cast

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ExternalApiSettings:
    """Configuration for Open-Meteo APIs used by workflow tools."""

    open_meteo_geocoding_url: str
    open_meteo_forecast_url: str
    open_meteo_air_quality_url: str
    timeout_seconds: float


@dataclass(frozen=True)
class FirmsSettings:
    """Configuration for the NASA FIRMS fire detection API."""

    map_key: str
    area_api_url: str
    source: str
    timeout_seconds: float


def get_external_api_settings() -> ExternalApiSettings:
    """Load Open-Meteo API configuration from environment variables."""
    geocoding_url = os.getenv("OPEN_METEO_GEOCODING_URL")
    forecast_url = os.getenv("OPEN_METEO_FORECAST_URL")
    air_quality_url = os.getenv("OPEN_METEO_AIR_QUALITY_URL")

    timeout_seconds = float(
        os.getenv("EXTERNAL_API_TIMEOUT_SECONDS", "10")
    )

    required_settings = [
        ("OPEN_METEO_GEOCODING_URL", geocoding_url),
        ("OPEN_METEO_FORECAST_URL", forecast_url),
        ("OPEN_METEO_AIR_QUALITY_URL", air_quality_url),
    ]

    missing = [
        name
        for name, value in required_settings
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing required Open-Meteo configuration: "
            + ", ".join(missing)
        )

    return ExternalApiSettings(
        open_meteo_geocoding_url=cast(str, geocoding_url),
        open_meteo_forecast_url=cast(str, forecast_url),
        open_meteo_air_quality_url=cast(str, air_quality_url),
        timeout_seconds=timeout_seconds,
    )


def get_firms_settings() -> FirmsSettings:
    """Load NASA FIRMS configuration from environment variables."""
    map_key = os.getenv("NASA_FIRMS_MAP_KEY")
    area_api_url = os.getenv("NASA_FIRMS_AREA_API_URL")
    source = os.getenv("NASA_FIRMS_SOURCE")

    timeout_seconds = float(
        os.getenv("EXTERNAL_API_TIMEOUT_SECONDS", "10")
    )

    required_settings = [
        ("NASA_FIRMS_MAP_KEY", map_key),
        ("NASA_FIRMS_AREA_API_URL", area_api_url),
        ("NASA_FIRMS_SOURCE", source),
    ]

    missing = [
        name
        for name, value in required_settings
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing required NASA FIRMS configuration: "
            + ", ".join(missing)
        )

    return FirmsSettings(
        map_key=cast(str, map_key),
        area_api_url=cast(str, area_api_url),
        source=cast(str, source),
        timeout_seconds=timeout_seconds,
    )
