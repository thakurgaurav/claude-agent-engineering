"""Location resolution shared by travel intelligence tools.

Author:
Gaurav Thakur

Description:
Resolves destination names into geographic coordinates using Open-Meteo
geocoding. Resolved locations are cached in process-local memory so
travel tools can reuse previously resolved locations.
"""

import threading
import time
from dataclasses import dataclass

import httpx

from workflow_engineering.config import get_external_api_settings


@dataclass(frozen=True)
class Location:
    """Resolved geographic location."""

    name: str
    latitude: float
    longitude: float
    country: str


# Process-local in-memory cache.
_location_cache: dict[str, Location] = {}

# Protects cache writes. The lock is intentionally not held during
# external API calls.
_location_cache_lock = threading.Lock()


def _normalize_destination(destination: str) -> str:
    """Normalize a destination into a stable cache key."""
    return destination.strip().casefold()


def resolve_location(destination: str) -> Location:
    """Resolve a destination using a process-local memory cache.

    Cache reads do not acquire the write lock. On a cache miss, location
    resolution happens without holding the lock because network I/O may
    take significant time.

    The lock is acquired only for the short cache update operation.
    """
    cache_key = _normalize_destination(destination)

    # Fast path: read from the local cache without holding the write lock.
    cached_location = _location_cache.get(cache_key)

    if cached_location is not None:
        print(
            f"[CACHE HIT] resolve_location('{destination}')"
        )
        return cached_location

    print(
        f"[CACHE MISS] resolve_location('{destination}')"
    )

    # Resolve the location without holding the cache lock.
    settings = get_external_api_settings()

    start = time.perf_counter()

    response = httpx.get(
        settings.open_meteo_geocoding_url,
        params={
            "name": destination,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=settings.timeout_seconds,
    )
    response.raise_for_status()

    elapsed = time.perf_counter() - start

    print(
        f"[TIMING] resolve_location('{destination}'): "
        f"{elapsed:.2f}s"
    )

    payload = response.json()
    results = payload.get("results")

    if not results:
        raise ValueError(
            f"Unable to resolve destination: {destination}"
        )

    result = results[0]

    resolved_location = Location(
        name=result["name"],
        latitude=float(result["latitude"]),
        longitude=float(result["longitude"]),
        country=result.get("country", ""),
    )

  
    with _location_cache_lock:
        existing_location = _location_cache.get(cache_key)

        if existing_location is not None:
            return existing_location

        _location_cache[cache_key] = resolved_location

    return resolved_location