from dataclasses import dataclass
from datetime import date, time
from enum import Enum
from typing import Optional

from src.domain.common.value_object import ValueObject


class DispatchStatus(ValueObject, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Container(ValueObject):
    number: str

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

@dataclass
class Appointment(ValueObject):
        appointment_type: AppointmentType
        start_time: Optional[time] = None
        end_time: Optional[time] = None
