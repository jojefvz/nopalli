"""
This module contains domain-specific exceptions for the todo application.
These exceptions represent error conditions specific to the domain model.
"""

from uuid import UUID


class DomainError(Exception):
    """Base class for domain-specific errors."""

    pass


class LocationNotFoundError(DomainError):
    """Raised when attempting to access a task that doesn't exist."""

    def __init__(self, location_id: UUID) -> None:
        self.location_id = location_id
        super().__init__(f"Location with id {location_id} not found")


class ValidationError(DomainError):
    """Raised when domain validation rules are violated."""

    pass


class BusinessRuleViolation(DomainError):
    """Raised when a business rule is violated."""

    pass
