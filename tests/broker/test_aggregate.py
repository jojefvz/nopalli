from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.broker.value_objects import BrokerStatus
from src.domain.aggregates.location.value_objects import Address


def test_broker_init():
    broker = Broker('Cornerstone', Address('1234 Apple St.', 'Chicago', 'Illinois', 11111))

    assert broker.id
    assert broker.name == 'Cornerstone'
    assert broker.status == BrokerStatus.ACTIVE
    assert broker.address == Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)

def test_updating_broker_address(fake_broker):
    fake_broker.update_address('5678 Peach St.', 'Chicago', 'Illinois', 22222)

    assert fake_broker
    assert fake_broker.name == 'Cornerstone'
    assert fake_broker.address == Address('5678 Peach St.', 'Chicago', 'Illinois', 22222)

def test_deactivating_broker(fake_broker):
    fake_broker.deactivate()

    assert fake_broker.status == BrokerStatus.INACTIVE

def test_reactivating_broker(fake_broker):
    fake_broker.reactivate()

    assert fake_broker.status == BrokerStatus.ACTIVE
