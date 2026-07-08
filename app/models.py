"""
ORM models — these map Python classes onto the tables we already created
in sql/01_schema.sql. We're not using these to CREATE the tables (the SQL
file already did that); we're just using them so the rest of the app can
work with Python objects instead of writing raw SQL everywhere.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    ratings = relationship("Rating", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True)
    title = Column(String(500), nullable=False)
    release_year = Column(Integer)
    genres = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())

    ratings = relationship("Rating", back_populates="movie")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Numeric(2, 1), nullable=False)
    rated_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")
