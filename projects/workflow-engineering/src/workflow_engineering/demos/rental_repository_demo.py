"""Demo for MongoDB rental-property candidate retrieval.

Author: Gaurav Thakur

Description:
Demonstrates retrieving rental-property candidates from MongoDB.
"""

from pymongo import MongoClient

from workflow_engineering.config import get_mongodb_settings
from workflow_engineering.domain.rental import RentalSearchCriteria
from workflow_engineering.repositories.rental_property_repository import (
    RentalPropertyRepository,
)


def main() -> None:
    """Retrieve rental candidates using deterministic hard constraints."""
    settings = get_mongodb_settings()

    criteria = RentalSearchCriteria(
        city="San Jose",
        max_monthly_rent=3500,
        min_bedrooms=2,
        pets_required=True,
        parking_required=True,
    )

    with MongoClient(settings.uri) as client:
        collection = client[settings.database][
            settings.properties_collection
        ]

        repository = RentalPropertyRepository(collection)
        candidates = repository.find_candidates(criteria, limit=10)

        print(f"Candidates found: {len(candidates)}")

        for candidate in candidates:
            print(
                candidate.property_id,
                candidate.city,
                candidate.monthly_rent,
                candidate.bedrooms,
                candidate.pets_allowed,
                candidate.parking,
                candidate.safety_score,
            )


if __name__ == "__main__":
    main()
