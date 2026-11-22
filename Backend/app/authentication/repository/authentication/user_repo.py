import logging

import psycopg2
from psycopg2.extras import RealDictCursor

from app.authentication.settings.db import database_connection



def _connect():
    connection = database_connection()
    if connection is None:
        raise ConnectionError("Database connection failed.")
    return connection


def get_user_by_email(email:str) -> dict |None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT u.id, u.first_name, u.last_name, u.email, u.username, u.user_type, "
                "u.password, COALESCE(v.version, 0) AS token_version "
                "FROM users u "
                "LEFT JOIN user_token_versions v ON v.user_id = u.id "
                "WHERE u.email = %s",
                (email,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_id(user_id: int) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT u.id, u.first_name, u.last_name, u.email, u.username, u.user_type, "
                "u.password, COALESCE(v.version, 0) AS token_version "
                "FROM users u "
                "LEFT JOIN user_token_versions v ON v.user_id = u.id "
                "WHERE u.id = %s",
                (user_id,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_username(username: str) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, email, username, password FROM users WHERE username = %s",
                (username,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(first_name, last_name, email, username, hash_password, user_type="other"):
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password, user_type) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, username, hash_password, user_type),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()




def save_pending_user(first_name, last_name, email, username, hash_password, user_type):
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            # One pending row per email; the service refuses re-staging while a
            # pending row exists, so this is a plain insert.
            cursor.execute(
                """
                INSERT INTO pending_users (first_name, last_name, email, username, password, user_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (first_name, last_name, email, username, hash_password, user_type),
            )
        connection.commit()
    except psycopg2.errors.UniqueViolation as exc:
        connection.rollback()
        # Two registrations can pass the pre-checks concurrently; the table's
        # UNIQUE constraint is the final arbiter.
        if exc.diag.constraint_name == "pending_users_username_key":
            raise ValueError("Username already taken.") from exc
        raise
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
                "SELECT first_name, last_name, email, username, password, user_type "
                "FROM pending_users WHERE email = %s",
                (email,),
            )
            pending_user = cursor.fetchone()
            if not pending_user:
                raise ValueError("No pending user found for this email.")
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, username, password, user_type) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    pending_user["first_name"],
                    pending_user["last_name"],
                    pending_user["email"],
                    pending_user["username"],
                    pending_user["password"],
                    pending_user["user_type"],
                ),
            )
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,),)
        connection.commit()
    except psycopg2.errors.UniqueViolation as exc:
        connection.rollback()
        # The username was free at staging time but a verified user claimed it
        # before the code was verified; the pending row can never be promoted.
        if exc.diag.constraint_name == "users_username_key":
            raise ValueError("Username already in use. Please register again.") from exc
        raise
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


def update_user_password(email: str, hashed_password: str) -> int | None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s RETURNING id",
                (hashed_password, email),
            )
            row = cursor.fetchone()
            if row is None:
                connection.rollback()
                return None
            token_version = _bump_token_version(cursor, row["id"])
        connection.commit()
        return token_version
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_user_password_by_id(user_id: int, hashed_password: str) -> int | None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s RETURNING id",
                (hashed_password, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                connection.rollback()
                return None
            token_version = _bump_token_version(cursor, user_id)
        connection.commit()
        return token_version
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_user_profile(user_id: int, first_name, last_name, username):
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET first_name = %s, last_name = %s, "
                "username = %s WHERE id = %s",
                (first_name, last_name, username, user_id),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_token_version(user_id: int) -> int | None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(v.version, 0) AS version "
                "FROM users u "
                "LEFT JOIN user_token_versions v ON v.user_id = u.id "
                "WHERE u.id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            return row["version"] if row else None
    finally:
        connection.close()


def _bump_token_version(cursor, user_id: int) -> int:
    cursor.execute(
        "INSERT INTO user_token_versions (user_id, version) VALUES (%s, 1) "
        "ON CONFLICT (user_id) DO UPDATE SET "
        "version = user_token_versions.version + 1 "
        "RETURNING version",
        (user_id,),
    )
    return cursor.fetchone()["version"]


def get_pending_email_change(user_id: int) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT user_id, new_email, otp_hash, attempts, total_attempts, "
                "created_at, expires_at FROM pending_email_changes "
                "WHERE user_id = %s",
                (user_id,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def save_pending_email_change(
    user_id: int,
    new_email: str,
    otp_hash: str,
    expires_at,
    total_attempts: int,
) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pending_email_changes
                    (user_id, new_email, otp_hash, attempts, total_attempts,
                     created_at, expires_at)
                VALUES (%s, %s, %s, 0, %s, now(), %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    new_email = EXCLUDED.new_email,
                    otp_hash = EXCLUDED.otp_hash,
                    attempts = 0,
                    total_attempts = EXCLUDED.total_attempts,
                    created_at = now(),
                    expires_at = EXCLUDED.expires_at
                """,
                (user_id, new_email, otp_hash, total_attempts, expires_at),
            )
        connection.commit()
    except psycopg2.errors.UniqueViolation as exc:
        connection.rollback()
        raise ValueError("Email already in use.") from exc
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def increment_email_change_attempts(user_id: int) -> dict | None:
    connection = _connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "UPDATE pending_email_changes "
                "SET attempts = attempts + 1 "
                "WHERE user_id = %s "
                "RETURNING attempts, total_attempts",
                (user_id,),
            )
            row = cursor.fetchone()
        connection.commit()
        return row
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_pending_email_change(user_id: int) -> None:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM pending_email_changes WHERE user_id = %s",
                (user_id,),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def email_in_use_exact(email: str, exclude_user_id: int | None = None) -> bool:
    exclude_user_id = exclude_user_id if exclude_user_id is not None else -1
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM users
                    WHERE email = %s AND id <> %s
                UNION ALL
                SELECT 1 FROM pending_users
                    WHERE email = %s
                UNION ALL
                SELECT 1 FROM pending_email_changes
                    WHERE new_email = %s AND user_id <> %s
                LIMIT 1
                """,
                (email, exclude_user_id, email, email, exclude_user_id),
            )
            return cursor.fetchone() is not None
    finally:
        connection.close()


def username_in_use(username: str, exclude_user_id: int | None = None) -> bool:
    """True when a verified user or a pending registration holds the name."""
    exclude_user_id = exclude_user_id if exclude_user_id is not None else -1
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM users
                    WHERE username = %s AND id <> %s
                UNION ALL
                SELECT 1 FROM pending_users
                    WHERE username = %s
                LIMIT 1
                """,
                (username, exclude_user_id, username),
            )
            return cursor.fetchone() is not None
    finally:
        connection.close()


def update_user_email_and_bump_version(user_id: int, new_email: str) -> int:
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM users WHERE id = %s FOR UPDATE",
                (user_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError("User not found.")
            old_email = row["email"]

            cursor.execute(
                """
                SELECT 1 FROM users
                    WHERE email = %s AND id <> %s
                UNION ALL
                SELECT 1 FROM pending_users
                    WHERE email = %s
                UNION ALL
                SELECT 1 FROM pending_email_changes
                    WHERE new_email = %s AND user_id <> %s
                LIMIT 1
                """,
                (new_email, user_id, new_email, new_email, user_id),
            )
            if cursor.fetchone() is not None:
                raise ValueError("Email already in use.")

            cursor.execute(
                "UPDATE users SET email = %s WHERE id = %s",
                (new_email, user_id),
            )
            token_version = _bump_token_version(cursor, user_id)
            cursor.execute(
                "DELETE FROM pending_email_changes WHERE user_id = %s",
                (user_id,),
            )
            cursor.execute(
                "DELETE FROM otp_table WHERE email IN (%s, %s)",
                (old_email, new_email),
            )
        connection.commit()
        return token_version
    except psycopg2.errors.UniqueViolation as exc:
        connection.rollback()
        raise ValueError("Email already in use.") from exc
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
