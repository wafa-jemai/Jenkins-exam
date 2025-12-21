from fastapi import FastAPI
from app.api.movies import movies
from app.api.db import metadata, database, engine
import asyncio
import uvicorn

metadata.create_all(engine)

# Fix uvloop bug: force default event loop policy
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

app = FastAPI(openapi_url="/api/v1/movies/openapi.json", docs_url="/api/v1/movies/docs")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(movies, prefix='/api/v1/movies', tags=['movies'])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        reload=False
    )

