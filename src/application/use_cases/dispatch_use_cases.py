from dataclasses import dataclass

from ..common.result import Error, Result
from ..dtos.dispatch_dtos import CreateDispatchRequest, DispatchResponse
from ..repositories.dispatch_repository import DispatchRepository
from ...domain.aggregates.dispatch.aggregate import Dispatch
from ...domain.exceptions import ValidationError, BusinessRuleViolation


@dataclass
class CreateDispatchUseCase:
    """Use case for creating a new dispatch."""

    dispatch_repository: DispatchRepository

    def execute(self, request: CreateDispatchRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            dispatch = Dispatch(
                broker_ref=params['broker_ref'],
                containers=params['containers'],
                plan=params['plan'],
                driver_ref=params['driver_ref'],
            )

            self.dispatch_repository.save(dispatch)

            return Result.success(DispatchResponse.from_entity(dispatch))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))