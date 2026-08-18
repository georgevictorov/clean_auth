import os


def get_postgres_uri():
    return os.getenv("DATABASE_URL")
