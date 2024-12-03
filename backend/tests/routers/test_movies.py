from unittest.mock import MagicMock, Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from dependencies.movie_service import get_movie_service
from main import app
from schemas.movies import MovieUpdate


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_movie_service():
    # Mock the MovieService methods
    mock_service = MagicMock()
    mock_service.create_movie_from_title = Mock(
        return_value={
            "id": 1,
            "title": "Inception",
            "imdb_id": "tt1234567",
            "type": "movie",
            "poster_url": "http://example.com/poster.jpg",
            "year": 2024,
            "genre": "Sci-Fi",
            "director": "Director",
            "plot": "Plot"
        }
    )
    mock_service.create_movie = Mock(
        return_value={
            "id": 2,
            "title": "Another Mock Movie",
            "imdb_id": "tt9876543",
            "type": "movie",
            "poster_url": "http://example.com/poster2.jpg",
            "year": 2023,
            "genre": "Action",
            "director": "Director",
            "plot": "Plot"
        }
    )
    mock_service.update_movie = Mock(return_value={"id": 1, "title": "Updated Movie"})
    mock_service.search_movies_by_name = Mock(return_value=[])
    mock_service.get_movie_by_id = Mock(return_value=None)
    mock_service.get_movies_with_pagination = Mock(return_value=([], 0))
    mock_service.delete_movie_by_id = Mock(return_value=True)
    return mock_service


@pytest.fixture(autouse=True)
def override_dependency(mock_movie_service):
    app.dependency_overrides[get_movie_service] = lambda: mock_movie_service


@pytest.mark.asyncio
async def test_create_movie_with_title(test_client, mock_movie_service):
    response = test_client.post("/api/movies/create", params={"title": "Inception"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Inception",
        "imdb_id": "tt1234567",
        "type": "movie",
        "poster_url": "http://example.com/poster.jpg",
        "year": 2024,
        "genre": "Sci-Fi",
        "director": "Director",
        "plot": "Plot"
    }

    mock_movie_service.create_movie_from_title.assert_called_once_with("Inception")


async def test_create_movie_with_data(test_client, mock_movie_service):
    movie_data = {"title": "Matrix", "description": "Sci-fi classic"}
    response = test_client.post("/api/movies/create", json={"movie_data": movie_data})
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "title": "Another Mock Movie",
        "imdb_id": "tt9876543",
        "type": "movie",
        "poster_url": "http://example.com/poster2.jpg",
        "year": 2023,
        "genre": "Action",
        "director": "Director",
        "plot": "Plot"
    }

    mock_movie_service.create_movie.assert_called_once_with(movie_data)


@pytest.mark.asyncio
async def test_update_movie_success(test_client, mock_movie_service):
    # Create a MovieUpdate instance
    movie_data = MovieUpdate(
        title="Updated Movie Title",
        year=None,
        type=None,
        poster=None,
        plot=None,
        genre=None,
        director=None
    )

    # Mock the return value
    mock_movie_service.update_movie.return_value = {
        "id": 1,
        "title": "Updated Movie Title",
        "imdb_id": "tt1234567",
        "type": "movie",
        "poster_url": "http://example.com/poster.jpg",
        "year": None,
        "genre": None,
        "director": None,
        "plot": None
    }

    # Send the request
    response = test_client.patch("/api/movies/1", json=movie_data.model_dump())
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Updated Movie Title",
        "imdb_id": "tt1234567",
        "type": "movie",
        "poster_url": "http://example.com/poster.jpg",
        "year": None,
        "genre": None,
        "director": None,
        "plot": None
    }

    # Verify the mock was called with the correct arguments
    mock_movie_service.update_movie.assert_called_once_with(1, movie_data)


@pytest.mark.asyncio
async def test_update_movie_not_found(test_client, mock_movie_service):
    movie_data = {"title": "Updated Movie Title"}
    mock_movie_service.update_movie.side_effect = HTTPException(status_code=404, detail="Movie not found")
    response = test_client.patch("/api/movies/999", json=movie_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}


