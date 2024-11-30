import logging

from config.settings import settings
import httpx


async def fetch_movie_from_omdb(title: str):
    """
    Fetch movie details from the OMDB API by title.
    """
    try:
        url = f"http://www.omdbapi.com/?apikey={settings.OMDB_API_KEY}&t={title}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return data
        logging.error(f"OMDB API returned error: {response.text}")
        return None
    except Exception as e:
        logging.error(f"Failed to fetch movie from OMDB: {e}")
        return None

