import logging
from psycopg2.extras import RealDictCursor
from settings.db import database_connection



def _connect():
    connection = database_connection()
    if connection is None:
        raise ConnectionError("Database connection failed.")
    return connection


def get_user_by_email(email:str) -> dict |None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email,username,password FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_username(username: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email,username,password FROM users WHERE username = %s", (username,))
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(first_name, last_name, email, username, hash_password):
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




def save_pending_user(first_name, last_name, email, username, hash_password):
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            # One pending row per email: re-staging replaces the old one
            # instead of failing on a unique constraint.
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,),)
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


def get_pending_user(email: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT email FROM pending_users WHERE email = %s",
                (email,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def move_pending_user_to_users(email: str) -> None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT first_name, last_name, email, username, password "
                "FROM pending_users WHERE email = %s",
                (email,),
            )
            pending_user = cursor.fetchone()
            if not pending_user:
                raise ValueError("No pending user found for this email.")
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    pending_user["first_name"],
                    pending_user["last_name"],
                    pending_user["email"],
                    pending_user["username"],
                    pending_user["password"],
                ),
            )
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,),)
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
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,),)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def save_otp(email: str, hash_otp: str, created_at, expired_at, total_attempts: int):
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM otp_table WHERE email = %s", (email,),)
            cursor.execute(
                """
                INSERT INTO otp_table (email, hash_otp, created_at, expired_at, attempts, total_attempts)
                VALUES (%s, %s, %s, %s, 0, %s)
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




def increment_attempts(email: str):
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "UPDATE otp_table SET attempts = attempts + 1 WHERE email = %s RETURNING attempts, total_attempts",
                (email,),
            )
            row = cursor.fetchone()
        connection.commit()
        return row
    except Exception:
        connection.rollback()
        logging.exception("Failed to increment OTP attempts")
        raise
    finally:
        connection.close()


def clear_otp(email: str) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM otp_table WHERE email = %s", (email,),)
        connection.commit()
    except Exception:
        connection.rollback()
        logging.exception("Failed to clear OTP")
        raise
    finally:
        connection.close()


def update_user_password(email: str, hashed_password: str):
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
