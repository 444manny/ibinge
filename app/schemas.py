"""
Pydantic schemas — these define the shape of data going IN to the API
(request bodies) and OUT of the API (responses). FastAPI uses these to
auto-validate requests and auto-generate the /docs page.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ---------- Users / Auth ----------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Movies ----------

class MovieOut(BaseModel):
    id: int
    title: str
    release_year: Optional[int]
    genres: list[str]

    class Config:
        from_attributes = True


# ---------- Ratings ----------

class RatingCreate(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=0.5, le=5.0)


class RatingOut(BaseModel):
    id: int
    movie_id: int
    rating: float
    rated_at: datetime

    class Config:
        from_attributes = True
