from datetime import date
from typing import Optional

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.broker.value_objects import BrokerStatus
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.utilities import _STARTABLE, _ALLOWED_FOLLOWS, _ALLOWED_REPEAT, _ENDABLE
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, Container, DispatchStatus, Instruction
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.aggregates.location.aggregate import Location
from src.domain.aggregates.location.value_objects import LocationStatus
from src.domain.exceptions import BusinessRuleViolation


class Dispatcher:
    @staticmethod
    def create_task(
        priority: int,
        location: Location,
        instruction: Instruction,
        container: Optional[Container],
        date: date,
        appointment: Optional[Appointment],
        ) -> Task:
        if location.status == LocationStatus.INACTIVE:
            raise BusinessRuleViolation('Cannot set a deactivated location on a new task.')

        return Task(
            priority,
            location,
            instruction,
            container,
            date,
            appointment
        )
    
    @staticmethod
    def create_dispatch(
        broker: Broker,
        current_driver: Optional[Driver],
        plan: list[Task]
        ) -> Dispatch:
        if broker.status == BrokerStatus.INACTIVE:
            raise BusinessRuleViolation('Cannot set a deactivated broker on a dispatch.')
        if current_driver and current_driver.status == DriverStatus.UNAVAILABLE:
            raise BusinessRuleViolation('Cannot set an unavailable driver on a dispatch.')
        if current_driver and current_driver.status == DriverStatus.DEACTIVATED:
            raise BusinessRuleViolation('Cannot set a deactivated driver on a dispatch.')
        if len(plan) < 2:
            raise BusinessRuleViolation("A new dispatch plan requires at least two tasks.")
        
        return Dispatch(broker, current_driver, plan)
    
    @staticmethod
    def assign_driver(dispatch: Dispatch, driver: Driver):
        if dispatch.status == DispatchStatus.IN_PROGRESS:
            raise ValueError('A dispatch in progress cannot have a driver assigned.')
        if dispatch.status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot have a driver assigned.')
        if dispatch.status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot have a driver assigned.')
        if driver.status == DriverStatus.UNAVAILABLE:
            raise ValueError('Unavailable drivers cannot be assigned.')
        if driver.status == DriverStatus.DEACTIVATED:
            raise ValueError('Deactivated drivers cannot be assigned.')

        dispatch.driver_ref = driver.id

    @staticmethod
    def remove_driver(dispatch: Dispatch):
        if dispatch.driver_ref is None:
            raise ValueError('Dispatch does not have a driver to remove.')
        if dispatch.status == DispatchStatus.IN_PROGRESS:
            raise ValueError('Cannot remove a driver from a dispatch that is in progress.')
        dispatch.driver_ref = None
    
    @staticmethod
    def verify_dispatch_before_starting(dispatch: Dispatch, driver: Driver) -> None:
        if not self.driver:
            raise ValueError('A driver has not been assigned to dispatch.')
        if not self._appointment_exists():
            raise ValueError('An appointment has not been set on at least one task.')
        if not self._containers_assigned():
            raise ValueError('A multi-container dispatch requires containers to be assigned to tasks.')
        if not self._valid_plan():
            raise ValueError('Plan instructions are not valid.')
        
    def _appointment_exists(self) -> bool:
        for task in self.plan:
            if task.appointment:
                return True
        return False
    
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
    
    def _valid_plan(self) -> bool:
        # Check first task
        if self.plan[0].instruction not in _STARTABLE:
            return False
        
        # Walk through tasks
        for idx in range(0, len(self.plan) - 1):
            current = self.plan[idx].instruction
            next = self.plan[idx + 1].instruction

            allowed = _ALLOWED_FOLLOWS[current]

            if not allowed and next:
                return False
            if allowed and next not in allowed:
                return False
    
        # Check last task
        if self.plan[-1].instruction not in _ENDABLE:
            return False

        return True

    @staticmethod
    def start_dispatch(dispatch: Dispatch, driver: Driver):
        try:
            initial_dispatch_status = dispatch.status
            dispatch.start()
            driver.begin_operating()
        except ValueError as err:
            if initial_dispatch_status == DispatchStatus.DRAFT \
                and dispatch.status == DispatchStatus.IN_PROGRESS: # driver causes the error
                dispatch.revert_to_draft()
            raise err  

    @staticmethod
    def revert_dispatch_to_draft(dispatch: Dispatch, driver: Driver):
        if dispatch.status == DispatchStatus.PAUSED:
            raise ValueError('A paused dispatch cannot be reverted to draft.')
        if dispatch.status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot be reverted to draft.')
        if dispatch.status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot be reverted to draft.')
        if dispatch.driver_ref != driver.id:
            raise ValueError('Reverting dispatch with wrong driver.')
        try:
            dispatch.revert_to_draft()
            driver.release()
        except ValueError as err:
            raise err
        
    @staticmethod
    def pause_dispatch(dispatch: Dispatch, driver: Driver):
        if dispatch.status == DispatchStatus.PAUSED:
            raise ValueError('Dispatch cannot be paused without a driver assigned.')
        if dispatch.status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot be paused.')
        if dispatch.status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot be paused.')
        if dispatch.driver_ref != driver.id:
            raise ValueError('Pausing dispatch with wrong driver.')
        try:
            dispatch.pause()
            driver.release()
            Dispatcher.remove_driver(dispatch)
        except ValueError as err:
            raise err
        
    @staticmethod
    def resume_dispatch(dispatch: Dispatch, driver: Driver):
        if dispatch.status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot be resumed.')
        if dispatch.status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot be resumed.')
        if not dispatch.driver_ref:
            raise ValueError('Dispatch cannot resume without a driver assigned.')
        if dispatch.driver_ref != driver.id:
            raise ValueError('Resuming dispatch with wrong driver.')
        try:
            dispatch.resume()
            driver.begin_operating()
        except ValueError as err:
            raise err

    @staticmethod
    def complete_dispatch(dispatch: Dispatch, driver: Driver):
        if dispatch.status == DispatchStatus.COMPLETED:
            raise ValueError('A completed dispatch cannot be completed.')
        if dispatch.status == DispatchStatus.CANCELLED:
            raise ValueError('A cancelled dispatch cannot be completed.')
        if dispatch.driver_ref != driver.id:
            raise ValueError('Completing dispatch with wrong driver.')
        try:
            dispatch.complete()
            driver.release()
            Dispatcher.remove_driver(dispatch)
        except ValueError as err:
            raise err
        
    @staticmethod
    def cancel_dispatch(dispatch: Dispatch, driver: Optional[Driver] = None):
        if dispatch.status == DispatchStatus.IN_PROGRESS and not driver:
            raise ValueError('Driver must be specified when cancelling a dispatch in progress.')
        if dispatch.status == DispatchStatus.IN_PROGRESS and \
            dispatch.driver_ref != driver.id:
            raise ValueError('Cancelling dispatch with wrong driver.')
        if dispatch.status == DispatchStatus.PAUSED and driver:
            raise ValueError('Driver does need to be inputted when cancelling a paused dispatch.')
        try:
            dispatch.cancel()
            if driver:
                driver.release()
                Dispatcher.remove_driver(dispatch)
        except ValueError as err:
            raise err
