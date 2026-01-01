from dataclasses import dataclass

from src.infrastructure.repository_factory import create_repositories
from src.application.use_cases.broker_use_cases import (
    ListBrokersUseCase,
    CreateBrokerUseCase,
    DeactivateBrokerUseCase,
    ActivateBrokerUseCase,
    EditBrokerUseCase
)
from src.application.use_cases.dispatch_use_cases import (
    CreateDispatchUseCase,
    ListDispatchesUseCase,
#     EditDispatchUseCase
)
from src.application.use_cases.driver_use_cases import (
    ListDriversUseCase,
    CreateDriverUseCase,
    DeactivateDriverUseCase,
    ActivateDriverUseCase,
    EditDriverUseCase
)
from src.application.use_cases.location_use_cases import (
    ListLocationsUseCase,
    CreateLocationUseCase,
    DeactivateLocationUseCase,
    ActivateLocationUseCase,
    EditLocationUseCase,
)
from src.application.repositories.broker_repository import BrokerRepository
from src.interfaces.controllers.broker_controller import BrokerController
from src.interfaces.presenters.broker_presenter import BrokerPresenter
from src.application.repositories.dispatch_repository import DispatchRepository
from src.interfaces.controllers.dispatch_controller import DispatchController
from src.interfaces.presenters.dispatch_presenter import DispatchPresenter
from src.application.repositories.driver_repository import DriverRepository
from src.interfaces.controllers.driver_controller import DriverController
from src.interfaces.presenters.driver_presenter import DriverPresenter
from src.application.repositories.location_repository import LocationRepository
from src.interfaces.controllers.location_controller import LocationController
from src.interfaces.presenters.location_presenter import LocationPresenter


def create_application(
        broker_presenter: BrokerPresenter,
        dispatch_presenter: DispatchPresenter,
        driver_presenter: DriverPresenter,
        location_presenter: LocationPresenter
) -> "Application":
    """
    Factory function for the Application container.
    Create and configure the application container with all required dependencies.

    Args:
        broker_presenter: Presenter for broker-related output
        dispatch_presenter: Presenter for dispatch-related output
        driver_presenter: Presenter for driver-related output
        location_presenter: Presenter for location-related output

    Returns:
        Configured Application instance
    """
    (
        broker_repository,
        dispatch_repository,
        driver_repository,
        location_repository
    ) = create_repositories()

    return Application(
        broker_repository=broker_repository,
        broker_presenter=broker_presenter,
        dispatch_repository=dispatch_repository,
        dispatch_presenter=dispatch_presenter,
        driver_repository=driver_repository,
        driver_presenter=driver_presenter,
        location_repository=location_repository,
        location_presenter=location_presenter
    )

@dataclass
class Application:
    """Application container that wires together all components."""

    broker_repository: BrokerRepository
    broker_presenter: BrokerPresenter
    dispatch_repository: DispatchRepository
    dispatch_presenter: DispatchPresenter
    driver_repository: DriverRepository
    driver_presenter: DriverPresenter
    location_repository: LocationRepository
    location_presenter: LocationPresenter
    

    def __post_init__(self):

        # configure broker use cases
        self.list_brokers_use_case = ListBrokersUseCase(self.broker_repository)
        self.create_broker_use_case = CreateBrokerUseCase(self.broker_repository)
        self.deactivate_broker_use_case = DeactivateBrokerUseCase(self.broker_repository)
        self.activate_broker_use_case = ActivateBrokerUseCase(self.broker_repository)
        self.edit_broker_use_case = EditBrokerUseCase(self.broker_repository)

        # configure driver use cases
        self.list_drivers_use_case = ListDriversUseCase(self.driver_repository)
        self.create_driver_use_case = CreateDriverUseCase(self.driver_repository)
        self.deactivate_driver_use_case = DeactivateDriverUseCase(self.driver_repository)
        self.activate_driver_use_case = ActivateDriverUseCase(self.driver_repository)
        self.edit_driver_use_case = EditDriverUseCase(self.driver_repository)

        # configure dispatch use cases
        self.list_dispatches_use_case = ListDispatchesUseCase(self.dispatch_repository)
        self.create_dispatch_use_case = CreateDispatchUseCase(
            self.dispatch_repository,
            self.broker_repository,
            self.driver_repository,
            self.location_repository,
            )
        # self.edit_dispatch_use_case = EditDispatchUseCase(self.dispatch_repository)

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
        
        # wire up dispatch controller
        self.dispatch_controller = DispatchController(
            self.create_dispatch_use_case,
            self.list_dispatches_use_case,
            # self.edit_dispatch_use_case,
            self.dispatch_presenter
            )
        
        # wire up driver controller
        self.driver_controller = DriverController(
            self.list_drivers_use_case,
            self.create_driver_use_case,
            self.deactivate_driver_use_case,
            self.activate_driver_use_case,
            self.edit_driver_use_case,
            self.driver_presenter
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
