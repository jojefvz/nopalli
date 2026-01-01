"""
This module defines the repository interface for Location entity persistence.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.location.aggregate import Location



class LocationRepository(ABC):
    """Repository interface for Location entity persistence."""

    @abstractmethod
    def get(self, location_id: UUID) -> Location:
        """
        Retrieve a location by its ID.

        Args:
            location_id: The unique identifier of the location

        Returns:
            The requested Location entity

        Raises:
            LocationNotFoundError: If no location exists with the given ID
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Location]:
        """
        Retrieve all locations.
        """
        pass

    @abstractmethod
    def save(self, location: Location) -> None:
        """
        Save a location to the repository.

        Args:
            location: The Location entity to save
        """
        pass

    @abstractmethod
    def delete(self, location_id: UUID) -> None:
        """
        Delete a location from the repository.

        Args:
            location_id: The unique identifier of the location to delete
        """
        pass
