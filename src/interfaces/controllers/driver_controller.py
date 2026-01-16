"""
This module contains controllers that implement the Interface Adapters layer of Clean Architecture.

Controllers are responsible for:
1. Accepting input from external sources (CLI, web, etc.)
2. Converting that input into the format required by use cases
3. Executing the appropriate use case
4. Converting the result into a view model suitable for the interface
5. Handling and formatting any errors that occur

Key Clean Architecture benefits demonstrated in these controllers:
- Dependency Rule is followed: controllers depend inward towards use cases
- Separation of Concerns: controllers handle routing and data conversion only
- Independence: business logic remains isolated in use cases
- Flexibility: new interfaces can be added without changing use cases
"""

from dataclasses import dataclass

from src.domain.exceptions import ValidationError
from src.interfaces.presenters.driver_presenter import DriverPresenter
from src.interfaces.view_models.driver_vm import DriverViewModel
from src.interfaces.view_models.base import OperationResult
from src.application.dtos.driver_dtos import (
    CreateDriverRequest,
    DeactivateDriverRequest,
    ActivateDriverRequest,
    EditDriverRequest,
    MakeAvailableDriverRequest,
    SitOutDriverRequest
    )
from src.application.use_cases.driver_use_cases import (
    ListDriversUseCase,
    CreateDriverUseCase,
    DeactivateDriverUseCase,
    ActivateDriverUseCase,
    EditDriverUseCase,
    MakeAvailableDriverUseCase,
    SitOutDriverUseCase,
    AvailableAndOperatingDriversUseCase
)


@dataclass
class DriverController:
    """
    Controller for driver-related operations, demonstrating Clean Architecture principles.

    This controller adheres to Clean Architecture by:
    - Depending only on abstractions (use cases and presenters)
    - Converting external input into use case request models
    - Ensuring business rules remain in the use cases
    - Using presenters to format output appropriately for the interface

    The clear separation of concerns allows:
    - Easy testing through dependency injection
    - Addition of new interfaces without changing business logic
    - Modification of presentation logic without affecting core functionality

    Attributes:
        create_use_case: Use case for creating drivers
        presenter: Handles formatting of driver data for the interface
    """

    list_use_case: ListDriversUseCase
    create_use_case: CreateDriverUseCase
    sit_out_use_case: SitOutDriverUseCase
    make_available_use_case: MakeAvailableDriverUseCase
    deactivate_use_case: DeactivateDriverUseCase
    activate_use_case: ActivateDriverUseCase
    edit_use_case: EditDriverUseCase
    available_and_operating_drivers_use_case: AvailableAndOperatingDriversUseCase
    presenter: DriverPresenter

    def handle_create(
            self,
            name: str
        ) -> OperationResult[DriverViewModel]:
        """
        Handle driver creation requests from any interface.

        This method demonstrates Clean Architecture's separation of concerns by:
        1. Accepting primitive types as input (making it interface-agnostic)
        2. Converting input into the use case's required format
        3. Executing the use case without knowing its implementation details
        4. Using a presenter to format the response appropriately

        Args:
            title: The driver title
            description: The driver description

        Returns:
            OperationResult containing either:
            - Success: DriverViewModel formatted for the interface
            - Failure: Error information formatted for the interface
        """
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated
            request = CreateDriverRequest(name=name)

            # Execute use case and get domain-oriented result
            result = self.create_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_driver(result.value)
                return OperationResult.succeed(view_model)

            # Handle domain errors
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_list(self) -> OperationResult[list[DriverViewModel]]:
        result = self.list_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_driver(driver) for driver in result.value]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)
    
    def handle_edit(
            self,
            id: str,
            name: str
        ) -> OperationResult[DriverViewModel]:
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated
            request = EditDriverRequest(
                id=id,
                name=name
            )

            # Execute use case and get domain-oriented result
            result = self.edit_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_driver(result.value)
                return OperationResult.succeed(view_model)

            # Handle domain errors
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_sit_out(
            self,
            id: str
            ) -> OperationResult[DriverViewModel]:
        try:
            request = SitOutDriverRequest(id)

            result = self.sit_out_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_driver(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
        
    def handle_make_available(
            self,
            id: str
            ) -> OperationResult[DriverViewModel]:
        try:
            request = MakeAvailableDriverRequest(id)

            result = self.make_available_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_driver(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
    
    def handle_deactivate(
            self,
            id: str
            ) -> OperationResult[DriverViewModel]:
        try:
            request = DeactivateDriverRequest(id)

            result = self.deactivate_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_driver(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
        
    def handle_activate(
            self,
            id: str
            ) -> OperationResult[DriverViewModel]:
        try:
            request = ActivateDriverRequest(id)

            result = self.activate_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_driver(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_available_and_operating_drivers(self) -> OperationResult[list[DriverViewModel]]:
        result = self.available_and_operating_drivers_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_driver(driver) for driver in result.value]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)