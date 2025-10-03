from datetime import date, time
from hmac import new
from uuid import uuid4

import pytest

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, DispatchStatus, Instruction
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.aggregates.location.value_objects import Address
from src.domain.services import Dispatcher
from tests import dispatch, driver


def create_minimal_dispatch() -> Dispatch:
    """
    Creates a dispatch without an assigned driver or an
    appointment set.
    """
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    plan = [
        Task(1, Instruction.PICKUP_EMPTY, uuid4()),
        Task(2, Instruction.LIVE_LOAD, uuid4())
        ]
    
    return Dispatcher.create_dispatch(broker.id, containers, plan)


def create_dispatch_ready_to_start() -> Dispatch:
    dispatch = create_minimal_dispatch()
    dispatch.add_task(Task(3, Instruction.INGATE, uuid4(),))
    dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))

    return dispatch

def create_dispatch_in_progress() -> tuple[Dispatch, Driver]:
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)

    return dispatch, driver

def create_completed_dispatch() -> Dispatch:
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)
    dispatch.start_task(4)
    dispatch.complete_task(4)

    Dispatcher.complete_dispatch(dispatch, driver)

    return dispatch, driver


def create_cancelled_dispatch() -> Dispatch:
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    Dispatcher.cancel_dispatch(dispatch, driver)

    return dispatch, driver


# ---------------------------------------- TESTING DISPATCH UNDER DRAFT STATUS ----------------------------------------


def test_create_minimal_dispatch():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    plan = [
        Task(1, Instruction.PICKUP_EMPTY),
        Task(2, Instruction.LIVE_LOAD)
    ]

    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)
    
    assert dispatch.id
    assert dispatch.status == DispatchStatus.DRAFT
    assert dispatch.plan
    assert dispatch.containers
    assert dispatch.driver_ref is None


def test_creating_dispatch_with_one_task():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    plan = [Task(1, Instruction.PICKUP_EMPTY)]

    match = 'A new dispatch plan requires at least two tasks.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.create_dispatch(broker.id, containers, plan)
    

def test_creating_dispatch_without_a_container():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    plan = [
        Task(1, Instruction.PICKUP_EMPTY),
        Task(2, Instruction.LIVE_LOAD)
        ]
    
    match = 'A new dispatch requires at least one container.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.create_dispatch(broker.id, [], plan)


def test_new_dispatch_with_one_container_gets_assigned_to_tasks():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    plan = [
        Task(1, Instruction.PICKUP_EMPTY),
        Task(2, Instruction.LIVE_LOAD),
        Task(3, Instruction.INGATE),
        ]
    
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)

    for task in dispatch.plan:
        assert task.container


def test_new_dispatch_does_not_assign_container_to_tasks_that_do_not_require_container():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    plan = [
        Task(1, Instruction.FETCH_CHASSIS),
        Task(2, Instruction.PICKUP_LOADED),
        Task(3, Instruction.LIVE_UNLOAD),
        Task(4, Instruction.TERMINATE_EMPTY),
        Task(5, Instruction.TERMINATE_CHASSIS)
        ]
    
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)

    for task in dispatch.plan:
        if task.instruction == Instruction.FETCH_CHASSIS:
            assert not task.container
        if task.instruction == Instruction.TERMINATE_CHASSIS:
            assert not task.container


def test_new_dispatch_with_two_containers_do_not_get_assigned_to_tasks():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456', 'UMXU123456']
    plan = [
        Task(1, Instruction.PICKUP_EMPTY),
        Task(2, Instruction.LIVE_LOAD),
        Task(3, Instruction.INGATE),
        ]
    
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)

    for task in dispatch.plan:
        assert not task.container


def test_assigning_draft_dispatch_containers_to_tasks():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456', 'UMXU123456']
    plan = [
        Task(1, Instruction.PICKUP_LOADED),
        Task(2, Instruction.LIVE_UNLOAD),
        Task(3, Instruction.DROP_EMPTY),
        Task(4, Instruction.PICKUP_LOADED),
        Task(5, Instruction.INGATE),
        ]
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)

    Dispatcher.assign_container_to_tasks(dispatch, 'CMAU123456', [1, 2, 3])
    Dispatcher.assign_container_to_tasks(dispatch, 'UMXU123456', [4, 5])

    for priority in range(1, 4):
        assert dispatch.get_task(priority).container == 'CMAU123456'
    for priority in range(4, 6):
        assert dispatch.get_task(priority).container == 'UMXU123456' 


