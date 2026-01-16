from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.domain.aggregates.dispatch.entities import Task
from src.domain.exceptions import TaskNotFoundError
from src.application.repositories.task_repository import TaskRepository


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

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
        session = self.session_factory()

        try:
            if task := session.get(Task, task_id):
                session.expunge(task)
                return task
            raise TaskNotFoundError(task_id)
        finally:
            session.close()

    def get_all(self) -> list[Task]:
        """
        Retrieve all tasks.
        """
        session = self.session_factory()

        try:
            tasks = session.scalars(select(Task)).all()
            session.expunge_all()
            return tasks
        finally:
            session.close()

    def save(self, task: Task) -> None:
        """
        Save a task to the repository.

        Args:
            task: The Task entity to save
        """
        session = self.session_factory()

        try:
            session.add(task)
            session.commit()
            session.refresh(task)
            session.expunge(task)
        finally:
            session.close()

    def delete(self, task_id: UUID) -> None:
        """
        Delete a task from the repository.

        Args:
            task_id: The unique identifier of the task to delete
        """
        session = self.session_factory()

        try:
            task = session.get(Task, task_id)
            session.delete(task)
            session.commit()
        finally:
            session.close()
