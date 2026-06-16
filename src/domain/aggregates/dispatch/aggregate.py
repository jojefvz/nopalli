from typing import Optional

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.value_objects import Instruction
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus

from src.domain.common.entity import AggregateRoot
from src.domain.exceptions import BusinessRuleViolation
from .entities import Task
from .utilities import _ALLOWED_FOLLOWS, _ENDABLE, _STARTABLE
from .value_objects import Appointment, DispatchStatus, TaskStatus


MINIMUM_TASKS_REQUIRED = 2
MAXIMUM_TASKS_PERMITTED = 10

class Dispatch(AggregateRoot):
    def __init__(
            self, 
            broker: Broker,
            current_driver: Optional[Driver],
            plan: list[Task],
            ):
        super().__init__()
        self.reference = None
        self._status = DispatchStatus.DRAFT
        self.broker = broker
        self.current_driver = current_driver
        self.plan = plan
        self._current_task = Optional[Task] = None

    @property
    def status(self):
        return self._status

    @property
    def assigned_drivers(self):
        drivers = [task.completed_by for task in self.plan if task.completed_by]
        if self.current_driver:
            drivers.append(self.current_driver) 
        return list(dict.fromkeys(drivers))
    
    @property
    def current_container(self):
        curr_container = [task.container for task in self.plan if task.status == 'in_progress']
        return curr_container[0] if curr_container else None
    @property
    def containers(self):
        containers = [task.container for task in self.plan if task.container]
        return list(dict.fromkeys(containers))
    
    @property
    def appointments(self):
        return [(task.date, task.appointment) for task in self.plan if task.appointment]
    
    def _containers_assigned(self) -> bool:
        for task in self.plan:
            if task.instruction in (
                Instruction.FETCH_CHASSIS,
                Instruction.BOBTAIL_TO,
                Instruction.TERMINATE_CHASSIS,
            ):
                continue
            elif not task.container:
                return False
        return True
    
    def _get_invalid_transition(self) -> tuple | None:
        if self.plan[0].instruction not in _STARTABLE:
            return (None, self.plan[0].instruction)
        
        for idx in range(len(self.plan) - 1):
            current = self.plan[idx].instruction
            next_instruction = self.plan[idx + 1].instruction
            if next_instruction not in _ALLOWED_FOLLOWS[current]:
                return (current, next_instruction)
        
        if self.plan[-1].instruction not in _ENDABLE:
            return (self.plan[-1].instruction, None)
        
        return None

    def _get_start_errors(self) -> list:
        errors = []
        if not self.current_driver:
            errors.append('A driver has not been assigned to dispatch.')
        if self.current_driver.status != DriverStatus.AVAILABLE:
            errors.append('Driver is not available to be dispatched.')
        if not self.appointments:
            errors.append('An appointment has not been set on at least one task.')
        if not self._containers_assigned:
            errors.append('Certain stops are missing their container assignment.')

        invalid_transition = self._get_invalid_transition()
        if invalid_transition:
            current, next_instruction = invalid_transition
            if current is None:
                errors.append(f'{next_instruction.value} is not a valid starting instruction.')
            elif next_instruction is None:
                errors.append(f'{current.value} is not a valid ending instruction.')
            else:
                errors.append(f'{next_instruction.value} cannot follow {current.value}.')

        return errors

    def start(self) -> None:
        if self._status != DispatchStatus.DRAFT:
            raise BusinessRuleViolation('Only a draft dispatch can be started.')
        
        errors = self._get_start_errors()
        if errors:
            return errors
        
        self._status = DispatchStatus.IN_PROGRESS
        self._current_task = self.plan[0]
        return []

    def pause(self) -> None:
        if self._status != DispatchStatus.IN_PROGRESS:
                raise ValueError('Only a dispatch in progress can be paused.')
        for task in self.plan:
            if task.status == TaskStatus.IN_PROGRESS:
                raise ValueError('Cannot pause a dispatch when a task is in progress.')
            
        self._status = DispatchStatus.PAUSED

    def resume(self) -> None:
        if self._status != DispatchStatus.PAUSED:
            raise ValueError('Only a paused dispatch can resume.')
        
        self._status = DispatchStatus.IN_PROGRESS

    def complete(self) -> None:
        if self._status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can be completed.')
        for task in self.plan:
            if task.status == TaskStatus.STOP_OFF:
                continue
            if task.status != TaskStatus.COMPLETED:
                raise ValueError('All tasks must be completed before dispatch can be completed.')
            
        self._status = DispatchStatus.COMPLETED

    def cancel(self) -> None:
        if self._status == DispatchStatus.DRAFT:
            raise ValueError('Draft dispatch cannot be cancelled.')
        if self._status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot be cancelled.')
        if self._status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot be cancelled.')
            
        self._status = DispatchStatus.CANCELLED

    def revert_to_draft(self) -> None:
        if self._status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can revert back to draft.')
        if self.get_task(1).status != TaskStatus.NOT_STARTED:
            raise ValueError('Only a dispatch without any tasks started can revert to draft.')
        
        self._status = DispatchStatus.DRAFT

    def advance_to_next_task(self) -> None:
        if self._status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can proceed to next task.')
        for i in range(len(self.plan)):
            if self.plan[i] == self.plan[-1]:
                raise ValueError('Cannot advance from final task.')
            if self.plan[i].status != TaskStatus.COMPLETED or self.plan[i].status != TaskStatus.STOP_OFF:
                raise ValueError('Can only advance from a task that is completed or a stop off task.')
            
            self._current_task = self.plan[i + 1]

    def start_task(self, priority: int) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can start a task.')
        if priority > 1 and self.get_task(priority - 1).status != TaskStatus.COMPLETED:
            raise ValueError('Cannot start tasks out of order.')
        
        self.get_task(priority).start()

    def complete_task(self, priority: int) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can complete a task.')
        
        self.get_task(priority).complete(self.current_driver)
    
    def revert_task(self, priority: int) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can revert a task.')
        
        self.get_task(priority).revert_status()

    def mark_stopoff(self, priority: int) -> None:
        if self.status != DispatchStatus.IN_PROGRESS:
            raise ValueError('Only a dispatch in progress can mark a task as stopoff.')
        
        self.get_task(priority).stopoff(self.driver)

    def get_task(self, priority: int):
        return self.plan[priority - 1]
    
    def add_task(self, task: Task) -> None:
        if len(self.plan) ==  MAXIMUM_TASKS_PERMITTED:
            raise ValueError('Cannot have more than 10 tasks in dispatch plan.')
        if self._status == DispatchStatus.COMPLETED:
            raise ValueError('Completed dispatches cannot add tasks.')
        if self._status == DispatchStatus.CANCELLED:
            raise ValueError('Cancelled dispatches cannot add tasks.')
        if self._status in (DispatchStatus.IN_PROGRESS, DispatchStatus.PAUSED):
            if self.get_task(task.priority).status == TaskStatus.COMPLETED:
                raise ValueError('Cannot add a new task before a completed task.')
            if not self._valid_additional_task(task):
                raise ValueError('Invalid task cannot be added.')
            
        if len(self.containers) == 1:
            task.container = self.containers[0]
        self.plan.insert(task.priority - 1, task)
        self._update_task_priorities()
        return

    def _update_task_priorities(self):
        for new_priority, task in enumerate(self.plan, start=1):
            task.priority = new_priority

    def _valid_additional_task(self, task: Task):
        if task.priority == 1 and task.instruction in _STARTABLE:
            return True
        elif task.priority == len(self.plan) + 1 and task.instruction in _ENDABLE:
            return True
        elif 1 < task.priority < len(self.plan) + 1:
            if self.get_task(task.priority - 1).status != TaskStatus.STOP_OFF \
            and task.instruction in _ALLOWED_FOLLOWS[self.get_task(task.priority - 1).instruction]:
                return True
            elif self.get_task(task.priority - 1).status == TaskStatus.STOP_OFF \
            and self.get_task(task.priority).instruction in _ALLOWED_FOLLOWS[task.instruction]:
                return True
        
        return False
    
    def remove_task(self, priority: int) -> None:
        if self._status != DispatchStatus.DRAFT:
            raise ValueError('Only a draft dispatch can remove a task.')
        if len(self.plan) == 2:
            raise ValueError('Dispatch plan cannot have less than two tasks.')
        
        if priority == len(self.plan):
            self.plan.pop()
        else:
            if self.get_task(priority).status == TaskStatus.COMPLETED:
                raise ValueError('Cannot remove a completed task.')
            
            self.plan.pop(priority - 1)
            self._update_task_priorities()
    
    def set_appointment(self, priority: int, appointment: Appointment):
        if self._status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot set an appointment.')
        if self._status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot set an appointment.')
        
        self.get_task(priority).set_appointment(appointment)

    def remove_appointment(self, priority: int):
        if self._status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot remove an appointment.')
        if self._status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot remove an appointment.')
        
        number_of_appts = 0
        for task in self.plan:
            if task.appointment:
                number_of_appts += 1

        if number_of_appts == 1 and self.status != DispatchStatus.DRAFT:
            raise ValueError('Cannot remove the only appointment on a dispatch that is in progress.')
        
        self.get_task(priority).appointment = None
