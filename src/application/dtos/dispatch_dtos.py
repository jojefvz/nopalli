from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Self
from uuid import UUID

from src.application.dtos.task_dtos import TaskResponse
from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Container, DispatchStatus, Instruction
from src.domain.aggregates.driver.aggregate import Driver


@dataclass(frozen=True)
class CreateDispatchRequest:
    """Request data for creating a new dispatch."""

    broker_id: str
    driver_id: str
    plan: list[dict]

    def __post_init__(self) -> None:
        """Validate request data"""
        # if not self.name.strip():
        #     raise ValueError("Dispatch name is required")
        pass
    
    def _parse_time(self, t_str):
            return time.fromisoformat(t_str) if t_str else None
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        plan = [
            {
                "priority": int(task["priority"]),
                "location_id": UUID(task["location_id"]) if task['location_id'] else None,
                "instruction": Instruction(task["instruction"]),
                "container": Container(task["container"]) if task['container'] else None,
                "date": date.fromisoformat(task["date"]),
                "appointment": None if not task["appointment"]["type"] else Appointment(
                        AppointmentType(task["appointment"]["type"]),
                        self._parse_time(task["appointment"]["start_time"]),
                        self._parse_time(task["appointment"]["end_time"]),
                    )
            } 
            for task in self.plan
        ]

        return {
            "broker_id": UUID(self.broker_id),
            "driver_id": UUID(self.driver_id) if self.driver_id else None,
            "plan": plan,
        }


@dataclass(frozen=True)
class DispatchResponse:
    """Response data for basic dispatch operations."""
    id: str
    reference: int
    status: DispatchStatus
    broker: Broker
    driver: Optional[Driver]
    container_numbers: list[str]
    plan: list[Task]
    
    @classmethod
    def from_entity(cls, dispatch: Dispatch) -> Self:
        """Create response from a Dispatch entity."""
        print("DISPATCH CONTAINERS:", dispatch.containers)
        return cls(
            id=str(dispatch.id),
            reference=dispatch.reference,
            status=dispatch.status,
            broker=dispatch.broker,
            driver=dispatch.driver,
            container_numbers=dispatch.containers,
            plan=[TaskResponse.from_entity(task) for task in dispatch.plan],   
        )
