import dis
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.driver.aggregate import Driver
from src.domain.aggregates.driver.value_objects import DriverStatus


class Dispatcher:
    @staticmethod
    def assign_driver(dispatch: Dispatch, driver: Driver):
        if driver.status not in (DriverStatus.AVAILABLE, DriverStatus.OPERATING):
            raise ValueError('Only available and operating drivers can be assigned.')

        dispatch.driver_ref = driver.id

    @staticmethod
    def remove_driver(dispatch: Dispatch):
        dispatch.driver_ref = None

    @staticmethod
    def start_dispatch(dispatch: Dispatch, driver: Driver):
        dispatch.start()
        driver.begin_operating()

    @staticmethod
    def revert_dispatch_status(dispatch: Dispatch, driver: Driver):
        dispatch.revert_status()
        driver.release()
