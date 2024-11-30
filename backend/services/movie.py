import logging
from typing import List, Optional, Type, Tuple

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from config.constants import OMDB_BASE_URL
from models.movies import Movie
from repositories.movie import MovieRepository
from schemas.movies import MovieCreate, MovieUpdate


class MovieService:
    def __init__(self, db_session: Session):
        self.movie_repository = MovieRepository(db_session)

    def fetch_movie_from_omdb(self, title: str) -> MovieCreate:
        """
        Fetch movie details from OMDB API and map them to MovieCreate schema.
        Raises HTTPException if the movie is not found or the API call fails.
        """
        try:
            search_url = f"{OMDB_BASE_URL}t={title}"
            logging.info(f"Fetching movie from OMDB: {search_url}")
            response = httpx.get(search_url)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    logging.info(f"OMDB API responded with data: {data}")
                    return MovieCreate(
                        title=data['Title'],
                        year=int(data['Year']),
                        genre=data['Genre'],
                        type=data['Type'],
                        director=data['Director'],
                        plot=data['Plot'],
                        imdb_id=data['imdbID'],
                        poster_url=data.get('Poster')
                    )
                else:
                    logging.warning(f"OMDB API responded with error: {data.get('Error')}")
                    raise HTTPException(status_code=404, detail=f"Movie '{title}' not found in OMDB.")
            else:
                logging.error(f"OMDB API call failed with status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch movie from OMDB. Please try again later."
                )
        except Exception as e:
            logging.error(f"Error calling OMDB API: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while communicating with OMDB."
            )

    def create_movie(self, movie_data: MovieCreate) -> Movie:
        """
        Create a movie in the database using provided MovieCreate data.
        """
        try:
            logging.info(f"Creating movie with provided data: {movie_data}")
            return self.movie_repository.create(movie_data)
        except Exception as e:
            logging.error(f"Error creating movie in database: {e}")
            raise HTTPException(status_code=400, detail="Error creating movie.")

    def create_movie_from_title(self, title: str) -> Movie:
        """
        Fetch movie details from OMDB by title and create it in the database.
        """
        movie_data = self.fetch_movie_from_omdb(title)
        return self.create_movie(movie_data)

    def get_all_movies(self, page: int = 1, limit: int = 10) -> List[Movie]:
        return self.movie_repository.get_all(page, limit)

    def get_movies_with_pagination(self, skip: int, limit: int) -> Tuple[List[Movie], int]:
        """Get movies with pagination."""
        # Get the paginated results from the repository
        movies = self.movie_repository.get_all(skip, limit)
        total_movies = self.movie_repository.count_movies()
        return movies, total_movies

    def count_movies(self) -> int:
        return self.movie_repository.count_movies()

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        return self.movie_repository.get_by_id(movie_id)

    def search_movies_by_name(self, title: str) -> List[Type[Movie]]:
        return self.movie_repository.search_by_name(title)

    def update_movie(self, movie_id: int, movie_data: MovieUpdate) -> Movie:
        """
        Partially update an existing movie's details.
        """
        logging.info(f"Updating movie ID: {movie_id} with data: {movie_data}")
        return self.movie_repository.update(movie_id, movie_data)

    def delete_movie_by_id(self, movie_id: int) -> bool:
        return self.movie_repository.delete_by_id(movie_id)
