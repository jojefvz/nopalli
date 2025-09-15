from datetime import date, time
from uuid import UUID, uuid4

import pytest

from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, DispatchStatus, Instruction, TaskStatus
from src.domain.aggregates.location.aggregate import Location
from src.domain.aggregates.location.value_objects import Address
from src.domain.services import Dispatcher


def test_dispatch_init(three_locations, fake_broker, fake_container1):
    loc1, loc2, loc3 = three_locations
    task1 = Task(1, Instruction.PICKUP_EMPTY, loc1.id, None, fake_container1.number)
    task2 = Task(2, Instruction.LIVE_LOAD, loc2.id, None, fake_container1.number)
    task3 = Task(3, Instruction.INGATE, loc3.id, None, fake_container1.number)

    dispatch = Dispatch(fake_broker.id, None, [fake_container1], tasks=[task1, task2, task3])
    
    assert dispatch.id
    assert dispatch.status == DispatchStatus.DRAFT
    assert isinstance(dispatch.broker_ref, UUID)
    assert dispatch.driver_ref is None
    assert dispatch.containers == [fake_container1]
    assert dispatch.tasks == [task1, task2, task3]
    

# ---------------------------------------- TESTING DISPATCH IN DRAFT STATUS ----------------------------------------
def test_draft_dispatch_can_add_task(incomplete_draft_dispatch, fake_container1):
    third_task = Task(3, Instruction.INGATE, uuid4(), None, fake_container1.number)

    incomplete_draft_dispatch.add_task(third_task)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 3
    assert incomplete_draft_dispatch.get_task(3) is third_task

def test_draft_dispatch_can_insert_task(incomplete_draft_dispatch, fake_container1):
    new_second_task = Task(2, Instruction.LIVE_LOAD, uuid4(), None, fake_container1.number)

    incomplete_draft_dispatch.add_task(new_second_task)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 3
    assert incomplete_draft_dispatch.get_task(2) is new_second_task
    assert incomplete_draft_dispatch.get_task(3).priority == 3

def test_draft_dispatch_cannot_add_a_ninth_task(incomplete_draft_dispatch, fake_container1):
    location = Location('Warehouse', Address('2345 West St.', 'Chicago', 'Illinois', 00000))
    def make_task(priority): 
        return Task(priority, Instruction.LIVE_LOAD, location.id, None, fake_container1.number)

    batch_of_tasks = [make_task(i) for i in range(3, 10)]

    match = 'Cannot have more than 8 tasks.'
    with pytest.raises(ValueError, match=match):
        for task in batch_of_tasks:
            incomplete_draft_dispatch.add_task(task)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 8
    assert incomplete_draft_dispatch.get_task(3).priority == 3
    assert incomplete_draft_dispatch.get_task(4).priority == 4
    assert incomplete_draft_dispatch.get_task(7).priority == 7
    assert incomplete_draft_dispatch.get_task(8).priority == 8

def test_draft_dispatch_can_remove_task(incomplete_draft_dispatch, fake_container1):
    task = Task(3, Instruction.DROP_EMPTY, uuid4(), None, fake_container1)
    incomplete_draft_dispatch.add_task(task)

    incomplete_draft_dispatch.remove_task(3)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 2
    assert incomplete_draft_dispatch.get_task(2).priority == 2

def test_draft_dispatch_cannot_remove_task_when_only_two_tasks_exist(incomplete_draft_dispatch):
    match = 'Cannot have less than two tasks.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch.remove_task(2)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 2

def test_draft_dispatch_can_remove_task_by_position(incomplete_draft_dispatch, fake_container1):
    task = Task(2, Instruction.LIVE_LOAD, uuid4(), None, fake_container1)
    incomplete_draft_dispatch.add_task(task)
    
    incomplete_draft_dispatch.remove_task(2)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 2
    assert incomplete_draft_dispatch.get_task(1).priority == 1
    assert incomplete_draft_dispatch.get_task(2).priority == 2

def test_draft_dispatch_cannot_remove_task_when_only_two_tasks_exist(incomplete_draft_dispatch):
    match = 'Cannot have less than two tasks.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch.remove_task(1)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert len(incomplete_draft_dispatch.tasks) == 2

