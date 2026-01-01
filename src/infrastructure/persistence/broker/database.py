from typing import final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.exceptions import BrokerNotFoundError
from src.application.repositories.broker_repository import BrokerRepository


class SQLAlchemyBrokerRepository(BrokerRepository):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

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
        session = self.session_factory()

        try:
            if broker := session.get(Broker, broker_id):
                return broker
            raise BrokerNotFoundError(broker_id)
        finally:
            session.close()

    def get_all(self) -> list[Broker]:
        """
        Retrieve all brokers.
        """
        session = self.session_factory()

        try:
            brokers = session.scalars(select(Broker)).all()
            return brokers
        finally:
            session.close()

    def save(self, broker: Broker) -> None:
        """
        Save a broker to the repository.

        Args:
            broker: The Broker entity to save
        """
        session = self.session_factory()

        try:
            session.add(broker)
            session.commit()
        finally:
            session.close()

    def delete(self, broker_id: UUID) -> None:
        """
        Delete a broker from the repository.

        Args:
            broker_id: The unique identifier of the broker to delete
        """
        session = self.session_factory()

        try:
            broker = session.get(Broker, broker_id)
            session.delete(broker)
            session.commit()
        finally:
            session.close()
