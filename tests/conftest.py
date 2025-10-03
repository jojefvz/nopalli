from datetime import date, time

import pytest

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Instruction
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.location.value_objects import Address
from src.domain.services import Dispatcher


@pytest.fixture
def test_dispatch():
    Dispatch()


@pytest.fixture(params=[
    Instruction.LIVE_LOAD,
    Instruction.LIVE_UNLOAD,
    Instruction.TERMINATE_EMPTY,
    Instruction.INGATE,
    Instruction.STREET_TURN,
    Instruction.DROP_EMPTY,
    Instruction.DROP_LOADED,
    ])
def invalid_first_instruction(request):
    return request.param


@pytest.fixture(params=[
    Instruction.LIVE_LOAD,
    Instruction.LIVE_UNLOAD,
    Instruction.TERMINATE_EMPTY,
    Instruction.INGATE,
    Instruction.DROP_EMPTY,
    Instruction.DROP_LOADED,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
    Instruction.PREPULL,
    Instruction.YARD_PULL,
    ])
def compatible_instruction(request):
    return request.param


@pytest.fixture(params=[
    Instruction.FETCH_CHASSIS,
    Instruction.TERMINATE_CHASSIS,
    Instruction.STREET_TURN,
    Instruction.BOBTAIL_TO,
    ])
def incompatible_instruction(request):
    return request.param


invalid_plans = [
    [Task(1, Instruction.DROP_LOADED), Task(2, Instruction.PICKUP_EMPTY), Task(3, Instruction.TERMINATE_EMPTY)],
    [Task(1, Instruction.BOBTAIL_TO), Task(2, Instruction.BOBTAIL_TO), Task(3, Instruction.PICKUP_EMPTY), Task(4, Instruction.TERMINATE_EMPTY)],
    [Task(1, Instruction.FETCH_CHASSIS), Task(2, Instruction.PICKUP_EMPTY), Task(3, Instruction.LIVE_LOAD), Task(4, Instruction.TERMINATE_EMPTY)],
    [Task(1, Instruction.FETCH_CHASSIS), Task(2, Instruction.PICKUP_EMPTY), Task(3, Instruction.LIVE_LOAD), Task(4, Instruction.STREET_TURN)],
    [Task(1, Instruction.FETCH_CHASSIS), Task(2, Instruction.PICKUP_LOADED), Task(3, Instruction.LIVE_UNLOAD)],
    [Task(1, Instruction.LIVE_UNLOAD), Task(2, Instruction.DROP_EMPTY), Task(3, Instruction.BOBTAIL_TO)],
    [Task(1, Instruction.FETCH_CHASSIS), Task(2, Instruction.TERMINATE_CHASSIS)],
    [Task(1, Instruction.PICKUP_EMPTY), Task(2, Instruction.TERMINATE_CHASSIS)],
    [Task(1, Instruction.FETCH_CHASSIS), Task(2, Instruction.FETCH_CHASSIS), Task(3, Instruction.PICKUP_LOADED), Task(4, Instruction.LIVE_UNLOAD), Task(5, Instruction.TERMINATE_EMPTY),],
]
@pytest.fixture(params=invalid_plans)
def invalid_plan(request):
    return request.param


def create_two_container_dispatch(plan) -> Dispatch:
    """
    Creates a dispatch with two containers, an assigned driver, 
    an appointment set.
    """
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456', 'UMXU123456']
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    return dispatch


first_invalid_plan = [
    Task(1, Instruction.BOBTAIL_TO),
    Task(2, Instruction.LIVE_UNLOAD),
    Task(3, Instruction.DROP_EMPTY),
    Task(4, Instruction.PICKUP_LOADED),
    Task(5, Instruction.INGATE),
]

dispatch_1 = create_two_container_dispatch(first_invalid_plan)
Dispatcher.assign_container_to_tasks(dispatch_1, 'CMAU123456', [2, 3])
Dispatcher.assign_container_to_tasks(dispatch_1, 'UMXU123456', [4, 5])


second_invalid_plan = [
    Task(1, Instruction.BOBTAIL_TO),
    Task(2, Instruction.PICKUP_EMPTY),
    Task(3, Instruction.LIVE_UNLOAD),
    Task(4, Instruction.DROP_EMPTY),
    Task(5, Instruction.PICKUP_LOADED),
    Task(6, Instruction.STREET_TURN),
    Task(7, Instruction.TERMINATE_CHASSIS),
]

dispatch_2 = create_two_container_dispatch(second_invalid_plan)
Dispatcher.assign_container_to_tasks(dispatch_2, 'CMAU123456', [2, 3, 4])
Dispatcher.assign_container_to_tasks(dispatch_2, 'UMXU123456', [5, 6])


third_invalid_plan = [
    Task(1, Instruction.FETCH_CHASSIS),
    Task(2, Instruction.PICKUP_EMPTY),
    Task(3, Instruction.LIVE_LOAD),
    Task(4, Instruction.DROP_EMPTY),
    Task(5, Instruction.PICKUP_LOADED),
    Task(6, Instruction.INGATE),
    Task(7, Instruction.TERMINATE_CHASSIS),
]

dispatch_3 = create_two_container_dispatch(second_invalid_plan)
Dispatcher.assign_container_to_tasks(dispatch_3, 'CMAU123456', [2, 3, 4])
Dispatcher.assign_container_to_tasks(dispatch_3, 'UMXU123456', [5, 6])


invalid_two_container_plans = [
    dispatch_1,
    dispatch_2,
    dispatch_3,
]
@pytest.fixture(params=invalid_two_container_plans)
def invalid_two_container_plan(request):
    return request.param


def create_two_container_dispatch() -> Dispatch:
    """
    Creates a dispatch with two containers, containers assigned to tasks, an assigned driver, 
    an appointment set.
    """
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
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)
    Dispatcher.assign_container_to_tasks(dispatch, 'CMAU123456', [1, 2, 3])
    Dispatcher.assign_container_to_tasks(dispatch, 'CMAU123456', [4, 5])

    return dispatch


def create_dispatch(plan) -> Dispatch:
    """
    Creates a dispatch with one container, an assigned driver, 
    an appointment set, and an invalid plan.
    """
    broker = Broker("Cornerstone", Address('First St.', 'Chicago', 'IL', 00000))
    containers = ['CMAU123456']
    dispatch = Dispatcher.create_dispatch(broker.id, containers, plan)
    dispatch.set_appointment(2, Appointment(AppointmentType.EXACT_TIME, date(2025, 1, 1), time(9)))
    driver = Driver('John')
    Dispatcher.assign_driver(dispatch, driver)

    return dispatch


dispatch_1 = create_two_container_dispatch()
dispatch_2 = create_dispatch(
    [
        Task(1, Instruction.FETCH_CHASSIS),
        Task(2, Instruction.PICKUP_EMPTY),
        Task(3, Instruction.LIVE_LOAD),
        Task(4, Instruction.INGATE),
        Task(5, Instruction.TERMINATE_CHASSIS)
    ]
)
dispatch_3 = create_dispatch(
    [
        Task(1, Instruction.FETCH_CHASSIS),
        Task(2, Instruction.PICKUP_LOADED),
        Task(3, Instruction.LIVE_UNLOAD),
        Task(4, Instruction.TERMINATE_EMPTY),
    ]
)

ready_draft_dispatches = [
    dispatch_1,
    dispatch_2,
    dispatch_3,
]
@pytest.fixture(params=ready_draft_dispatches)
def ready_draft_dispatch(request):
    return request.param