def test_cannot_assign_container_that_is_not_in_draft_dispatch_to_tasks():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456', 'UMXU123456']
    plan = [
        Task(1, Instruction.PICKUP_LOADED),
        Task(2, Instruction.LIVE_UNLOAD),
        Task(3, Instruction.DROP_EMPTY),
        Task(4, Instruction.PICKUP_LOADED),
        Task(5, Instruction.INGATE),
        ]
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)

    match = 'Container number is not in dispatch cannot be assigned to tasks.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_container_to_tasks(dispatch, 'MSMU123456', [1, 2, 3])


def test_cannot_assign_draft_dispatch_container_to_task_that_does_not_require_container():
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456', 'UMXU123456']
    plan = [
        Task(1, Instruction.FETCH_CHASSIS),
        Task(2, Instruction.PICKUP_LOADED),
        Task(3, Instruction.LIVE_UNLOAD),
        Task(4, Instruction.DROP_EMPTY),
        Task(5, Instruction.PICKUP_LOADED),
        Task(6, Instruction.INGATE),
        ]
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)

    match = 'Invalid assignment of container to task that does not require a container.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_container_to_tasks(dispatch, 'CMAU123456', [1, 2, 3, 4])


def test_assigning_available_driver_to_draft_dispatch():
    dispatch = create_minimal_dispatch()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    assert dispatch.driver_ref == driver.id
    assert driver.status == DriverStatus.AVAILABLE
    

def test_assigning_unavailable_driver_to_draft_dispatch():
    dispatch = create_minimal_dispatch()
    driver = Driver('John')
    driver.sit_out()

    match = 'Unavailable drivers cannot be assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(dispatch, driver)

    assert driver.status == DriverStatus.UNAVAILABLE
    assert dispatch.driver_ref is None


def test_assigning_deactivated_driver_to_draft_dispatch():
    dispatch = create_minimal_dispatch()
    driver = Driver('John')
    driver.deactivate()

    match = 'Deactivated drivers cannot be assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(dispatch, driver)

    assert driver.status == DriverStatus.DEACTIVATED
    assert dispatch.driver_ref is None


def test_removing_available_driver_from_draft_dispatch():
    dispatch = create_minimal_dispatch()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    Dispatcher.remove_driver(dispatch)

    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_starting_dispatch():
    dispatch = create_minimal_dispatch()
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(1, 1, 25), time(9)))
    dispatch.add_task(Task(3, Instruction.INGATE, uuid4()))
    dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    Dispatcher.start_dispatch(dispatch, driver)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert driver.status == DriverStatus.OPERATING


def test_starting_dispatch_with_unavailable_driver():
    dispatch = create_minimal_dispatch()
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(1, 1, 25), time(9)))
    dispatch.add_task(Task(3, Instruction.INGATE, uuid4()))
    dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    driver = Driver('John')
    driver.sit_out()

    match = 'A driver has not been assigned to dispatch.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(dispatch, driver)

    assert dispatch.status == DispatchStatus.DRAFT
    assert driver.status == DriverStatus.UNAVAILABLE


def test_starting_dispatch_with_deactivated_driver():
    dispatch = create_minimal_dispatch()
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(1, 1, 25), time(9)))
    dispatch.add_task(Task(3, Instruction.INGATE, uuid4()))
    dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    driver = Driver('John')
    driver.deactivate()

    match = 'A driver has not been assigned to dispatch.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(dispatch, driver)

    assert dispatch.status == DispatchStatus.DRAFT
    assert driver.status == DriverStatus.DEACTIVATED


