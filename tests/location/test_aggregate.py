from src.domain.aggregates.location.aggregate import Location, LocationStatus
from src.domain.aggregates.location.value_objects import Address


def test_location_init():
    location = Location('BNSF LPC', Address('1234 Red St.', 'Elwood', 'Illinois', 11111))

    assert location.id
    assert location.name == 'BNSF LPC'
    assert location.status == LocationStatus.ACTIVE

def test_updating_location_address(fake_location):
    fake_location.update_address('5678 Green St.', 'Elwood', 'Illinois', 22222)

    assert fake_location
    assert fake_location.name == 'BNSF LPC'
    assert fake_location.address == Address('5678 Green St.', 'Elwood', 'Illinois', 22222)

def test_deactivating_location(fake_location):
    fake_location.deactivate()

    assert fake_location.status == LocationStatus.INACTIVE

def test_reactivating_location(fake_location):
    fake_location.reactivate()

    assert fake_location.status == LocationStatus.ACTIVE
