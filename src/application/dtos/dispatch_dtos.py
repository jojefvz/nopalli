from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Self
from uuid import UUID

from src.application.dtos.task_dtos import TaskResponse
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Container, DispatchStatus, Instruction


@dataclass(frozen=True)
class CreateDispatchRequest:
    """Request data for creating a new dispatch."""

    broker_ref: str
    driver_ref: Optional[str]
    containers: list[str]
    plan: list[dict]

    def __post_init__(self) -> None:
        """Validate request data"""
        # if not self.name.strip():
        #     raise ValueError("Dispatch name is required")
        pass

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        def parse_time(t_str):
            return time.fromisoformat(t_str) if t_str else None
        
        plan = [
            {
                "priority": int(task["priority"]),
                "location_ref": UUID(task["location_ref"]) if task['location_ref'] else None,
                "instruction": Instruction(task["instruction"]),
                "container": Container(task["container"]),
                "date": date.fromisoformat(task["date"]),
                "appointment": None if not task["appointment"]["type"] else Appointment(
                        AppointmentType(task["appointment"]["type"]),
                        parse_time(task["appointment"]["start_time"]),
                        parse_time(task["appointment"]["end_time"]),
                    )
            } 
            for task in self.plan
        ]
            

        return {
            "broker_ref": UUID(self.broker_ref),
            "driver_ref": UUID(self.driver_ref) if self.driver_ref else None,
            "containers": [Container(con) for con in self.containers],
            "plan": plan,
        }


@dataclass(frozen=True)
class DispatchResponse:
    """Response data for basic project operations."""
    id: str
    status: DispatchStatus
    broker_ref: str
    containers: list[Container]
    plan: list[Task]
    driver_ref: Optional[str] = None

    @classmethod
    def from_entity(cls, dispatch: Dispatch) -> Self:
        """Create response from a Project entity."""
        return cls(
            id=str(dispatch.id),
            status=dispatch.status,
            broker_ref=str(dispatch.broker_ref),
            containers=dispatch.containers,
            plan=[TaskResponse.from_entity(task) for task in dispatch.plan],
            driver_ref=str(dispatch.driver_ref)
        )
