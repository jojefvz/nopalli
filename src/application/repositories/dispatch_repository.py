"""
This module defines the repository interface for Dispatch entity persistence.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.dispatch.aggregate import Dispatch


class DispatchRepository(ABC):
    """Repository interface for Dispatch entity persistence."""

    @abstractmethod
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
        pass

    @abstractmethod
    def save(self, dispatch: Dispatch) -> None:
        """
        Save a project to the repository.

        Args:
            project: The Dispatch entity to save
        """
        pass

    @abstractmethod
    def delete(self, dispatch_id: UUID) -> None:
        """
        Delete a dispatch from the repository.

        Args:
            dispatch_id: The unique identifier of the dispatch to delete
        """
        pass