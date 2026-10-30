"""MongoDB repository for rental property data.

Author: Gaurav Thakur

Description:
Retrieves rental-property candidates from MongoDB using hard constraints.
"""

from typing import Any

from pymongo.collection import Collection

from workflow_engineering.domain.rental import (
    RentalProperty,
    RentalSearchCriteria,
)


class RentalPropertyRepository:
    """Provide read-only access to rental property data stored in MongoDB."""

    def __init__(self, collection: Collection) -> None:
        """Initialize the repository with a MongoDB collection."""
        self._collection = collection

    def find_candidates(
        self,
        criteria: RentalSearchCriteria,
        *,
        limit: int = 100,
    ) -> list[RentalProperty]:
        """Find rental properties satisfying the renter's hard constraints."""
        if limit <= 0:
            raise ValueError("Candidate limit must be greater than zero.")

        query: dict[str, Any] = {
            "city": criteria.city,
        }

        if criteria.max_monthly_rent is not None:
            query["monthly_rent"] = {
                "$lte": criteria.max_monthly_rent,
            }

        if criteria.min_bedrooms is not None:
            query["bedrooms"] = {
                "$gte": criteria.min_bedrooms,
            }

        if criteria.min_bathrooms is not None:
            query["bathrooms"] = {
                "$gte": criteria.min_bathrooms,
            }

        if criteria.pets_required:
            query["pets_allowed"] = "Yes"

        if criteria.parking_required:
            query["parking"] = "Yes"

        if criteria.property_type is not None:
            query["property_type"] = (
            self._to_storage_property_type(criteria.property_type)
            )

        documents = self._collection.find(query).limit(limit)
        
        return [
            self._to_rental_property(document)
            for document in documents
        ]

    @staticmethod
    def _to_rental_property(
        document: dict[str, Any],
    ) -> RentalProperty:
        """Map a MongoDB document to the rental property domain model."""
        return RentalProperty(
            property_id=document["property_id"],
            city=document["city"],
            state=document["state"],
            zip_code=document["zip_code"],
            neighborhood=document["neighborhood"],
            property_type=document["property_type"],
            bedrooms=document["bedrooms"],
            bathrooms=document["bathrooms"],
            square_feet=document["square_feet"],
            year_built=document["year_built"],
            monthly_rent=document["monthly_rent"],
            security_deposit=document["security_deposit"],
            lease_term_months=document["lease_term_months"],
            available_from=document["available_from"],
            parking=document["parking"] == "Yes",
            pets_allowed=document["pets_allowed"] == "Yes",
            furnished=document["furnished"] == "Yes",
            in_unit_laundry=document["in_unit_laundry"] == "Yes",
            gym=document["gym"] == "Yes",
            pool=document["pool"] == "Yes",
            air_conditioning=document["air_conditioning"] == "Yes",
            transit_score=document["transit_score"],
            walkability_score=document["walkability_score"],
            school_rating=document["school_rating"],
            safety_score=document["safety_score"],
            )
        
    @staticmethod
    def _to_storage_property_type(property_type: str) -> str:
        """Convert a domain property type to its MongoDB representation."""
        return property_type.strip().capitalize()
        
