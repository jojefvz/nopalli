from dataclasses import dataclass

from src.application.common.result import Error, Result
from src.application.dtos.dispatch_dtos import (
    CreateDispatchRequest,
    DispatchResponse,
    GetDispatchRequest,
    EditDispatchRequest,
    StartDispatchRequest
)
from src.application.repositories.broker_repository import BrokerRepository
from src.application.repositories.dispatch_repository import DispatchRepository
from src.application.repositories.driver_repository import DriverRepository
from src.application.repositories.location_repository import LocationRepository
from src.application.repositories.task_repository import TaskRepository
from src.domain.exceptions import ValidationError, BusinessRuleViolation
from src.domain.services import Dispatcher
from src.infrastructure.web.routes.dispatch.routes import edit_dispatch


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
                    self.location_repository.get(task['location_id']),
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
            print("DISPATCH CURRENT DRIVER:", dispatch.current_driver)
            print("DISPATCH ASSIGNED DRIVERS:", dispatch.assigned_drivers)
            print("DISPATCH USE CASE CONTAINERS:", dispatch.containers)
            print("DISPATCH PLAN:", dispatch.plan)

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


@dataclass
class GetDispatchUseCase:
    """Use case for listing all the dispatches."""

    dispatch_repository: DispatchRepository

    def execute(self, request: GetDispatchRequest):
        try:
            params = request.to_execution_params()
            dispatch = self.dispatch_repository.get(params['dispatch_id'])

            return Result.success(DispatchResponse.from_entity(dispatch))
        
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class EditDispatchUseCase:
    """Use case for creating a new dispatch."""

    dispatch_repository: DispatchRepository
    broker_repository: BrokerRepository
    driver_repository: DriverRepository
    location_repository: LocationRepository
    task_repository: TaskRepository

    def execute(self, request: EditDispatchRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            print("PARAMS PRINTED", params)

            edited_dispatch = self.dispatch_repository.get(params['dispatch_id'])

            if params['broker_id'] != edited_dispatch.broker.id:
                edited_dispatch.broker = self.broker_repository.get(params['broker_id'])

            if params['driver_id'] and params['driver_id'] != edited_dispatch.current_driver.id:
                edited_dispatch.current_driver = self.driver_repository.get(params['driver_id'])
            elif params['driver_id'] is None:
                edited_dispatch.current_driver = None

            plan_length_difference = (len(edited_dispatch.plan) - len(params['plan']))
            plan_length_overlap = len(edited_dispatch.plan) if plan_length_difference <= 0 else len(params['plan'])

            for i in range(plan_length_overlap):
                edited_dispatch.plan[i].priority = params['plan'][i]['priority']
                if params['plan'][i]['location_id'] != edited_dispatch.plan[i].location.id:
                    edited_dispatch.plan[i].location = self.location_repository.get(params['plan'][i]['location_id'])
                edited_dispatch.plan[i].instruction = params['plan'][i]['instruction']
                edited_dispatch.plan[i].container = params['plan'][i]['container']
                edited_dispatch.plan[i].date = params['plan'][i]['date']
                edited_dispatch.plan[i].appointment = params['plan'][i]['appointment']

            if plan_length_difference > 0:
                for _ in range(plan_length_difference):
                    edited_dispatch.plan.pop()

            elif plan_length_difference < 0:
                for i in range(len(edited_dispatch.plan), len(params['plan'])):
                    edited_dispatch.plan.append(
                        Dispatcher.create_task(
                            params['plan'][i]['priority'],
                            self.location_repository.get(params['plan'][i]['location_id']),
                            params['plan'][i]['instruction'],
                            params['plan'][i]['container'],
                            params['plan'][i]['date'],
                            params['plan'][i]['appointment']
                        )
                    )

            self.dispatch_repository.save(edited_dispatch)

            print("NEWLY EDITED DISPATCH:", edited_dispatch)
            print("NEWLY EDITED BROKER:", edited_dispatch.broker)
            print("NEWLY EDITED CURRENT DRIVER:", edited_dispatch.current_driver)
            print("NEWLY EDITED ASSIGNED DRIVERS:", edited_dispatch.assigned_drivers)
            print("NEWLY EDITED CONTAINERS:", edited_dispatch.containers)
            print("NEWLY EDITED PLAN:", edited_dispatch.plan)

            return Result.success(DispatchResponse.from_entity(edited_dispatch))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        except Exception as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class StartDispatchUseCase:
    """Use case for listing all the dispatches."""

    dispatch_repository: DispatchRepository

    def execute(self, request: StartDispatchRequest):
        try:
            params = request.to_execution_params()
            dispatch = self.dispatch_repository.get(params['dispatch_id'])

            Dispatcher.start_dispatch(params['dispatch_id'], dispatch.current_driver)
            
            return Result.success(DispatchResponse.from_entity(dispatch))
        
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))