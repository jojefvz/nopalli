from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskViewModel:
    """View-specific representation of a project."""

    id: str
    priority: str
    status: str
    instruction: str
    date: str
    location_name: Optional[str]
    container_number: Optional[str]
    appointment_type: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]