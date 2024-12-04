import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config.constants import SEED_MOVIE_COUNT
from config.database import SessionLocal, get_movie_seeder
from config.settings import settings
from models import metadata
from repositories.movie import MovieRepository
from routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = SessionLocal()  # Create the DB session
    try:
        logging.info("Creating database and models")
        engine = settings.get_db_connection()
        try:
            metadata.create_all(bind=engine)
            logging.info("Tables created successfully.")
        except Exception as e:
            logging.error(f"Failed to create tables: {e}")

        # Movie repository and seeding logic
        movie_repo = MovieRepository(db)
        if movie_repo.count_movies() == 0:
            logging.info("Database is not ready, seeding...")
            try:
                seed_movies = await get_movie_seeder(SEED_MOVIE_COUNT)
                for movie_data in seed_movies:
                    movie_repo.create(movie_data)
                logging.info("Database seeded successfully.")
            except Exception as e:
                logging.error(f"Error while seeding the database: {e}")

        yield

    except Exception as e:
        logging.error(f"Error while creating the database: {e}")
    finally:
        db.close()


app = FastAPI(title=settings.APP_TITLE, debug=settings.DEBUG, lifespan=lifespan)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app.include_router(api_router, prefix="/api")

# CORS settings
origins = [
    "http://localhost:3000",
    "https://frontend-dot-pro-groove-443318-s8.ew.r.appspot.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def app_settings():
    return {
        "message": "Welcome to the Brite movies backend!",
        "docs": "https://pro-groove-443318-s8.ew.r.appspot.com/docs",
    }


@app.get("/settings")
async def app_settings():
    return {
        "DEBUG": settings.DEBUG,
        "ENV": os.getenv("ENV")
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
