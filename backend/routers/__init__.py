from fastapi import APIRouter

from routers.movies import router as movies_router

# Create a main router to include all sub-routers
api_router = APIRouter()

# Include route modules
api_router.include_router(movies_router, prefix="/movies", tags=["Movies"])
