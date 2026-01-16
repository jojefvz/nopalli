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
from src.interfaces.presenters.broker_presenter import BrokerPresenter
from src.interfaces.view_models.broker_vm import BrokerViewModel
from src.interfaces.view_models.base import OperationResult
from src.application.dtos.broker_dtos import (
    CreateBrokerRequest,
    DeactivateBrokerRequest,
    ActivateBrokerRequest,
    EditBrokerRequest
    )
from src.application.use_cases.broker_use_cases import (
    ListBrokersUseCase,
    CreateBrokerUseCase,
    DeactivateBrokerUseCase,
    ActivateBrokerUseCase,
    EditBrokerUseCase,
    ActiveBrokersUseCase
)


@dataclass
class BrokerController:
    """
    Controller for broker-related operations, demonstrating Clean Architecture principles.

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
        create_use_case: Use case for creating brokers
        presenter: Handles formatting of broker data for the interface
    """

    list_use_case: ListBrokersUseCase
    create_use_case: CreateBrokerUseCase
    deactivate_use_case: DeactivateBrokerUseCase
    activate_use_case: ActivateBrokerUseCase
    edit_use_case: EditBrokerUseCase
    active_brokers_use_case: ActiveBrokersUseCase
    presenter: BrokerPresenter

    def handle_create(
            self,
            name: str,
            street_address: str,
            city: str,
            state: str,
            zipcode: str
        ) -> OperationResult[BrokerViewModel]:
        """
        Handle broker creation requests from any interface.

        This method demonstrates Clean Architecture's separation of concerns by:
        1. Accepting primitive types as input (making it interface-agnostic)
        2. Converting input into the use case's required format
        3. Executing the use case without knowing its implementation details
        4. Using a presenter to format the response appropriately

        Args:
            title: The broker title
            description: The broker description

        Returns:
            OperationResult containing either:
            - Success: BrokerViewModel formatted for the interface
            - Failure: Error information formatted for the interface
        """
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated
            request = CreateBrokerRequest(
                name=name,
                street_address=street_address,
                city=city,
                state=state,
                zipcode=zipcode,
                )

            # Execute use case and get domain-oriented result
            result = self.create_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_broker(result.value)
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

    def handle_list(self) -> OperationResult[list[BrokerViewModel]]:
        result = self.list_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_broker(broker) for broker in result.value]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)
    
    def handle_edit(
            self,
            id: str,
            name: str,
            street_address: str,
            city: str,
            state: str,
            zipcode: str
        ) -> OperationResult[BrokerViewModel]:
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated
            request = EditBrokerRequest(
                id=id,
                name=name,
                street_address=street_address,
                city=city,
                state=state,
                zipcode=zipcode
                )

            # Execute use case and get domain-oriented result
            result = self.edit_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_broker(result.value)
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

    def handle_deactivate(
            self,
            id: str
            ) -> OperationResult[BrokerViewModel]:
        try:
            request = DeactivateBrokerRequest(id)

            result = self.deactivate_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_broker(result.value)
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
            ) -> OperationResult[BrokerViewModel]:
        try:
            request = ActivateBrokerRequest(id)

            result = self.activate_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_broker(result.value)
                return OperationResult.succeed(view_model)
            
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        
        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_active_brokers(self) -> OperationResult[list[BrokerViewModel]]:
        result = self.active_brokers_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_broker(broker) for broker in result.value]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)
