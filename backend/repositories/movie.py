from typing import List, Type

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.movies import Movie
from repositories.base import BaseRepository
from schemas.movies import MovieCreate, MovieUpdate


class MovieRepository(BaseRepository[Movie, MovieCreate]):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Movie)

    def get_all_ordered_by_title(self, skip: int = 0, limit: int = 10) -> List[Type[Movie]]:
        """Retrieve all movies ordered by title with optional pagination."""
        return (
            self.db_session.query(Movie)
            .order_by(Movie.title)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, movie_id: int, movie_data: MovieUpdate) -> Movie:
        """Update a movie."""
        movie = self.get_by_id(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found.")

        update_data = movie_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(movie, key, value)

        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def search_by_name(self, title: str) -> List[Type[Movie]]:
        """Search for movies by title."""
        return (
            self.db_session.query(Movie)
            .filter(Movie.title.ilike(f"%{title}%"))
            .order_by(Movie.title)
            .all()
        )

    def count_movies(self) -> int:
        """Return the total count of entities."""
        return self.db_session.query(func.count(Movie.id)).scalar()
