import pytest

from src.domain.aggregates.broker.aggregate import Broker
from src.domain.aggregates.broker.value_objects import BrokerStatus
from src.domain.aggregates.location.value_objects import Address


def test_broker_init():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'Cornerstone'

    broker = Broker(name, address)

    assert broker.id
    assert broker.name == 'Cornerstone'
    assert broker.status == BrokerStatus.ACTIVE
    assert broker.address == Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)


def test_deactivating_broker():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'Cornerstone'
    broker = Broker(name, address)

    broker.deactivate()

    assert broker.status == BrokerStatus.INACTIVE


def test_deactivating_deactivated_broker():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'Cornerstone'
    broker = Broker(name, address)
    broker.deactivate()

    match = 'Only active brokers can be deactivated.'
    with pytest.raises(ValueError, match=match):
        broker.deactivate()


def test_reactivating_broker():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'Cornerstone'
    broker = Broker(name, address)
    broker.deactivate()

    broker.reactivate()

    assert broker.status == BrokerStatus.ACTIVE


def test_reactivating_active_broker():
    address = Address('1234 Apple St.', 'Chicago', 'Illinois', 11111)
    name = 'Cornerstone'
    broker = Broker(name, address)

    match = 'Only deactivated brokers can be reactivated.'
    with pytest.raises(ValueError, match=match):
        broker.reactivate()

