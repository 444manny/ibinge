"""
Sets up the SQLAlchemy engine and session that the rest of the app uses
to talk to Postgres. Keeping this in its own file means every other
module just imports `get_db` instead of re-configuring a connection.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Matches the credentials in docker-compose.yml.
# In a real deployment you'd load this from an environment variable instead
# of hardcoding it — we'll switch to that when we deploy to AWS (RDS).
DATABASE_URL = "postgresql://movieapp:devpassword@localhost:5432/movie_recommender"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: gives each request its own DB session,
    and always closes it afterwards even if the request raised an error."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
