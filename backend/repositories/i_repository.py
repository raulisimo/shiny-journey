from abc import ABC, abstractmethod
from typing import TypeVar, List, Optional, Generic

from pydantic import BaseModel

TEntity = TypeVar('TEntity')  # Entity type (e.g., Movie, User)
TSchema = TypeVar('TSchema', bound=BaseModel)  # Schema type (e.g., MovieCreate, UserCreate)


class ICreateRepository(ABC, Generic[TEntity, TSchema]):
    @abstractmethod
    def create(self, data: TSchema) -> TEntity:
        """Create a new record in the databas."""
        pass


class IGetRepository(ABC, Generic[TEntity]):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[TEntity]:
        """Retrieve an entity by its ID"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[TEntity]:
        """Retrieve all records with pagination"""
        pass

    @abstractmethod
    def search_by_name(self, name: str) -> List[TEntity]:
        """Search for entities by name"""
        pass


class IDeleteRepository(ABC, Generic[TEntity]):
    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """Delete an entity by its ID"""
        pass


class IUpdateRepository(ABC, Generic[TEntity, TSchema]):
    @abstractmethod
    def update(self, id: int, data: TSchema) -> TEntity:
        """Update an entity by its ID"""
        pass


class IRepository(
    ICreateRepository[TEntity, TSchema],
    IGetRepository[TEntity],
    IDeleteRepository[TEntity],
    IUpdateRepository[TEntity, TSchema],
    ABC,
):
    """Combine all the repository interfaces."""
    pass
