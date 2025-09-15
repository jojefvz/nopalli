from datetime import date, datetime
from typing import Optional
from uuid import UUID

from ...common.entity import Entity
from .value_objects import Appointment, Instruction, TaskStatus


class Task(Entity):
    def __init__(
            self,
            priority: int,
            instruction: Instruction,
            loc_ref: Optional[UUID], 
            appointment: Optional[Appointment],
            container_num: Optional[str]
            ):
        super().__init__()
        self._status = TaskStatus.NOT_STARTED
        self.priority = priority
        self.instruction = instruction
        self.location_ref = loc_ref
        self._check_in_datetime = None
        self._check_out_datetime = None
        self.appointment = appointment
        self.container_num = container_num
        self.completed_by = None

    @property
    def status(self) -> TaskStatus:
        return self._status

    def start(self) -> None:
        if self._status != TaskStatus.NOT_STARTED:
            raise ValueError('Only tasks not started can be started.')
        
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
        
        self._status = TaskStatus.STOP_OFF
        self.completed_by = driver_ref
        self._check_out_datetime = datetime.now()

    def yardpull(self, driver_ref: UUID):
        if self._status not in (TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS):
            raise ValueError('Only tasks not started or in progress can be marked yardpull.')
        self._status = TaskStatus.YARD_PULL
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
        
        if self._status in (TaskStatus.STOP_OFF, TaskStatus.YARD_PULL):
            self._status = TaskStatus.NOT_STARTED
            self._check_in_datetime = None
            self._check_out_datetime = None
            self.completed_by = None
            return
        
    def set_appointment(self, appointment: Appointment) -> None:
        if self.status != TaskStatus.NOT_STARTED:
            raise ValueError('Can only set an appointment on tasks not started.')
        
        if  appointment.appointment_date < date.today():
            raise ValueError('Cannot set an appointment with a past date.')
        
        if appointment.start_time and appointment.end_time \
            and appointment.end_time < appointment.start_time:
            raise ValueError('Cannot set a start time that is later than the end time.')
        
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
