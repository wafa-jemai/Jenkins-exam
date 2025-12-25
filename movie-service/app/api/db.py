import os
from sqlalchemy import Column, Integer, String, Table, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL must be set")

metadata = MetaData()

movies = Table(
    "movies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("plot", String(250)),
)

database = Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL)

