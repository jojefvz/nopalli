from datetime import date, time
from uuid import uuid4

import pytest

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, DispatchStatus, Instruction, TaskStatus
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.location.value_objects import Address
from src.domain.services import Dispatcher


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


def create_two_container_dispatch_without_containers_assigned() -> Dispatch:
    """
    Creates a dispatch with two containers, an assigned driver, 
    an appointment set.
    """
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456', 'UMXU123456']
    plan = [
        Task(1, Instruction.FETCH_CHASSIS),
        Task(2, Instruction.PICKUP_LOADED),
        Task(3, Instruction.LIVE_UNLOAD),
        Task(4, Instruction.DROP_EMPTY),
        Task(5, Instruction.PICKUP_LOADED),
        Task(6, Instruction.INGATE),
        Task(7, Instruction.TERMINATE_CHASSIS),
        ]
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    return dispatch


def create_dispatch_with_invalid_plan(plan) -> Dispatch:
    """
    Creates a dispatch with one container, an assigned driver, 
    an appointment set, and takes in an invalid plan.
    """
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    return dispatch


def create_in_progress_dispatch() -> Dispatch:
    dispatch = create_minimal_dispatch()
    dispatch.add_task(Task(3, Instruction.INGATE, uuid4(),))
    dispatch.add_task(Task(4, Instruction.TERMINATE_CHASSIS, uuid4()))
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    dispatch.start()

    return dispatch


def create_completed_dispatch() -> Dispatch:
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)
    dispatch.start_task(4)
    dispatch.complete_task(4)

    dispatch.complete()

    return dispatch


# ---------------------------------------- TESTING DISPATCH IN DRAFT STATUS ----------------------------------------


def test_draft_dispatch_can_add_task():
    dispatch = create_minimal_dispatch()
    third_task = Task(3, Instruction.INGATE)

    dispatch.add_task(third_task)

    assert dispatch.status == DispatchStatus.DRAFT
    assert len(dispatch.plan) == 3
    assert dispatch.get_task(3) is third_task
    assert dispatch.get_task(3).container


def test_draft_dispatch_can_insert_task():
    dispatch = create_minimal_dispatch()
    new_second_task = Task(2, Instruction.LIVE_LOAD)

    dispatch.add_task(new_second_task)

    assert dispatch.status == DispatchStatus.DRAFT
    assert len(dispatch.plan) == 3
    assert dispatch.get_task(2) is new_second_task
    assert dispatch.get_task(2).container
    assert dispatch.get_task(3).priority == 3
    

def test_draft_dispatch_cannot_add_a_eleventh_task():
    dispatch = create_minimal_dispatch()
    batch_of_tasks = [Task(i, Instruction.LIVE_LOAD) for i in range(3, 12)]

    match = 'Cannot have more than 10 tasks in dispatch plan.'
    with pytest.raises(ValueError, match=match):
        for task in batch_of_tasks:
            dispatch.add_task(task)

    assert dispatch.status == DispatchStatus.DRAFT
    assert len(dispatch.plan) == 10
    assert dispatch.get_task(3).priority == 3
    assert dispatch.get_task(6).priority == 6
    assert dispatch.get_task(10).priority == 10


def test_draft_dispatch_can_remove_task():
    dispatch = create_minimal_dispatch()
    third_task = Task(3, Instruction.INGATE)
    dispatch.add_task(third_task)

    dispatch.remove_task(3)

    assert dispatch.status == DispatchStatus.DRAFT
    assert len(dispatch.plan) == 2
    assert dispatch.get_task(2).priority == 2


def test_draft_dispatch_cannot_remove_task_when_only_two_tasks_exist():
    dispatch = create_minimal_dispatch()

    match = 'Dispatch plan cannot have less than two tasks.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_task(2)

    assert dispatch.status == DispatchStatus.DRAFT
    assert len(dispatch.plan) == 2


def test_draft_dispatch_can_remove_intermediate_task():
    dispatch = create_minimal_dispatch()
    new_second_task = Task(2, Instruction.LIVE_LOAD)
    dispatch.add_task(new_second_task)
    
    dispatch.remove_task(2)

    assert dispatch.status == DispatchStatus.DRAFT
    assert len(dispatch.plan) == 2
    assert dispatch.get_task(1).priority == 1
    assert dispatch.get_task(2).priority == 2


