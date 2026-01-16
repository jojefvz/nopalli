from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.exceptions import DriverNotFoundError
from src.application.repositories.driver_repository import DriverRepository


class SQLAlchemyDriverRepository(DriverRepository):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def get(self, driver_id: UUID) -> Driver:
        """
        Retrieve a driver by its ID.

        Args:
            driver_id: The unique identifier of the driver

        Returns:
            The requested Driver entity

        Raises:
            DriverNotFoundError: If no driver exists with the given ID
        """
        session = self.session_factory()
        try:
            if driver := session.get(Driver, driver_id):
                session.expunge(driver)
                return driver
            raise DriverNotFoundError(driver_id)
        finally:
            session.close()

    def get_by_name(self, driver_name: str, driver_id: Optional[UUID] = None) -> Driver:
        session = self.session_factory()
        try:
            if driver_id:
                stmt = select(Driver).where(and_(
                    Driver.id != driver_id,
                    Driver.name == driver_name
                    )
                )
            else:
                stmt = select(Driver).where(Driver.name == driver_name)

            if driver := session.scalars(stmt).first():
                session.expunge(driver)
            return driver

        finally:
            session.close()

    def get_all(self) -> list[Driver]:
        """
        Retrieve all drivers.
        """
        session = self.session_factory()
        try:
            drivers = session.scalars(select(Driver)).all()
            session.expunge_all()
            return drivers
        finally:
            session.close()

    def get_available_and_operating(self) -> list[Driver]:
        """
        Retrieve all drivers.
        """
        session = self.session_factory()
        try:
            stmt = select(Driver).where(or_(
                Driver._status == DriverStatus.AVAILABLE,
                Driver._status == DriverStatus.OPERATING,
                )
            )
            drivers = session.scalars(stmt).all()
            session.expunge_all()
            return drivers
        finally:
            session.close()

    def save(self, driver: Driver) -> None:
        """
        Save a driver to the repository.

        Args:
            driver: The Driver entity to save
        """
        session = self.session_factory()
        try:
            session.add(driver)
            session.commit()
            session.refresh(driver)
            session.expunge(driver)
        finally:
            session.close()

    def delete(self, driver_id: UUID) -> None:
        """
        Delete a driver from the repository.

        Args:
            driver_id: The unique identifier of the driver to delete
        """
        session = self.session_factory()

        try:
            driver = session.get(Driver, driver_id)
            session.delete(driver)
            session.commit()
        finally:
            session.close()