"""Demonstrate parallel travel safety intelligence.

Author:
Gaurav Thakur

Description:
Runs a travel-safety request requiring weather, air-quality, and recent
satellite fire-activity information. Claude selects the required tools,
the application executes them concurrently, and Claude aggregates the
results into a travel assessment.
"""

import asyncio

from workflow_engineering.parallelization import (
    run_parallel_travel_workflow,
)


async def main() -> None:
    """Run the parallel travel workflow with an example request."""
    travel_request = (
        "I'm planning to spend the day outdoors in Los Angeles "
        "on October 30, 2026. Before I go, check the weather forecast, "
        "air quality, and recent nearby fire activity. "
        "Use all three sources and tell me whether conditions look "
        "suitable for outdoor activities."
    )

    result = await run_parallel_travel_workflow(
        travel_request
    )

    print("\nTravel safety assessment:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())