def test_draft_dispatch_cannot_start_a_task(incomplete_draft_dispatch):
    match = 'Only a dispatch in progress can start a task.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch.start_task(1)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert incomplete_draft_dispatch.get_task(1).status == TaskStatus.NOT_STARTED

def test_draft_dispatch_cannot_complete_a_task(incomplete_draft_dispatch):
    match = 'Only a dispatch in progress can complete a task.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch.complete_task(1, uuid4())

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert incomplete_draft_dispatch.get_task(1).status == TaskStatus.NOT_STARTED

def test_draft_dispatch_cannot_revert_a_task(incomplete_draft_dispatch):
    match = 'Only a dispatch in progress can revert a task.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch.revert_task(1)

    assert incomplete_draft_dispatch.status == DispatchStatus.DRAFT
    assert incomplete_draft_dispatch.get_task(1).status == TaskStatus.NOT_STARTED

def test_draft_dispatch_reverting_to_draft(ready_draft_dispatch):
    match = 'Cannot revert a draft dispatch.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.revert_status()

    assert ready_draft_dispatch.status == DispatchStatus.DRAFT

def test_draft_dispatch_cannot_mark_a_stopoff(ready_draft_dispatch):
    match = 'Only a dispatch in progress can mark a task as stopoff.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.mark_stopoff(1, uuid4())

    assert ready_draft_dispatch.status == DispatchStatus.DRAFT

def test_draft_dispatch_cannot_mark_a_yardpull(ready_draft_dispatch):
    match = 'Only a dispatch in progress can mark a task as yardpull.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.mark_yardpull(1, uuid4())

    assert ready_draft_dispatch.status == DispatchStatus.DRAFT

def test_setting_an_appointment_to_draft(incomplete_draft_dispatch):
    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)

    incomplete_draft_dispatch.set_appointment(appointment, 2)

    assert incomplete_draft_dispatch.get_task(2).appointment == appointment

# --------- TESTING PLAN VERIFICATION ---------
def test_plan_verification_raises_for_missing_driver(incomplete_draft_dispatch):
    match = 'A driver has not been assigned to dispatch.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

    assert incomplete_draft_dispatch.driver_ref is None

def test_plan_verification_raises_for_missing_appointment(incomplete_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)

    match = 'An appointment has not been set on at least one task.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()
    
