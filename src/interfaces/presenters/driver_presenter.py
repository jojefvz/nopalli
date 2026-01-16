from abc import ABC, abstractmethod
from typing import Optional

from src.interfaces.view_models.base import ErrorViewModel
from src.application.dtos.driver_dtos import DriverResponse
from src.interfaces.view_models.driver_vm import DriverViewModel


class DriverPresenter(ABC):
    """Abstract base presenter for driver-related output."""

    @abstractmethod
    def present_driver(self, driver_response: DriverResponse) -> DriverViewModel:
        """Convert driver response to view model."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error message for display."""
        pass


class WebDriverPresenter(DriverPresenter):
    """Web-specific driver presenter."""

    def present_driver(self, driver_response: DriverResponse) -> DriverViewModel:
        """Format driver for web display."""
        return DriverViewModel(
            id=driver_response.id,
            name=driver_response.name,
            status=driver_response.status.capitalize(),
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
