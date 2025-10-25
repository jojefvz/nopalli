from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LocationViewModel:
    """View-specific representation of a project."""

    id: str
    name: str
    status: str
    street_address: str
    city: str
    state: int
    zipcode: int


@dataclass(frozen=True)
class LocationListItemViewModel:
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