def test_draft_dispatch_cannot_start_a_task():
    dispatch = create_minimal_dispatch()

    match = 'Only a dispatch in progress can start a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.start_task(1)

    assert dispatch.status == DispatchStatus.DRAFT
    assert dispatch.get_task(1).status == TaskStatus.NOT_STARTED


def test_draft_dispatch_cannot_complete_a_task():
    dispatch = create_minimal_dispatch()

    match = 'Only a dispatch in progress can complete a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete_task(1)

    assert dispatch.status == DispatchStatus.DRAFT
    assert dispatch.get_task(1).status == TaskStatus.NOT_STARTED


def test_draft_dispatch_cannot_revert_a_task():
    dispatch = create_minimal_dispatch()

    match = 'Only a dispatch in progress can revert a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.revert_task(1)

    assert dispatch.status == DispatchStatus.DRAFT
    assert dispatch.get_task(1).status == TaskStatus.NOT_STARTED


def test_draft_dispatch_reverting_to_draft():
    dispatch = create_minimal_dispatch()

    match = 'Only a dispatch in progress can revert back to draft.'
    with pytest.raises(ValueError, match=match):
        dispatch.revert_to_draft()

    assert dispatch.status == DispatchStatus.DRAFT


def test_draft_dispatch_cannot_mark_a_stopoff():
    dispatch = create_minimal_dispatch()

    match = 'Only a dispatch in progress can mark a task as stopoff.'
    with pytest.raises(ValueError, match=match):
        dispatch.mark_stopoff(1)

    assert dispatch.status == DispatchStatus.DRAFT


def test_setting_an_appointment_to_draft():
    dispatch = create_minimal_dispatch()
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)

    dispatch.set_appointment(2, appointment)

    assert dispatch.get_task(2).appointment == appointment


def test_removing_an_appointment_from_draft():
    dispatch = create_minimal_dispatch()
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)
    dispatch.set_appointment(2, appointment)

    dispatch.remove_appointment(2)

    assert dispatch.get_task(2).appointment is None


# --------- TESTING DISPATCH VERIFICATION BEFORE STARTING ---------


def test_dispatch_verification_catches_missing_driver_before_starting_dispatch():
    dispatch = create_minimal_dispatch()

    match = 'A driver has not been assigned to dispatch.'
    with pytest.raises(ValueError, match=match):
        dispatch.start()

    assert not dispatch.driver_ref


def test_dispatch_verification_catches_missing_appointment_before_starting_dispatch():
    dispatch = create_minimal_dispatch()
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    match = 'An appointment has not been set on at least one task.'
    with pytest.raises(ValueError, match=match):
        dispatch.start()
    
    assert not dispatch._appointment_exists()


def test_dispatch_verification_catches_tasks_without_containers_before_starting_two_container_dispatch():
    dispatch = create_two_container_dispatch_without_containers_assigned()

    match = 'A multi-container dispatch requires containers to be assigned to tasks.'
    with pytest.raises(ValueError, match=match):
        dispatch.start()
    
    assert not dispatch._containers_assigned()


def test_dispatch_verification_catches_invalid_plan_before_starting_dispatch(invalid_plan):
    dispatch = create_dispatch_with_invalid_plan(invalid_plan)
    dispatch.plan = invalid_plan

    match = 'Plan instructions are not valid.'
    with pytest.raises(ValueError, match=match):
        dispatch.start()

    assert not dispatch._valid_plan()


def test_dispatch_verification_catches_invalid_plan_before_starting_two_container_dispatch(invalid_two_container_plan):
    dispatch = invalid_two_container_plan

    match = 'Plan instructions are not valid.'
    with pytest.raises(ValueError, match=match):
        dispatch.start()

    assert not dispatch._valid_plan()


def test_starting_a_draft_dispatch(ready_draft_dispatch):
    dispatch = ready_draft_dispatch

    dispatch.start()

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS


