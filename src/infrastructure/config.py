"""
Configuration setup for the Nopalli.
"""

from enum import Enum
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.orm import set_orm_mapping


# Repository types
class RepositoryType(Enum):
    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"


class Config:
    """Application configuration."""

    # Default values
    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.MEMORY
    DEFAULT_DATA_DIR = "repo_data"
    DEFAULT_DATABASE_URL = 'postgresql+psycopg2://root:root@db:5432/nopalli'

    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """Get the configured repository type."""
        repo_type_str = os.getenv("NOPALLI_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid repository type: {repo_type_str}")

    @classmethod
    def get_data_directory(cls) -> Path:
        """Get the data directory path."""
        data_dir = os.getenv("NOPALLI_DATA_DIR", cls.DEFAULT_DATA_DIR)
        path = Path(data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def get_session_factory(cls) -> sessionmaker:
        db_url = os.getenv('NOPALLI_DATABASE_URL', cls.DEFAULT_DATABASE_URL)
        engine = create_engine(db_url, echo=True)
        set_orm_mapping(engine)
        return sessionmaker(bind=engine)


