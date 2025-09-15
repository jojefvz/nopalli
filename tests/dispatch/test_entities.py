from datetime import date, time
import time as clock
from uuid import UUID, uuid4

import pytest

from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Instruction, TaskStatus


# ---------- TESTING INITIALIZATION --------------
def test_task_init():
    task = Task(
        1,
        Instruction.PICKUP_EMPTY,
        uuid4(),
        None,
        'CMAU123456'
        )

    assert task.id
    assert task.priority
    assert task.instruction == Instruction.PICKUP_EMPTY
    assert isinstance(task.location_ref, UUID)
    assert task.appointment is None
    assert task.container_num

# ---------------------------------------- TESTING TASK WHEN NOT STARTED --------------------------------------------
def test_starting_task(fake_task):
    fake_task.start()

    assert fake_task.status == TaskStatus.IN_PROGRESS

def test_completing_task_not_started(fake_task):
    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        fake_task.complete(uuid4())

    assert fake_task.status == TaskStatus.NOT_STARTED

def test_not_started_task_cannot_revert_status(fake_task):
    match = 'A task not started cannot revert status.'
    with pytest.raises(ValueError, match=match):
        fake_task.revert_status()

    assert fake_task.status == TaskStatus.NOT_STARTED

def test_marking_task_as_stopoff(fake_task):
    fake_task.stopoff(uuid4())

    assert fake_task.status == TaskStatus.STOP_OFF
    assert fake_task._check_out_datetime

def test_marking_task_as_yardpull(fake_task):
    fake_task.yardpull(uuid4())

    assert fake_task.status == TaskStatus.YARD_PULL
    assert fake_task._check_out_datetime

def test_setting_appointment_when_not_started(fake_task):
    fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert fake_task.status == TaskStatus.NOT_STARTED
    assert fake_task.appointment
    assert fake_task.appointment.appointment_type == AppointmentType.EXACT_TIME


# ---------------------------------------- TESTING TASK WHEN IN PROGRESS --------------------------------------------
def test_starting_task_in_progress(fake_task):
    match = 'Only tasks not started can be started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        fake_task.start()

    assert fake_task.status == TaskStatus.IN_PROGRESS

def test_completing_task_in_progress(fake_task):
    fake_task.start()
    driver_id = uuid4()
    fake_task.complete(driver_id)

    assert fake_task.status == TaskStatus.COMPLETED
    assert fake_task.completed_by == driver_id

def test_task_in_progress_reverting_to_not_started(fake_task):
    fake_task.start()
    fake_task.revert_status()

    assert fake_task.status == TaskStatus.NOT_STARTED
    assert fake_task._check_in_datetime is None

def test_start_updates_checkin_datetime(fake_task):
    fake_task.start()

    assert fake_task._check_in_datetime

def test_marking_in_progress_task_as_stopoff(fake_task):
    fake_task.stopoff(uuid4())

    assert fake_task.status == TaskStatus.STOP_OFF
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_marking_in_progress_task_as_yardpull(fake_task):
    fake_task.yardpull(uuid4())

    assert fake_task.status == TaskStatus.YARD_PULL
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_setting_appointment_on_task_in_progress(fake_task):
    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert fake_task.appointment is None

def test_removing_appointment_when_task_in_progress(fake_task):
    fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        fake_task.remove_appointment()

    assert fake_task.appointment

# ---------------------------------------- TESTING TASK WHEN COMPLETED --------------------------------------------
def test_starting_completed_task(fake_task):
    match = 'Only tasks not started can be started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        fake_task.complete(uuid4())
        fake_task.start()

    assert fake_task.status == TaskStatus.COMPLETED
    assert fake_task._check_in_datetime
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_completing_already_completed_task(fake_task):
    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        first_driver_id = uuid4()
        second_driver_id = uuid4()
        fake_task.complete(first_driver_id)
        fake_task.complete(second_driver_id)

    assert fake_task.status == TaskStatus.COMPLETED
    assert fake_task.completed_by == first_driver_id

def test_completed_task_reverting_to_in_progress(fake_task):
    fake_task.start()
    fake_task.complete(uuid4())
    fake_task.revert_status()

    assert fake_task.status == TaskStatus.IN_PROGRESS
    assert fake_task._check_in_datetime
    assert fake_task._check_out_datetime is None
    assert fake_task.completed_by is None

def test_completed_task_reverting_to_not_started_when_called_twice(fake_task):
    fake_task.start()
    fake_task.complete(uuid4())
    fake_task.revert_status()
    fake_task.revert_status()

    assert fake_task.status == TaskStatus.NOT_STARTED
    assert fake_task._check_in_datetime is None
    assert fake_task._check_out_datetime is None
    assert fake_task.completed_by is None

def test_complete_updates_checkout_datetime(fake_task):
    fake_task.start()
    fake_task.complete(uuid4())

    assert fake_task._check_out_datetime

def test_complete_updates_total_time_spent_completing(fake_task):
    fake_task.start()
    clock.sleep(0.5)
    fake_task.complete(uuid4())

    assert fake_task.time_spent_completing_task

def test_marking_stopoff_on_completed_task(fake_task):
    fake_task.start()
    fake_task.complete(uuid4())

    match = 'Only tasks not started or in progress can be marked stopoff.'
    with pytest.raises(ValueError, match=match):
        fake_task.stopoff(uuid4)

    assert fake_task.status == TaskStatus.COMPLETED

