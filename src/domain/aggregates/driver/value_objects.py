from enum import Enum


class DriverStatus(Enum):
    AVAILABLE = 'available'
    OPERATING = 'operating'
    UNAVAILABLE = 'unavailable'
    DEACTIVATED = 'deactivated'
