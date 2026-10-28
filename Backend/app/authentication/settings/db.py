"""PostgreSQL connections with validated SSL settings."""

import logging
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")
DB_CONNECT_TIMEOUT_SECONDS = int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "3"))

logger = logging.getLogger(__name__)


def database_connection():
    """Open a connection, or return ``None`` when the database is unreachable."""
    required = (
        ("DB_HOST", DB_HOST),
        ("DB_NAME", DB_NAME),
        ("DB_USER", DB_USER),
        ("DB_PASSWORD", DB_PASSWORD),
    )
    missing = [name for name, value in required if not value]
    if missing:
        logger.error("Missing database settings: %s", ", ".join(missing))
        return None

    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode=DB_SSLMODE,
            cursor_factory=RealDictCursor,
            connect_timeout=DB_CONNECT_TIMEOUT_SECONDS,
        )
    except psycopg2.Error:
        logger.exception("Database connection error")
        return None
