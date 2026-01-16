"""
This module contains domain-specific exceptions for the todo application.
These exceptions represent error conditions specific to the domain model.
"""

from uuid import UUID


class DomainError(Exception):
    """Base class for domain-specific errors."""

    pass


class BrokerNotFoundError(DomainError):
    """Raised when attempting to access a broker that doesn't exist."""

    def __init__(self, broker_id: UUID) -> None:
        self.broker_id = broker_id
        super().__init__(f"Broker with id {broker_id} not found")


class LocationNotFoundError(DomainError):
    """Raised when attempting to access a location that doesn't exist."""

    def __init__(self, location_id: UUID) -> None:
        self.location_id = location_id
        super().__init__(f"Location with id {location_id} not found")


class DriverNotFoundError(DomainError):
    """Raised when attempting to access a driver that doesn't exist."""

    def __init__(self, driver_id: UUID) -> None:
        self.driver_id = driver_id
        super().__init__(f"Driver with id {driver_id} not found")


class DispatchNotFoundError(DomainError):
    """Raised when attempting to access a dispatch that doesn't exist."""

    def __init__(self, dispatch_id: UUID) -> None:
        self.dispatch_id = dispatch_id
        super().__init__(f"Driver with id {dispatch_id} not found")

class TaskNotFoundError(DomainError):
    """Raised when attempting to access a task that doesn't exist."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Driver with id {task_id} not found")


class ValidationError(DomainError):
    """Raised when domain validation rules are violated."""

    pass


class BusinessRuleViolation(DomainError):
    """Raised when a business rule is violated."""

    pass
