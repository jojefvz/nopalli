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

from src.interfaces.presenters.dispatch_presenter import DispatchPresenter
from src.interfaces.view_models.dispatch_vm import DispatchViewModel
from src.interfaces.view_models.base import OperationResult
from src.application.dtos.dispatch_dtos import (
    CreateDispatchRequest,
    )
from src.application.use_cases.dispatch_use_cases import (
    CreateDispatchUseCase,
    ListDispatchesUseCase,
)


@dataclass
class DispatchController:
    """
    Controller for dispatch-related operations, demonstrating Clean Architecture principles.

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
        create_use_case: Use case for creating dispatchs
        presenter: Handles formatting of dispatch data for the interface
    """

    create_use_case: CreateDispatchUseCase
    list_use_case: ListDispatchesUseCase
    presenter: DispatchPresenter

    # def handle_list(self) -> OperationResult[list[DispatchViewModel]]:
    #     result = self.list_use_case.execute()

    #     if result.is_success:
    #         view_models = [self.presenter.present_dispatch(d) for d in result.value]
    #         return OperationResult.succeed(view_models)

    #     error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
    #     return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_create(
            self,
            broker_ref: str,
            driver_ref: str,
            containers: list[str],
            plan: list[dict]
        ) -> OperationResult[DispatchViewModel]:
        """
        Handle dispatch creation requests from any interface.

        This method demonstrates Clean Architecture's separation of concerns by:
        1. Accepting primitive types as input (making it interface-agnostic)
        2. Converting input into the use case's required format
        3. Executing the use case without knowing its implementation details
        4. Using a presenter to format the response appropriately

        Args:
            title: The dispatch title
            description: The dispatch description

        Returns:
            OperationResult containing either:
            - Success: DispatchViewModel formatted for the interface
            - Failure: Error information formatted for the interface
        """
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated
            request = CreateDispatchRequest(
                broker_ref=broker_ref,
                driver_ref=driver_ref,
                containers=containers,
                plan=plan
                )

            # Execute use case and get domain-oriented result
            result = self.create_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_dispatch(result.value)
                return OperationResult.succeed(view_model)

            # Handle domain errors
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_list(self) -> OperationResult[list[DispatchViewModel]]:
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated

            # Execute use case and get domain-oriented result
            result = self.list_use_case.execute()

            if result.is_success:
                # Convert domain response to view model
                view_models = [self.presenter.present_dispatch(disp) for disp in result.value]
                return OperationResult.succeed(view_models)

            # Handle domain errors
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
