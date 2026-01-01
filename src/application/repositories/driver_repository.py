"""
This module defines the repository interface for Driver entity persistence.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.driver.aggregate import Driver



class DriverRepository(ABC):
    """Repository interface for Driver entity persistence."""

    @abstractmethod
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
        pass

    @abstractmethod
    def get_all(self) -> list[Driver]:
        """
        Retrieve all drivers.
        """
        pass

    @abstractmethod
    def save(self, driver: Driver) -> None:
        """
        Save a driver to the repository.

        Args:
            driver: The Driver entity to save
        """
        pass

    @abstractmethod
    def delete(self, driver_id: UUID) -> None:
        """
        Delete a driver from the repository.

        Args:
            driver_id: The unique identifier of the driver to delete
        """
        pass
