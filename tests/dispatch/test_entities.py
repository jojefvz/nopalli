from datetime import date, datetime, time
import time as clock
from uuid import uuid4

import pytest

from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Instruction, TaskStatus


def create_dispatch_ready_task() -> Task:
    return Task(1, Instruction.PICKUP_EMPTY, uuid4(),)


def create_completed_task() -> Task:
    task = create_dispatch_ready_task()
    task.start()
    driver_ref = uuid4()
    task.complete(driver_ref)
    return task


def create_stopoff_task() -> Task:
    task = create_dispatch_ready_task()
    driver_ref = uuid4()
    task.stopoff(driver_ref)
    return task


# ---------- TEST TASK INITIALIZATION --------------


def test_creating_minimal_task():
    priority = 1
    instruction = Instruction.PICKUP_EMPTY

    task = Task(priority, instruction)

    assert task.id
    assert task.priority
    assert task.instruction == Instruction.PICKUP_EMPTY
    assert isinstance(task.location_ref, str)
    assert task.appointment is None
    assert task.container is None


def test_creating_task_with_appointment():
    appt = Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9))

    task = Task(1, Instruction.PICKUP_EMPTY, appt=appt)

    assert task.id
    assert task.priority
    assert task.instruction == Instruction.PICKUP_EMPTY
    assert task.appointment


def test_creating_task_with_location_and_appt():
    loc_ref = uuid4()
    appt = Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9))

    task = Task(1, Instruction.PICKUP_EMPTY, loc_ref, appt)

    assert task.id
    assert task.priority
    assert task.instruction == Instruction.PICKUP_EMPTY
    assert task.location_ref
    assert task.appointment


# ---------------------------------------- TESTING TASK WHEN NOT STARTED AND DISPATCH IN PROGRESS --------------------------------------------


def test_starting_task():
    task = create_dispatch_ready_task()

    task.start()

    assert task.status == TaskStatus.IN_PROGRESS
    assert task._check_in_datetime


def test_starting_task_without_location():
    task = Task(1, Instruction.PICKUP_EMPTY)

    match = 'Cannot start a task without a location set.'
    with pytest.raises(ValueError, match=match):
        task.start()

    assert task.status == TaskStatus.NOT_STARTED
    assert isinstance(task.location_ref, str)
    assert not task._check_in_datetime


def test_completing_task_not_started():
    task = create_dispatch_ready_task()
    driver_ref = uuid4()

    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        task.complete(driver_ref)

    assert task.status == TaskStatus.NOT_STARTED


def test_not_started_task_cannot_revert_status():
    task = create_dispatch_ready_task()

    match = 'A task not started cannot revert status.'
    with pytest.raises(ValueError, match=match):
        task.revert_status()

    assert task.status == TaskStatus.NOT_STARTED


def test_marking_not_started_task_as_stopoff():
    task = create_dispatch_ready_task()
    driver_ref = uuid4()

    task.stopoff(driver_ref)

    assert task.status == TaskStatus.STOP_OFF
    assert task.completed_by
    assert task._check_out_datetime


def test_setting_appointment_when_task_not_started():
    task = create_dispatch_ready_task()
    appt = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)
    
    task.set_appointment(appt)

    assert task.appointment


def test_removing_existing_appointment_when_task_not_started():
    task = create_dispatch_ready_task()
    appt = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)
    task.set_appointment(appt)

    task.remove_appointment()

    assert task.appointment is None


# ---------------------------------------- TESTING TASK IN PROGRESS --------------------------------------------


def test_starting_task_in_progress():
    task = create_dispatch_ready_task()
    task.start()

    match = 'Only tasks not started can be started.'
    with pytest.raises(ValueError, match=match):
        task.start()

    assert task.status == TaskStatus.IN_PROGRESS


def test_completing_task_in_progress():
    task = create_dispatch_ready_task()
    task.start()
    driver_id = uuid4()

    task.complete(driver_id)

    assert task.status == TaskStatus.COMPLETED
    assert task.completed_by
    assert task._check_out_datetime


def test_task_in_progress_reverting_to_not_started():
    task = create_dispatch_ready_task()
    task.start()

    task.revert_status()

    assert task.status == TaskStatus.NOT_STARTED
    assert task._check_in_datetime is None


def test_marking_in_progress_task_as_stopoff():
    task = create_dispatch_ready_task()
    task.start()

    task.stopoff(uuid4())

    assert task.status == TaskStatus.STOP_OFF
    assert task._check_out_datetime
    assert task.completed_by


def test_setting_appointment_on_task_in_progress():
    task = create_dispatch_ready_task()
    task.start()
    appt = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)

    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        task.set_appointment(appt)

    assert task.appointment is None


