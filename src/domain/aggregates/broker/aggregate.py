from .value_objects import BrokerStatus
from ...common.entity import AggregateRoot
from ..location.value_objects import Address


class Broker(AggregateRoot):
    def __init__(self, name: str, address: Address):
        super().__init__()
        self._status = BrokerStatus.ACTIVE
        self.name = name
        self.address = address

    @property
    def status(self) -> None:
        return self._status
    
    def update_address(self, street_address, city, state, zipcode):
        self.address = Address(street_address, city, state, zipcode)

    def deactivate(self):
        self._status = BrokerStatus.INACTIVE

    def reactivate(self):
        self._status = BrokerStatus.ACTIVE