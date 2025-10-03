from token import OP
from typing import Optional
from uuid import UUID

from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Container, DispatchStatus, Instruction
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus


class Dispatcher:
    @staticmethod
    def create_dispatch(
        broker_ref: UUID,
        containers: list[Container],
        plan: list[Task],
        driver_ref: Optional[Driver] = None
        ) -> Dispatch:
        if len(containers) < 1:
            raise ValueError("A new dispatch requires at least one container.")
        if len(plan) < 2:
            raise ValueError("A new dispatch plan requires at least two tasks.")
        
        if len(containers) == 1:
            for task in plan:
                if task.instruction in (
                    Instruction.FETCH_CHASSIS,
                    Instruction.BOBTAIL_TO,
                    Instruction.TERMINATE_CHASSIS,
                ):
                    continue
                task.container = containers[0]
        
        return Dispatch(broker_ref, containers, plan, driver_ref)
    
    @staticmethod
    def assign_container_to_tasks(dispatch: Dispatch, container: str, task_priorities: list[int]):
        if container not in dispatch.containers:
            raise ValueError('Container number is not in dispatch cannot be assigned to tasks.')
        for priority in task_priorities:
            if dispatch.get_task(priority).instruction in (
                Instruction.FETCH_CHASSIS,
                Instruction.BOBTAIL_TO,
                Instruction.TERMINATE_CHASSIS,
            ):
                raise ValueError('Invalid assignment of container to task that does not require a container.')
            
        for priority in task_priorities:
            dispatch.get_task(priority).container = container
    
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
