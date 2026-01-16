from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.location.aggregate import Location
from src.domain.aggregates.location.value_objects import Address
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
                session.expunge(location)
                return location
            raise LocationNotFoundError(location_id)
        finally:
            session.close()

    def get_by_name(self, location_name: str, location_id: Optional[UUID] = None) -> Location:
        session = self.session_factory()

        try:
            if location_id:
                stmt = select(Location).where(and_(
                    Location.id != location_id,
                    Location.name == location_name
                    )
                )
            else:
                stmt = select(Location).where(Location.name == location_name)

            if location := session.scalars(stmt).first():
                session.expunge(location)
            return location

        finally:
            session.close()

    def get_by_address(self, address: Address, location_id: Optional[UUID] = None) -> Location:
        session = self.session_factory()

        try:
            if location_id:
                stmt = select(Location).where(and_(
                    Location.id != location_id,
                    Location.street_address == address.street_address,
                    Location.city == address.city,
                    Location.state == address.state,
                    Location.zipcode == address.zipcode,
                    )
                )
            else:
                stmt = select(Location).where(and_(
                        Location.street_address == address.street_address,
                        Location.city == address.city,
                        Location.state == address.state,
                        Location.zipcode == address.zipcode,
                    )
                )
            if location := session.scalars(stmt).first():
                session.expunge(location)
            return location

        finally:
            session.close()


    def get_all(self) -> list[Location]:
        """
        Retrieve all locations.
        """
        session = self.session_factory()

        try:
            locations = session.scalars(select(Location)).all()
            session.expunge_all()
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
            session.refresh(location)
            session.expunge(location)
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
