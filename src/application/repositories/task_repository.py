"""
This module defines the repository interface for Task entity persistence.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.aggregates.dispatch.entities import Task


class TaskRepository(ABC):
    """Repository interface for Task entity persistence."""

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The requested Task entity

        Raises:
            TaskNotFoundError: If no task exists with the given ID
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """
        Retrieve all tasks.
        """
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        """
        Save a task to the repository.

        Args:
            task: The Task entity to save
        """
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """
        Delete a task from the repository.

        Args:
            task_id: The unique identifier of the task to delete
        """
        pass
