from typing import Optional
from uuid import UUID

from src.domain.aggregates.driver.aggregate import Driver

from ...common.entity import AggregateRoot
from .entities import Instruction, Task
from .utility import (
    can_follow_prepull, can_follow_bobtail_to, can_follow_drop_empty,
    can_follow_drop_loaded, can_follow_live_load, can_follow_live_unload,
    can_follow_pickup_empty, can_follow_pickup_loaded
)
from .value_objects import Appointment, Container, DispatchStatus, TaskStatus


MINIMUM_TASKS_REQUIRED = 2
MAXIMUM_TASKS_PERMITTED = 8
MAXIMUM_CONTAINERS_PER_DISPATCH = 4

class Dispatch(AggregateRoot):
    def __init__(
            self, 
            broker_ref, 
            driver_ref: Optional[Driver], 
            containers: Optional[list[Container]], 
            tasks: list[Task]):
        super().__init__()
        self._status = DispatchStatus.DRAFT
        self.broker_ref = broker_ref
        self.driver_ref = driver_ref
        self.containers = containers
        self.tasks = tasks
        
    @property
    def status(self):
        return self._status
    
    def start(self):
        self._verify_plan()
        self._status = DispatchStatus.IN_PROGRESS

    def complete(self):
        for task in self.tasks:
            if task.status not in (TaskStatus.COMPLETED, TaskStatus.STOP_OFF, TaskStatus.YARD_PULL):
                raise ValueError('All tasks must be completed before dispatch can be completed.')
        self._status = DispatchStatus.COMPLETED

    def revert_status(self):
        if self._status == DispatchStatus.DRAFT:
            raise ValueError('Cannot revert a draft dispatch.')
        if self.get_task(1).status == TaskStatus.IN_PROGRESS:
            raise ValueError('Canot revert dispatch to draft when first task is in progress.')
        
        self._status = DispatchStatus.DRAFT

    def start_task(self, priority: int) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can start a task.')
        
        self.get_task(priority).start()

    def complete_task(self, priority: int, driver_ref: UUID) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can complete a task.')
        
        self.get_task(priority).complete(driver_ref)
    
    def revert_task(self, priority: int) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can revert a task.')
        
        self.get_task(priority).revert_status()

    def mark_stopoff(self, priority: int, driver_ref: UUID) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can mark a task as stopoff.')
        
        self.get_task(priority).stopoff(driver_ref)

    def mark_yardpull(self, priority: int, driver_ref: UUID) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can mark a task as yardpull.')
        
        self.get_task(priority).yardpull(driver_ref)

    def add_task(self, task: Task) -> None:
        if len(self.tasks) ==  MAXIMUM_TASKS_PERMITTED:
            raise ValueError('Cannot have more than 8 tasks.')

        if task.priority > len(self.tasks):
            self.tasks.append(task)
            return
        else:
            if self.get_task(task.priority).status == TaskStatus.COMPLETED:
                raise ValueError('Cannot add a new task before a completed task.')
            
            self.tasks.insert(task.priority - 1, task)
            self._update_task_priorities()

    def _update_task_priorities(self):
        for new_priority, task in enumerate(self.tasks, start=1):
            task.priority = new_priority

    def get_task(self, priority: int):
        return self.tasks[priority - 1]

    def remove_task(self, priority: int) -> None:
        if len(self.tasks) == 2:
            raise ValueError('Cannot have less than two tasks.')
        
        if priority == len(self.tasks):
            self.tasks.pop()
        else:
            if self.get_task(priority).status == TaskStatus.COMPLETED:
                raise ValueError('Cannot remove a completed task.')
            
            self.tasks.pop(priority - 1)
            self._update_task_priorities()

    def set_appointment(self, appointment: Appointment, priority: int):
        self.get_task(priority).set_appointment(appointment)

    def remove_appointment(self, priority: int):
        number_of_appts = 0
        for task in self.tasks:
            if task.appointment:
                number_of_appts += 1
        if number_of_appts == 1:
            raise ValueError('Cannot remove the only appointment on a dispatch that\'s in progress.')
        
        self.get_task(priority).appointment = None

    def _verify_plan(self) -> None:
        if self.driver_ref is None:
            raise ValueError('A driver has not been assigned to dispatch.')
        if not self._appointment_exists():
            raise ValueError('An appointment has not been set on at least one task.')
        if self._illogical_instruction_at_first_position():
            raise ValueError('Only prepull, pickup empty, or pickup loaded can be the first task.')
        if self._consecutive_tasks_with_same_instruction():
            raise ValueError('Only live load or live unload tasks can be repeated in sequence.')
        if self._has_illogical_adjacent_instructions():
            raise ValueError('Two adjacent tasks have illogical instructions.')
        
    def _appointment_exists(self) -> bool:
        for task in self.tasks:
            if task.appointment:
                return True
        return False
    
    def _illogical_instruction_at_first_position(self) -> bool:
        if self.tasks[0].instruction not in \
            (Instruction.PREPULL,
             Instruction.PICKUP_EMPTY,
             Instruction.PICKUP_LOADED,
             Instruction.BOBTAIL_TO):
            return True
        return False

    def _consecutive_tasks_with_same_instruction(self) -> bool:
        for idx in range(0, len(self.tasks) - 1):
            if self.tasks[idx].instruction == self.tasks[idx + 1].instruction \
                and self.tasks[idx] not in (Instruction.LIVE_LOAD, Instruction.LIVE_UNLOAD):
                return True
        return False
    
    def _has_illogical_adjacent_instructions(self) -> bool:
        for idx in range(0, len(self.tasks) - 1):
            if self.tasks[idx].instruction == Instruction.PREPULL \
                and self.tasks[idx + 1].instruction not in can_follow_prepull:
                return True
            if self.tasks[idx].instruction == Instruction.BOBTAIL_TO \
                and self.tasks[idx + 1].instruction not in can_follow_bobtail_to:
                return True
            if self.tasks[idx].instruction == Instruction.PICKUP_EMPTY \
                and self.tasks[idx + 1].instruction not in can_follow_pickup_empty:
                return True
            if self.tasks[idx].instruction == Instruction.PICKUP_LOADED \
                and self.tasks[idx + 1].instruction not in can_follow_pickup_loaded:
                return True
            if self.tasks[idx].instruction == Instruction.DROP_EMPTY \
                and self.tasks[idx + 1].instruction not in can_follow_drop_empty:
                return True
            if self.tasks[idx].instruction == Instruction.DROP_LOADED \
                and self.tasks[idx + 1].instruction not in can_follow_drop_loaded:
                return True
            if self.tasks[idx].instruction == Instruction.LIVE_UNLOAD \
                and self.tasks[idx + 1].instruction not in can_follow_live_unload:
                return True
            if self.tasks[idx].instruction == Instruction.LIVE_LOAD \
                and self.tasks[idx + 1].instruction not in can_follow_live_load:
                return True
            if self.tasks[idx].instruction == Instruction.STREET_TURN \
                and self.tasks[idx + 1]:
                return True
            if self.tasks[idx].instruction == Instruction.INGATE \
                and self.tasks[idx + 1]:
                return True
            if self.tasks[idx].instruction == Instruction.TERMINATE \
                and self.tasks[idx + 1]:
                return True
        return False
    
    # def _illogical_instructions_before_completing_dispatch(self) -> bool:
    #     for idx in range(0, len(self.tasks)):
    #         if self.tasks[idx].instruction == Instruction.PREPULL \
    #             and idx != 0:
    #             return True
    #         if self.tasks[idx].instruction == Instruction.BOBTAIL_TO \
    #             and idx == len(self.tasks) - 1:
    #             return True
    #         if self.tasks[idx].instruction == Instruction.PICKUP_EMPTY \
    #             and idx == len(self.tasks) - 1:
    #             return True
    #         if self.tasks[idx].instruction == Instruction.PICKUP_LOADED \
    #             and idx == len(self.tasks) - 1:
    #             return True
    #         if self.tasks[idx].instruction == Instruction.DROP_EMPTY \
    #             and (idx == 0 or idx == len(self.tasks) - 1):
    #             return True
    #         if self.tasks[idx].instruction == Instruction.DROP_LOADED \
    #             and (idx == 0 or idx == len(self.tasks) - 1):
    #             return True
    #         if self.tasks[idx].instruction == Instruction.LIVE_UNLOAD \
    #             and (idx == 0 or idx == len(self.tasks) - 1):
    #             return True
    #         if self.tasks[idx].instruction == Instruction.LIVE_LOAD \
    #             and (idx == 0 or idx == len(self.tasks) - 1):
    #             return True
    #         if self.tasks[idx].instruction == Instruction.TERMINATE \
    #             and idx == 0:
    #             return True
    #         if self.tasks[idx].instruction == Instruction.INGATE \
    #             and idx == 0:
    #             return True
    #         if self.tasks[idx].instruction == Instruction.STREET_TURN \
    #             and idx == 0:
    #             return True
    #     return False