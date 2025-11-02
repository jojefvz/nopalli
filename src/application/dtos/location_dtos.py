from dataclasses import dataclass
from typing import Self

from ...domain.aggregates.location.aggregate import Location
from ...domain.aggregates.location.value_objects import Address, LocationStatus
from ...domain.exceptions import ValidationError


@dataclass(frozen=True)
class CreateLocationRequest:
    """Request data for creating a new location."""

    name: str
    street_address: str
    city: str
    state: str
    zipcode: str

    def __post_init__(self) -> None:
        """Validate request data"""
        if not self.name.strip():
            raise ValidationError("Location name is required")
        if len(self.name) > 100:
            raise ValidationError("Location name cannot exceed 100 characters")
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
class LocationResponse:
    """Response data for basic location operations."""

    id: str
    name: str
    status: LocationStatus
    street_address: str
    city: str
    state: str
    zipcode: str

    @classmethod
    def from_entity(cls, location: Location) -> Self:
        """Create response from a Location entity."""
        return cls(
            id=str(location.id),
            name=location.name,
            status=location.status.value,
            street_address=location.address.street_address,
            city=location.address.city,
            state=location.address.state,
            zipcode=str(location.address.zipcode),
        )
