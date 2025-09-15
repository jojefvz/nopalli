from dataclasses import dataclass
from enum import Enum

from src.domain.common.value_object import ValueObject

@dataclass
class Address(ValueObject):
    street_address: str
    city: str
    state: str
    zipcode: int

class LocationStatus(Enum):
    INACTIVE = 'INACTIVE'
    ACTIVE = 'ACTIVE'
