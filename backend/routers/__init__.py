from fastapi import APIRouter
from routers.movies import router as movies_router
# from routers.users import router as users_router

# Create a main router to include all sub-routers
api_router = APIRouter()

# Include route modules
api_router.include_router(movies_router, prefix="/movies", tags=["Movies"])
# api_router.include_router(users_router, prefix="/users", tags=["Users"])
