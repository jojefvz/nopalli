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

from src.application.dtos.dispatch_dtos import (
    CreateDispatchRequest,
    GetDispatchRequest,
    EditDispatchRequest,
    StartDispatchRequest,
    GetLoadboardDispatchesRequest,
    StartTaskRequest,
    RevertTaskRequest,
    CompleteTaskRequest,
    )
from src.application.use_cases.dispatch_use_cases import (
    CreateDispatchUseCase,
    ListDispatchesUseCase,
    GetDispatchUseCase,
    EditDispatchUseCase,
    StartDispatchUseCase,
    GetLoadboardDispatchesUseCase,
    StartTaskUseCase,
    RevertTaskUseCase,
    CompleteTaskUseCase,
)
from src.domain.exceptions import ValidationError
from src.interfaces.presenters.dispatch_presenter import DispatchPresenter
from src.interfaces.view_models.dispatch_vm import (
    DispatchViewModel,
    EditDispatchViewModel,
    DispatchSuccessViewModel,
    StartDispatchSuccessViewModel,
    StartTaskSuccessViewModel,
    RevertTaskSuccessViewModel,
    CompleteTaskSuccessViewModel,
)
from src.interfaces.view_models.base import OperationResult


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
    get_dispatch_use_case: GetDispatchUseCase
    edit_use_case: EditDispatchUseCase
    start_dispatch_use_case: StartDispatchUseCase
    get_loadboard_use_case: GetLoadboardDispatchesUseCase
    start_task_use_case: StartTaskUseCase
    revert_task_use_case: RevertTaskUseCase
    complete_task_use_case: CompleteTaskUseCase
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
            broker_id: str,
            driver_id: str,
            plan: list[dict]
        ) -> OperationResult[DispatchSuccessViewModel]:
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
                broker_id=broker_id,
                driver_id=driver_id,
                plan=plan
                )

            # Execute use case and get domain-oriented result
            result = self.create_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_dispatch_success(result.value)
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

        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
        
    def handle_get_dispatch(self, dispatch_id: str) -> OperationResult[EditDispatchViewModel]:
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated

            # Execute use case and get domain-oriented result
            request = GetDispatchRequest(dispatch_id=dispatch_id)

            result = self.get_dispatch_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_edit_dispatch(result.value)
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

    def handle_edit(
            self,
            dispatch_id: str,
            broker_id: str,
            driver_id: str,
            plan: list[dict]
        ) -> OperationResult[DispatchSuccessViewModel]:
        """
        Handle dispatch edit requests from any interface.

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
            request = EditDispatchRequest(
                dispatch_id=dispatch_id,
                broker_id=broker_id,
                driver_id=driver_id,
                plan=plan
                )

            # Execute use case and get domain-oriented result
            result = self.edit_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_dispatch_success(result.value)
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
        
    def handle_start_dispatch(self, dispatch_id: str) -> OperationResult[StartDispatchSuccessViewModel]:
        try:
            request = StartDispatchRequest(dispatch_id=dispatch_id)

            # Execute use case and get domain-oriented result
            result = self.start_dispatch_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_start_dispatch_success(result.value)
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
        
    def handle_loadboard_list(self, date: str) -> OperationResult[list[DispatchViewModel]]:
        try:
            # Convert primitive input to use case request model specifically designed for the
            # Interface->Application boundary crossing
            # It contains validation specific to application needs
            # Ensures data entering the application layer is properly formatted and validated

            # Execute use case and get domain-oriented result
            request = GetLoadboardDispatchesRequest(date=date)
            result = self.get_loadboard_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_models = [self.presenter.present_dispatch(disp) for disp in result.value]
                return OperationResult.succeed(view_models)

            # Handle domain errors
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValidationError as e:
            # Handle validation errors
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
        
    def handle_start_task(self, dispatch_id: str, task_priority: str) -> OperationResult[StartTaskSuccessViewModel]:
        try:
            request = StartTaskRequest(dispatch_id, task_priority)

            # Execute use case and get domain-oriented result
            result = self.start_task_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_start_task_success(result.value)
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
        
    def handle_revert_task(self, dispatch_id: str, task_priority: str) -> OperationResult[RevertTaskSuccessViewModel]:
        try:
            request = RevertTaskRequest(dispatch_id, task_priority)

            # Execute use case and get domain-oriented result
            result = self.revert_task_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_revert_task_success(result.value)
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
        
    def handle_complete_task(self, dispatch_id: str, task_priority: str) -> OperationResult[CompleteTaskSuccessViewModel]:
        try:
            request = CompleteTaskRequest(dispatch_id, task_priority)

            # Execute use case and get domain-oriented result
            result = self.complete_task_use_case.execute(request)

            if result.is_success:
                # Convert domain response to view model
                view_model = self.presenter.present_complete_task_success(result.value)
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