def test_plan_verification_raises_for_illogical_first_task(
        incomplete_draft_dispatch,
        fake_driver,
        faulty_instruction
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(1).instruction = faulty_instruction # parametrize test to run other faulty task instructions
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 9, 10), time(9), None))

    match = 'Only prepull, pickup empty, or pickup loaded can be the first task.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_plan_verification_raises_for_adjancent_tasks_with_same_instruction(
        incomplete_draft_dispatch,
        fake_driver
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 9, 10), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.PICKUP_EMPTY

    match = 'Only live load or live unload tasks can be repeated in sequence.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_illogical_instruction_following_bobtail_to(
        incomplete_draft_dispatch,
        fake_driver
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(1).instruction = Instruction.BOBTAIL_TO
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.DROP_EMPTY
        
    assert incomplete_draft_dispatch.get_task(1).instruction == Instruction.BOBTAIL_TO
    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.DROP_EMPTY
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_llogical_instruction_following_pickup_empty(
        incomplete_draft_dispatch,
        fake_driver
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.DROP_LOADED
        
    assert incomplete_draft_dispatch.get_task(1).instruction == Instruction.PICKUP_EMPTY
    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.DROP_LOADED
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_illogical_instruction_following_pickup_loaded(
        incomplete_draft_dispatch,
        fake_driver
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(1).instruction = Instruction.PICKUP_LOADED
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.DROP_EMPTY

    assert incomplete_draft_dispatch.get_task(1).instruction == Instruction.PICKUP_LOADED
    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.DROP_EMPTY
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_illogical_instruction_following_drop_empty(
        incomplete_draft_dispatch,
        fake_driver,
        fake_container1
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.DROP_EMPTY
    third_task = Task(3, Instruction.INGATE, uuid4(), None, fake_container1.number)
    incomplete_draft_dispatch.add_task(third_task)

    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.DROP_EMPTY
    assert incomplete_draft_dispatch.get_task(3).instruction == Instruction.INGATE
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_illogical_instruction_following_drop_loaded(
        incomplete_draft_dispatch,
        fake_driver,
        fake_container1
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(1).instruction = Instruction.PICKUP_LOADED
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.DROP_LOADED
    third_task = Task(3, Instruction.INGATE, uuid4(), None, fake_container1)
    incomplete_draft_dispatch.add_task(third_task)

    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.DROP_LOADED
    assert incomplete_draft_dispatch.get_task(3).instruction == Instruction.INGATE
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_illogical_instruction_following_live_unload(
        incomplete_draft_dispatch,
        fake_driver,
        fake_container1
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(1).instruction = Instruction.PICKUP_LOADED
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    incomplete_draft_dispatch.get_task(2).instruction = Instruction.LIVE_UNLOAD
    third_task = Task(3, Instruction.INGATE, uuid4(), None, fake_container1)
    incomplete_draft_dispatch.add_task(third_task)
        
    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.LIVE_UNLOAD
    assert incomplete_draft_dispatch.get_task(3).instruction == Instruction.INGATE
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

def test_illogical_instruction_following_live_load(
        incomplete_draft_dispatch,
        fake_driver,
        fake_container1
        ):
    Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)
    incomplete_draft_dispatch.get_task(2).set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    third_task = Task(3, Instruction.TERMINATE, uuid4(), None, fake_container1)
    incomplete_draft_dispatch.add_task(third_task)
        
    assert incomplete_draft_dispatch.get_task(2).instruction == Instruction.LIVE_LOAD
    assert incomplete_draft_dispatch.get_task(3).instruction == Instruction.TERMINATE
    assert incomplete_draft_dispatch._has_illogical_adjacent_instructions() == True
    
    match = 'Two adjacent tasks have illogical instructions.'
    with pytest.raises(ValueError, match=match):
        incomplete_draft_dispatch._verify_plan()

# ------------ TEST CHANGING DISPATCH TO IN PROGRESS STATUS ------------
def test_starting_a_draft_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start()

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS



# ---------------------------------------- TESTING DISPATCH IN PROGRESS ----------------------------------------
def test_dispatch_reverting_to_draft_when_first_task_not_started(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.revert_status()

    assert ready_draft_dispatch.status == DispatchStatus.DRAFT

def test_dispatch_reverting_to_draft_when_first_task_in_progress(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)

    match = 'Canot revert dispatch to draft when first task is in progress.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.revert_status()

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS

def test_dispatch_starting_first_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.IN_PROGRESS

def test_dispatch_completing_first_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.COMPLETED

def test_dispatch_reverting_first_started_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.revert_task(1)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.NOT_STARTED

def test_dispatch_reverting_first_completed_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)
    ready_draft_dispatch.revert_task(1)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.IN_PROGRESS

def test_dispatch_reverting_stopoff_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.mark_stopoff(1, fake_driver.id)
    ready_draft_dispatch.revert_task(1)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.NOT_STARTED

def test_dispatch_reverting_yardpull_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.mark_yardpull(1, fake_driver.id)
    ready_draft_dispatch.revert_task(1)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.NOT_STARTED

def test_dispatch_completing_all_tasks(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    ready_draft_dispatch.start_task(2)
    ready_draft_dispatch.complete_task(2, fake_driver.id)

    ready_draft_dispatch.start_task(3)
    ready_draft_dispatch.complete_task(3, fake_driver.id)

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert ready_draft_dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert ready_draft_dispatch.get_task(3).status == TaskStatus.COMPLETED

def test_setting_an_appointment_to_in_progress_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(11), None)

    ready_draft_dispatch.set_appointment(appointment, 2)

    assert ready_draft_dispatch.get_task(2).appointment == appointment

def test_setting_a_second_appointment_to_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)
    ready_draft_dispatch.start_task(2)
    ready_draft_dispatch.complete_task(2, fake_driver.id)

    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(12), time(16))
    ready_draft_dispatch.set_appointment(appointment, 3)

    assert ready_draft_dispatch.get_task(3).appointment == appointment

def test_removing_the_only_appointment_on_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    match = 'Cannot remove the only appointment on a dispatch that\'s in progress.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.remove_appointment(2)

    assert ready_draft_dispatch.get_task(2).appointment

def test_removing_the_second_existing_appointment_on_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(12), time(16))
    ready_draft_dispatch.set_appointment(appointment, 3)

    ready_draft_dispatch.remove_appointment(3)

    assert ready_draft_dispatch.get_task(3).appointment is None

def test_marking_first_task_a_stop_off(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    ready_draft_dispatch.start_task(1)

    ready_draft_dispatch.mark_stopoff(1, fake_driver.id)

    assert ready_draft_dispatch.get_task(1).status == TaskStatus.STOP_OFF

def test_marking_second_task_a_stop_off(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    ready_draft_dispatch.mark_stopoff(2, fake_driver.id)

    assert ready_draft_dispatch.get_task(2).status == TaskStatus.STOP_OFF

def test_marking_second_task_a_stop_off_and_adding_a_new_task_after(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)
    
    ready_draft_dispatch.mark_stopoff(2, fake_driver.id)

    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)
    third_task = Task(3, Instruction.LIVE_LOAD, uuid4(), appointment, 'CMAU123456')
    ready_draft_dispatch.add_task(third_task)

    assert ready_draft_dispatch.get_task(2).status == TaskStatus.STOP_OFF
    assert ready_draft_dispatch.get_task(3)
    assert ready_draft_dispatch.get_task(3).status == TaskStatus.NOT_STARTED

def test_marking_first_task_as_yardpull(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    ready_draft_dispatch.start_task(1)

    ready_draft_dispatch.mark_yardpull(1, fake_driver.id)

    assert ready_draft_dispatch.get_task(1).status == TaskStatus.YARD_PULL

def test_marking_second_task_as_yardpull(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    ready_draft_dispatch.mark_yardpull(2, fake_driver.id)

    assert ready_draft_dispatch.get_task(2).status == TaskStatus.YARD_PULL

def test_marking_second_task_as_yardpull_and_adding_a_new_task_after(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)
    
    ready_draft_dispatch.mark_yardpull(2, fake_driver.id)

    appointment = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)
    third_task = Task(3, Instruction.LIVE_LOAD, uuid4(), appointment, 'CMAU123456')
    ready_draft_dispatch.add_task(third_task)

    assert ready_draft_dispatch.get_task(2).status == TaskStatus.YARD_PULL
    assert ready_draft_dispatch.get_task(2)
    assert ready_draft_dispatch.get_task(3).status == TaskStatus.NOT_STARTED

def test_adding_a_task_in_a_position_before_a_completed_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    new_first_task = Task(1, Instruction.LIVE_LOAD, uuid4(), None, 'CMAU123456')
    
    match = 'Cannot add a new task before a completed task.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.add_task(new_first_task)

    assert ready_draft_dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert len(ready_draft_dispatch.tasks) == 3

def test_removing_a_completed_task(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)
    
    match = 'Cannot remove a completed task.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.remove_task(1)

    assert ready_draft_dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert len(ready_draft_dispatch.tasks) == 3

def test_dispatch_can_complete_when_all_tasks_are_completed(ready_draft_dispatch,fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    ready_draft_dispatch.start_task(2)
    ready_draft_dispatch.complete_task(2, fake_driver.id)

    ready_draft_dispatch.start_task(3)
    ready_draft_dispatch.complete_task(3, fake_driver.id)

    ready_draft_dispatch.complete()

    assert ready_draft_dispatch.status == DispatchStatus.COMPLETED
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert ready_draft_dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert ready_draft_dispatch.get_task(3).status == TaskStatus.COMPLETED

def test_dispatch_cannot_complete_when_last_task_not_completed(ready_draft_dispatch,fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    ready_draft_dispatch.start_task(1)
    ready_draft_dispatch.complete_task(1, fake_driver.id)

    ready_draft_dispatch.start_task(2)
    ready_draft_dispatch.complete_task(2, fake_driver.id)

    match = 'All tasks must be completed before dispatch can be completed.'
    with pytest.raises(ValueError, match=match):
        ready_draft_dispatch.complete()

    assert ready_draft_dispatch.status == DispatchStatus.IN_PROGRESS
    assert ready_draft_dispatch.get_task(1).status == TaskStatus.COMPLETED
    assert ready_draft_dispatch.get_task(2).status == TaskStatus.COMPLETED
    assert ready_draft_dispatch.get_task(3).status == TaskStatus.NOT_STARTED
