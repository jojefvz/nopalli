from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.broker.value_objects import BrokerStatus
from src.domain.aggregates.location.value_objects import Address
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
                session.expunge(broker)
                return broker
            raise BrokerNotFoundError(broker_id)
        finally:
            session.close()

    def get_by_name(self, broker_name: str, broker_id: Optional[UUID] = None) -> Broker:
        session = self.session_factory()

        try:
            if broker_id:
                stmt = select(Broker).where(and_(
                    Broker.id != broker_id,
                    Broker.name == broker_name
                    )
                )
            else:
                stmt = select(Broker).where(Broker.name == broker_name)

            if broker := session.scalars(stmt).first():
                session.expunge(broker)
            return broker

        finally:
            session.close()

    def get_active_brokers(self):
        session = self.session_factory()

        try:
            stmt = select(Broker).where(Broker._status == BrokerStatus.ACTIVE)

            brokers = session.scalars(stmt).all()
            print("ACITVE BROKERS", brokers)

            session.expunge_all()

            return brokers
        finally:
            session.close()

    def get_by_address(self, address: Address, broker_id: Optional[UUID] = None) -> Broker:
        session = self.session_factory()

        try:
            if broker_id:
                stmt = select(Broker).where(and_(
                    Broker.id != broker_id,
                    Broker.street_address == address.street_address,
                    Broker.city == address.city,
                    Broker.state == address.state,
                    Broker.zipcode == address.zipcode,
                    )
                )
            else:
                stmt = select(Broker).where(and_(
                        Broker.street_address == address.street_address,
                        Broker.city == address.city,
                        Broker.state == address.state,
                        Broker.zipcode == address.zipcode,
                    )
                )
            if broker := session.scalars(stmt).first():
                session.expunge(broker)
            return broker

        finally:
            session.close()

    def get_all(self) -> list[Broker]:
        """
        Retrieve all brokers.
        """
        session = self.session_factory()

        try:
            brokers = session.scalars(select(Broker)).all()
            session.expunge_all()
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
            session.refresh(broker)
            session.expunge(broker)
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