def test_dispatch_cannot_start_when_driver_operating_on_different_dispatch():
    # first dispatch that is in progress
    first_dispatch = create_minimal_dispatch()
    first_dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(1, 1, 25), time(9)))
    first_dispatch.add_task(Task(3, Instruction.INGATE, uuid4()))
    first_dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    operating_driver = Driver('John')
    Dispatcher.assign_driver(first_dispatch, operating_driver)
    Dispatcher.start_dispatch(first_dispatch, operating_driver)

    # second dispatch that will attempt to start
    second_dispatch = create_minimal_dispatch()
    second_dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(1, 1, 25), time(11)))
    second_dispatch.add_task(Task(3, Instruction.INGATE, uuid4()))
    second_dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    Dispatcher.assign_driver(second_dispatch, operating_driver)
    
    match = 'Only available drivers can begin operating.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(second_dispatch, operating_driver)

    assert second_dispatch.status == DispatchStatus.DRAFT
    assert operating_driver.status == DriverStatus.OPERATING


# ---------------------------------------- TESTING DISPATCH IN PROGRESS ----------------------------------------


def test_assigning_a_driver_to_dispatch_in_progress():
    dispatch, driver = create_dispatch_in_progress()
    different_driver = Driver('Same')

    match = 'A dispatch in progress cannot have a driver assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(dispatch, different_driver)

    assert dispatch.driver_ref != different_driver.id

def test_assigning_operating_driver_to_different_draft_dispatch():
    first_dispatch = create_dispatch_ready_to_start()
    operating_driver = Driver('John')
    Dispatcher.assign_driver(first_dispatch, operating_driver)
    Dispatcher.start_dispatch(first_dispatch, operating_driver)
    second_dispatch = create_minimal_dispatch()

    Dispatcher.assign_driver(second_dispatch, operating_driver)
    
    assert operating_driver.status == DriverStatus.OPERATING
    assert first_dispatch.status == DispatchStatus.IN_PROGRESS
    assert second_dispatch.status == DispatchStatus.DRAFT
    assert second_dispatch.driver_ref == operating_driver.id


def test_removing_driver_from_dispatch_in_progress():
    dispatch, driver = create_dispatch_in_progress()

    match = 'Cannot remove a driver from a dispatch that is in progress.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.remove_driver(dispatch)    

    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_reverting_dispatch_in_progress_to_draft():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)

    Dispatcher.revert_dispatch_to_draft(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.DRAFT
    assert driver.status == DriverStatus.AVAILABLE


def test_reverting_dispatch_with_tasks_already_started_back_to_draft():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)

    match = 'Only a dispatch without any tasks started can revert to draft.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.revert_dispatch_to_draft(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert driver.status == DriverStatus.OPERATING


def test_reverting_dispatch_in_progress_to_draft_with_wrong_driver():
    dispatch, driver = create_dispatch_in_progress()
    wrong_driver = Driver('Sam')

    match = 'Reverting dispatch with wrong driver.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.revert_dispatch_to_draft(dispatch, wrong_driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref != wrong_driver.id
    assert driver != wrong_driver


def test_starting_dispatch_when_already_in_progress():
    dispatch, driver = create_dispatch_in_progress()

    match = 'Only a draft dispatch can be started.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_pausing_dispatch_in_progress():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)

    Dispatcher.pause_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.PAUSED
    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_pausing_dispatch_in_progress_with_tasks_completed():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)

    Dispatcher.pause_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.PAUSED
    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_pausing_dispatch_while_task_is_in_progress():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)

    match = 'Cannot pause a dispatch when a task is in progress.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.pause_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref
    assert driver.status == DriverStatus.OPERATING


def test_pausing_dispatch_in_progress_with_wrong_driver():
    dispatch, driver = create_dispatch_in_progress()
    wrong_driver = Driver('Sam')

    match = 'Pausing dispatch with wrong driver.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.pause_dispatch(dispatch, wrong_driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref != wrong_driver.id
    assert driver != wrong_driver


def test_resuming_dispatch_in_progress():
    dispatch, driver = create_dispatch_in_progress()

    match = 'Only a paused dispatch can resume.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.resume_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_completing_dispatch_in_progress():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)
    dispatch.start_task(4)
    dispatch.complete_task(4)

    Dispatcher.complete_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.COMPLETED
    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_completing_dispatch_in_progress_without_all_tasks_completed():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)

    match = 'All tasks must be completed before dispatch can be completed.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.complete_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref
    assert driver.status == DriverStatus.OPERATING


