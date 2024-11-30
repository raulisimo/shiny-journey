from typing import Optional, List

from pydantic import BaseModel, Field


class MovieBase(BaseModel):
    title: str = Field(..., example="Inception", description="The title of the movie")
    imdb_id: str = Field(..., pattern=r"tt\d{7,8}", example="tt1375666", description="The IMDb ID of the movie")
    year: Optional[int] = Field(
        None,
        ge=1888,
        le=2100,
        example=2010,
        description="The release year of the movie"
    )
    type: str = Field(..., example="movie", description="The type of the content (e.g., movie, series, episode)")

    # poster_url: Optional[HttpUrl] = Field(None, example="https://example.com/poster.jpg",
    #                                   description="URL of the movie poster")

    poster_url: Optional[str] = Field(..., example="https://example.com/poster.jpg",
                                      description="URL of the movie poster")
    genre: Optional[str] = Field(None, example="Action, Sci-Fi", description="The genre(s) of the movie")
    director: Optional[str] = Field(None, example="Christopher Nolan", description="The director of the movie")
    plot: Optional[str] = Field(None,
                                example="A thief who steals corporate secrets through the use of dream-sharing technology.",
                                description="A brief description or plot of the movie")


class MovieCreate(MovieBase):
    """Schema for creating a new movie."""
    pass  # Inherits all fields from MovieBase


class MovieOut(MovieCreate):
    id: int

    class Config:
        from_attributes = True


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Inception")
    year: Optional[int] = Field(None, example=2010, ge=1888, le=2100)
    type: Optional[str] = Field(None, example="movie")
    poster: Optional[str] = Field(None, example="https://example.com/poster.jpg")
    plot: Optional[str] = Field(None, example="A thief who enters dreams to steal secrets.")
    genre: Optional[str] = Field(None, example="Action, Sci-Fi")
    director: Optional[str] = Field(None, example="Christopher Nolan")


class MovieListResponse(BaseModel):
    movies: List[MovieOut] = Field(..., example=["movie1", "movie2"])
    total_pages: int = Field(..., example=2)


class MovieResponse(MovieBase):
    id: int = Field(..., example=1, description="The unique identifier of the movie in the database")

    class Config:
        from_attributes = True
