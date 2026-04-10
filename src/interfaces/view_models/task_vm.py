from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskViewModel:
    """View-specific representation of a project."""

    id: str
    priority: str
    status: str
    location_name: str
    instruction: str
    container_number: Optional[str]
    date: str
    appointment_type: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]


@dataclass(frozen=True)
class EditTaskViewModel:
    """View-specific representation of a project."""

    location_name: str
    location_id: str
    instruction: str
    container_number: Optional[str]
    date: str
    appointment_type: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]