from dataclasses import dataclass

from ..repository_factory import create_repositories
from ...application.use_cases.broker_use_cases import (
    ListBrokersUseCase,
    CreateBrokerUseCase,
    DeactivateBrokerUseCase,
    ActivateBrokerUseCase,
    EditBrokerUseCase
)
from ...application.use_cases.location_use_cases import (
    ListLocationsUseCase,
    CreateLocationUseCase,
    DeactivateLocationUseCase,
    ActivateLocationUseCase,
    EditLocationUseCase,
)
from ...application.repositories.broker_repository import BrokerRepository
from ...interfaces.controllers.broker_controller import BrokerController
from ...interfaces.presenters.broker_presenter import BrokerPresenter
from ...application.repositories.location_repository import LocationRepository
from ...interfaces.controllers.location_controller import LocationController
from ...interfaces.presenters.location_presenter import LocationPresenter


def create_application(
        broker_presenter: BrokerPresenter,
        location_presenter: LocationPresenter
) -> "Application":
    """
    Factory function for the Application container.
    Create and configure the application container with all required dependencies.

    Args:
        broker_presenter: Presenter for broker-related output
        location_presenter: Presenter for location-related output

    Returns:
        Configured Application instance
    """
    broker_repository, location_repository = create_repositories()

    return Application(
        broker_repository=broker_repository,
        broker_presenter=broker_presenter,
        location_repository=location_repository,
        location_presenter=location_presenter
    )

@dataclass
class Application:
    """Application container that wires together all components."""

    broker_repository: BrokerRepository
    broker_presenter: BrokerPresenter
    location_repository: LocationRepository
    location_presenter: LocationPresenter

    def __post_init__(self):

        # configure broker use cases
        self.list_brokers_use_case = ListBrokersUseCase(self.broker_repository)
        self.create_broker_use_case = CreateBrokerUseCase(self.broker_repository)
        self.deactivate_broker_use_case = DeactivateBrokerUseCase(self.broker_repository)
        self.activate_broker_use_case = ActivateBrokerUseCase(self.broker_repository)
        self.edit_broker_use_case = EditBrokerUseCase(self.broker_repository)

        # configure location use cases
        self.list_locations_use_case = ListLocationsUseCase(self.location_repository)
        self.create_location_use_case = CreateLocationUseCase(self.location_repository)
        self.deactivate_location_use_case = DeactivateLocationUseCase(self.location_repository)
        self.activate_location_use_case = ActivateLocationUseCase(self.location_repository)
        self.edit_location_use_case = EditLocationUseCase(self.location_repository)

        # wire up broker controller
        self.broker_controller = BrokerController(
            self.list_brokers_use_case,
            self.create_broker_use_case,
            self.deactivate_broker_use_case,
            self.activate_broker_use_case,
            self.edit_broker_use_case,
            self.broker_presenter
            )
        
        # wire up location controller
        self.location_controller = LocationController(
            self.list_locations_use_case,
            self.create_location_use_case,
            self.deactivate_location_use_case,
            self.activate_location_use_case,
            self.edit_location_use_case,
            self.location_presenter
            )
