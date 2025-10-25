from .config import Config, RepositoryType
from .persistence.location.memory import InMemoryLocationRepository
from ..application.repositories.location_repository import LocationRepository


def create_repositories() -> LocationRepository:
    repo_type = Config.get_repository_type()

    if repo_type == RepositoryType.MEMORY:
        location_repo = InMemoryLocationRepository()
        return location_repo
    else:
        raise ValueError(f"Invalid repository type: {repo_type}")
