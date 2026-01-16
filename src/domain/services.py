from datetime import date
from typing import Optional

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.broker.value_objects import BrokerStatus
from src.domain.aggregates.dispatch.aggregate import Dispatch
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
        location: Optional[Location],
        instruction: Instruction,
        container: Optional[Container],
        date: date,
        appointment: Optional[Appointment],
        ) -> Task:
        if location and location.status == LocationStatus.INACTIVE:
            raise BusinessRuleViolation('Cannot set a deactivated location on a new task.')
        
        location = location if location else None

        return Task(
            priority,
            instruction,
            date,
            location,
            container,
            appointment
        )
    
    @staticmethod
    def create_dispatch(
        broker: Broker,
        driver: Optional[Driver],
        plan: list[Task]
        ) -> Dispatch:
        if broker.status == BrokerStatus.INACTIVE:
            raise BusinessRuleViolation('Cannot set a deactivated broker on a dispatch.')
        if driver.status == DriverStatus.UNAVAILABLE:
            raise BusinessRuleViolation('Cannot set an unavailable driver on a dispatch.')
        if driver.status == DriverStatus.DEACTIVATED:
            raise BusinessRuleViolation('Cannot set a deactivated driver on a dispatch.')
        if len(plan) < 2:
            raise BusinessRuleViolation("A new dispatch plan requires at least two tasks.")
        
        return Dispatch(broker, plan, driver)
    
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
