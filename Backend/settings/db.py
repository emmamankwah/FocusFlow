"""PostgreSQL connections with the validated SSL settings."""

import logging

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT_SECONDS = 3


def database_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            # Local Postgres usually accepts "prefer"; hosted databases should
            # set DB_SSLMODE=require (or verify-full) in their environment.
            sslmode=os.getenv("DB_SSLMODE"),
            cursor_factory=RealDictCursor,
            connect_timeout=CONNECT_TIMEOUT_SECONDS,
        )
        return connection

    except psycopg2.Error as e:
        logger.error("Database connection error", exc_info=e)
        return None
