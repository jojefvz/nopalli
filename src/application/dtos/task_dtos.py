from dataclasses import dataclass
import datetime
from typing import Optional, Self

from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, Container, Instruction, TaskStatus
from src.domain.aggregates.location.aggregate import Location


@dataclass(frozen=True)
class CreateTaskRequest:
    pass


@dataclass(frozen=True)
class TaskResponse:
    id: str
    priority: int
    status: TaskStatus
    instruction: Instruction
    date: datetime.date
    location: Optional[Location]
    container: Optional[Container]
    appointment: Optional[Appointment]

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        return cls(
            id=str(task.id),
            status=task.status,
            priority=task.priority,
            instruction=task.instruction,
            date=task.date,
            location=task.location,
            container=task.container,
            appointment=task.appointment
        )
