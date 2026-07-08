from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=schemas.RatingOut, status_code=201)
def rate_movie(
    rating_in: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    movie = db.query(models.Movie).filter(models.Movie.id == rating_in.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Upsert: if this user already rated this movie, update it instead
    # of erroring — matches how rating a movie twice should behave.
    stmt = insert(models.Rating).values(
        user_id=current_user.id,
        movie_id=rating_in.movie_id,
        rating=rating_in.rating,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "movie_id"],
        set_={"rating": rating_in.rating},
    ).returning(models.Rating.id)

    result = db.execute(stmt)
    db.commit()
    rating_id = result.scalar_one()

    rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    return rating


@router.get("/me", response_model=list[schemas.RatingOut])
def my_ratings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Rating)
        .filter(models.Rating.user_id == current_user.id)
        .order_by(models.Rating.rated_at.desc())
        .all()
    )
