from config.settings import settings

OMDB_BASE_URL = f'http://www.omdbapi.com/?apikey={settings.OMDB_API_KEY}&'

SEED_MOVIE_COUNT = 10

MOVIE_NOT_FOUND_MESSAGE = "Movie not found"

