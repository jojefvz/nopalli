from src.domain.common.entity import AggregateRoot
from .value_objects import Address, LocationStatus


class Location(AggregateRoot):
    def __init__(self, name: str, address: Address):
        super().__init__()
        self._status = LocationStatus.ACTIVE
        self.name = name
        self.address = address

    @property
    def status(self) -> LocationStatus:
        return self._status
    
    def update_address(self, street_address, city, state, zipcode) -> None:
        self.address = Address(street_address, city, state, zipcode)
    
    def deactivate(self):
        self._status = LocationStatus.INACTIVE

    def reactivate(self):
        self._status = LocationStatus.ACTIVE
