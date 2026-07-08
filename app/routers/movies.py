from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=list[schemas.MovieOut])
def list_movies(
    search: Optional[str] = Query(None, description="Filter by title, case-insensitive"),
    genre: Optional[str] = Query(None, description="Filter by exact genre, e.g. 'Comedy'"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.Movie)

    if search:
        query = query.filter(models.Movie.title.ilike(f"%{search}%"))
    if genre:
        query = query.filter(models.Movie.genres.any(genre))

    return query.order_by(models.Movie.title).offset(offset).limit(limit).all()


@router.get("/{movie_id}", response_model=schemas.MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
