from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Self
from uuid import UUID

from src.application.dtos.task_dtos import TaskResponse
from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import (
     Appointment, AppointmentType, Container, 
     ContainerSize, DispatchStatus, Instruction
)
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
                "location_id": UUID(task["location_id"]),
                "instruction": Instruction(task["instruction"]),
                "container": Container(
                    task["container"]["number"],
                    ContainerSize(task["container"]["size"])
                ) if task['container'] else None,
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
class GetDispatchRequest:
    """Request data for creating a new dispatch."""

    dispatch_id: str

    def __post_init__(self) -> None:
        """Validate request data"""
        # if not self.name.strip():
        #     raise ValueError("Dispatch name is required")
        pass
    
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "dispatch_id": UUID(self.dispatch_id),
        }


@dataclass(frozen=True)
class EditDispatchRequest:
    """Request data for creating a new dispatch."""

    dispatch_id: str
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
                "location_id": UUID(task["location_id"]) if task["location_id"] else None,
                "instruction": Instruction(task["instruction"]),
                "container": Container(
                    task["container"]["number"],
                    ContainerSize(task["container"]["size"])
                ) if task['container'] else None,
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
            "dispatch_id": UUID(self.dispatch_id),
            "broker_id": UUID(self.broker_id),
            "driver_id": UUID(self.driver_id) if self.driver_id else None,
            "plan": plan,
        }


@dataclass(frozen=True)
class StartDispatchRequest:
    """Request to start a dispatch."""

    dispatch_id: str

    def __post_init__(self) -> None:
        """Validate request data"""
        pass
    
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "dispatch_id": UUID(self.dispatch_id),
        }


@dataclass(frozen=True)
class GetLoadboardDispatchesRequest:
    """Request data for creating a new dispatch."""

    date: str

    def __post_init__(self) -> None:
        """Validate request data"""
        # if not self.name.strip():
        #     raise ValueError("Dispatch name is required")
        pass
    
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "date": date.fromisoformat(self.date),
        }


@dataclass(frozen=True)
class StartTaskRequest:
    """Request to start current task on in progress dispatch."""

    dispatch_id: str
    task_priority: str

    def __post_init__(self) -> None:
        """Validate request data"""
        pass
    
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "dispatch_id": UUID(self.dispatch_id),
            "task_priority": int(self.task_priority),
        }
    

@dataclass(frozen=True)
class RevertTaskRequest:
    """Request to revert current task on in progress dispatch."""

    dispatch_id: str
    task_priority: str

    def __post_init__(self) -> None:
        """Validate request data"""
        pass
    
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "dispatch_id": UUID(self.dispatch_id),
            "task_priority": int(self.task_priority),
        }
    
@dataclass(frozen=True)
class CompleteTaskRequest:
    """Request to revert current task on in progress dispatch."""

    dispatch_id: str
    task_priority: str

    def __post_init__(self) -> None:
        """Validate request data"""
        pass
    
    
    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "dispatch_id": UUID(self.dispatch_id),
            "task_priority": int(self.task_priority),
        }


@dataclass(frozen=True)
class DispatchResponse:
    """Response data for basic dispatch operations."""
    id: str
    reference: int
    status: DispatchStatus
    broker: Broker
    current_driver: Optional[Driver]
    assigned_drivers: list[Driver]
    containers: list[Container]
    appointments: list[tuple[date, Appointment]]
    plan: list[Task]
    
    @classmethod
    def from_entity(cls, dispatch: Dispatch) -> Self:
        """Create response from a Dispatch entity."""
        return cls(
            id=str(dispatch.id),
            reference=dispatch.reference,
            status=dispatch.status,
            broker=dispatch.broker,
            current_driver=dispatch.current_driver,
            assigned_drivers=dispatch.assigned_drivers,
            containers=dispatch.containers,
            appointments=dispatch.appointments,
            plan=[TaskResponse.from_entity(task) for task in dispatch.plan],   
        )
    

@dataclass(frozen=True)
class StartDispatchResponse:
    """Response data for basic dispatch operations."""
    id: str
    reference: int
    status: DispatchStatus
    broker: Broker
    current_driver: Optional[Driver]
    containers: list[Container]
    plan: list[Task]
    errors: list[str]
    
    @classmethod
    def from_entity_and_errors(cls, dispatch: Dispatch, errors: list) -> Self:
        """Create response after calling to start dispatch."""
        return cls(
            id=str(dispatch.id),
            reference=dispatch.reference,
            status=dispatch.status,
            broker=dispatch.broker,
            current_driver=dispatch.current_driver,
            containers=dispatch.containers,
            plan=dispatch.plan,
            errors=errors
        )


@dataclass(frozen=True)
class StartTaskResponse:
    """Response data for basic dispatch operations."""
    reference: int
    
    @classmethod
    def from_entity(cls, dispatch: Dispatch) -> Self:
        """Create response from a Dispatch entity."""
        return cls(
            reference=dispatch.reference,
        )
    
@dataclass(frozen=True)
class RevertTaskResponse:
    """Response data for basic dispatch operations."""
    reference: int
    
    @classmethod
    def from_entity(cls, dispatch: Dispatch) -> Self:
        """Create response from a Dispatch entity."""
        return cls(
            reference=dispatch.reference,
        )
    
@dataclass(frozen=True)
class CompleteTaskResponse:
    """Response data for basic dispatch operations."""
    reference: int
    
    @classmethod
    def from_entity(cls, dispatch: Dispatch) -> Self:
        """Create response from a Dispatch entity."""
        return cls(
            reference=dispatch.reference,
        )