from dataclasses import dataclass
from typing import Self
from uuid import UUID

from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class CreateDriverRequest:
    """Request data for creating a new driver."""

    name: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not self.name.strip():
            raise ValidationError("Driver name is required")
        if len(self.name) > 100:
            raise ValidationError("Driver name cannot exceed 100 characters")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "name": self.name.strip()
        }


@dataclass(frozen=True)
class DeactivateDriverRequest:
    """Deactivate a driver."""

    id: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Driver id is not of uuid4 format.')

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id)
        }
    

@dataclass(frozen=True)
class ActivateDriverRequest:
    """Deactivate a driver."""

    id: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Driver id is not of uuid4 format.')

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id)
        }
    

@dataclass(frozen=True)
class EditDriverRequest:
    """Request data for creating a new driver."""
    id: str
    name: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Driver id is not of uuid4 format.')
        if not self.name.strip():
            raise ValidationError("Driver name is required")
        if len(self.name) > 100:
            raise ValidationError("Driver name cannot exceed 100 characters")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id),
            "name": self.name.strip(),
        }
    

@dataclass(frozen=True)
class DriverResponse:
    """Response data for basic driver operations."""

    id: str
    name: str
    status: DriverStatus

    @classmethod
    def from_entity(cls, driver: Driver) -> Self:
        """Create response from a Driver entity."""
        return cls(
            id=str(driver.id),
            name=driver.name,
            status=driver.status.value,
        )
