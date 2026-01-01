from datetime import date, datetime
from typing import Optional
from uuid import UUID

from click import Option

from src.domain.common.entity import Entity
from .value_objects import Appointment, Container, Instruction, TaskStatus


class Task(Entity):
    def __init__(
            self,
            priority: int,
            instruction: Instruction,
            date: date,
            container: Optional[Container] = None,
            location_ref: Optional[UUID] = None, 
            appointment: Optional[Appointment] = None
            ):
        super().__init__()
        self._status = TaskStatus.NOT_STARTED
        self.priority = priority
        self.instruction = instruction
        self.location_ref = location_ref
        self.date = date
        self._check_in_datetime = None
        self._check_out_datetime = None
        self.appointment = appointment
        self.container = container
        self.completed_by = None

    @property
    def status(self) -> TaskStatus:
        return self._status

    def start(self) -> None:
        if self._status != TaskStatus.NOT_STARTED:
            raise ValueError('Only tasks not started can be started.')
        if isinstance(self.location_ref, str):
            raise ValueError('Cannot start a task without a location set.')
        
        self._status = TaskStatus.IN_PROGRESS
        self._check_in_datetime = datetime.now()

    def complete(self, driver_ref: UUID) -> None:
        if self._status != TaskStatus.IN_PROGRESS:
            raise ValueError('Only tasks in progress can be completed.')
        
        self._status = TaskStatus.COMPLETED
        self.completed_by = driver_ref
        self._check_out_datetime = datetime.now()

    def stopoff(self, driver_ref: UUID):
        if self._status not in (TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS):
            raise ValueError('Only tasks not started or in progress can be marked stopoff.')
        
        if self.instruction in (
            Instruction.BOBTAIL_TO,
            Instruction.FETCH_CHASSIS,
            Instruction.TERMINATE_CHASSIS,
            Instruction.STREET_TURN,
        ):
            raise ValueError('Task instruction is incompatible with being marked stop off.')
        
        self._status = TaskStatus.STOP_OFF
        self.completed_by = driver_ref
        self._check_out_datetime = datetime.now()

    def revert_status(self) -> None:
        if self._status == TaskStatus.NOT_STARTED:
            raise ValueError('A task not started cannot revert status.')
        
        if self._status == TaskStatus.IN_PROGRESS:
            self._status = TaskStatus.NOT_STARTED
            self._check_in_datetime = None
            return
        
        if self._status == TaskStatus.COMPLETED:
            self._status = TaskStatus.IN_PROGRESS
            self._check_out_datetime = None
            self.completed_by = None
            return
        
        if self._status == TaskStatus.STOP_OFF:
            self._status = TaskStatus.NOT_STARTED
            self._check_in_datetime = None
            self._check_out_datetime = None
            self.completed_by = None
            return
        
    def set_appointment(self, appointment: Appointment) -> None:
        if self.status != TaskStatus.NOT_STARTED:
            raise ValueError('Can only set an appointment on tasks not started.')
        
        self.appointment = appointment

    def remove_appointment(self):
        if self.status != TaskStatus.NOT_STARTED:
            raise ValueError('Can only remove appointment when task not started.')
        
        self.appointment = None

    @property
    def time_spent_completing_task(self):
        if self._status != TaskStatus.COMPLETED:
            raise AttributeError('Task has not been completed.')
        
        return self._check_out_datetime - self._check_in_datetime
