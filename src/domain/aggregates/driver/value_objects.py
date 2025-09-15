from enum import Enum


class DriverStatus(Enum):
    AVAILABLE = 1
    OPERATING = 2
    UNAVAILABLE = 3
    DEACTIVATED = 4
