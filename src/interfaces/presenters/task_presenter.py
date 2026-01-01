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

    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """Format task for web display."""
                
        def parse_start_time(task_response):
            if task_response.appointment and task_response.appointment.start_time:
                return True
            return False
        
        def parse_end_time(task_response):
            if task_response.appointment and task_response.appointment.end_time:
                return True
            return False

        return TaskViewModel(
            id=task_response.id,
            status=task_response.status,
            instruction=task_response.instruction.name,
            container=task_response.container.number,
            date=task_response.date.isoformat(),
            appointment_type=task_response.appointment.appointment_type if task_response.appointment else None,
            start_time=task_response.appointment.start_time.isoformat() if parse_start_time(task_response) else None,
            end_time=task_response.appointment.end_time.isoformat() if parse_end_time(task_response) else None
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
