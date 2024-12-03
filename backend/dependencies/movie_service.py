from fastapi import Depends
from sqlalchemy.orm import Session

from dependencies.database import get_db
from services.movie import MovieService


# Dependency to provide MovieService
def get_movie_service(db: Session = Depends(get_db)) -> MovieService:
    """
    Dependency that returns a MovieService instance
    It automatically injects the database session using get_db
    """
    return MovieService(db)