@pytest.mark.asyncio
async def test_update_movie_server_error(test_client, mock_movie_service):
    movie_data = {"title": "Updated Movie Title"}
    mock_movie_service.update_movie.side_effect = Exception("Unexpected Error")
    response = test_client.patch("/api/movies/1", json=movie_data)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}


@pytest.mark.asyncio
async def test_search_movies_success(test_client, mock_movie_service):
    mock_movie_service.search_movies_by_name.return_value = [
        {
            "id": 1,
            "title": "Mock Movie",
            "imdb_id": "tt1234567",
            "type": "movie",
            "poster_url": "http://example.com/poster.jpg",
            "year": None,
            "genre": None,
            "director": None,
            "plot": None
        }
    ]
    response = test_client.get("/api/movies/search", params={"title": "Mock"})
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Mock Movie",
            "imdb_id": "tt1234567",
            "type": "movie",
            "poster_url": "http://example.com/poster.jpg",
            "year": None,
            "genre": None,
            "director": None,
            "plot": None
        }
    ]
    mock_movie_service.search_movies_by_name.assert_called_once_with("Mock")


@pytest.mark.asyncio
async def test_search_movies_missing_title(test_client):
    response = test_client.get("/api/movies/search")
    assert response.status_code == 400
    assert response.json() == {"detail": "Title is required for searching"}


@pytest.mark.asyncio
async def test_search_movies_not_found(test_client, mock_movie_service):
    mock_movie_service.search_movies_by_name.return_value = []
    response = test_client.get("/api/movies/search", params={"title": "Nonexistent"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Movies not found"}


@pytest.mark.asyncio
async def test_get_movie_by_id_success(test_client, mock_movie_service):
    mock_movie_service.get_movie_by_id.return_value = {
        "id": 1,
        "title": "Mock Movie",
        "imdb_id": "tt1234567",
        "type": "movie",
        "poster_url": "http://example.com/poster.jpg",
        "year": None,
        "genre": None,
        "director": None,
        "plot": None
    }
    response = test_client.get("/api/movies/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Mock Movie",
        "imdb_id": "tt1234567",
        "type": "movie",
        "poster_url": "http://example.com/poster.jpg",
        "year": None,
        "genre": None,
        "director": None,
        "plot": None
    }
    mock_movie_service.get_movie_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_movie_by_id_not_found(test_client, mock_movie_service):
    mock_movie_service.get_movie_by_id.return_value = None
    response = test_client.get("/api/movies/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}


@pytest.mark.asyncio
async def test_get_movies_success(test_client, mock_movie_service):
    mock_movie_service.get_movies_with_pagination.return_value = ([
      {
          "id": 1,
          "title": "Mock Movie",
          "imdb_id": "tt1234567",
          "type": "movie",
          "poster_url": "http://example.com/poster.jpg",
          "year": None,
          "genre": None,
          "director": None,
          "plot": None
      }
  ], 1)
    response = test_client.get("/api/movies", params={"page": 1, "limit": 10})
    assert response.status_code == 200
    assert response.json() == {
        "movies": [
            {
                "id": 1,
                "title": "Mock Movie",
                "imdb_id": "tt1234567",
                "type": "movie",
                "poster_url": "http://example.com/poster.jpg",
                "year": None,
                "genre": None,
                "director": None,
                "plot": None
            }
        ],
        "total_pages": 1
    }
    mock_movie_service.get_movies_with_pagination.assert_called_once_with(0, 10)


@pytest.mark.asyncio
async def test_delete_movie_success(test_client, mock_movie_service):
    mock_movie_service.delete_movie_by_id.return_value = True

    headers = {"Authorization": "Bearer token123"}
    response = test_client.delete("/api/movies/1", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"detail": "Movie deleted successfully"}
    mock_movie_service.delete_movie_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_movie_not_found(test_client, mock_movie_service):
    mock_movie_service.delete_movie_by_id.return_value = False

    headers = {"Authorization": "Bearer token123"}
    response = test_client.delete("/api/movies/999", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}
    mock_movie_service.delete_movie_by_id.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_delete_movie_unauthorized(test_client):
    # No headers provided
    response = test_client.delete("/api/movies/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.delete("/api/movies/1", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
