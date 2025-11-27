"""
This module defines the repository interface for Broker entity persistence.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from ...domain.aggregates.broker.aggregate import Broker



class BrokerRepository(ABC):
    """Repository interface for Broker entity persistence."""

    @abstractmethod
    def get(self, broker_id: UUID) -> Broker:
        """
        Retrieve a broker by its ID.

        Args:
            broker_id: The unique identifier of the broker

        Returns:
            The requested Broker entity

        Raises:
            BrokerNotFoundError: If no broker exists with the given ID
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Broker]:
        """
        Retrieve all brokers.
        """
        pass

    @abstractmethod
    def save(self, broker: Broker) -> None:
        """
        Save a broker to the repository.

        Args:
            broker: The Broker entity to save
        """
        pass

    @abstractmethod
    def delete(self, broker_id: UUID) -> None:
        """
        Delete a broker from the repository.

        Args:
            broker_id: The unique identifier of the broker to delete
        """
        pass
