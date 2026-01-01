from dataclasses import dataclass
from typing import Self
from uuid import UUID

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.broker.value_objects import BrokerStatus
from src.domain.aggregates.location.value_objects import Address
from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class CreateBrokerRequest:
    """Request data for creating a new broker."""

    name: str
    street_address: str
    city: str
    state: str
    zipcode: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not self.name.strip():
            raise ValidationError("Broker name is required")
        if len(self.name) > 100:
            raise ValidationError("Broker name cannot exceed 100 characters")
        if not self.street_address.strip():
            raise ValidationError("Street address is required")
        if len(self.street_address) > 100:
            raise ValidationError("Street address cannot exceed 100 characters")
        if not self.city.strip():
            raise ValidationError("City name is required")
        if len(self.city) > 100:
            raise ValidationError("City name cannot exceed 100 characters")
        if not self.state.strip():
            raise ValidationError("State abbreviation is required")
        if len(self.state) != 2:
            raise ValidationError("State abbreviation must be 2 characters")
        if not self.zipcode.strip():
            raise ValidationError("Zipcode is required")
        if len(self.zipcode) != 5:
            raise ValidationError("Zipcode must be exactly 5 numbers.")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "name": self.name.strip(),
            "address": Address(
                self.street_address.strip(),
                self.city.strip(),
                self.state.strip(),
                int(self.zipcode.strip())
            )
        }


@dataclass(frozen=True)
class DeactivateBrokerRequest:
    """Deactivate a broker."""

    id: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Broker id is not of uuid4 format.')

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id)
        }
    

@dataclass(frozen=True)
class ActivateBrokerRequest:
    """Deactivate a broker."""

    id: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Broker id is not of uuid4 format.')

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id)
        }
    

@dataclass(frozen=True)
class EditBrokerRequest:
    """Request data for creating a new broker."""
    id: str
    name: str
    street_address: str
    city: str
    state: str
    zipcode: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not UUID(self.id, version=4):
            raise ValidationError('Broker id is not of uuid4 format.')
        if not self.name.strip():
            raise ValidationError("Broker name is required")
        if len(self.name) > 100:
            raise ValidationError("Broker name cannot exceed 100 characters")
        if not self.street_address.strip():
            raise ValidationError("Street address is required")
        if len(self.street_address) > 100:
            raise ValidationError("Street address cannot exceed 100 characters")
        if not self.city.strip():
            raise ValidationError("City name is required")
        if len(self.city) > 100:
            raise ValidationError("City name cannot exceed 100 characters")
        if not self.state.strip():
            raise ValidationError("State abbreviation is required")
        if len(self.state) != 2:
            raise ValidationError("State abbreviation must be 2 characters")
        if not self.zipcode.strip():
            raise ValidationError("Zipcode is required")
        if len(self.zipcode) != 5:
            raise ValidationError("Zipcode must be exactly 5 numbers.")

    def to_execution_params(self) -> dict:
        """Convert request data to use case parameters."""
        return {
            "id": UUID(self.id),
            "name": self.name.strip(),
            "address": Address(
                self.street_address.strip(),
                self.city.strip(),
                self.state.strip(),
                int(self.zipcode.strip())
            )
        }
    

@dataclass(frozen=True)
class BrokerResponse:
    """Response data for basic broker operations."""

    id: str
    name: str
    status: BrokerStatus
    street_address: str
    city: str
    state: str
    zipcode: str

    @classmethod
    def from_entity(cls, broker: Broker) -> Self:
        """Create response from a Broker entity."""
        return cls(
            id=str(broker.id),
            name=broker.name,
            status=broker.status.value,
            street_address=broker.address.street_address,
            city=broker.address.city,
            state=broker.address.state,
            zipcode=str(broker.address.zipcode),
        )
