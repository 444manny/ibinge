# 🎬 iBinge

iBinge is my take on a movie recommendation app — built from scratch so I could
actually understand how recommendation engines work under the hood, instead of
just calling someone else's API.

I'm building it in stages: get real movie data into a real database first, then
layer an API on top, then get into the actual recommendation logic (starting
simple with popularity/cold-start, working up to collaborative filtering with
scikit-learn). This README tracks where things stand and what I've learned
along the way.

## Features so far

- **Real dataset, not fake data** — loads the MovieLens dataset (9,700+ movies,
  100k+ ratings) into Postgres instead of using seed/mock data.
- **A schema I actually designed on purpose** — `users`, `movies`, and `ratings`
  tables, with a `UNIQUE (user_id, movie_id)` constraint so a rating gets
  updated instead of duplicated, and indexes on the columns I know the
  recommender will hammer (`user_id`, `movie_id`, and a GIN index on `genres`
  for fast "all Sci-Fi movies" style lookups).
- **One-command local setup** — `docker compose up -d` spins up Postgres and
  runs the schema automatically, no manual `psql` setup required.
- **A data loader that cleans up after MovieLens** — parses release years out
  of titles like `Toy Story (1995)`, splits pipe-delimited genres into arrays,
  and maps MovieLens's raw ids to my own so the data can be re-imported safely.

## My journey

**Day 1 — Data + database.** Before writing a single line of recommendation
logic, I wanted a solid data layer. That meant picking Postgres over just
reading CSVs at runtime, designing a schema that wouldn't fall over once
ratings started piling up, and writing a loader script to get the real
MovieLens dataset into it. Getting the schema right up front (indexes,
constraints, the `external_id` mapping) saved me from having to redo this
later.

**Next up — the API layer.** Building out FastAPI endpoints
(`GET /movies`, `GET /movies/{id}`, `POST /ratings`) on top of this database,
then starting on the actual recommendation logic with scikit-learn.

## Tech stack

- **Postgres** — the source of truth for movies, users, and ratings
- **Python** (pandas, psycopg2) — data loading and cleaning
- **FastAPI** — the API layer (in progress)
- **scikit-learn** — recommendation logic (coming soon)
- **Docker Compose** — local dev environment

## Running it locally

```bash
# 1. Start Postgres (creates the DB and runs the schema automatically)
docker compose up -d

# 2. Grab the dataset from https://grouplens.org/datasets/movielens/100k/
#    (ml-latest-small.zip) and drop movies.csv + ratings.csv into data/

# 3. Install dependencies
python -m venv venv
source venv/bin/activate       # venv\Scripts\activate on Windows
pip install -r requirements.txt

# 4. Load the data
python load_data.py
```

Check it worked:

```sql
SELECT title, release_year, genres FROM movies LIMIT 5;
SELECT COUNT(*) FROM ratings;
```
