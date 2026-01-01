from abc import ABC, abstractmethod
from typing import Optional

from src.interfaces.view_models.base import ErrorViewModel
from src.application.dtos.location_dtos import LocationResponse
from src.interfaces.view_models.location_vm import LocationViewModel


class LocationPresenter(ABC):
    """Abstract base presenter for location-related output."""

    @abstractmethod
    def present_location(self, location_response: LocationResponse) -> LocationViewModel:
        """Convert location response to view model."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error message for display."""
        pass


class WebLocationPresenter(LocationPresenter):
    """Web-specific location presenter."""

    def present_location(self, location_response: LocationResponse) -> LocationViewModel:
        """Format location for web display."""
        return LocationViewModel(
            id=location_response.id,
            name=location_response.name,
            status=location_response.status.capitalize(),
            street_address=location_response.street_address,
            city=location_response.city,
            state=location_response.state,
            zipcode=location_response.zipcode,
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """Format error for web display."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")
