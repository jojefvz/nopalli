from dataclasses import dataclass
from typing import Optional, Self
from uuid import UUID

from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class CreateDriverRequest:
    """Request data for creating a new driver."""

    first_name: str
    last_name: str
    nickname: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not self.first_name.strip():
            raise ValidationError("Driver first name is required")
        if len(self.first_name) > 100:
            raise ValidationError("Driver first name cannot exceed 100 characters")
        if not self.last_name.strip():
            raise ValidationError("Driver last name is required")
        if len(self.last_name) > 100:
            raise ValidationError("Driver last name cannot exceed 100 characters")
        if self.nickname and len(self.nickname) > 100:
            raise ValidationError("Driver nickname cannot exceed 100 characters")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "first_name": self.first_name.strip(),
            "last_name": self.last_name.strip(),
            "nickname": self.nickname.strip() if self.nickname else None
        }


@dataclass(frozen=True)
class SitOutDriverRequest:
    """Sit out a driver."""

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
class MakeAvailableDriverRequest:
    """Make a driver available."""

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
    first_name: str
    last_name: str
    nickname: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Driver id is not of uuid4 format.')
        if not self.first_name.strip():
            raise ValidationError("Driver first name is required.")
        if len(self.first_name) > 100:
            raise ValidationError("Driver first name cannot exceed 100 characters.")
        if not self.last_name.strip():
            raise ValidationError("Driver last name is required.")
        if len(self.last_name) > 100:
            raise ValidationError("Driver last name cannot exceed 100 characters.")
        if self.nickname and len(self.last_name) > 100:
            raise ValidationError("Driver nickname cannot exceed 100 characters.")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id),
            "first_name": self.first_name.strip(),
            "last_name": self.last_name.strip(),
            "nickname": self.nickname.strip() if self.nickname else None,
        }
    

@dataclass(frozen=True)
class DriverResponse:
    """Response data for basic driver operations."""

    id: str
    status: DriverStatus
    first_name: str
    last_name: str
    nickname: Optional[str]
    
    @classmethod
    def from_entity(cls, driver: Driver) -> Self:
        """Create response from a Driver entity."""
        return cls(
            id=str(driver.id),
            status=driver.status.value,
            first_name=driver.first_name,
            last_name=driver.last_name,
            nickname=driver.nickname
        )
