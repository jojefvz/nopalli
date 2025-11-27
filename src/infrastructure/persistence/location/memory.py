from typing import Dict, Sequence
from uuid import UUID
from logging import getLogger

from ....application.repositories.location_repository import LocationRepository
from ....domain.aggregates.location.aggregate import Location
from ....domain.exceptions import LocationNotFoundError

logger = getLogger(__name__)


class InMemoryLocationRepository(LocationRepository):
    """In-memory implementation of LocationRepository."""

    def __init__(self) -> None:
        self._locations: Dict[UUID, Location] = {}

    def get(self, location_id: UUID) -> Location:
        """
        Retrieve a location by ID.

        Args:
            location_id: The unique identifier of the location

        Returns:
            The requested location

        Raises:
            LocationNotFoundError: If no location exists with the given ID
        """
        if location := self._locations.get(location_id):
            return location
        raise LocationNotFoundError(location_id)

    def save(self, location: Location) -> None:
        """
        Save a location.

        Args:
            location: The location to save
        """
        logger.debug(f"Saving location {location.id}")
        self._locations[location.id] = location

    def delete(self, location_id: UUID) -> None:
        """
        Delete a location.

        Args:
            location_id: The unique identifier of the location to delete
        """
        self._locations.pop(location_id, None)

    def get_all(self) -> Sequence[Location]:
        """
        Get all locations.

        Returns:
            A sequence of all locations
        """
        return [location for location in self._locations.values()]
