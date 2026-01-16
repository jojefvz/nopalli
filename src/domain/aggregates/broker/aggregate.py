from .value_objects import BrokerStatus
from src.domain.aggregates.location.value_objects import Address
from src.domain.common.entity import AggregateRoot
from src.domain.exceptions import BusinessRuleViolation


class Broker(AggregateRoot):
    def __init__(self, name: str, address: Address):
        super().__init__()
        self._status = BrokerStatus.ACTIVE
        self.name = name
        self.address = address

    @property
    def status(self) -> BrokerStatus:
        return self._status

    def deactivate(self) -> None:
        if self.status == BrokerStatus.INACTIVE:
            raise BusinessRuleViolation('Only active brokers can be deactivated.')
        
        self._status = BrokerStatus.INACTIVE

    def reactivate(self) -> None:
        if self.status == BrokerStatus.ACTIVE:
            raise BusinessRuleViolation('Only deactivated brokers can be reactivated.')
        
        self._status = BrokerStatus.ACTIVE