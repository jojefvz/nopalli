from abc import ABC, abstractmethod
from typing import Optional

from src.interfaces.presenters.task_presenter import WebTaskPresenter
from src.interfaces.view_models.base import ErrorViewModel
from src.application.dtos.dispatch_dtos import DispatchResponse
from src.interfaces.view_models.dispatch_vm import DispatchViewModel


class DispatchPresenter(ABC):
    """Abstract base presenter for dispatch-related output."""

    @abstractmethod
    def present_dispatch(self, dispatch_response: DispatchResponse) -> DispatchViewModel:
        """Convert dispatch response to view model."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error message for display."""
        pass


class WebDispatchPresenter(DispatchPresenter):
    """Web-specific dispatch presenter."""
    def __init__(self):
        self.task_presenter = WebTaskPresenter()

    def present_dispatch(self, dispatch_response: DispatchResponse) -> DispatchViewModel:
        """Format dispatch for web display."""
        return DispatchViewModel(
            id=dispatch_response.id,
            status=dispatch_response.status,
            containers=[con.number for con in dispatch_response.containers],
            plan=[self.task_presenter.present_task(task) for task in dispatch_response.plan]
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
