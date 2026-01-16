from dataclasses import dataclass

from src.application.common.result import Error, Result
from src.application.dtos.task_dtos import (
    CreateTaskRequest, 
    TaskResponse,
    )
from src.application.repositories.task_repository import TaskRepository
from src.domain.aggregates.dispatch.entities import Task
from src.domain.exceptions import ValidationError, BusinessRuleViolation
        

@dataclass
class CreateTaskUseCase:
    """Use case for creating a new task."""

    task_repository: TaskRepository

    def execute(self, request: CreateTaskRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            if self.task_repository.get_by_name(params['name']):
                raise BusinessRuleViolation('A task with that name already exists.')
            
            if self.task_repository.get_by_address(params['address']):
                raise BusinessRuleViolation('A task with that address already exists.')
            
            task = Task(
                name=params['name'],
                address=params['address'],
            )

            self.task_repository.save(task)

            return Result.success(TaskResponse.from_entity(task))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))