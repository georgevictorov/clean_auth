import pytest
from psycopg_pool import ConnectionPool

from auth.config import get_postgres_uri


@pytest.fixture(scope="session")
def db_pool():
    with ConnectionPool(
            conninfo=get_postgres_uri(),
            min_size=1,
            max_size=4,
    ) as pool:
        yield pool


@pytest.fixture
def db_connection(db_pool):
    with db_pool.connection() as conn:
        yield conn


@pytest.fixture
def clean_db(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("TRUNCATE users, sessions CASCADE")
    db_connection.commit()
