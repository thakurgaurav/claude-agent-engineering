"""Claude-facing tools for travel decision workflows.

Author:
Gaurav Thakur

Description:
Exposes travel-related capabilities to Claude-powered workflows, including
destination weather, air quality, and recent satellite fire activity.
"""

from anthropic import beta_tool

from workflow_engineering.tools.air_quality import check_air_quality
from workflow_engineering.tools.fire_activity import check_fire_activity
from workflow_engineering.tools.weather import check_weather


@beta_tool
def get_destination_weather(
    destination: str,
    travel_date: str,
) -> str:
    """Get the weather forecast for a destination on a specific travel date."""
    result = check_weather(destination, travel_date)

    return (
        f"Destination: {result.destination}\n"
        f"Date: {result.travel_date}\n"
        f"Maximum temperature: {result.temperature_max_c} °C\n"
        f"Minimum temperature: {result.temperature_min_c} °C\n"
        f"Precipitation probability: "
        f"{result.precipitation_probability_percent}%\n"
        f"Weather code: {result.weather_code}"
    )


@beta_tool
def get_destination_air_quality(
    destination: str,
    travel_date: str,
) -> str:
    """Get air quality information for a destination on a specific travel date."""
    result = check_air_quality(destination, travel_date)

    return (
        f"Destination: {result.destination}\n"
        f"Date: {result.travel_date}\n"
        f"Maximum US AQI: {result.us_aqi}\n"
        f"PM2.5 at maximum AQI: {result.pm2_5} µg/m³\n"
        f"PM10 at maximum AQI: {result.pm10} µg/m³"
    )


@beta_tool
def get_nearby_fire_activity(
    destination: str,
) -> str:
    """Get recent satellite fire activity near a travel destination."""
    result = check_fire_activity(destination)

    if result.detection_count == 0:
        return (
            f"Destination: {result.destination}\n"
            f"Search period: last {result.search_days} days\n"
            f"Search radius: {result.nearby_radius_km:.0f} km\n"
            "Nearby satellite thermal detections: 0"
        )

    return (
        f"Destination: {result.destination}\n"
        f"Search period: last {result.search_days} days\n"
        f"Search radius: {result.nearby_radius_km:.0f} km\n"
        f"Nearby satellite thermal detections: "
        f"{result.detection_count}\n"
        f"Closest detection: "
        f"{result.closest_detection_km:.1f} km\n"
        f"Most recent detection date: "
        f"{result.most_recent_detection_date}"
    )