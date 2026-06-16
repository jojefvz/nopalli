from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.interfaces.view_models.task_vm import TaskViewModel


@dataclass(frozen=True)
class DispatchViewModel:
    """View-specific representation of a dispatch."""

    id: str
    reference: str
    status: str
    broker_name: str
    current_driver_name: Optional[str]
    assigned_drivers: list[str]
    containers: list[dict]
    appointments: list[tuple[date, dict]]
    plan: list[TaskViewModel]

@dataclass(frozen=True)
class EditDispatchViewModel:
    """View-specific representation of a dispatch that will be edited."""

    id: str
    reference: str
    broker_name: str
    broker_id: str
    current_driver_name: Optional[str]
    current_driver_id: Optional[str]
    containers: list[dict]
    plan: list[TaskViewModel]

@dataclass(frozen=True)
class DispatchSuccessViewModel:
    """View model for projects in hierarchical list."""

    reference: str

@dataclass(frozen=True)
class StartDispatchSuccessViewModel:
    """View model for projects in hierarchical list."""

    id: str
    reference: str
    status: str
    broker_name: str
    current_driver_name: Optional[str]
    containers: list[dict]
    plan: list[TaskViewModel]
    errors: list[str]

@dataclass(frozen=True)
class StartTaskSuccessViewModel:
    """View model for projects in hierarchical list."""

    reference: str

@dataclass(frozen=True)
class RevertTaskSuccessViewModel:
    """View model for projects in hierarchical list."""

    reference: str

@dataclass(frozen=True)
class CompleteTaskSuccessViewModel:
    """View model for projects in hierarchical list."""

    reference: str