from fastapi import FastAPI

from .routers import auth, movies, ratings

app = FastAPI(
    title="Binge API",
    description="A movie recommendation API — browse movies, rate them, and get personalized suggestions.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(ratings.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "binge-api"}
