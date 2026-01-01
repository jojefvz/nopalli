from typing import final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.location.aggregate import Location
from src.domain.exceptions import LocationNotFoundError
from src.application.repositories.location_repository import LocationRepository


class SQLAlchemyLocationRepository(LocationRepository):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

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
        session = self.session_factory()

        try:
            if location := session.get(Location, location_id):
                return location
            raise LocationNotFoundError(location_id)
        finally:
            session.close()

    def get_all(self) -> list[Location]:
        """
        Retrieve all locations.
        """
        session = self.session_factory()

        try:
            locations = session.scalars(select(Location)).all()
            return locations
        finally:
            session.close()

    def save(self, location: Location) -> None:
        """
        Save a location to the repository.

        Args:
            location: The Location entity to save
        """
        session = self.session_factory()

        try:
            session.add(location)
            session.commit()
        finally:
            session.close()

    def delete(self, location_id: UUID) -> None:
        """
        Delete a location from the repository.

        Args:
            location_id: The unique identifier of the location to delete
        """
        session = self.session_factory()

        try:
            location = session.get(Location, location_id)
            session.delete(location)
            session.commit()
        finally:
            session.close()
