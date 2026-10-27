"""Tests for NASA FIRMS fire-activity processing.

Author:
Gaurav Thakur

Description:
Verifies deterministic parsing and geographic-distance behavior for
satellite thermal detections without calling the live NASA FIRMS API.
"""

from workflow_engineering.tools.fire_activity import parse_fire_activity
from workflow_engineering.tools.location import Location


def test_parse_fire_activity_calculates_detection_distance() -> None:
    """Parse FIRMS CSV data and calculate distance from the destination."""
    location = Location(
        name="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
        country="United States",
    )

    csv_payload = """latitude,longitude,bright_ti4,acq_date
34.0522,-118.2437,320.5,2026-10-26
34.1522,-118.2437,315.0,2026-10-25
"""

    detections = parse_fire_activity(
        csv_payload,
        location,
    )

    assert len(detections) == 2

    first_detection = detections[0]
    second_detection = detections[1]

    assert first_detection.latitude == 34.0522
    assert first_detection.longitude == -118.2437
    assert first_detection.brightness == 320.5
    assert first_detection.acquisition_date == "2026-10-26"

    assert first_detection.distance_km < 0.1

    assert 10.0 < second_detection.distance_km < 12.5


def test_parse_fire_activity_handles_empty_payload() -> None:
    """Return no detections when FIRMS returns no data."""
    location = Location(
        name="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
        country="United States",
    )

    csv_payload = "latitude,longitude,bright_ti4,acq_date\n"

    detections = parse_fire_activity(
        csv_payload,
        location,
    )

    assert detections == ()