from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Optional

from src.interfaces.presenters.task_presenter import WebTaskPresenter
from src.interfaces.view_models.base import ErrorViewModel
from src.application.dtos.dispatch_dtos import (
    DispatchResponse,
    StartDispatchResponse,
    StartTaskResponse,
    RevertTaskResponse,
    CompleteTaskResponse,
    )
from src.interfaces.view_models.dispatch_vm import (
    DispatchViewModel,
    EditDispatchViewModel,
    DispatchSuccessViewModel,
    StartDispatchSuccessViewModel,
    StartTaskSuccessViewModel,
    RevertTaskSuccessViewModel,
    CompleteTaskSuccessViewModel,
)


class DispatchPresenter(ABC):
    """Abstract base presenter for dispatch-related output."""

    @abstractmethod
    def present_dispatch(self, dispatch_response: DispatchResponse) -> DispatchViewModel:
        """Convert dispatch response to view model."""
        pass

    @abstractmethod
    def present_edit_dispatch(self, dispatch_response: DispatchResponse) -> EditDispatchViewModel:
        """Convert dispatch response to an editing view model."""
        pass

    @abstractmethod
    def present_dispatch_success(self, dispatch_response: DispatchResponse) -> DispatchSuccessViewModel:
        """Convert dispatch response to an editing view model."""
        pass

    @abstractmethod
    def present_start_dispatch_success(self, dispatch_response: StartDispatchResponse) -> StartDispatchSuccessViewModel:
        """Convert dispatch response to an editing view model."""
        pass
    
    @abstractmethod
    def present_start_task_success(self, dispatch_response: StartTaskResponse) -> StartTaskSuccessViewModel:
        """Convert dispatch response to an editing view model."""
        pass

    @abstractmethod
    def present_revert_task_success(self, dispatch_response: RevertTaskResponse) -> RevertTaskSuccessViewModel:
        """Convert dispatch response to an editing view model."""
        pass

    @abstractmethod
    def present_complete_task_success(self, dispatch_response: CompleteTaskResponse) -> CompleteTaskSuccessViewModel:
        """Convert dispatch response to an editing view model."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error message for display."""
        pass


class WebDispatchPresenter(DispatchPresenter):
    """Web-specific dispatch presenter."""
    def __init__(self):
        self.task_presenter = WebTaskPresenter()

    def _extract_driver_names(self, drivers_list):
        return [d.nickname if d.nickname else f'{d.first_name} {d.last_name}' for d in drivers_list]

    def present_dispatch(self, dispatch_response: DispatchResponse) -> DispatchViewModel:
        """Format dispatch for web display."""
        print("CONTAINERS PRESENTED:", [{**asdict(c), 'size': c.size.value} for c in dispatch_response.containers])
        return DispatchViewModel(
            id=dispatch_response.id,
            reference=str(dispatch_response.reference),
            status=dispatch_response.status.value,
            broker_name=dispatch_response.broker.name,
            current_driver_name=(
                    dispatch_response.current_driver.nickname
                    if dispatch_response.current_driver.nickname
                    else f"{dispatch_response.current_driver.first_name} {dispatch_response.current_driver.last_name}"
                ) if dispatch_response.current_driver else None,
            assigned_drivers=self._extract_driver_names(dispatch_response.assigned_drivers) if dispatch_response.assigned_drivers else None,
            containers=[{**asdict(c), 'size': c.size.value} for c in dispatch_response.containers],
            appointments=[
                {  
                    'date': str(a[0]),
                    'appointment_type': a[1].appointment_type.value.replace('_', ' ').title(),
                    'start_time': a[1].start_time.strftime("%I:%M %p") if a[1].start_time else None,
                    'end_time': a[1].end_time.strftime("%I:%M %p") if a[1].end_time else None,
                } for a in dispatch_response.appointments],
            plan=[self.task_presenter.present_task(task) for task in dispatch_response.plan]
        )
    
    def present_edit_dispatch(self, dispatch_response: DispatchResponse) -> EditDispatchViewModel:
        """Format dispatch for web display."""
        print("CONTAINERS PRESENTED:", [{**asdict(c), 'size': c.size.value} for c in dispatch_response.containers])
        return EditDispatchViewModel(
            id=dispatch_response.id,
            reference=str(dispatch_response.reference),
            broker_name=dispatch_response.broker.name,
            broker_id=str(dispatch_response.broker.id),
            current_driver_name=(
                    dispatch_response.current_driver.nickname
                    if dispatch_response.current_driver.nickname
                    else f"{dispatch_response.current_driver.first_name} {dispatch_response.current_driver.last_name}"
                ) if dispatch_response.current_driver else None,
            current_driver_id=str(dispatch_response.current_driver.id) if dispatch_response.current_driver else None,
            containers=[{**asdict(c), 'size': c.size.value} for c in dispatch_response.containers],
            plan=[self.task_presenter.present_edit_task(task) for task in dispatch_response.plan]
        )
    
    def present_dispatch_success(self, dispatch_response: DispatchResponse) -> DispatchSuccessViewModel:
        """Format error for web display."""
        return DispatchSuccessViewModel(reference=str(dispatch_response.reference))
    
    def present_start_dispatch_success(self, dispatch_response: StartDispatchResponse) -> StartDispatchSuccessViewModel:
        """Format error for web display."""
        return StartDispatchSuccessViewModel(
            id=str(dispatch_response.id),
            reference=str(dispatch_response.reference),
            status=str(dispatch_response.status.value),
            broker_name=dispatch_response.broker.name,
            current_driver_name=(
                    dispatch_response.current_driver.nickname
                    if dispatch_response.current_driver.nickname
                    else f"{dispatch_response.current_driver.first_name} {dispatch_response.current_driver.last_name}"
                ) if dispatch_response.current_driver else None,
            containers=[{**asdict(c), 'size': c.size.value} for c in dispatch_response.containers],
            plan=[self.task_presenter.present_edit_task(task) for task in dispatch_response.plan],
            errors=dispatch_response.errors
            )

    def present_start_task_success(self, dispatch_response: StartTaskResponse) -> StartTaskSuccessViewModel:
        return StartTaskSuccessViewModel(reference=str(dispatch_response.reference))
    
    def present_revert_task_success(self, dispatch_response: RevertTaskResponse) -> RevertTaskSuccessViewModel:
        return RevertTaskSuccessViewModel(reference=str(dispatch_response.reference))
    
    def present_complete_task_success(self, dispatch_response: CompleteTaskResponse) -> CompleteTaskSuccessViewModel:
        return CompleteTaskSuccessViewModel(reference=str(dispatch_response.reference))
    
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
