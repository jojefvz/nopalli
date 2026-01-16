from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.common.entity import AggregateRoot
from src.domain.exceptions import BusinessRuleViolation


class Driver(AggregateRoot):
    def __init__(self, name):
        super().__init__()
        self._status = DriverStatus.AVAILABLE
        self.name = name

    @property
    def status(self) -> DriverStatus:
        return self._status

    def begin_operating(self) -> None:
        if self.status != DriverStatus.AVAILABLE:
            raise BusinessRuleViolation('Only available drivers can begin operating.')
        
        self._status = DriverStatus.OPERATING

    def release(self) -> None:
        if self.status != DriverStatus.OPERATING:
            raise BusinessRuleViolation('Only operating drivers can be released.')
        
        self._status = DriverStatus.AVAILABLE

    def sit_out(self) -> None:
        if self.status != DriverStatus.AVAILABLE:
            raise BusinessRuleViolation('Only available drivers can sit out.')
        
        self._status = DriverStatus.UNAVAILABLE

    def make_available(self) -> None:
        if self.status != DriverStatus.UNAVAILABLE:
            raise BusinessRuleViolation('Only unavailable drivers can be made available.')
        
        self._status = DriverStatus.AVAILABLE

    def deactivate(self) -> None:
        if self.status not in (DriverStatus.UNAVAILABLE, DriverStatus.AVAILABLE):
            raise BusinessRuleViolation('Only available and unavailable drivers can be deactivated.')
    
        self._status = DriverStatus.DEACTIVATED

    def reactivate(self) -> None:
        if self.status != DriverStatus.DEACTIVATED:
            raise BusinessRuleViolation('Only deactivated drivers can be reactivated.')
        
        self._status = DriverStatus.AVAILABLE
