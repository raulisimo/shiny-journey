from typing import Dict, Optional


def transform_movie_data(api_data: Dict) -> Optional[Dict]:
    """
    Transform API data to match the MovieCreate schema
    """
    if not api_data or api_data.get("Response") != "True":
        return None

    transformed_data = {
        "title": api_data.get("Title"),
        "year": int(api_data.get("Year")) if api_data.get("Year").isdigit() else None,
        "imdb_id": api_data.get("imdbID"),
        "type": api_data.get("Type"),
        "poster_url": api_data.get("Poster") if api_data.get("Poster") != "N/A" else None,
        "genre": api_data.get("Genre") if api_data.get("Genre") != "N/A" else None,
        "director": api_data.get("Director") if api_data.get("Director") != "N/A" else None,
        "plot": api_data.get("Plot") if api_data.get("Plot") != "N/A" else None,
    }

    return transformed_data
