from .value_objects import Address, LocationStatus
from src.domain.common.entity import AggregateRoot
from src.domain.exceptions import BusinessRuleViolation


class Location(AggregateRoot):
    def __init__(self, name: str, address: Address):
        super().__init__()
        self._status = LocationStatus.ACTIVE
        self.name = name
        self.address = address

    @property
    def status(self) -> LocationStatus:
        return self._status
    
    def deactivate(self) -> None:
        if self._status == LocationStatus.INACTIVE:
            raise BusinessRuleViolation('Only active locations can be deactivated.')
        
        self._status = LocationStatus.INACTIVE

    def reactivate(self) -> None:
        if self._status == LocationStatus.ACTIVE:
            raise BusinessRuleViolation('Only deactivated locations can be reactivated.')
        
        self._status = LocationStatus.ACTIVE
