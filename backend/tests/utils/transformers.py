from utils.transformers import transform_movie_data


def test_transform_movie_data_success():
    api_data = {
        "Response": "True",
        "Title": "Inception",
        "Year": "2010",
        "imdbID": "tt1375666",
        "Type": "movie",
        "Poster": "https://example.com/inception.jpg",
        "Genre": "Action, Adventure, Sci-Fi",
        "Director": "Christopher Nolan",
        "Plot": "A thief who steals corporate secrets through dream-sharing technology."
    }

    result = transform_movie_data(api_data)

    # Assertions
    assert result is not None
    assert result["title"] == "Inception"
    assert result["year"] == 2010
    assert result["imdb_id"] == "tt1375666"
    assert result["type"] == "movie"
    assert result["poster_url"] == "https://example.com/inception.jpg"
    assert result["genre"] == "Action, Adventure, Sci-Fi"
    assert result["director"] == "Christopher Nolan"
    assert result["plot"] == "A thief who steals corporate secrets through dream-sharing technology."


def test_transform_movie_data_invalid():
    api_data = {"Response": "False"}
    result = transform_movie_data(api_data)
    assert result is None


def test_transform_movie_data_partial_data():
    api_data = {
        "Response": "True",
        "Title": "Incomplete Movie",
        "Year": "N/A",
        "imdbID": "tt1234567",
        "Type": "movie",
        "Poster": "N/A",
        "Genre": "N/A",
        "Director": "N/A",
        "Plot": "N/A"
    }

    result = transform_movie_data(api_data)

    # Assertions
    assert result is not None
    assert result["title"] == "Incomplete Movie"
    assert result["year"] is None
    assert result["imdb_id"] == "tt1234567"
    assert result["type"] == "movie"
    assert result["poster_url"] is None
    assert result["genre"] is None
    assert result["director"] is None
    assert result["plot"] is None
