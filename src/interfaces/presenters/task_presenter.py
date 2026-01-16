from abc import ABC, abstractmethod
from importlib.resources import read_text
from typing import Optional

from src.interfaces.view_models.base import ErrorViewModel
from src.application.dtos.task_dtos import TaskResponse
from src.interfaces.view_models.task_vm import TaskViewModel


class TaskPresenter(ABC):
    """Abstract base presenter for task-related output."""

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """Convert task response to view model."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error message for display."""
        pass


class WebTaskPresenter(TaskPresenter):
    """Web-specific task presenter."""

    def _parse_start_time(self, task_response):
            if task_response.appointment.appointment_type and task_response.appointment.start_time:
                return True
            return False
        
    def _parse_end_time(self, task_response):
        if task_response.appointment.appointment_type and task_response.appointment.end_time:
            return True
        return False

    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """Format task for web display."""
        print("APPOINTMENT OBJECT:", task_response.appointment)
        return TaskViewModel(
            id=task_response.id,
            priority=str(task_response.priority),
            status=task_response.status.value.capitalize(),
            instruction=task_response.instruction.value,
            date=task_response.date.isoformat(),
            location_name=task_response.location.name if task_response.location else None,
            container_number=task_response.container.number if task_response.container else None,
            appointment_type=task_response.appointment.appointment_type.value if task_response.appointment.appointment_type else None,
            start_time=task_response.appointment.start_time.isoformat() if self._parse_start_time(task_response) else "",
            end_time=task_response.appointment.end_time.isoformat() if self._parse_end_time(task_response) else ""
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
