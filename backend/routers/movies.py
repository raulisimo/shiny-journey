import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query

from config.authorization import require_role
from config.constants import MOVIE_NOT_FOUND_MESSAGE
from config.dependencies import get_movie_service
from schemas.movies import MovieOut, MovieCreate, MovieUpdate, MovieListResponse
from schemas.users import UserBase
from services.movie import MovieService

router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/create", response_model=MovieOut)
async def create_movie(
        title: Optional[str] = Query(None, description="Title of the movie to fetch from OMDB"),
        movie_data: Optional[MovieCreate] = None,
        movie_service: MovieService = Depends(get_movie_service)
):
    """
    Create a movie in two ways:
    1. Provide `title` to fetch details from OMDB and save it to the database.
    2. Provide full `MovieCreate` data to directly save it to the database.
    """
    # movie_service = MovieService(db)

    if title:
        # Fetch movie details from OMDB and create it
        return movie_service.create_movie_from_title(title)
    elif movie_data:
        # Create movie directly with provided data
        return movie_service.create_movie(movie_data)
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'title' or 'movie_data' must be provided."
        )


@router.patch("/{movie_id}", response_model=MovieOut)
async def update_movie(
        movie_id: int,
        movie_data: MovieUpdate,
        movie_service: MovieService = Depends(get_movie_service)
):
    """
    Partially update an existing movie's details.
    """

    try:
        updated_movie = movie_service.update_movie(movie_id, movie_data)
        return updated_movie
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/search", response_model=List[MovieOut])
async def search_movies(
        title: Optional[str] = None,
        movie_service: MovieService = Depends(get_movie_service),
):
    if not title:
        raise HTTPException(status_code=400, detail="Title is required for searching")

    movies = movie_service.search_movies_by_name(title)
    if not movies:
        raise HTTPException(status_code=404, detail="Movies not found")

    return movies


@router.get("/{movie_id}", response_model=MovieOut)
async def get_movie_by_id(movie_id: int, movie_service: MovieService = Depends(get_movie_service), ):
    # movie_service = MovieService(db)
    movie = movie_service.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=MOVIE_NOT_FOUND_MESSAGE)
    return movie


@router.get("/", response_model=MovieListResponse)
async def get_movies(
        page: int = 1, limit: int = 10,
        movie_service: MovieService = Depends(get_movie_service),
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than 0")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")

    # Calculate skip based on page and limit
    skip = (page - 1) * limit
    movies, total_movies = movie_service.get_movies_with_pagination(skip, limit)

    # Calculate total pages
    total_pages = (total_movies + limit - 1) // limit

    return {
        "movies": movies,
        "total_pages": total_pages
    }


@router.delete("/{movie_id}")
async def delete_movie(movie_id: int,
                       movie_service: MovieService = Depends(get_movie_service),
                       user: UserBase = Depends(require_role("admin"))):
    result = movie_service.delete_movie_by_id(movie_id)
    if not result:
        raise HTTPException(status_code=404, detail=MOVIE_NOT_FOUND_MESSAGE)
    return {"detail": "Movie deleted successfully"}