def test_completing_dispatch_in_progress_with_wrong_driver():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)
    dispatch.start_task(4)
    dispatch.complete_task(4)
    wrong_driver = Driver('Sam')

    match = 'Completing dispatch with wrong driver.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.complete_dispatch(dispatch, wrong_driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref
    assert driver.status == DriverStatus.OPERATING


def test_cancelling_dispatch_in_progress():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)

    Dispatcher.cancel_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.CANCELLED
    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_cancelling_dispatch_in_progress_with_some_tasks_completed():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)

    Dispatcher.cancel_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.CANCELLED
    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_cancelling_dispatch_in_progress_with_task_in_progress():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)

    Dispatcher.cancel_dispatch(dispatch, driver)
        
    assert dispatch.status == DispatchStatus.CANCELLED
    assert dispatch.driver_ref is None
    assert driver.status == DriverStatus.AVAILABLE


def test_cancelling_dispatch_in_progress_with_wrong_driver():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)

    wrong_driver = Driver('Sam')

    match = 'Cancelling dispatch with wrong driver.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.cancel_dispatch(dispatch, wrong_driver)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref
    assert driver.status == DriverStatus.OPERATING


def test_cancelling_dispatch_in_progress_without_entering_driver():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
  

    match = 'Driver must be specified when cancelling a dispatch in progress.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.cancel_dispatch(dispatch)
        
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.driver_ref
    assert driver.status == DriverStatus.OPERATING


# ---------------------------------------- TESTING PAUSED DISPATCH ----------------------------------------


def test_paused_dispatch_can_assign_a_driver():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    
    Dispatcher.assign_driver(dispatch, driver)

    assert dispatch.driver_ref == driver.id
    assert dispatch.status == DispatchStatus.PAUSED
    assert driver.status == DriverStatus.AVAILABLE


def test_paused_dispatch_can_assign_a_driver_and_resume():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    Dispatcher.assign_driver(dispatch, driver)

    Dispatcher.resume_dispatch(dispatch, driver)

    assert dispatch.driver_ref == driver.id
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert driver.status == DriverStatus.OPERATING


def test_removing_assigned_driver_from_paused_dispatch():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    Dispatcher.assign_driver(dispatch, driver)

    Dispatcher.remove_driver(dispatch)

    assert dispatch.driver_ref is None


def test_removing_driver_from_paused_dispatch():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)

    match = 'Dispatch does not have a driver to remove.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.remove_driver(dispatch)

    assert dispatch.driver_ref is None


def test_pausing_paused_dispatch():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    
    match = 'Dispatch cannot be paused without a driver assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.pause_dispatch(dispatch, driver)


def test_resuming_paused_dispatch_without_driver_assigned():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    
    match = 'Dispatch cannot resume without a driver assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.resume_dispatch(dispatch, driver)


def test_resuming_paused_dispatch_with_a_new_driver():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    new_driver = Driver('Sam')
    Dispatcher.assign_driver(dispatch, new_driver)

    Dispatcher.resume_dispatch(dispatch, new_driver)

    assert dispatch.driver_ref == new_driver.id
    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert new_driver.status == DriverStatus.OPERATING
    

def test_starting_a_paused_dispatch():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    new_driver = Driver('Sam')
    Dispatcher.assign_driver(dispatch, new_driver)

    match = 'Only a draft dispatch can be started.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(dispatch, new_driver)

    assert dispatch.driver_ref == new_driver.id
    assert dispatch.status == DispatchStatus.PAUSED
    assert new_driver.status == DriverStatus.AVAILABLE


def test_reverting_paused_dispatch_to_draft():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)

    match = 'A paused dispatch cannot be reverted to draft.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.revert_dispatch_to_draft(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.PAUSED
    assert driver.status == DriverStatus.AVAILABLE
    

def test_completing_a_paused_dispatch():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)
    new_driver = Driver('Sam')
    Dispatcher.assign_driver(dispatch, new_driver)

    match = 'Only a dispatch in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.complete_dispatch(dispatch, new_driver)

    assert dispatch.driver_ref == new_driver.id
    assert dispatch.status == DispatchStatus.PAUSED
    assert new_driver.status == DriverStatus.AVAILABLE


