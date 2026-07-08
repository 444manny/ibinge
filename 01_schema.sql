-- ============================================================
-- Movie Recommender Database Schema
-- ============================================================

-- Users of our application (not the same as MovieLens's raw user ids,
-- but we keep the mapping simple by reusing their ids)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Movies catalog
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    external_id INTEGER UNIQUE,          -- original MovieLens movie id, for re-importing
    title VARCHAR(500) NOT NULL,
    release_year INTEGER,
    genres TEXT[],                        -- e.g. {'Action','Sci-Fi'}
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Ratings: the core signal our recommender learns from
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    rating NUMERIC(2,1) NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
    rated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, movie_id)            -- one rating per user per movie
);

-- ============================================================
-- Indexes — these matter once you're querying "all ratings for
-- a movie" or "all ratings by a user" at any real scale.
-- ============================================================
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_movie_id ON ratings(movie_id);
CREATE INDEX idx_movies_external_id ON movies(external_id);

-- GIN index lets us efficiently query "movies with genre X"
CREATE INDEX idx_movies_genres ON movies USING GIN (genres);
