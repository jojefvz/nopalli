from typing import Dict, Sequence
from uuid import UUID
from logging import getLogger

from ....application.repositories.broker_repository import BrokerRepository
from ....domain.aggregates.broker.aggregate import Broker
from ....domain.exceptions import BrokerNotFoundError


logger = getLogger(__name__)


class InMemoryBrokerRepository(BrokerRepository):
    """In-memory implementation of BrokerRepository."""

    def __init__(self) -> None:
        self._brokers: Dict[UUID, Broker] = {}

    def get(self, broker_id: UUID) -> Broker:
        """
        Retrieve a broker by ID.

        Args:
            broker_id: The unique identifier of the broker

        Returns:
            The requested broker

        Raises:
            BrokerNotFoundError: If no broker exists with the given ID
        """
        if broker := self._brokers.get(broker_id):
            return broker
        raise BrokerNotFoundError(broker_id)

    def save(self, broker: Broker) -> None:
        """
        Save a broker.

        Args:
            broker: The broker to save
        """
        logger.debug(f"Saving broker {broker.id}")
        self._brokers[broker.id] = broker

    def delete(self, broker_id: UUID) -> None:
        """
        Delete a broker.

        Args:
            broker_id: The unique identifier of the broker to delete
        """
        self._brokers.pop(broker_id, None)

    def get_all(self) -> Sequence[Broker]:
        """
        Get all brokers.

        Returns:
            A sequence of all brokers
        """
        return [broker for broker in self._brokers.values()]
