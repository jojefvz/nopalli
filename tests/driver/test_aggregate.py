from os import read
import pytest
from src.domain.aggregates.dispatch.value_objects import TaskStatus
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.services import Dispatcher


# ---------- CREATING NEW DRIVER ----------
def test_driver_init():
    driver = Driver('John')

    assert driver.id
    assert driver.status == DriverStatus.AVAILABLE
    assert driver.name == 'John'


# ---------------------------------------- TESTING DRIVER WHILE AVAILABLE ----------------------------------------
def test_making_available_already_available_driver(fake_driver):
    match = 'Only unavailable drivers can be made available.'
    with pytest.raises(ValueError, match=match):
        fake_driver.make_available()

    assert fake_driver.status == DriverStatus.AVAILABLE

def test_driver_changing_to_operating_status(fake_driver):
    fake_driver.begin_operating()

    assert fake_driver.status == DriverStatus.OPERATING

def test_sitting_driver_out(fake_driver):
    fake_driver.sit_out()

    assert fake_driver.status == DriverStatus.UNAVAILABLE

def test_deactivating_available_driver(fake_driver):
    fake_driver.deactivate()

    assert fake_driver.status == DriverStatus.DEACTIVATED

def test_releasing_available_driver(fake_driver):
    match = 'Only operating drivers can be released.'
    with pytest.raises(ValueError, match=match):
        fake_driver.release()

    assert fake_driver.status == DriverStatus.AVAILABLE

def test_reactivating_available_driver(fake_driver):
    match = 'Only deactivated drivers can be reactivated.'
    with pytest.raises(ValueError, match=match):
        fake_driver.reactivate()

    assert fake_driver.status == DriverStatus.AVAILABLE

# ---------------------------------------- TESTING DRIVER WHILE OPERATING ----------------------------------------
def test_driver_changing_to_operating_when_already_operating(fake_driver):
    fake_driver.begin_operating()

    match = 'Only available drivers can begin operating.'
    with pytest.raises(ValueError, match=match):
        fake_driver.begin_operating()

    assert fake_driver.status == DriverStatus.OPERATING

def test_releasing_driver_when_operating(fake_driver):
    fake_driver.begin_operating()

    fake_driver.release()

    assert fake_driver.status == DriverStatus.AVAILABLE

def test_making_driver_available_when_operating(fake_driver):
    fake_driver.begin_operating()

    match = 'Only unavailable drivers can be made available'
    with pytest.raises(ValueError, match=match):
        fake_driver.make_available()

    assert fake_driver.status == DriverStatus.OPERATING

def test_sitting_driver_out_when_operating(fake_driver):
    fake_driver.begin_operating()

    match = 'Only available drivers can sit out.'
    with pytest.raises(ValueError, match=match):
        fake_driver.sit_out()

    assert fake_driver.status == DriverStatus.OPERATING

def test_deactivating_operating_driver(fake_driver):
    fake_driver.begin_operating()

    match = 'Only available and unavailable drivers can be deactivated.'
    with pytest.raises(ValueError, match=match):
        fake_driver.deactivate()

    assert fake_driver.status == DriverStatus.OPERATING

def test_reactivating_operating_driver(fake_driver):
    fake_driver.begin_operating()

    match = 'Only deactivated drivers can be reactivated.'
    with pytest.raises(ValueError, match=match):
        fake_driver.reactivate()

    assert fake_driver.status == DriverStatus.OPERATING

# ---------------------------------------- TEST DRIVER WHILE UNAVAILABLE ----------------------------------------
def test_making_unavailable_driver_available(fake_driver):
    fake_driver.sit_out()

    fake_driver.make_available()

    assert fake_driver.status == DriverStatus.AVAILABLE

def test_deactivating_unavailable_driver(fake_driver):
    
    fake_driver.sit_out()   

    fake_driver.deactivate()

    assert fake_driver.status == DriverStatus.DEACTIVATED

def test_sitting_out_unavailable_driver(fake_driver):
    fake_driver.sit_out()
    
    match = 'Only available drivers can sit out.'
    with pytest.raises(ValueError, match=match):
        fake_driver.sit_out()

    assert fake_driver.status == DriverStatus.UNAVAILABLE

def test_changing_unavailable_driver_to_operating(fake_driver):
    fake_driver.sit_out()
    
    match = 'Only available drivers can begin operating.'
    with pytest.raises(ValueError, match=match):
        fake_driver.begin_operating()

    assert fake_driver.status == DriverStatus.UNAVAILABLE

def test_unavailable_driver_being_released(fake_driver):
    fake_driver.sit_out()
    
    match = 'Only operating drivers can be released.'
    with pytest.raises(ValueError, match=match):
        fake_driver.release()

    assert fake_driver.status == DriverStatus.UNAVAILABLE

def test_deactivating_unavailable_driver(fake_driver):
    fake_driver.sit_out()   

    fake_driver.deactivate()

    assert fake_driver.status == DriverStatus.DEACTIVATED

def test_reactivating_unavailable_driver(fake_driver):
    fake_driver.sit_out()

    match = 'Only deactivated drivers can be reactivated.'
    with pytest.raises(ValueError, match=match):
        fake_driver.reactivate()

    assert fake_driver.status == DriverStatus.UNAVAILABLE

# ---------------------------------------- TESTING DRIVER WHILE DEACTIVATED ----------------------------------------
def test_reactivating_deactivated_driver(fake_driver):
    fake_driver.deactivate()

    fake_driver.reactivate()

    assert fake_driver.status == DriverStatus.AVAILABLE

def test_deactivating_deactivated_driver(fake_driver):
    fake_driver.deactivate()
    
    match = 'Only available and unavailable drivers can be deactivated.'
    with pytest.raises(ValueError, match=match):
        fake_driver.deactivate()

    assert fake_driver.status == DriverStatus.DEACTIVATED

def test_changing_deactivated_driver_to_operating(fake_driver):
    fake_driver.deactivate()
    
    match = 'Only available drivers can begin operating.'
    with pytest.raises(ValueError, match=match):
        fake_driver.begin_operating()

    assert fake_driver.status == DriverStatus.DEACTIVATED

def test_deactivated_driver_being_released(fake_driver):
    fake_driver.deactivate()
    
    match = 'Only operating drivers can be released.'
    with pytest.raises(ValueError, match=match):
        fake_driver.release()

    assert fake_driver.status == DriverStatus.DEACTIVATED
