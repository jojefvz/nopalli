from datetime import date, time

import pytest

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Container, Instruction
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.location.aggregate import Location
from src.domain.aggregates.location.value_objects import Address


@pytest.fixture()
def fake_location():
    return Location('BNSF LPC', Address('1234 Red St.', 'Elwood', 'Illinois', 11111))

@pytest.fixture()
def two_locations():
    return (
        Location('BNSF LPC', Address('1234 Red St.', 'Elwood', 'Illinois', 11111)),
        Location('LIPPERT ELKHART', Address('1234 Green St.', 'Elkhart', 'Indiana', 22222)),
    )

@pytest.fixture()
def three_locations():
    return (
        Location('BNSF LPC', Address('1234 Red St.', 'Elwood', 'Illinois', 11111)),
        Location('LIPPERT ELKHART', Address('1234 Green St.', 'Elkhart', 'Indiana', 22222)),
        Location('UP G4', Address('1234 Yellow St.', 'Elwood', 'Illinois', 33333))
    )

@pytest.fixture()
def fake_broker():
    return Broker('Cornerstone', Address('1234 Apple St.', 'Chicago', 'Illinois', 11111))

@pytest.fixture()
def fake_container1():
    return Container('CMAU123456')

@pytest.fixture()
def fake_container2():
    return Container('MATU123456')

@pytest.fixture()
def fake_task(fake_location, fake_container1):
    return Task(1, Instruction.PICKUP_EMPTY, fake_location.id, None, fake_container1.number)

@pytest.fixture()
def incomplete_draft_dispatch(two_locations, fake_broker, fake_container1):
    loc1, loc2 = two_locations    

    task_1 = Task(1, Instruction.PICKUP_EMPTY, loc1.id, None, fake_container1.number)
    task_2 = Task(2, Instruction.LIVE_LOAD, loc2.id, None, fake_container1.number)

    return Dispatch(fake_broker.id, None, [fake_container1], tasks=[task_1, task_2])

@pytest.fixture()
def ready_draft_dispatch(three_locations, fake_broker, fake_container1):
    loc1, loc2, loc3 = three_locations    

    task1 = Task(1, Instruction.PICKUP_EMPTY, loc1.id, None, fake_container1.number)
    task2 = Task(2, Instruction.LIVE_LOAD, loc2.id, None, fake_container1.number)
    task2.set_appointment(Appointment(AppointmentType.EXACT_TIME, date(2026, 1, 1), time(9), None))
    task3 = Task(3, Instruction.INGATE, loc3.id, None, fake_container1.number)

    return Dispatch(fake_broker.id, None, [fake_container1], tasks=[task1, task2, task3])

@pytest.fixture()
def fake_driver():
    return Driver('John')


@pytest.fixture(params=[
    Instruction.LIVE_LOAD,
    Instruction.LIVE_UNLOAD,
    Instruction.TERMINATE,
    Instruction.INGATE,
    Instruction.STREET_TURN,
    Instruction.DROP_EMPTY,
    Instruction.DROP_LOADED,
    ])
def faulty_instruction(request):
    return request.param