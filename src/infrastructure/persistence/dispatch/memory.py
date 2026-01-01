from typing import Dict, Sequence
from uuid import UUID
from logging import getLogger

from src.application.repositories.dispatch_repository import DispatchRepository
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.exceptions import DispatchNotFoundError


logger = getLogger(__name__)


class InMemoryDispatchRepository(DispatchRepository):
    """In-memory implementation of DispatchRepository."""

    def __init__(self) -> None:
        self._dispatches: Dict[UUID, Dispatch] = {}

    def get(self, dispatch_id: UUID) -> Dispatch:
        """
        Retrieve a dispatch by ID.

        Args:
            dispatch_id: The unique identifier of the dispatch

        Returns:
            The requested dispatch

        Raises:
            DispatchNotFoundError: If no dispatch exists with the given ID
        """
        if dispatch := self._dispatches.get(dispatch_id):
            return dispatch
        raise DispatchNotFoundError(dispatch_id)

    def save(self, dispatch: Dispatch) -> None:
        """
        Save a dispatch.

        Args:
            dispatch: The dispatch to save
        """
        logger.debug(f"Saving dispatch {dispatch.id}")
        self._dispatches[dispatch.id] = dispatch

    def delete(self, dispatch_id: UUID) -> None:
        """
        Delete a dispatch.

        Args:
            dispatch_id: The unique identifier of the dispatch to delete
        """
        self._dispatches.pop(dispatch_id, None)

    def get_all(self) -> Sequence[Dispatch]:
        """
        Get all dispatchs.

        Returns:
            A sequence of all dispatchs
        """
        return [dispatch for dispatch in self._dispatches.values()]
