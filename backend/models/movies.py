import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from models import ModelBase


class Movie(ModelBase):
    __tablename__ = "movies"

    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Title (string length should be reasonable for titles)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Year (4-digit integer, can be null)
    year: Mapped[int] = mapped_column(Integer, nullable=True)

    # IMDb ID (Unique and indexed for fast lookups)
    imdb_id: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)

    # Type (limited to 50 characters, non-nullable)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Poster URL (optional, limiting the length to browser-supported maximum URL length)
    poster_url: Mapped[str] = mapped_column(String(2083), nullable=True)

    # Genre (nullable, can be multiple genres, but stored as a single string)
    genre: Mapped[str] = mapped_column(String(255), nullable=True)

    # Director (nullable)
    director: Mapped[str] = mapped_column(String(255), nullable=True)

    # Plot (nullable)
    plot: Mapped[str] = mapped_column(Text, nullable=True)

    # Timestamps: Automatically set on creation and update
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    # MySQL 8.x has support for utf8mb4
    __table_args__ = (
        {'mysql_charset': 'utf8mb4'},
    )

    @classmethod
    def validate_title(cls, title: str) -> bool:
        """
        Validate the title length and ensure it adheres to business rules.
        """
        if len(title) > 255:
            raise ValueError("Title length cannot exceed 255 characters.")
        return True

    @classmethod
    def validate_imdb_id(cls, imdb_id: str) -> bool:
        """
        Validate IMDb ID format (e.g., tt1234567).
        """
        if not imdb_id.startswith("tt") or len(imdb_id) != 10:
            raise ValueError("IMDb ID must be in the format 'tt1234567'.")
        return True
