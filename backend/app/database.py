from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import settings


engine: Engine | None = (
    create_engine(settings.database_url, future=True)
    if settings.database_url
    else None
)


@contextmanager
def get_connection():
    if engine is None:
        yield None
        return
    with engine.begin() as conn:
        yield conn


def insert_rows(table_name: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    if engine is None:
        return len(rows)
    keys = list(rows[0].keys())
    columns = ", ".join(keys)
    values = ", ".join(f":{key}" for key in keys)
    statement = text(f"INSERT INTO data_asset.{table_name} ({columns}) VALUES ({values})")
    with get_connection() as conn:
        assert conn is not None
        conn.execute(statement, rows)
    return len(rows)
