from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, sessionmaker

from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import DispatchStatus
from src.domain.exceptions import DispatchNotFoundError
from src.application.repositories.dispatch_repository import DispatchRepository


class SQLAlchemyDispatchRepository(DispatchRepository):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def get(self, dispatch_id: UUID) -> Dispatch:
        """
        Retrieve a dispatch by its ID.

        Args:
            dispatch_id: The unique identifier of the dispatch

        Returns:
            The requested Dispatch entity

        Raises:
            DispatchNotFoundError: If no dispatch exists with the given ID
        """
        session = self.session_factory()

        try:
            dispatch = session.get(Dispatch, dispatch_id, options=[
                joinedload(Dispatch.broker),
                joinedload(Dispatch.current_driver),
                joinedload(Dispatch.plan).joinedload(Task.location),
            ])
            if dispatch is None:
                raise DispatchNotFoundError(dispatch_id)
            session.expunge_all()
            return dispatch
        finally:
            session.close()

    def get_all(self) -> list[Dispatch]:
        """
        Retrieve all dispatchs.
        """
        session = self.session_factory()

        try:
            dispatches = session.scalars(select(Dispatch)).all()
            session.expunge_all()
            return dispatches
        finally:
            session.close()
    
    def get_loadboard_by_date(self, date: date) -> list[Dispatch]:
        """
        Retrieve all in progress dispatches by date.
        """
        session = self.session_factory()

        try:
            earliest_appointment = session.query(
            Task.dispatch_id,
            func.min(Task.date).label('earliest_date')
            ).filter(
                Task.appointment_type.isnot(None)
            ).group_by(
                Task.dispatch_id
            ).subquery()

            dispatches = session.query(Dispatch).join(
                earliest_appointment,
                earliest_appointment.c.dispatch_id == Dispatch.id
            ).filter(
                Dispatch._status == DispatchStatus.IN_PROGRESS,
                earliest_appointment.c.earliest_date == date
            ).options(
                joinedload(Dispatch.broker),
                joinedload(Dispatch.current_driver),
                joinedload(Dispatch.plan).joinedload(Task.location),
            ).all()

            session.expunge_all()
            return dispatches
        finally:
            session.close()

    def save(self, dispatch: Dispatch) -> None:
        """
        Save a dispatch to the repository.

        Args:
            dispatch: The Dispatch entity to save
        """
        session = self.session_factory()

        try:
            merged = session.merge(dispatch)
            session.commit()
            session.refresh(merged)
            session.expunge_all()
        finally:
            session.close()

    def delete(self, dispatch_id: UUID) -> None:
        """
        Delete a dispatch from the repository.

        Args:
            dispatch_id: The unique identifier of the dispatch to delete
        """
        session = self.session_factory()

        try:
            dispatch = session.get(Dispatch, dispatch_id)
            session.delete(dispatch)
            session.commit()
        finally:
            session.close()