def test_pausing_draft_dispatch():
    dispatch = create_minimal_dispatch()
    
    match = 'Only a dispatch in progress can be paused.'
    with pytest.raises(ValueError, match=match):
        dispatch.pause()

    assert dispatch.status == DispatchStatus.DRAFT


def test_resuming_draft_dispatch():
    dispatch = create_minimal_dispatch()
    
    match = 'Only a paused dispatch can resume.'
    with pytest.raises(ValueError, match=match):
        dispatch.resume()

    assert dispatch.status == DispatchStatus.DRAFT


def test_completing_a_draft_dispatch():
    dispatch = create_minimal_dispatch()
    
    match = 'Only a dispatch in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete()

    assert dispatch.status == DispatchStatus.DRAFT


# ---------------------------------------- TESTING DISPATCH IN PROGRESS ----------------------------------------


def test_starting_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()

    match = 'Only a draft dispatch can be started.'
    with pytest.raises(ValueError, match=match):
        dispatch.start()


def test_dispatch_in_progress_reverting_to_draft_when_first_task_not_started():
    dispatch = create_in_progress_dispatch()

    dispatch.revert_to_draft()

    assert dispatch.status == DispatchStatus.DRAFT


def test_dispatch_in_progress_reverting_to_draft_when_first_task_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)

    match = 'Only a dispatch without any tasks started can revert to draft.'
    with pytest.raises(ValueError, match=match):
        dispatch.revert_to_draft()

    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_dispatch_in_progress_starting_first_task():
    dispatch = create_in_progress_dispatch()
    
    dispatch.start_task(1)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.IN_PROGRESS


def test_dispatch_in_progress_skipping_first_task_and_starting_second_task():
    dispatch = create_in_progress_dispatch()
    
    match = 'Cannot start tasks out of order.'
    with pytest.raises(ValueError, match=match):
        dispatch.start_task(2)

    assert dispatch.get_task(2).status == TaskStatus.NOT_STARTED


def test_dispatch_in_progress_skipping_second_task_and_starting_third_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)

    match = 'Cannot start tasks out of order.'
    with pytest.raises(ValueError, match=match):
        dispatch.start_task(3)

    assert dispatch.get_task(3).status == TaskStatus.NOT_STARTED


def test_dispatch_in_progress_completing_first_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)

    dispatch.complete_task(1)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.COMPLETED


def test_dispatch_in_progress_reverting_first_started_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)

    dispatch.revert_task(1)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.NOT_STARTED


def test_dispatch_in_progress_reverting_first_completed_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)

    dispatch.revert_task(1)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.IN_PROGRESS


def test_dispatch_in_progress_reverting_stopoff_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.mark_stopoff(1)

    dispatch.revert_task(1)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.NOT_STARTED


def test_dispatch_in_progress_completing_all_tasks():
    dispatch = create_in_progress_dispatch()

    dispatch.start_task(1)
    dispatch.complete_task(1)

    dispatch.start_task(2)
    dispatch.complete_task(2)

    dispatch.start_task(3)
    dispatch.complete_task(3)

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert dispatch.get_task(3).status == TaskStatus.COMPLETED


def test_overwriting_an_appointment_to_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(11), None)

    dispatch.set_appointment(2, appointment)

    assert dispatch.get_task(2).appointment == appointment
    

def test_setting_a_second_appointment_to_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(12), time(16))

    dispatch.set_appointment(3, appointment)

    assert dispatch.get_task(3).appointment == appointment


def test_setting_an_appointment_to_a_completed_task_on_a_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(12), time(16))

    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        dispatch.set_appointment(1, appointment)

    assert not dispatch.get_task(1).appointment


def test_removing_the_only_appointment_on_dispatch():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)

    match = 'Cannot remove the only appointment on a dispatch that is in progress'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_appointment(2)

    assert dispatch.get_task(2).appointment


def test_removing_the_second_existing_appointment_on_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(12), time(16))
    dispatch.set_appointment(3, appointment)

    dispatch.remove_appointment(3)

    assert dispatch.get_task(3).appointment is None


