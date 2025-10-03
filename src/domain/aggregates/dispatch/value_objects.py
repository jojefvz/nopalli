from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Optional

from ...common.value_object import ValueObject


class DispatchStatus(ValueObject, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

@dataclass
class Container(ValueObject):
    number: str

class TaskStatus(Enum):
    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    STOP_OFF = 'STOP_OFF'
    VOIDED = 'VOIDED'

class Instruction(Enum):
    FETCH_CHASSIS = 'FETCH_CHASSIS'
    PREPULL = 'PREPULL'
    BOBTAIL_TO = 'BOBTAIL_TO'
    PICKUP_EMPTY = 'PICKUP_EMPTY'
    DROP_EMPTY = 'DROP_EMPTY'
    LIVE_LOAD = 'LIVE_LOAD'
    PICKUP_LOADED = 'PICKUP_LOADED'
    DROP_LOADED = 'DROP_LOADED'
    LIVE_UNLOAD = 'LIVE_UNLOAD'
    TERMINATE_EMPTY = 'TERMINATE_EMPTY'
    TERMINATE_CHASSIS = 'TERMINATE_CHASSIS'
    INGATE = 'INGATE'
    YARD_PULL = 'YARD_PULL'
    STREET_TURN = 'STREET_TURN'

class AppointmentType(Enum):
    OPEN = 'OPEN'
    EXACT_TIME = 'EXACT_TIME'
    TIME_WINDOW = 'TIME_WINDOW'
    READY_AFTER = 'READY_AFTER'
    DEADLINE = 'DEADLINE'

@dataclass
class Appointment(ValueObject):
        appointment_type: AppointmentType
        appointment_date: date
        start_time: Optional[time] = None
        end_time: Optional[time] = None
