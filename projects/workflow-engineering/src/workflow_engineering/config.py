"""Configuration for workflow-engineering integrations.

Author:
    Gaurav Thakur
Description:
    Loads environment-backed settings for external APIs and MongoDB.
"""

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

@dataclass(frozen=True)
class MongoDbConfig:
    """Mongodb Configuration for connecting to mongodb"""
    uri: str
    database: str
    properties_collection: str



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

    check_missing(required_settings, "Missing required Open-Meteo configuration: ")

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

    check_missing(required_settings, "Missing required NASA FIRMS configuration: ")

    return FirmsSettings(
        map_key=cast(str, map_key),
        area_api_url=cast(str, area_api_url),
        source=cast(str, source),
        timeout_seconds=timeout_seconds,
    )

def get_mongodb_settings() -> MongoDbConfig:
    """Load MongoDB configuration from environment variables."""
    uri = os.getenv("MONGODB_URI")
    database = os.getenv("MONGODB_DATABASE")
    properties_collection = os.getenv("MONGODB_PROPERTIES_COLLECTION")

    required_settings = [
        ("MONGODB_URI", uri),
        ("MONGODB_DATABASE", database),
        ("MONGODB_PROPERTIES_COLLECTION", properties_collection),
    ]

    check_missing(required_settings, "Missing required MongoDB configuration: ")
    return MongoDbConfig(
        uri = cast(str, uri),
        database = cast(str, database),
        properties_collection= cast(str, properties_collection),
    )

def check_missing(
    required_settings: list[tuple[str, str | None]],
    error_message: str,
) -> None:
    missing = [
        name
        for name, value in required_settings
        if not value
    ]
    if missing:
        raise RuntimeError(
            error_message + ", ".join(missing)
        )
