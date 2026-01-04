from fastapi import FastAPI
from app.api.db import database, metadata, engine
from app.api.movies import movies

app = FastAPI(
    openapi_url="/api/v1/movies/openapi.json",
    docs_url="/api/v1/movies/docs"
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(movies, prefix="/api/v1/movies", tags=["movies"])

