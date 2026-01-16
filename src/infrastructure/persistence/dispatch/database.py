from typing import final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.dispatch.aggregate import Dispatch
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
            if dispatch := session.get(Dispatch, dispatch_id):
                return dispatch
            raise DispatchNotFoundError(dispatch_id)
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

    def save(self, dispatch: Dispatch) -> None:
        """
        Save a dispatch to the repository.

        Args:
            dispatch: The Dispatch entity to save
        """
        session = self.session_factory()

        try:
            session.add(dispatch)
            session.commit()
            session.refresh(dispatch)
            session.expunge(dispatch)
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
