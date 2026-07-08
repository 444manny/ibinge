"""
Loads the MovieLens dataset (ml-latest-small or ml-100k) into Postgres.

Expects two CSV files in ../data/:
  - movies.csv   (columns: movieId, title, genres)
  - ratings.csv  (columns: userId, movieId, rating, timestamp)

These come straight from https://grouplens.org/datasets/movielens/100k/
Download "ml-latest-small.zip", unzip it, and copy movies.csv + ratings.csv
into the data/ folder before running this.

Usage:
    pip install -r ../requirements.txt
    python load_data.py
"""

import os
import re
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "movie_recommender"),
    "user": os.environ.get("DB_USER", "movieapp"),
    "password": os.environ.get("DB_PASSWORD", "devpassword"),
}

DATA_DIR = "data"


def parse_year(title: str):
    """MovieLens titles look like 'Toy Story (1995)' — pull the year out."""
    match = re.search(r"\((\d{4})\)\s*$", title)
    return int(match.group(1)) if match else None


def clean_title(title: str):
    return re.sub(r"\s*\(\d{4}\)\s*$", "", title).strip()


def load_movies(conn, movies_df):
    rows = []
    for _, row in movies_df.iterrows():
        genres = row["genres"].split("|") if row["genres"] != "(no genres listed)" else []
        rows.append((
            int(row["movieId"]),
            clean_title(row["title"]),
            parse_year(row["title"]),
            genres,
        ))

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO movies (external_id, title, release_year, genres)
            VALUES %s
            ON CONFLICT (external_id) DO NOTHING
            """,
            rows,
        )
    conn.commit()
    print(f"Loaded {len(rows)} movies.")


def load_users(conn, ratings_df):
    """MovieLens doesn't give us real user accounts, just numeric ids.
    We create a placeholder user row for each unique id so ratings
    have someone to belong to. In a real app these would be signups."""
    unique_user_ids = ratings_df["userId"].unique()
    rows = [
        (f"ml_user_{uid}", f"ml_user_{uid}@example.com", "not_a_real_password")
        for uid in unique_user_ids
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO users (username, email, password_hash)
            VALUES %s
            ON CONFLICT (username) DO NOTHING
            """,
            rows,
        )
    conn.commit()
    print(f"Loaded {len(rows)} placeholder users.")


def load_ratings(conn, ratings_df):
    # Build lookup maps from external MovieLens ids -> our internal serial ids
    with conn.cursor() as cur:
        cur.execute("SELECT id, external_id FROM movies")
        movie_map = {ext_id: internal_id for internal_id, ext_id in cur.fetchall()}

        cur.execute("SELECT id, username FROM users")
        user_map = {
            int(username.replace("ml_user_", "")): internal_id
            for internal_id, username in cur.fetchall()
        }

    rows = []
    skipped = 0
    for _, row in ratings_df.iterrows():
        movie_id = movie_map.get(int(row["movieId"]))
        user_id = user_map.get(int(row["userId"]))
        if movie_id is None or user_id is None:
            skipped += 1
            continue
        rows.append((user_id, movie_id, float(row["rating"])))

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ratings (user_id, movie_id, rating)
            VALUES %s
            ON CONFLICT (user_id, movie_id) DO NOTHING
            """,
            rows,
        )
    conn.commit()
    print(f"Loaded {len(rows)} ratings ({skipped} skipped due to missing refs).")


def main():
    movies_df = pd.read_csv(f"{DATA_DIR}/movies.csv")
    ratings_df = pd.read_csv(f"{DATA_DIR}/ratings.csv")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        load_movies(conn, movies_df)
        load_users(conn, ratings_df)
        load_ratings(conn, ratings_df)
    finally:
        conn.close()

    print("Done.")


if __name__ == "__main__":
    main()