def test_cancelling_a_paused_dispatch():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)

    Dispatcher.cancel_dispatch(dispatch)

    assert dispatch.status == DispatchStatus.CANCELLED


def test_cancelling_a_paused_dispatch_by_entering_driver():
    dispatch = create_dispatch_ready_to_start()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.start_dispatch(dispatch, driver)
    Dispatcher.pause_dispatch(dispatch, driver)

    match = 'Driver does need to be inputted when cancelling a paused dispatch.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.cancel_dispatch(dispatch, driver)

    assert dispatch.status == DispatchStatus.PAUSED


# ---------------------------------------- TESTING COMPLETED DISPATCH ----------------------------------------


def test_assigning_driver_to_completed_dispatch():
    dispatch, driver = create_completed_dispatch()

    match = 'A completed dispatch cannot have a driver assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED


def test_removing_driver_from_completed_dispatch():
    dispatch, driver = create_completed_dispatch()

    match = 'Dispatch does not have a driver to remove.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.remove_driver(dispatch)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED


def test_starting_completed_dispatch():
    dispatch, driver = create_completed_dispatch()

    match = 'A driver has not been assigned to dispatch.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED
    assert driver.status == DriverStatus.AVAILABLE


def test_reverting_completed_dispatch_to_draft():
    dispatch, driver = create_completed_dispatch()

    match = 'A completed dispatch cannot be reverted to draft.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.revert_dispatch_to_draft(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED
    assert driver.status == DriverStatus.AVAILABLE


def test_pausing_a_completed_dispatch():
    dispatch, driver = create_completed_dispatch()

    match = 'A completed dispatch cannot be paused.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.pause_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED
    assert driver.status == DriverStatus.AVAILABLE


def test_resuming_a_completed_dispatch():
    dispatch, driver = create_completed_dispatch()

    match = 'A completed dispatch cannot be resumed.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.resume_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED
    assert driver.status == DriverStatus.AVAILABLE


def test_completing_a_completed_dispatch():
    dispatch, driver = create_completed_dispatch()

    match = 'A completed dispatch cannot be completed.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.complete_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.COMPLETED
    assert driver.status == DriverStatus.AVAILABLE


# ---------------------------------------- TESTING CANCELLED DISPATCH ----------------------------------------


def test_assigning_driver_to_cancelled_dispatch():
    dispatch, driver = create_cancelled_dispatch()

    match = 'A cancelled dispatch cannot have a driver assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED


def test_removing_driver_from_cancelled_dispatch():
    dispatch, driver = create_cancelled_dispatch()

    match = 'Dispatch does not have a driver to remove.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.remove_driver(dispatch)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED


def test_starting_cancelled_dispatch():
    dispatch, driver = create_cancelled_dispatch()

    match = 'A driver has not been assigned to dispatch.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.start_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED
    assert driver.status == DriverStatus.AVAILABLE


def test_reverting_cancelled_dispatch_to_draft():
    dispatch, driver = create_cancelled_dispatch()

    match = 'A cancelled dispatch cannot be reverted to draft.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.revert_dispatch_to_draft(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED
    assert driver.status == DriverStatus.AVAILABLE


def test_pausing_a_completed_dispatch():
    dispatch, driver = create_cancelled_dispatch()

    match = 'A cancelled dispatch cannot be paused.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.pause_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED


def test_resuming_a_completed_dispatch():
    dispatch, driver = create_cancelled_dispatch()

    match = 'A cancelled dispatch cannot be resumed.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.resume_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED
    assert driver.status == DriverStatus.AVAILABLE


def test_completing_a_cancelled_dispatch():
    dispatch, driver = create_cancelled_dispatch()

    match = 'A cancelled dispatch cannot be completed.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.complete_dispatch(dispatch, driver)

    assert dispatch.driver_ref is None
    assert dispatch.status == DispatchStatus.CANCELLED
    assert driver.status == DriverStatus.AVAILABLE