def test_yardpulling_completed_task(fake_task):
    fake_task.start()
    fake_task.complete(uuid4())

    match = 'Only tasks not started or in progress can be marked yardpull.'
    with pytest.raises(ValueError, match=match):
        fake_task.yardpull(uuid4)

    assert fake_task.status == TaskStatus.COMPLETED

def test_setting_appointment_when_completed(fake_task):
    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        fake_task.complete(uuid4())
        fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert fake_task.appointment is None

def test_removing_appointment_when_task_completed(fake_task):
    fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()
        fake_task.complete(uuid4())
        fake_task.remove_appointment()

    assert fake_task.appointment

# ---------------------------------------- TESTING TASK MARKED AS STOPOFF ----------------------------------------
def test_starting_stopoff_task(fake_task):
    fake_task.stopoff(uuid4())

    match = 'Only tasks not started can be started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()

    assert fake_task.status == TaskStatus.STOP_OFF

def test_completing_stopoff_task(fake_task):
    fake_task.stopoff(uuid4())

    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        fake_task.complete(uuid4())

    assert fake_task.status == TaskStatus.STOP_OFF

def test_yardpulling_stopoff_task(fake_task):
    fake_task.stopoff(uuid4())

    match = 'Only tasks not started or in progress can be marked yardpull.'
    with pytest.raises(ValueError, match=match):
        fake_task.yardpull(uuid4())

    assert fake_task.status == TaskStatus.STOP_OFF

def test_marking_stopoff_on_stopoff_task(fake_task):
    fake_task.stopoff(uuid4())

    match = 'Only tasks not started or in progress can be marked stopoff.'
    with pytest.raises(ValueError, match=match):
        fake_task.stopoff(uuid4())

    assert fake_task.status == TaskStatus.STOP_OFF

def test_reverting_stopoff_to_not_started(fake_task):
    fake_task.stopoff(uuid4())
    fake_task.revert_status()
 
    assert fake_task.status == TaskStatus.NOT_STARTED
    assert fake_task.completed_by is None

def test_setting_appointment_on_stopoff_task(fake_task):
    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.stopoff(uuid4())
        fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert fake_task.appointment is None

def test_removing_appointment_when_stopoff(fake_task):
    fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    
    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.stopoff(uuid4())
        fake_task.remove_appointment()

    assert fake_task.appointment

# ---------------------------------------- TESTING TASK MARKED AS YARD PULL ----------------------------------------
def test_starting_yardpull_task(fake_task):
    fake_task.yardpull(uuid4())

    match = 'Only tasks not started can be started.'
    with pytest.raises(ValueError, match=match):
        fake_task.start()

    assert fake_task.status == TaskStatus.YARD_PULL
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_completing_yardpull_task(fake_task):
    fake_task.yardpull(uuid4())

    match = 'Only tasks in progress can be completed.'
    with pytest.raises(ValueError, match=match):
        fake_task.complete(uuid4())

    assert fake_task.status == TaskStatus.YARD_PULL
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_marking_stopoff_on_yardpull_task(fake_task):
    fake_task.yardpull(uuid4())

    match = 'Only tasks not started or in progress can be marked stopoff.'
    with pytest.raises(ValueError, match=match):
        fake_task.stopoff(uuid4())

    assert fake_task.status == TaskStatus.YARD_PULL
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_yardpulling_yardpull_task(fake_task):
    fake_task.yardpull(uuid4())

    match = 'Only tasks not started or in progress can be marked yardpull.'
    with pytest.raises(ValueError, match=match):
        fake_task.yardpull(uuid4())

    assert fake_task.status == TaskStatus.YARD_PULL
    assert fake_task._check_out_datetime
    assert fake_task.completed_by

def test_reverting_yardpull_to_not_started(fake_task):
    fake_task.yardpull(uuid4())
    fake_task.revert_status()
 
    assert fake_task.status == TaskStatus.NOT_STARTED
    assert fake_task._check_in_datetime is None
    assert fake_task._check_out_datetime is None
    assert fake_task.completed_by is None

def test_setting_appointment_on_yardpull_task(fake_task):
    match = 'Can only set an appointment on tasks not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.yardpull(uuid4())
        fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    assert fake_task.appointment is None

def test_removing_appointment_when_yardpull(fake_task):
    fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    
    match = 'Can only remove appointment when task not started.'
    with pytest.raises(ValueError, match=match):
        fake_task.yardpull(uuid4())
        fake_task.remove_appointment()

    assert fake_task.appointment

# ---------------------------------------- TESTING SETTING APPOINTMENTS ----------------------------------------
def test_setting_appointment_with_a_past_date(fake_task):
    match = 'Cannot set an appointment with a past date.'
    with pytest.raises(ValueError, match=match):
        fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9), None))

    assert fake_task.appointment is None

def test_setting_appointment_with_start_time_later_than_end_time(fake_task):
    match = 'Cannot set a start time that is later than the end time.'
    with pytest.raises(ValueError, match=match):
        fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), time(6)))

    assert fake_task.appointment is None
    
def test_removing_appointment(fake_task):
    fake_task.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))

    fake_task.remove_appointment()

    assert fake_task.appointment is None

# ----------- TESTING TOTAL TIME PROPERTY ---------------
def test_total_time_spent_completing_task_when_task_not_started(fake_task):
    with pytest.raises(AttributeError):
        fake_task.time_spent_completing_task

def test_total_time_spent_completing_task_when_task_in_progress(fake_task):
    with pytest.raises(AttributeError):
        fake_task.start()
        fake_task.time_spent_completing_task


