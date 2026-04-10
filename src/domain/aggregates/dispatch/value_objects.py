from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import Optional


class DispatchStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ContainerSize(Enum):
    TWENTY_STANDARD = 'twenty_standard'
    TWENTY_HIGHCUBE = 'twenty_highcube'
    FORTY_STANDARD = 'forty_standard'
    FORTY_HIGHCUBE = 'forty_highcube'
    FORTY_FIVE = 'forty_five'
    FIFTY_THREE = 'fifty_three'

@dataclass(init=False, eq=False)
class Container:
    number: str
    size: ContainerSize
    
    def __new__(cls, number=None, size=None):
        """Return None if number is not set (no container)."""
        if number is None:
            return None
        instance = object.__new__(cls)
        return instance
    
    def __init__(self, number=None, size=None):
        """Initialize only if instance was created."""
        if self is not None:
            self.number = number
            self.size = size
    
    def __composite_values__(self):
        """For SQLAlchemy composite."""
        if self is None:
            return (None, None)
        return (self.number, self.size)

    def __eq__(self, other):
        if not isinstance(other, Container):
            return NotImplemented
        return self.number == other.number and self.size == other.size

    def __hash__(self):
        return hash((self.number, self.size))

class TaskStatus(Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    STOP_OFF = 'stop_off'
    VOIDED = 'voided'

class Instruction(Enum):
    FETCH_CHASSIS = 'fetch_chassis'
    PREPULL = 'prepull'
    BOBTAIL_TO = 'bobtail_to'
    PICKUP_EMPTY = 'pickup_empty'
    DROP_EMPTY = 'drop_empty'
    LIVE_LOAD = 'live_load'
    PICKUP_LOADED = 'pickup_loaded'
    DROP_LOADED = 'drop_loaded'
    LIVE_UNLOAD = 'live_unload'
    TERMINATE_EMPTY = 'terminate_empty'
    TERMINATE_CHASSIS = 'terminate_chassis'
    INGATE = 'ingate'
    YARD_PULL = 'yard_pull'
    STREET_TURN = 'street_turn'

class AppointmentType(Enum):
    OPEN = 'open'
    EXACT_TIME = 'exact_time'
    TIME_WINDOW = 'time_window'
    READY_AFTER = 'ready_after'
    FINISH_BY = 'finish_by'

@dataclass(init=False)
class Appointment:
    appointment_type: AppointmentType
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    def __new__(cls, appointment_type=None, start_time=None, end_time=None):
        """Return None if type is not set."""
        if appointment_type is None:
            return None
        # Create instance normally if type exists
        instance = object.__new__(cls)
        return instance
    
    def __init__(self, appointment_type=None, start_time=None, end_time=None):
        """Initialize only if instance was created (type is not None)."""
        if self is not None:
            self.appointment_type = appointment_type
            self.start_time = start_time
            self.end_time = end_time
    
    def __composite_values__(self):
        """For SQLAlchemy composite."""
        if self is None:
            return (None, None, None)
        return (self.appointment_type, self.start_time, self.end_time)
