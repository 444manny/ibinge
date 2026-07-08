# Movie Recommender — Day 1: Data + Database

## What's in this folder so far

```
movie-recommender/
├── docker-compose.yml   # spins up local Postgres
├── sql/
│   └── 01_schema.sql    # runs automatically on first container start
├── scripts/
│   └── load_data.py     # loads MovieLens CSVs into Postgres
├── data/                # put movies.csv + ratings.csv here (not committed)
└── requirements.txt
```

## Step-by-step

### 1. Get Docker running and start Postgres

```bash
docker compose up -d
```

This starts a Postgres 16 container, creates the `movie_recommender` database,
and automatically runs `sql/01_schema.sql` to create your tables.

Check it worked:

```bash
docker exec -it movie_recommender_db psql -U movieapp -d movie_recommender -c "\dt"
```

You should see `users`, `movies`, `ratings`.

### 2. Download the dataset

Go to https://grouplens.org/datasets/movielens/100k/ and download
**ml-latest-small.zip**. Unzip it, then copy `movies.csv` and `ratings.csv`
into this project's `data/` folder.

### 3. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate       # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 4. Load the data

```bash
cd scripts
python load_data.py
```

You should see output like:

```
Loaded 9742 movies.
Loaded 610 placeholder users.
Loaded 100836 ratings (0 skipped due to missing refs).
Done.
```

### 5. Sanity-check it in the database

```bash
docker exec -it movie_recommender_db psql -U movieapp -d movie_recommender
```

Then try:

```sql
SELECT title, release_year, genres FROM movies LIMIT 5;
SELECT COUNT(*) FROM ratings;
SELECT m.title, AVG(r.rating) AS avg_rating, COUNT(*) AS num_ratings
FROM ratings r JOIN movies m ON m.id = r.movie_id
GROUP BY m.title
ORDER BY num_ratings DESC
LIMIT 10;
```

That last query gives you the most-rated movies — a nice way to confirm
everything loaded correctly, and it's also useful later for your
"cold start" fallback (recommend popular movies to new users).

## Why this schema

- **`users`** — real accounts in your app (MovieLens doesn't give us real
  users, so the loader creates placeholder ones — see the script comments).
- **`movies`** — `external_id` keeps the original MovieLens id around so you
  can always re-import or cross-reference; `genres` is a Postgres array so
  you can query "all Sci-Fi movies" without a join to a separate genres table.
- **`ratings`** — the actual signal your recommender will learn from. The
  `UNIQUE (user_id, movie_id)` constraint keeps one rating per user per movie,
  matching real-world behavior (you can update a rating, not duplicate it).
- **Indexes** on `user_id` and `movie_id` in `ratings` matter because your
  recommendation engine will constantly ask "give me all ratings for user X"
  or "all ratings for movie Y" — without an index that's a full table scan.

## Next: Day 3-4

Once your data's loaded and you've run a few sanity-check queries, we'll
build the FastAPI layer on top of this (`GET /movies`, `GET /movies/{id}`,
`POST /ratings`, etc.).
