from .config import Config, RepositoryType
from .persistence.broker.database import SQLAlchemyBrokerRepository
from .persistence.dispatch.database import SQLAlchemyDispatchRepository
from .persistence.driver.database import SQLAlchemyDriverRepository
from .persistence.location.database import SQLAlchemyLocationRepository
from .persistence.broker.memory import InMemoryBrokerRepository
from .persistence.dispatch.memory import InMemoryDispatchRepository
from .persistence.driver.memory import InMemoryDriverRepository
from .persistence.location.memory import InMemoryLocationRepository
from src.application.repositories.broker_repository import BrokerRepository
from src.application.repositories.dispatch_repository import DispatchRepository
from src.application.repositories.driver_repository import DriverRepository
from src.application.repositories.location_repository import LocationRepository


def create_repositories() -> tuple[BrokerRepository, DispatchRepository, DriverRepository, LocationRepository]:
    repo_type = Config.get_repository_type()

    if repo_type == RepositoryType.MEMORY:
        broker_repo = InMemoryBrokerRepository()
        dispatch_repo = InMemoryDispatchRepository()
        driver_repo = InMemoryDriverRepository()
        location_repo = InMemoryLocationRepository()
        return (
                broker_repo,
                dispatch_repo,
                driver_repo,
                location_repo
                )
    if repo_type == RepositoryType.DATABASE:
        session_factory = Config.get_session_factory()
        broker_repo = SQLAlchemyBrokerRepository(session_factory)
        dispatch_repo = SQLAlchemyDispatchRepository(session_factory)
        driver_repo = SQLAlchemyDriverRepository(session_factory)
        location_repo = SQLAlchemyLocationRepository(session_factory)
        return (
                broker_repo,
                dispatch_repo,
                driver_repo,
                location_repo
                )
    else:
        raise ValueError(f"Invalid repository type: {repo_type}")
