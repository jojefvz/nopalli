from dataclasses import dataclass

from src.application.common.result import Error, Result
from src.application.dtos.dispatch_dtos import CreateDispatchRequest, DispatchResponse
from src.application.repositories.broker_repository import BrokerRepository
from src.application.repositories.dispatch_repository import DispatchRepository
from src.application.repositories.driver_repository import DriverRepository
from src.application.repositories.location_repository import LocationRepository
from src.domain.exceptions import ValidationError, BusinessRuleViolation
from src.domain.services import Dispatcher


@dataclass
class CreateDispatchUseCase:
    """Use case for creating a new dispatch."""

    dispatch_repository: DispatchRepository
    broker_repository: BrokerRepository
    driver_repository: DriverRepository
    location_repository: LocationRepository

    def execute(self, request: CreateDispatchRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            tasks = [
                Dispatcher.create_task(
                    task['priority'],
                    self.location_repository.get(task['location_ref']) if task['location_ref'] else None,
                    task['instruction'],
                    task['container'],
                    task['date'],
                    task['appointment']
                ) for task in params["plan"] 
            ]

            dispatch = Dispatcher.create_dispatch(
                self.broker_repository.get(params['broker_ref']),
                params['containers'],
                tasks,
                self.driver_repository.get(params['driver_ref']) if params['driver_ref'] else None
            )

            self.dispatch_repository.save(dispatch)

            return Result.success(DispatchResponse.from_entity(dispatch))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        
        except Exception as e:
            print(e)


@dataclass
class ListDispatchesUseCase:
    """Use case for listing all the dispatches."""

    dispatch_repository: DispatchRepository

    def execute(self):
        try:
            dispatches = self.dispatch_repository.get_all()

            return Result.success([DispatchResponse.from_entity(dispatch) for dispatch in dispatches])
        
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))