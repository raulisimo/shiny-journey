import asyncio
import logging
import random
from typing import List, Optional, Dict

import httpx
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

from config.constants import OMDB_BASE_URL
from config.settings import settings
from schemas.movies import MovieCreate
from utils.transformers import transform_movie_data

# ORM setup
engine = settings.get_db_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base: DeclarativeMeta = declarative_base()


class MovieFetcher:
    """
    Class to handle fetching movie data from OMDB API
    """

    def __init__(self, client: httpx.AsyncClient, base_url: str = OMDB_BASE_URL):
        self.client = client
        self.base_url = base_url

    async def fetch_movie(self, imdb_id: str) -> Optional[Dict]:
        """
        Fetch a movie by IMDb ID from the OMDB API

        Args:
            imdb_id (str): IMDb ID of the movie.

        Returns:
            Optional[Dict]: Movie data if available, otherwise None
        """
        try:
            response = await self.client.get(f"{self.base_url}i={imdb_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    logging.debug(f"Movie data: {data}")
                    return data
                else:
                    logging.error(f"Error fetching movie {imdb_id}: {data.get('Error')}")
            else:
                logging.error(f"Error fetching movie {imdb_id}: HTTP {response.status_code}")
        except Exception as e:
            logging.error(f"Exception fetching movie {imdb_id}: {e}")
        return None


class MovieSeeder:
    """
    Class to handle seeding the database with movie data
    """

    def __init__(self, fetcher: MovieFetcher, movie_count: int = 100):
        self.fetcher = fetcher
        self.movie_count = movie_count

    async def seed_database(self) -> List[MovieCreate]:
        """
        Seed the database with a specified number of movies.

        Args:
            count (int): The number of movies to generate and fetch

        Returns:
            List[MovieCreate]: List of MovieCreate schemas to be inserted into the DB
        """
        ids = await self.generate_random_ids(self.movie_count)
        tasks = [self.fetcher.fetch_movie(imdb_id) for imdb_id in ids]
        results = await asyncio.gather(*tasks)

        logging.debug(f"Results: {results}")
        # Transform API responses and filter out invalid ones
        movies = [
            transform_movie_data(movie) for movie in results if movie
        ]
        logging.debug(f"Movies: {movies}")
        valid_movies = [MovieCreate(**movie) for movie in movies if movie]

        return valid_movies

    @staticmethod
    async def generate_random_ids(count: int) -> List[str]:
        """
        Generate a list of random IMDb IDs

        Args:
            count (int): Number of random IMDb IDs to generate

        Returns:
            List[str]: List of randomly generated IMDb IDs
        """
        return [f"tt{str(random.randint(1, 100000)).zfill(7)}" for _ in range(count)]


async def get_movie_seeder(count: int = 100) -> List[MovieCreate]:
    """
    Entry point to start the movie seeding process

    Args:
        count (int): Number of movies to generate and fetch

    Returns:
        List[MovieCreate]: A list of valid movies ready for insertion
    """
    async with httpx.AsyncClient() as client:
        fetcher = MovieFetcher(client)
        seeder = MovieSeeder(fetcher, count)
        return await seeder.seed_database()
