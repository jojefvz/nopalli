from dataclasses import dataclass
import datetime
from typing import Optional, Self, Sequence
from uuid import UUID

from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Container, DispatchStatus


@dataclass(frozen=True)
class CreateDispatchRequest:
    """Request data for creating a new dispatch."""

    broker_ref: UUID
    containers: list[Container]
    plan: list[Task]
    driver_ref: UUID

    def __post_init__(self) -> None:
        """Validate request data"""
        if not self.name.strip():
            raise ValueError("Dispatch name is required")
        if len(self.name) > 100:
            raise ValueError("Project name cannot exceed 100 characters")
        if len(self.description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "broker_ref": self.broker_ref.strip(),
            "containers": self.containers.strip(),
            "plan": self.plan.strip(),
            "driver_ref": self.driver_ref.strip(),
        }


@dataclass(frozen=True)
class DispatchResponse:
    """Response data for basic project operations."""

    id: str
    name: str
    description: str
    status: DispatchStatus
    completion_date: Optional[datetime]
    tasks: Sequence[TaskResponse]

    @classmethod
    def from_entity(cls, project: Dispatch) -> Self:
        """Create response from a Project entity."""
        return cls(
            id=str(project.id),
            name=project.name,
            description=project.description,
            status=project.status,
            completion_date=project.completed_at if project.completed_at else None,
            tasks=[TaskResponse.from_entity(task) for task in project.tasks],
        )