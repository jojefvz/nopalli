import pytest

from src.domain.aggregates.location.aggregate import Location
from src.domain.aggregates.location.value_objects import LocationStatus
from src.domain.aggregates.location.value_objects import Address


def test_location_init():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'UP Global 4'

    location = Location(name, address)

    assert location.id
    assert location.name == 'UP Global 4'
    assert location.status == LocationStatus.ACTIVE
    assert location.address == Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)


def test_deactivating_location():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'UP Global 4'
    location = Location(name, address)

    location.deactivate()

    assert location.status == LocationStatus.INACTIVE


def test_deactivating_deactivated_location():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'UP Global 4'
    location = Location(name, address)
    location.deactivate()

    match = 'Only active locations can be deactivated.'
    with pytest.raises(ValueError, match=match):
        location.deactivate()


def test_reactivating_location():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'UP Global 4'
    location = Location(name, address)
    location.deactivate()

    location.reactivate()

    assert location.status == LocationStatus.ACTIVE


def test_reactivating_active_location():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'UP Global 4'
    location = Location(name, address)

    match = 'Only deactivated locations can be reactivated.'
    with pytest.raises(ValueError, match=match):
        location.reactivate()
