from .config import Config, RepositoryType
from .persistence.broker.memory import InMemoryBrokerRepository
from .persistence.location.memory import InMemoryLocationRepository
from ..application.repositories.broker_repository import BrokerRepository
from ..application.repositories.location_repository import LocationRepository


def create_repositories() -> LocationRepository:
    repo_type = Config.get_repository_type()

    if repo_type == RepositoryType.MEMORY:
        broker_repo = InMemoryBrokerRepository()
        location_repo = InMemoryLocationRepository()
        return broker_repo, location_repo

    else:
        raise ValueError(f"Invalid repository type: {repo_type}")
