from dataclasses import dataclass
from datetime import date
from typing import Optional, Self
from uuid import UUID

from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, Container, Instruction, TaskStatus


@dataclass(frozen=True)
class TaskResponse:
    id: str
    status: TaskStatus
    priority: str
    instruction: Instruction
    date: date
    container: Optional[Container] = None
    location_ref: Optional[str] = None
    appointment: Optional[Appointment] = None

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        return cls(
            id=str(task.id),
            status=task.status,
            priority=task.priority,
            instruction=task.instruction,
            date=task.date,
            container=task.container,
            location_ref=task.location_ref,
            appointment=task.appointment
        )
