from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.common.entity import AggregateRoot


class Driver(AggregateRoot):
    def __init__(self, name):
        super().__init__()
        self.status = DriverStatus.AVAILABLE
        self.name = name

    def begin_operating(self) -> None:
        if self.status != DriverStatus.AVAILABLE:
            raise ValueError('Only available drivers can begin operating.')
        
        self.status = DriverStatus.OPERATING

    def release(self) -> None:
        if self.status != DriverStatus.OPERATING:
            raise ValueError('Only operating drivers can be released.')
        
        self.status = DriverStatus.AVAILABLE

    def sit_out(self) -> None:
        if self.status != DriverStatus.AVAILABLE:
            raise ValueError('Only available drivers can sit out.')
        
        self.status = DriverStatus.UNAVAILABLE

    def make_available(self) -> None:
        if self.status != DriverStatus.UNAVAILABLE:
            raise ValueError('Only unavailable drivers can be made available.')
        
        self.status = DriverStatus.AVAILABLE

    def deactivate(self) -> None:
        if self.status not in (DriverStatus.UNAVAILABLE, DriverStatus.AVAILABLE):
            raise ValueError('Only available and unavailable drivers can be deactivated.')
    
        self.status = DriverStatus.DEACTIVATED

    def reactivate(self) -> None:
        if self.status != DriverStatus.DEACTIVATED:
            raise ValueError('Only deactivated drivers can be reactivated.')
        
        self.status = DriverStatus.AVAILABLE
