from typing import Dict, Sequence
from uuid import UUID
from logging import getLogger

from src.application.repositories.driver_repository import DriverRepository
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.exceptions import DriverNotFoundError


logger = getLogger(__name__)


class InMemoryDriverRepository(DriverRepository):
    """In-memory implementation of DriverRepository."""

    def __init__(self) -> None:
        self._drivers: Dict[UUID, Driver] = {}

    def get(self, driver_id: UUID) -> Driver:
        """
        Retrieve a driver by ID.

        Args:
            driver_id: The unique identifier of the driver

        Returns:
            The requested driver

        Raises:
            DriverNotFoundError: If no driver exists with the given ID
        """
        if driver := self._drivers.get(driver_id):
            return driver
        raise DriverNotFoundError(driver_id)

    def save(self, driver: Driver) -> None:
        """
        Save a driver.

        Args:
            driver: The driver to save
        """
        logger.debug(f"Saving driver {driver.id}")
        self._drivers[driver.id] = driver

    def delete(self, driver_id: UUID) -> None:
        """
        Delete a driver.

        Args:
            driver_id: The unique identifier of the driver to delete
        """
        self._drivers.pop(driver_id, None)

    def get_all(self) -> Sequence[Driver]:
        """
        Get all drivers.

        Returns:
            A sequence of all drivers
        """
        return [driver for driver in self._drivers.values()]
