import os
from sqlalchemy import (
    MetaData, Table, Column, Integer, String
)
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/api/db.sqlite3")

database = Database(DATABASE_URL)
metadata = MetaData()

movies = Table(
    "movies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("description", String),
)

casts = Table(
    "casts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("movie_id", Integer),
    Column("actor", String),
)

