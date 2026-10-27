"""Tests for location resolution and process-local caching.

Author:
Gaurav Thakur

Description:
Verifies that resolved locations are cached in process-local memory and
that repeated requests for the same normalized destination do not trigger
additional geocoding requests.
"""

from unittest.mock import Mock

import workflow_engineering.tools.location as location_module
from workflow_engineering.tools.location import resolve_location


def test_resolve_location_reuses_cached_location(monkeypatch) -> None:
    """Reuse a cached location instead of calling geocoding again."""
    location_module._location_cache.clear()

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "results": [
            {
                "name": "Los Angeles",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "country": "United States",
            }
        ]
    }

    mock_get = Mock(return_value=mock_response)

    monkeypatch.setattr(
        location_module.httpx,
        "get",
        mock_get,
    )

    first_result = resolve_location("Los Angeles")
    second_result = resolve_location("  los angeles  ")

    assert first_result == second_result
    assert first_result.name == "Los Angeles"
    assert first_result.latitude == 34.0522
    assert first_result.longitude == -118.2437

    mock_get.assert_called_once()

    location_module._location_cache.clear()