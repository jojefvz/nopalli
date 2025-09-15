import pytest

from src.domain.aggregates.dispatch.value_objects import DispatchStatus, TaskStatus
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.services import Dispatcher
from tests.conftest import ready_draft_dispatch


# ---------------------------------------- TEST DISPATCH UNDER DRAFT STATUS ----------------------------------------
def test_assigning_available_driver_to_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)

    assert ready_draft_dispatch.driver_ref == fake_driver.id
    assert fake_driver.status == DriverStatus.AVAILABLE

def test_assigning_unavailable_driver_to_dispatch(ready_draft_dispatch, fake_driver):
    fake_driver.sit_out()

    match = 'Only available and operating drivers can be assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)

    assert fake_driver.status == DriverStatus.UNAVAILABLE
    assert ready_draft_dispatch.driver_ref is None

def test_assigning_deactivated_driver_to_dispatch(ready_draft_dispatch, fake_driver):
    fake_driver.deactivate()

    match = 'Only available and operating drivers can be assigned.'
    with pytest.raises(ValueError, match=match):
        Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)

    assert fake_driver.status == DriverStatus.DEACTIVATED
    assert ready_draft_dispatch.driver_ref is None

def test_removing_available_driver_from_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)

    Dispatcher.remove_driver(ready_draft_dispatch)

    assert ready_draft_dispatch.driver_ref is None
    assert fake_driver.status == DriverStatus.AVAILABLE


# ---------------------------------------- TEST STARTING DISPATCH ----------------------------------------
def test_starting_dispatch(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)

    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

    assert ready_draft_dispatch.status == DispatchStatus.STARTED
    assert fake_driver.status == DriverStatus.OPERATING

def test_reverting_dispatch_status(ready_draft_dispatch, fake_driver):
    Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
    
    Dispatcher.revert_dispatch_status(ready_draft_dispatch, fake_driver)

    assert ready_draft_dispatch.status == DispatchStatus.DRAFT
    assert fake_driver.status == DriverStatus.AVAILABLE

# ---------------------------------------- TEST DISPATCH UNDER STARTED STATUS ----------------------------------------




# def test_assigning_operating_driver_to_different_draft_dispatch(incomplete_draft_dispatch, ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
#     Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     Dispatcher.assign_driver(incomplete_draft_dispatch, fake_driver)

#     assert incomplete_draft_dispatch.driver_ref == ready_draft_dispatch.driver_ref
#     assert fake_driver.status == DriverStatus.OPERATING
#     assert ready_draft_dispatch.status == DispatchStatus.STARTED


# def test_starting_dispatch(ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
#     Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     assert ready_draft_dispatch.status == DispatchStatus.STARTED
#     assert fake_driver.status == DriverStatus.OPERATING

# def test_starting_dispatch_when_already_started(ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
#     Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     with pytest.raises(ValueError):
#         Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)
        
#     assert ready_draft_dispatch.status == DispatchStatus.STARTED
#     assert fake_driver.status == DriverStatus.OPERATING


# def test_dispatch_cannot_start_when_plan_not_valid(ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
#     Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     assert ready_draft_dispatch.status == DispatchStatus.STARTED
#     assert fake_driver.status == DriverStatus.AVAILABLE

# def test_dispatch_cannot_start_when_driver_already_operating(ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    
#     with pytest.raises(ValueError):
#         Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     assert ready_draft_dispatch.status == DispatchStatus.DRAFT
#     assert fake_driver.status == DriverStatus.OPERATING

# def test_dispatch_cannot_start_when_driver_unavailable(ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    
#     with pytest.raises(ValueError):
#         Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     assert ready_draft_dispatch.status == DispatchStatus.DRAFT
#     assert fake_driver.status == DriverStatus.UNAVAILABLE

# def test_dispatch_cannot_start_when_driver_deactivated(ready_draft_dispatch, fake_driver):
#     Dispatcher.assign_driver(ready_draft_dispatch, fake_driver)
    
#     with pytest.raises(ValueError):
#         Dispatcher.start_dispatch(ready_draft_dispatch, fake_driver)

#     assert ready_draft_dispatch.status == DispatchStatus.DRAFT
#     assert fake_driver.status == DriverStatus.UNAVAILABLE
