import logging
from psycopg2.extras import RealDictCursor
from settings.db import database_connection


def _connect():
    connection = database_connection()
    if connection is None:
        raise ConnectionError("Database connection failed.")
    return connection


def get_user_by_email(email):
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_username(username: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(first_name, last_name, email, username, hash_password) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password) "
                "VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, email, username, hash_password),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def save_pending_user(first_name, last_name, email, username, hash_password) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,))
            cursor.execute(
                """
                INSERT INTO pending_users (first_name, last_name, email, username, password)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (first_name, last_name, email, username, hash_password),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def move_pending_user_to_users(email: str) -> None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM pending_users WHERE email = %s", (email,))
            pending = cursor.fetchone()
            if not pending:
                raise ValueError("No pending user found for this email.")
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password) VALUES (%s, %s, %s, %s, %s)",
                (pending["first_name"], pending["last_name"], pending["email"], pending["username"], pending["password"]),
            )
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_pending_user(email: str) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def save_otp(email: str, hash_otp: str, created_at, expired_at, total_attempts: int = 5) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO otp_table (email, hash_otp, created_at, expired_at, attempts, total_attempts)
                VALUES (%s, %s, %s, %s, 0, %s)
                ON CONFLICT (email) DO UPDATE SET
                    hash_otp = EXCLUDED.hash_otp,
                    created_at = EXCLUDED.created_at,
                    expired_at = EXCLUDED.expired_at,
                    attempts = 0,
                    total_attempts = EXCLUDED.total_attempts
                """,
                (email, hash_otp, created_at, expired_at, total_attempts),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_user_otp(email: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT email, hash_otp, created_at, expired_at, attempts, total_attempts FROM otp_table WHERE email = %s",
                (email,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_otp_row(email: str) -> dict | None:
    return get_user_otp(email)


def verify_user_otp(email: str, otp: str = None) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT email, hash_otp, created_at, expired_at, attempts, total_attempts FROM otp_table WHERE email = %s",
                (email,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def increment_attempts(email: str) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE otp_table SET attempts = attempts + 1 WHERE email = %s",
                (email,),
            )
        connection.commit()
    except Exception:
        logging.exception("Failed to increment OTP attempts")
        raise
    finally:
        connection.close()


def clear_otp(email: str) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE otp_table 
                SET hash_otp = NULL, 
                    expired_at = NULL, 
                    attempts = 0 
                WHERE email = %s
                """,
                (email,),
            )
        connection.commit()
    except Exception:
        logging.exception("Failed to clear OTP")
        raise
    finally:
        connection.close()


def update_user_password(email: str, hashed_password: str) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (hashed_password, email),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
