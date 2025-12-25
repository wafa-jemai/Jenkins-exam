import os
from sqlalchemy import Column, Integer, String, Table, MetaData, create_engine
from sqlalchemy.dialects.sqlite import JSON
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL must be set")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

metadata = MetaData()

movies = Table(
    "movies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("plot", String(250)),
    Column("genres", JSON),
    Column("casts_id", JSON),
)

database = Database(DATABASE_URL)

