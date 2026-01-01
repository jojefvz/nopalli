from dataclasses import dataclass

from src.application.common.result import Error, Result
from src.application.dtos.location_dtos import (
    CreateLocationRequest, 
    LocationResponse,
    DeactivateLocationRequest,
    ActivateLocationRequest,
    EditLocationRequest,
    )
from src.application.repositories.location_repository import LocationRepository
from src.domain.aggregates.location.aggregate import Location
from src.domain.exceptions import ValidationError, BusinessRuleViolation
        

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
class DeactivateLocationUseCase:
    """Use case for deactivating a location."""

    location_repository: LocationRepository

    def execute(self, request: DeactivateLocationRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            location = self.location_repository.get(params['id'])

            location.deactivate()

            return Result.success(LocationResponse.from_entity(location))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class ActivateLocationUseCase:
    """Use case for activating a location."""

    location_repository: LocationRepository

    def execute(self, request: ActivateLocationRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            location = self.location_repository.get(params['id'])

            location.reactivate()

            return Result.success(LocationResponse.from_entity(location))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class EditLocationUseCase:
    """Use case for editing a location."""

    location_repository: LocationRepository

    def execute(self, request: EditLocationRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            id = params["id"]

            location = self.location_repository.get(id)

            location.name = params["name"]
            location.address = params["address"]

            return Result.success(LocationResponse.from_entity(location))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class GetLocationUseCase:
    """Use case for creating a new location."""

    location_repository: LocationRepository

    def execute(self, request) -> Result:
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
        

