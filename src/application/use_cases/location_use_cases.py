from dataclasses import dataclass

from ..common.result import Error, Result
from ..dtos.location_dtos import CreateLocationRequest, LocationResponse
from ..repositories.location_repository import LocationRepository
from ...domain.aggregates.location.aggregate import Location
from ...domain.exceptions import ValidationError, BusinessRuleViolation


@dataclass
class ListLocationsUseCase:
    location_repository: LocationRepository

    def execute(self) -> Result[list[LocationResponse]]:
        """
        List all locations.

        Returns:
            Result containing either:
            - Success: List of LocationResponse objects
            - Failure: Error information
        """
        try:
            locations = self.location_repository.get_all()
            return Result.success([LocationResponse.from_entity(l) for l in locations])
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class CreateLocationUseCase:
    """Use case for creating a new location."""

    location_repository: LocationRepository

    def execute(self, request: CreateLocationRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            location = Location(
                name=params['name'],
                address=params['address'],
            )

            self.location_repository.save(location)

            return Result.success(LocationResponse.from_entity(location))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class GetLocationUseCase:
    """Use case for creating a new location."""

    location_repository: LocationRepository

    def execute(self, request: CreateLocationRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            location = Location(
                name=params['name'],
                address=params['address'],
            )

            self.location_repository.save(location)

            return Result.success(LocationResponse.from_entity(location))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class UpdateLocationUseCase:
    """Use case for creating a new location."""

    location_repository: LocationRepository

    def execute(self, request: CreateLocationRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            location = Location(
                name=params['name'],
                address=params['address'],
            )

            self.location_repository.save(location)

            return Result.success(LocationResponse.from_entity(location))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))