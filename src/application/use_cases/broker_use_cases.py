from dataclasses import dataclass

from src.application.common.result import Error, Result
from src.application.dtos.broker_dtos import (
    CreateBrokerRequest, 
    BrokerResponse,
    DeactivateBrokerRequest,
    ActivateBrokerRequest,
    EditBrokerRequest,
    )
from src.application.repositories.broker_repository import BrokerRepository
from src.domain.aggregates.broker.aggregate import Broker
from src.domain.exceptions import ValidationError, BusinessRuleViolation


@dataclass
class ListBrokersUseCase:
    broker_repository: BrokerRepository

    def execute(self) -> Result[list[BrokerResponse]]:
        """
        List all brokers.

        Returns:
            Result containing either:
            - Success: List of BrokerResponse objects
            - Failure: Error information
        """
        try:
            brokers = self.broker_repository.get_all()
            return Result.success([BrokerResponse.from_entity(b) for b in brokers])
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

@dataclass
class CreateBrokerUseCase:
    """Use case for creating a new broker."""

    broker_repository: BrokerRepository

    def execute(self, request: CreateBrokerRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            broker = Broker(
                name=params['name'],
                address=params['address'],
            )

            self.broker_repository.save(broker)

            return Result.success(BrokerResponse.from_entity(broker))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        
@dataclass
class DeactivateBrokerUseCase:
    """Use case for deactivating a broker."""

    broker_repository: BrokerRepository

    def execute(self, request: DeactivateBrokerRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            broker = self.broker_repository.get(params['id'])

            broker.deactivate()

            return Result.success(BrokerResponse.from_entity(broker))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))

@dataclass
class ActivateBrokerUseCase:
    """Use case for activating a broker."""

    broker_repository: BrokerRepository

    def execute(self, request: ActivateBrokerRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            broker = self.broker_repository.get(params['id'])

            broker.reactivate()

            return Result.success(BrokerResponse.from_entity(broker))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class EditBrokerUseCase:
    """Use case for editing a broker."""

    broker_repository: BrokerRepository

    def execute(self, request: EditBrokerRequest) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            id = params["id"]

            broker = self.broker_repository.get(id)

            broker.name = params["name"]
            broker.address = params["address"]

            return Result.success(BrokerResponse.from_entity(broker))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class GetBrokerUseCase:
    """Use case for creating a new broker."""

    broker_repository: BrokerRepository

    def execute(self, request) -> Result:
        """Execute the use case."""
        try:
            params = request.to_execution_params()

            broker = Broker(
                name=params['name'],
                address=params['address'],
            )

            self.broker_repository.save(broker)

            return Result.success(BrokerResponse.from_entity(broker))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
        