def test_adding_a_task_to_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    task = Task(1, Instruction.FETCH_CHASSIS, uuid4())
    
    dispatch.add_task(task)

    assert dispatch.get_task(1).instruction == Instruction.FETCH_CHASSIS
    assert len(dispatch.plan) == 5


def test_adding_a_task_in_a_position_before_a_completed_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    new_first_task = Task(1, Instruction.FETCH_CHASSIS)
    
    match = 'Cannot add a new task before a completed task.'
    with pytest.raises(ValueError, match=match):
        dispatch.add_task(new_first_task)

    assert dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert len(dispatch.plan) == 4


def test_inserting_an_invalid_task_to_a_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    task = Task(1, Instruction.LIVE_LOAD)
    
    match = 'Invalid task cannot be added.'
    with pytest.raises(ValueError, match=match):
        dispatch.add_task(task)

    assert not dispatch._valid_additional_task(task)
    assert len(dispatch.plan) == 4


def test_removing_a_task_from_a_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    
    match = 'Only a draft dispatch can remove a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_task(1)

    assert len(dispatch.plan) == 4


def test_marking_first_task_a_stop_off_to_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)

    dispatch.mark_stopoff(1)

    assert dispatch.get_task(1).status == TaskStatus.STOP_OFF


def test_marking_second_task_a_stop_off_to_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)

    dispatch.mark_stopoff(2)

    assert dispatch.get_task(2).status == TaskStatus.STOP_OFF


def test_adding_a_new_task_after_a_stopoff_to_a_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.mark_stopoff(2)
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9))
    third_task = Task(3, Instruction.LIVE_LOAD, uuid4(), appointment)
   
    dispatch.add_task(third_task)

    assert dispatch.get_task(2).status == TaskStatus.STOP_OFF
    assert dispatch.get_task(3).status == TaskStatus.NOT_STARTED
    assert dispatch.get_task(3).container


def test_adding_an_invalid_task_after_a_stopoff_to_a_dispatch_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.mark_stopoff(1)
    task = Task(2, Instruction.BOBTAIL_TO, uuid4())

    match = 'Invalid task cannot be added.'
    with pytest.raises(ValueError, match=match):
        dispatch.add_task(task)

    assert not dispatch._valid_additional_task(task)
    assert len(dispatch.plan) == 4

def test_pausing_dispatch_that_is_in_progress():
    dispatch = create_in_progress_dispatch()

    dispatch.pause()

    assert dispatch.status == DispatchStatus.PAUSED


def test_pausing_in_progress_dispatch_with_task_in_progress():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    
    match = 'Cannot pause a dispatch when a task is in progress.'
    with pytest.raises(ValueError, match=match):
        dispatch.pause()

    assert dispatch.get_task(1).status == TaskStatus.IN_PROGRESS
    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_pausing_in_progress_dispatch_after_two_tasks_completed():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    
    dispatch.pause()

    assert dispatch.status == DispatchStatus.PAUSED


def test_resuming_in_progress_dispatch():
    dispatch = create_in_progress_dispatch()
    
    match = 'Only a paused dispatch can resume.'
    with pytest.raises(ValueError, match=match):
        dispatch.resume()

    assert dispatch.status == DispatchStatus.IN_PROGRESS

    
def test_dispatch_in_progress_can_complete_when_all_tasks_are_completed():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)
    dispatch.start_task(4)
    dispatch.complete_task(4)

    dispatch.complete()

    assert dispatch.status == DispatchStatus.COMPLETED
    assert dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert dispatch.get_task(3).status == TaskStatus.COMPLETED


def test_dispatch_in_progress_cannot_complete_when_last_task_not_completed():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.start_task(3)
    dispatch.complete_task(3)

    match = 'All tasks must be completed before dispatch can be completed.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete()

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert dispatch.get_task(4).status == TaskStatus.NOT_STARTED


def test_dispatch_in_progress_cannot_complete_when_last_two_tasks_not_completed():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)

    match = 'All tasks must be completed before dispatch can be completed.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete()

    assert dispatch.status == DispatchStatus.IN_PROGRESS
    assert dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert dispatch.get_task(3).status == TaskStatus.NOT_STARTED
    assert dispatch.get_task(4).status == TaskStatus.NOT_STARTED


