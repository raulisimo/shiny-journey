import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config.constants import SEED_MOVIE_COUNT
from config.database import engine, SessionLocal, get_movie_seeder
from config.settings import settings
from models import metadata
from repositories.movie import MovieRepository
from routers import api_router


# Check the database on startup and seed if empty
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create a database session
    db: Session = SessionLocal()

    try:
        # Initialize the repository with the session
        movie_repo = MovieRepository(db)

        # Check the database and seed if empty
        number_movies = movie_repo.count_movies()
        if number_movies == 0:
            logging.info("Database is not ready, seeding...")
            try:
                logging.info("Seeding database...")
                seed_movies = await get_movie_seeder(SEED_MOVIE_COUNT)
                for movie_data in seed_movies:
                    movie_repo.create(movie_data)
            except Exception as e:
                logging.error(f"Error while seeding the database: {e}")
            else:
                logging.info("Database seeded successfully.")
        yield
    finally:
        db.close()


app = FastAPI(title=settings.APP_TITLE, debug=settings.DEBUG, lifespan=lifespan)
metadata.create_all(engine)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
app.include_router(api_router, prefix="/api")

# Add CORS middleware to allow requests from frontend
origins = [
    "http://localhost:5173",  # Add your frontend URL here
    "https://yourfrontenddomain.com",  # Or the deployed frontend URL if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/settings")
async def app_settings():
    omdb_api_key = settings.OMDB_API_KEY
    database_url = settings.DATABASE_URL
    jwt_secret = settings.JWT_SECRET
    debug = settings.DEBUG

    return {
        "message": f'OMDB API Key: {omdb_api_key}, Database URL: {database_url}, JWT Secret: {jwt_secret}, debug: {debug}'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
