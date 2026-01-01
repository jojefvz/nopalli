from abc import ABC, abstractmethod
from typing import Optional

from src.interfaces.view_models.base import ErrorViewModel
from src.application.dtos.broker_dtos import BrokerResponse
from src.interfaces.view_models.broker_vm import BrokerViewModel


class BrokerPresenter(ABC):
    """Abstract base presenter for broker-related output."""

    @abstractmethod
    def present_broker(self, broker_response: BrokerResponse) -> BrokerViewModel:
        """Convert broker response to view model."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error message for display."""
        pass


class WebBrokerPresenter(BrokerPresenter):
    """Web-specific broker presenter."""

    def present_broker(self, broker_response: BrokerResponse) -> BrokerViewModel:
        """Format broker for web display."""
        return BrokerViewModel(
            id=broker_response.id,
            name=broker_response.name,
            status=broker_response.status,
            street_address=broker_response.street_address,
            city=broker_response.city,
            state=broker_response.state,
            zipcode=broker_response.zipcode,
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
