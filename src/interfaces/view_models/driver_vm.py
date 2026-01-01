from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DriverViewModel:
    """View-specific representation of a project."""

    id: str
    name: str
    status: str


@dataclass(frozen=True)
class DriverListItemViewModel:
    """View model for projects in hierarchical list."""

    id: str
    name: str
    is_inbox: bool
    tasks: list["TaskListItemViewModel"]


@dataclass(frozen=True)
class TaskListItemViewModel:
    """View model for tasks in hierarchical list."""

    id: str
    letter_id: str  # 'a', 'b', etc.
    title: str
    status_display: str
    priority_display: str
    due_date_display: Optional[str]
