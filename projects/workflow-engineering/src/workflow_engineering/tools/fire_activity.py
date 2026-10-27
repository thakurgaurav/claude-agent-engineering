"""NASA FIRMS fire activity integration for travel safety workflows."""

import csv
import io
import math
import time
from dataclasses import dataclass

import httpx

from workflow_engineering.config import get_firms_settings
from workflow_engineering.tools.location import (
    Location,
    resolve_location,
)


@dataclass(frozen=True)
class FireDetection:
    """A satellite fire or thermal-anomaly detection."""

    latitude: float
    longitude: float
    brightness: float | None
    confidence: str
    acquisition_date: str
    acquisition_time: str
    distance_km: float


@dataclass(frozen=True)
class FireActivityResult:
    """Recent satellite fire activity near a travel destination."""

    destination: str
    search_days: int
    nearby_radius_km: float
    detection_count: int
    closest_detection_km: float | None
    most_recent_detection_date: str | None
    detections: tuple[FireDetection, ...]


def _distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """Calculate great-circle distance using the Haversine formula."""
    earth_radius_km = 6371.0

    lat1 = math.radians(latitude_1)
    lon1 = math.radians(longitude_1)
    lat2 = math.radians(latitude_2)
    lon2 = math.radians(longitude_2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    central_angle = 2 * math.atan2(
        math.sqrt(haversine),
        math.sqrt(1 - haversine),
    )

    return earth_radius_km * central_angle


def _bounding_box(
    location: Location,
    radius_km: float,
) -> tuple[float, float, float, float]:
    """Create an approximate FIRMS bounding box around a location."""
    latitude_delta = radius_km / 111.0

    longitude_scale = (
        111.0
        * math.cos(
            math.radians(location.latitude)
        )
    )

    longitude_delta = radius_km / longitude_scale

    west = location.longitude - longitude_delta
    south = location.latitude - latitude_delta
    east = location.longitude + longitude_delta
    north = location.latitude + latitude_delta

    return west, south, east, north


def get_fire_activity(
    location: Location,
    *,
    radius_km: float = 50.0,
    day_range: int = 5,
) -> str:
    """Retrieve recent NASA FIRMS detections around a location."""
    settings = get_firms_settings()

    west, south, east, north = _bounding_box(
        location,
        radius_km,
    )

    area = f"{west},{south},{east},{north}"

    url = (
        f"{settings.area_api_url}/"
        f"{settings.map_key}/"
        f"{settings.source}/"
        f"{area}/"
        f"{day_range}"
    )

    start = time.perf_counter()

    response = httpx.get(
        url,
        timeout=settings.timeout_seconds,
    )
    response.raise_for_status()

    elapsed = time.perf_counter() - start

    print(
        "[TIMING] NASA FIRMS fire-activity API: "
        f"{elapsed:.2f}s"
    )

    return response.text


def _parse_float(
    value: str | None,
) -> float | None:
    """Convert an optional CSV value to a float."""
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def parse_fire_activity(
    csv_payload: str,
    location: Location,
) -> tuple[FireDetection, ...]:
    """Convert NASA FIRMS CSV data into domain objects."""
    if not csv_payload.strip():
        return ()

    reader = csv.DictReader(
        io.StringIO(csv_payload)
    )

    detections: list[FireDetection] = []

    for row in reader:
        latitude = _parse_float(
            row.get("latitude")
        )
        longitude = _parse_float(
            row.get("longitude")
        )

        if latitude is None or longitude is None:
            continue

        distance_km = _distance_km(
            location.latitude,
            location.longitude,
            latitude,
            longitude,
        )

        detections.append(
            FireDetection(
                latitude=latitude,
                longitude=longitude,
                brightness=_parse_float(
                    row.get("bright_ti4")
                    or row.get("brightness")
                ),
                confidence=row.get(
                    "confidence",
                    "",
                ),
                acquisition_date=row.get(
                    "acq_date",
                    "",
                ),
                acquisition_time=row.get(
                    "acq_time",
                    "",
                ),
                distance_km=distance_km,
            )
        )

    return tuple(detections)


def check_fire_activity(
    destination: str,
    *,
    radius_km: float = 50.0,
    day_range: int = 5,
) -> FireActivityResult:
    """Check recent satellite thermal activity near a destination."""
    location = resolve_location(destination)

    payload = get_fire_activity(
        location,
        radius_km=radius_km,
        day_range=day_range,
    )

    detections = parse_fire_activity(
        payload,
        location,
    )

    nearby_detections = tuple(
        sorted(
            (
                detection
                for detection in detections
                if detection.distance_km <= radius_km
            ),
            key=lambda detection: detection.distance_km,
        )
    )

    closest_detection_km = (
        nearby_detections[0].distance_km
        if nearby_detections
        else None
    )

    dates = [
        detection.acquisition_date
        for detection in nearby_detections
        if detection.acquisition_date
    ]

    most_recent_detection_date = (
        max(dates)
        if dates
        else None
    )

    return FireActivityResult(
        destination=location.name,
        search_days=day_range,
        nearby_radius_km=radius_km,
        detection_count=len(nearby_detections),
        closest_detection_km=closest_detection_km,
        most_recent_detection_date=most_recent_detection_date,
        detections=nearby_detections,
    )