def test_dispatch_in_progress_can_be_cancelled():
    dispatch = create_in_progress_dispatch()

    dispatch.cancel()

    assert dispatch.status == DispatchStatus.CANCELLED


def test_dispatch_in_progress_with_some_tasks_completed_can_be_cancelled():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)

    dispatch.cancel()

    assert dispatch.status == DispatchStatus.CANCELLED


def test_dispatch_in_progress_with_task_in_progress_can_be_cancelled():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)

    dispatch.cancel()

    assert dispatch.status == DispatchStatus.CANCELLED


# # --------------------------------- TESTING APPOINTMNET LOGIC ---------------------------------

# def test_setting_appointment_with_a_past_date(fake_task):
#     match = 'Cannot set an appointment with a past date.'
#     with pytest.raises(ValueError, match=match):
#         fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9), None))

#     assert fake_task.appointment is None

# def test_setting_appointment_with_start_time_later_than_end_time(fake_task):
#     match = 'Cannot set a start time that is later than the end time.'
#     with pytest.raises(ValueError, match=match):
#         fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), time(6)))

#     assert fake_task.appointment is None


# ---------------------------------------- TESTING PAUSED DISPATCH ----------------------------------------


def test_paused_dispatch_can_resume():
    dispatch = create_in_progress_dispatch()
    dispatch.pause()

    dispatch.resume()

    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_paused_dispatch_can_resume_after_two_completed_tasks():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.pause()

    dispatch.resume()

    assert dispatch.status == DispatchStatus.IN_PROGRESS


def test_pausing_paused_dispatch():
    dispatch = create_in_progress_dispatch()
    dispatch.pause()

    match = 'Only a dispatch in progress can be paused.'
    with pytest.raises(ValueError, match=match):
        dispatch.pause()

    assert dispatch.status == DispatchStatus.PAUSED


def test_paused_dispatch_cannot_complete():
    dispatch = create_in_progress_dispatch()
    dispatch.pause()

    match = 'Only a dispatch in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete()

    assert dispatch.status == DispatchStatus.PAUSED


def test_paused_dispatch_can_be_cancelled():
    dispatch = create_in_progress_dispatch()
    dispatch.pause()

    dispatch.cancel()

    assert dispatch.status == DispatchStatus.CANCELLED


def test_paused_dispatch_can_add_task():
    dispatch = create_in_progress_dispatch()
    dispatch.pause()
    task = Task(1, Instruction.FETCH_CHASSIS, uuid4())

    dispatch.add_task(task)

    assert dispatch.status == DispatchStatus.PAUSED


def test_paused_dispatch_cannot_remove_a_task():
    dispatch = create_in_progress_dispatch()
    dispatch.pause()

    match = 'Only a draft dispatch can remove a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_task(4)

    assert len(dispatch.plan) == 4


def test_paused_dispatch_can_set_appointment_on_third_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.pause()
    appt = Appointment(AppointmentType.TIME_WINDOW, date(2025, 1, 1), time(12), time(16))

    dispatch.set_appointment(3, appt)

    assert dispatch.get_task(3).appointment


def test_paused_dispatch_cannot_start_a_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.pause()

    match = 'Only a dispatch in progress can start a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.start_task(3)

    assert dispatch.get_task(3).status == TaskStatus.NOT_STARTED


def test_paused_dispatch_cannot_add_a_task_():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.pause()

    match = 'Only a dispatch in progress can start a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.start_task(3)

    assert dispatch.get_task(3).status == TaskStatus.NOT_STARTED


def test_paused_dispatch_cannot_mark_a_task_stopoff():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.complete_task(1)
    dispatch.start_task(2)
    dispatch.complete_task(2)
    dispatch.pause()

    match = 'Only a dispatch in progress can mark a task as stopoff.'
    with pytest.raises(ValueError, match=match):
        dispatch.mark_stopoff(3)

    assert dispatch.get_task(3).status == TaskStatus.NOT_STARTED


# ---------------------------------------- TESTING COMPLETED DISPATCH ----------------------------------------