def test_removing_appointment_when_task_in_progress():
    task = create_dispatch_ready_task()
    task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    task.start()

    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        task.remove_appointment()

    assert task.appointment


# ---------------------------------------- TESTING COMPLETED TASK --------------------------------------------


def test_completing_already_completed_task():
    task = create_completed_task()

    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        new_checkout_time = datetime.now()
        driver_ref = uuid4()
        task.complete(driver_ref)

    assert task._check_out_datetime < new_checkout_time


def test_completed_task_reverting_to_in_progress():
    task = create_completed_task()

    task.revert_status()

    assert task.status == TaskStatus.IN_PROGRESS
    assert task._check_in_datetime
    assert task._check_out_datetime is None
    assert task.completed_by is None


def test_completed_task_reverting_to_not_started_when_called_twice():
    task = create_completed_task()
    task.revert_status()
    
    task.revert_status()

    assert task.status == TaskStatus.NOT_STARTED
    assert task._check_in_datetime is None
    assert task._check_out_datetime is None
    assert task.completed_by is None


def test_complete_updates_total_time_spent_completing():
    task = create_dispatch_ready_task()
    task.start()
    clock.sleep(0.5)
    driver_ref = uuid4()

    task.complete(driver_ref)

    assert task.time_spent_completing_task


def test_setting_appointment_when_completed():
    task = create_completed_task()

    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert task.appointment is None


def test_removing_appointment_when_task_completed():
    task = create_dispatch_ready_task()
    task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    task.start()
    driver_ref = uuid4()
    task.complete(driver_ref)

    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        task.remove_appointment()

    assert task.appointment


# ---------------------------------------- TESTING TASK MARKED AS STOPOFF ----------------------------------------


def test_starting_stopoff_task():
    task = create_stopoff_task()

    match = 'Only tasks not started can be started.'
    with pytest.raises(ValueError, match=match):
        task.start()

    assert task.status == TaskStatus.STOP_OFF


def test_completing_stopoff_task():
    task = create_stopoff_task()

    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        driver_ref = uuid4()
        task.complete(driver_ref)

    assert task.status == TaskStatus.STOP_OFF


def test_marking_stopoff_on_stopoff_task():
    task = create_stopoff_task()

    match = 'Only tasks not started or in progress can be marked stopoff.'
    with pytest.raises(ValueError, match=match):
        driver_ref = uuid4()
        task.stopoff(driver_ref)

    assert task.status == TaskStatus.STOP_OFF


def test_reverting_stopoff_to_not_started():
    task = create_stopoff_task()

    task.revert_status()
 
    assert task.status == TaskStatus.NOT_STARTED
    assert task.completed_by is None
    assert task._check_in_datetime is None
    assert task._check_out_datetime is None


def test_setting_appointment_on_stopoff_task():
    task = create_stopoff_task()

    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert task.appointment is None


def test_removing_appointment_when_stopoff():
    task = create_dispatch_ready_task()
    appt = Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None)
    task.set_appointment(appt)
    driver_ref = uuid4()
    task.stopoff(driver_ref)
    
    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        task.remove_appointment()

    assert task.appointment


# ----------- TESTING MARKING STOP OFF ON DIFFERENT INSTRUCTION TYPES ---------------


def test_marking_stopoff_on_task_with_incompatible_instruction(compatible_instruction):
    task = create_dispatch_ready_task()
    task.instruction = compatible_instruction
    driver_ref = uuid4()

    task.stopoff(driver_ref)

    assert task.status == TaskStatus.STOP_OFF


def test_marking_stopoff_on_task_with_compatible_instruction(incompatible_instruction):
    task = create_dispatch_ready_task()
    task.instruction = incompatible_instruction
    driver_ref = uuid4()

    match = 'Task instruction is incompatible with being marked stop off.'
    with pytest.raises(ValueError, match=match):
        task.stopoff(driver_ref)

    assert task.status != TaskStatus.STOP_OFF


# ----------- TESTING TOTAL TIME PROPERTY ---------------


def test_total_time_spent_completing_task_when_task_not_started():
    task = create_dispatch_ready_task()

    with pytest.raises(AttributeError) as exc_info:
        task.time_spent_completing_task

    assert "Task has not been completed." in str(exc_info.value)


def test_total_time_spent_completing_task_when_task_in_progress():
    task = create_dispatch_ready_task()

    with pytest.raises(AttributeError) as exc_info:
        task.start()
        task.time_spent_completing_task

    assert "Task has not been completed." in str(exc_info.value)


