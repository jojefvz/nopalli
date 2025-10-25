from dataclasses import dataclass

from ..repository_factory import create_repositories
from ...application.use_cases.location_use_cases import (
    CreateLocationUseCase,
    GetLocationUseCase,
    ListLocationsUseCase,
    UpdateLocationUseCase
)
from ...application.repositories.location_repository import LocationRepository
from ...interfaces.controllers.location_controller import LocationController
from ...interfaces.presenters.location_presenter import LocationPresenter


def create_application(
        location_presenter: LocationPresenter
) -> "Application":
    """
    Factory function for the Application container.
    Create and configure the application container with all required dependencies.

    Args:
        location_presenter: Presenter for location-related output

    Returns:
        Configured Application instance
    """
    location_repository = create_repositories()

    return Application(
        location_repository=location_repository,
        location_presenter=location_presenter
    )

@dataclass
class Application:
    """Application container that wires together all components."""

    location_repository: LocationRepository
    location_presenter: LocationPresenter

    def __post_init__(self):

        # configure location use cases
        self.list_locations_use_case = ListLocationsUseCase(self.location_repository)
        self.create_location_use_case = CreateLocationUseCase(self.location_repository)
        self.get_location_use_case = GetLocationUseCase(self.location_repository)
        self.update_location_use_case = UpdateLocationUseCase(self.location_repository)

        # wire up location controller
        self.location_controller = LocationController(
            self.list_locations_use_case,
            self.create_location_use_case,
            self.location_presenter
            )
