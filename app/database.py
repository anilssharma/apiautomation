import sqlite3
from pathlib import Path
from typing import Iterator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

from app.models import metadata


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "001_create_tables.sql"


def create_database_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def initialize_database(engine: Engine) -> None:
    metadata.create_all(engine)


def get_connection(request: Request) -> Iterator[Connection]:
    with request.app.state.engine.connect() as connection:
        yield connection