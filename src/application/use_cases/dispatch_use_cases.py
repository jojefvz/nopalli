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

            print("PARAMS PRINTED", params)

            tasks = [
                Dispatcher.create_task(
                    task['priority'],
                    self.location_repository.get(task['location_id']) if task['location_id'] else None,
                    task['instruction'],
                    task['container'],
                    task['date'],
                    task['appointment']
                ) for task in params["plan"] 
            ]

            dispatch = Dispatcher.create_dispatch(
                self.broker_repository.get(params['broker_id']),
                self.driver_repository.get(params['driver_id']) if params['driver_id'] else None,
                tasks
            )

            self.dispatch_repository.save(dispatch)

            print("DISPATCH:", dispatch)
            print("DISPATCH BROKER:", dispatch.broker)
            print("DISPATCH PLAN:", dispatch.plan)
            print("DISPATCH CONTAINERS:", dispatch.containers)

            return Result.success(DispatchResponse.from_entity(dispatch))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        except Exception as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class ListDispatchesUseCase:
    """Use case for listing all the dispatches."""

    dispatch_repository: DispatchRepository

    def execute(self):
        try:
            dispatches = self.dispatch_repository.get_all()

            return Result.success([DispatchResponse.from_entity(dis) for dis in dispatches])
        
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
