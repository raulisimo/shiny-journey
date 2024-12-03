from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.movies import Movie
from repositories.movie import MovieRepository
from schemas.movies import MovieUpdate


@pytest.fixture
def mock_db_session():
    """Fixture for mocking the database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def movie_repository(mock_db_session):
    """Fixture for initializing the MovieRepository with a mock session."""
    return MovieRepository(db_session=mock_db_session)


@pytest.fixture
def mock_movie():
    """Fixture for a mock movie instance."""
    return Movie(
        id=1,
        title="Test Movie",
        year=2021,
        imdb_id="tt1234567",
        type="movie",
        poster_url="http://example.com/poster.jpg",
        genre="Drama",
        director="Jane Doe",
        plot="A test movie plot.",
    )


def test_update_movie_success(movie_repository, mock_db_session, mock_movie):
    # query().filter_by().first() returns the mock_movie instance
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_movie

    # Prepare update data
    movie_data = MovieUpdate(title="Updated Title")

    # Mock commit and refresh
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Perform the update
    updated_movie = movie_repository.update(movie_id=1, movie_data=movie_data)

    # Assertions
    assert updated_movie.title == "Updated Title"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_movie)


def test_update_movie_not_found(movie_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Prepare update data
    movie_data = MovieUpdate(title="Updated Title")

    # Expect HTTPException when movie is not found
    with pytest.raises(HTTPException) as exc_info:
        movie_repository.update(movie_id=1, movie_data=movie_data)

    # Assertions
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Movie not found."


# Test: Search movies by name
def test_search_by_name(movie_repository, mock_db_session, mock_movie):
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        mock_movie
    ]

    results = movie_repository.search_by_name(title="Test")

    assert len(results) == 1
    assert results[0].title == "Test Movie"
    mock_db_session.query.assert_called_once_with(Movie)


# Test: Count movies
def test_count_movies(movie_repository, mock_db_session):
    mock_db_session.query.return_value.scalar.return_value = 5

    count = movie_repository.count_movies()

    assert count == 5
    mock_db_session.query.assert_called_once()
    mock_db_session.query.return_value.scalar.assert_called_once()
