from abc import ABC, abstractmethod
from typing import TypeVar, List, Optional, Generic

from sqlalchemy.orm import Session

# Type variables for Entity and Schema
TEntity = TypeVar('TEntity')
TSchema = TypeVar('TSchema')


class BaseRepository(Generic[TEntity, TSchema], ABC):
    def __init__(self, db_session: Session, model: TEntity):
        self.db_session = db_session
        self.model = model

    def create(self, data: TSchema) -> TEntity:
        """Create a new record in the database."""
        entity = self.model(**data.dict())
        self.db_session.add(entity)
        self.db_session.commit()
        self.db_session.refresh(entity)
        return entity

    def get_by_id(self, id: int) -> Optional[TEntity]:
        """Retrieve an entity by its ID."""
        return self.db_session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 10) -> List[TEntity]:
        """Retrieve all entities with optional pagination."""
        return self.db_session.query(self.model).offset(skip).limit(limit).all()

    def delete_by_id(self, id: int) -> bool:
        """Delete an entity by its ID."""
        entity = self.get_by_id(id)
        if entity:
            self.db_session.delete(entity)
            self.db_session.commit()
            return True
        return False

    @abstractmethod
    def update(self, id: int, data: TSchema) -> TEntity:
        """Abstract method for updating an entity. Needs to be implemented in the child class."""
        pass
