from dataclasses import dataclass

from src.application.common.result import Error, Result
from src.application.dtos.driver_dtos import (
    CreateDriverRequest, 
    DriverResponse,
    DeactivateDriverRequest,
    ActivateDriverRequest,
    EditDriverRequest,
    MakeAvailableDriverRequest,
    SitOutDriverRequest,
    )
from src.application.repositories.driver_repository import DriverRepository
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.exceptions import ValidationError, BusinessRuleViolation


@dataclass
class CreateDriverUseCase:
    """Use case for creating a new driver."""

    driver_repository: DriverRepository

    def execute(self, request: CreateDriverRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            if self.driver_repository.get_by_name(params['name']):
                raise BusinessRuleViolation('A driver with that name already exists.')
            
            driver = Driver(name=params['name'])

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class ListDriversUseCase:
    driver_repository: DriverRepository

    def execute(self) -> Result[list[DriverResponse]]:
        """
        List all drivers.

        Returns:
            Result containing either:
            - Success: List of DriverResponse objects
            - Failure: Error information
        """
        try:
            drivers = self.driver_repository.get_all()
            return Result.success([DriverResponse.from_entity(l) for l in drivers])
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class SitOutDriverUseCase:
    """Use case for deactivating a driver."""

    driver_repository: DriverRepository

    def execute(self, request: SitOutDriverRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            driver = self.driver_repository.get(params['id'])

            driver.sit_out()

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class MakeAvailableDriverUseCase:
    """Use case for activating a driver."""

    driver_repository: DriverRepository

    def execute(self, request: MakeAvailableDriverRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            driver = self.driver_repository.get(params['id'])

            driver.make_available()

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class DeactivateDriverUseCase:
    """Use case for deactivating a driver."""

    driver_repository: DriverRepository

    def execute(self, request: DeactivateDriverRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            driver = self.driver_repository.get(params['id'])

            driver.deactivate()

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class ActivateDriverUseCase:
    """Use case for activating a driver."""

    driver_repository: DriverRepository

    def execute(self, request: ActivateDriverRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            driver = self.driver_repository.get(params['id'])

            driver.reactivate()

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class EditDriverUseCase:
    """Use case for editing a driver."""

    driver_repository: DriverRepository

    def execute(self, request: EditDriverRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            if self.driver_repository.get_by_name(params['name'], params['id']):
                raise BusinessRuleViolation('A driver with that name already exists.')
            
            id = params["id"]

            driver = self.driver_repository.get(id)

            driver.name = params["name"]

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class GetDriverUseCase:
    """Use case for creating a new driver."""

    driver_repository: DriverRepository

    def execute(self, request) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            driver = Driver(name=params['name'])

            self.driver_repository.save(driver)

            return Result.success(DriverResponse.from_entity(driver))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class AvailableAndOperatingDriversUseCase:
    """Use case for creating a new driver."""

    driver_repository: DriverRepository

    def execute(self) -> Result:
        """Execute the use case."""
        try:
            drivers = self.driver_repository.get_available_and_operating()
            print("AVAILABLE ANDFAS", drivers)
            return Result.success([DriverResponse.from_entity(d) for d in drivers])

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
