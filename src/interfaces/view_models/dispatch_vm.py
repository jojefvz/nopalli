from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.domain.aggregates.dispatch.value_objects import Appointment, Container
from src.interfaces.view_models.task_vm import TaskViewModel


@dataclass(frozen=True)
class DispatchViewModel:
    """View-specific representation of a dispatch."""

    id: str
    reference: str
    status: str
    broker_name: str
    current_driver: str
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
    current_driver_name: str
    current_driver_id: str
    containers: list[dict]
    plan: list[TaskViewModel]

@dataclass(frozen=True)
class DispatchSuccessViewModel:
    """View model for projects in hierarchical list."""

    reference: str

