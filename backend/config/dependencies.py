from fastapi import Depends
from sqlalchemy.orm import Session

from services.movie import MovieService


# Dependency for database session
def get_db():
    from config.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to provide MovieService
def get_movie_service(db: Session = Depends(get_db)) -> MovieService:
    """
    Dependency that returns a MovieService instance
    It automatically injects the database session using get_db
    """
    return MovieService(db)