def test_completed_dispatch_cannot_complete_again():
    dispatch = create_completed_dispatch()

    match = 'Only a dispatch in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete()


def test_completed_dispatch_cannot_be_cancelled():
    dispatch = create_completed_dispatch()

    match = 'A completed dispatch cannot be cancelled.'
    with pytest.raises(ValueError, match=match):
        dispatch.cancel()

    assert dispatch.status == DispatchStatus.COMPLETED


def test_completed_dispatch_cannot_add_a_task():
    dispatch = create_completed_dispatch()

    match = 'Completed dispatches cannot add tasks.'
    with pytest.raises(ValueError, match=match):
        dispatch.add_task(Task(1, Instruction.FETCH_CHASSIS, uuid4()))

    assert len(dispatch.plan) == 4


def test_completed_dispatch_cannot_remove_a_task():
    dispatch = create_completed_dispatch()

    match = 'Only a draft dispatch can remove a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_task(1)

    assert len(dispatch.plan) == 4


def test_completed_dispatch_cannot_revert_a_task():
    dispatch = create_completed_dispatch()

    match = 'Only a dispatch in progress can revert a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.revert_task(4)

    assert dispatch.get_task(4).status == TaskStatus.COMPLETED


def test_completed_dispatch_cannot_set_an_appointment():
    dispatch = create_completed_dispatch()

    match = 'A completed dispatch cannot set an appointment.'
    with pytest.raises(ValueError, match=match):
        dispatch.set_appointment(3, Appointment(AppointmentType.TIME_WINDOW, date(1, 1, 25), time(12), time(16)))

    assert not dispatch.get_task(3).appointment


def test_completed_dispatch_cannot_remove_an_appointment():
    dispatch = create_completed_dispatch()

    match = 'A completed dispatch cannot remove an appointment.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_appointment(2)

    assert dispatch.get_task(2).appointment


# ---------------------------------------- TESTING CANCELLED DISPATCH ----------------------------------------


def test_cancelled_dispatch_cannot_cancel_again():
    dispatch = create_in_progress_dispatch()
    dispatch.cancel()

    match = 'A cancelled dispatch cannot be cancelled.'
    with pytest.raises(ValueError, match=match):
        dispatch.cancel()


def test_cancelled_dispatch_cannot_be_completed():
    dispatch = create_in_progress_dispatch()
    dispatch.cancel()

    match = 'Only a dispatch in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        dispatch.complete()


def test_cancelled_dispatch_cannot_add_a_task():
    dispatch = create_in_progress_dispatch()
    dispatch.cancel()

    match = 'Cancelled dispatches cannot add tasks.'
    with pytest.raises(ValueError, match=match):
        dispatch.add_task(Task(1, Instruction.FETCH_CHASSIS, uuid4()))

    assert len(dispatch.plan) == 4


def test_cancelled_dispatch_cannot_remove_a_task():
    dispatch = create_in_progress_dispatch()
    dispatch.cancel()

    match = 'Only a draft dispatch can remove a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_task(1)

    assert len(dispatch.plan) == 4


def test_cancelled_dispatch_cannot_revert_a_task():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.cancel()

    match = 'Only a dispatch in progress can revert a task.'
    with pytest.raises(ValueError, match=match):
        dispatch.revert_task(1)

    assert dispatch.get_task(1).status == TaskStatus.IN_PROGRESS


def test_cancelled_dispatch_cannot_set_an_appointment():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.cancel()

    match = 'A cancelled dispatch cannot set an appointment.'
    with pytest.raises(ValueError, match=match):
        dispatch.set_appointment(3, Appointment(AppointmentType.TIME_WINDOW, date(1, 1, 25), time(12), time(16)))

    assert not dispatch.get_task(3).appointment

def test_cancelled_dispatch_cannot_remove_an_appointment():
    dispatch = create_in_progress_dispatch()
    dispatch.start_task(1)
    dispatch.cancel()

    match = 'A cancelled dispatch cannot remove an appointment.'
    with pytest.raises(ValueError, match=match):
        dispatch.remove_appointment(2)

    assert dispatch.get_task(2).appointment
