"""
Sets up the SQLAlchemy engine and session that the rest of the app uses
to talk to Postgres. Keeping this in its own file means every other
module just imports `get_db` instead of re-configuring a connection.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "movie_recommender")
DB_USER = os.environ.get("DB_USER", "movieapp")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "devpassword")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
