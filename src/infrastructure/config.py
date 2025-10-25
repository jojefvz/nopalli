"""
Configuration setup for the Nopalli.
"""

from enum import Enum
import os
from pathlib import Path


# Repository types
class RepositoryType(Enum):
    MEMORY = "memory"
    FILE = "file"


class Config:
    """Application configuration."""

    # Default values
    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.MEMORY
    DEFAULT_DATA_DIR = "repo_data"

    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """Get the configured repository type."""
        repo_type_str = os.getenv("TODO_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid repository type: {repo_type_str}")

    @classmethod
    def get_data_directory(cls) -> Path:
        """Get the data directory path."""
        data_dir = os.getenv("TODO_DATA_DIR", cls.DEFAULT_DATA_DIR)
        path = Path(data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
