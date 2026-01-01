from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskViewModel:
    """View-specific representation of a project."""

    id: str
    status: str
    instruction: str
    container: str
    date: str
    appointment_type: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]