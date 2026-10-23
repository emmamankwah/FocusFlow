"""
repository/user.py
==================

Data-access layer for user accounts and one-time passwords (OTPs).

Layer rules enforced here
-------------------------
* This module imports **nothing** from ``service``.  That single rule is what
  removes the old ``service.users <-> repository.user`` circular import.
* It takes plain values (``str``, ``int``) -- never Pydantic request models --
  so the storage layer does not depend on the HTTP layer.
* It translates ``psycopg2`` errors into two small domain exceptions
  (:class:`RepositoryError`, :class:`DuplicateUser`) so callers never need to
  import the database driver.
* Every statement is parameterised with ``%s``; SQL is never built by string
  formatting.
* Connections come from a lazily created, thread-safe pool and are always
  returned, so we no longer pay a TCP + authentication handshake per query.

The service layer owns business rules (normalising addresses, expiry
decisions, attempt limits).  This module only reads and writes rows.
"""

from __future__ import annotations  # Allow modern type hints (``dict | None``) on every supported Python.

import logging  # Standard-library logging for diagnostics.
import os  # Read database settings from environment variables.
import threading  # Serialise one-time creation of the connection pool.
from contextlib import contextmanager  # Build the ``connection()`` context manager.
from typing import Any, Iterator  # Type hints for dictionaries and the generator.

import psycopg2  # PostgreSQL driver.
from psycopg2 import pool  # Thread-safe connection pool implementation.
from psycopg2.extras import RealDictCursor  # Return rows as dictionaries instead of tuples.

logger = logging.getLogger(__name__)  # Namespaced logger; never rebind the ``logging`` module itself.


# ---------------------------------------------------------------------------
# Domain exceptions raised by this layer
# ---------------------------------------------------------------------------
class RepositoryError(Exception):  # Base class for every failure originating here.
    """An unexpected failure while talking to PostgreSQL (mapped to HTTP 503 upstream)."""


class DuplicateUser(RepositoryError):  # Raised when a UNIQUE constraint rejects an INSERT.
    """A row already exists for the given email or username."""

    def __init__(self, field: str = "unknown") -> None:  # ``field`` tells the service which one clashed.
        self.field = field  # Remember it so the service can raise EmailTaken/UsernameTaken.
        super().__init__(f"Duplicate value for {field}")  # Human-readable message for logs.


# ---------------------------------------------------------------------------
# Connection pooling
# ---------------------------------------------------------------------------
_pool: pool.ThreadedConnectionPool | None = None  # Module-level pool, created on first use.
_pool_lock = threading.Lock()  # Prevents two threads from creating two pools.


def _connection_kwargs() -> dict[str, Any]:  # One place that knows how to reach PostgreSQL.
    return {  # Keyword arguments accepted by ``psycopg2.connect``.
        "host": os.getenv("DB_HOST", "localhost"),  # Database host.
        "database": os.getenv("DB_NAME", "postgres"),  # Database name.
        "user": os.getenv("DB_USER"),  # Database user.
        "password": os.getenv("DB_PASSWORD"),  # Database password.
        "connect_timeout": 3,  # Fail fast instead of hanging a request for minutes.
    }


def _get_pool() -> pool.ThreadedConnectionPool:  # Lazy accessor for the shared pool.
    global _pool  # We assign to the module-level name.
    if _pool is not None:  # Fast path: the pool already exists.
        return _pool  # Hand it straight back.
    with _pool_lock:  # Slow path: only one thread may build it.
        if _pool is None:  # Double-checked locking: another thread may have won.
            try:  # Pool construction opens ``minconn`` connections immediately.
                _pool = pool.ThreadedConnectionPool(  # Create the pool exactly once.
                    minconn=1,  # Keep one warm connection ready for the next request.
                    maxconn=10,  # Cap concurrent connections so we never exhaust Postgres.
                    **_connection_kwargs(),  # Host, database, user, password, timeout.
                )  # End of pool construction.
            except psycopg2.Error as exc:  # Database unreachable or bad credentials.
                raise RepositoryError("could not create the database pool") from exc  # Surface as a domain error.
        return _pool  # Return the pool that now exists.


@contextmanager  # Turn this generator into a ``with`` block.
def connection() -> Iterator[Any]:  # Yields a borrowed connection and always returns it.
    """Borrow a pooled connection for the duration of a ``with`` block."""
    pool_ = _get_pool()  # Make sure the pool exists.
    try:  # ``getconn`` raises when every connection is already checked out.
        conn = pool_.getconn()  # Borrow a connection from the pool.
    except pool.PoolError as exc:  # Pool exhausted (all ``maxconn`` connections busy).
        raise RepositoryError("database pool exhausted") from exc  # Report it as a 503-class failure.
    try:  # Everything below always returns the connection to the pool.
        yield conn  # Hand the connection to the body of the ``with`` block.
    finally:  # Runs even when the body raises.
        healthy = not conn.closed  # A connection can die mid-statement.
        if healthy:  # Only try to clean up a live connection.
            try:  # ``rollback`` discards anything left uncommitted.
                conn.rollback()  # Guarantees the next borrower of this connection starts clean.
            except psycopg2.Error:  # The connection broke while rolling back.
                healthy = False  # Treat it as dead so the pool replaces it.
        pool_.putconn(conn, close=not healthy)  # Return it, or discard it if it is broken.


def _duplicate_field(exc: psycopg2.errors.UniqueViolation) -> str:  # Work out which column clashed.
    constraint = (getattr(exc.diag, "constraint_name", None) or "").lower()  # Postgres names the violated constraint.
    if "username" in constraint:  # A username index/constraint was hit.
        return "username"  # Tell the caller.
    if "email" in constraint:  # An email index/constraint was hit.
        return "email"  # Tell the caller.
    return "unknown"  # Fall back to a generic answer.


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------
def get_user_by_email(email: str) -> dict[str, Any] | None:  # Look up an account by its email address.
    """Return the full account row (including the password hash), or ``None``."""
    sql = (  # Query: read one account, including the hash that login needs.
        """
        SELECT id,            -- Surrogate key used by callers and logs.
               first_name,    -- Given name.
               last_name,     -- Family name.
               email,         -- Normalised login address.
               username,      -- Unique handle.
               password,      -- Argon2 hash; only this function returns it.
               is_verified,   -- Whether the email has been confirmed.
               created_at     -- Registration timestamp.
          FROM users          -- Account table.
         WHERE email = %s     -- Parameterised predicate.
        """
    )
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Rows come back as dicts.
                cur.execute(sql, (email,))  # Run the query with the bound value.
                return cur.fetchone()  # One row or ``None``; never more.
    except psycopg2.Error as exc:  # Network failure, syntax error, missing table, ...
        logger.exception("get_user_by_email failed")  # Keep the traceback for debugging.
        raise RepositoryError("get_user_by_email failed") from exc  # Hide the driver from callers.


def get_user_by_username(username: str) -> dict[str, Any] | None:  # Look up an account by its handle.
    """Return a public account row (no password hash), or ``None``."""
    sql = (  # Query: read one account without exposing the hash.
        """
        SELECT id,            -- Surrogate key.
               first_name,    -- Given name.
               last_name,     -- Family name.
               email,         -- Address (not a secret here).
               username,      -- Handle.
               is_verified,   -- Confirmation flag.
               created_at     -- Registration timestamp.
          FROM users          -- Account table.
         WHERE username = %s  -- Parameterised predicate.
        """
    )
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Rows come back as dicts.
                cur.execute(sql, (username,))  # Run the query with the bound value.
                return cur.fetchone()  # One row or ``None``.
    except psycopg2.Error as exc:  # Any driver-level failure.
        logger.exception("get_user_by_username failed")  # Log with traceback.
        raise RepositoryError("get_user_by_username failed") from exc  # Re-raise as a domain error.


def create_user(  # Insert a brand-new account.
    first_name: str,  # Given name, already trimmed by the service.
    last_name: str,  # Family name, already trimmed by the service.
    email: str,  # Normalised, lower-cased address.
    username: str,  # Trimmed handle.
    password_hash: str,  # Argon2 digest -- an opaque string from this layer's point of view.
) -> int:  # Returns the new row's primary key.
    """Insert an account and return its id. Raises :class:`DuplicateUser` on a clash."""
    sql = (  # Query: one round-trip insert that also reports the new key.
        """
        INSERT INTO users (first_name, last_name, email, username, password)  -- Columns we supply.
             VALUES (%s, %s, %s, %s, %s)  -- Five bound parameters, in this order.
          RETURNING id  -- Ask Postgres for the generated key.
        """
    )
    try:  # Order matters: UniqueViolation is a subclass of psycopg2.Error.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # We need the returned row as a dict.
                cur.execute(sql, (first_name, last_name, email, username, password_hash))  # Bind all five values.
                row = cur.fetchone()  # Capture the ``RETURNING id`` row.
            conn.commit()  # Persist the insert; ``connection()`` only borrows, it does not commit.
            return int(row["id"])  # Give the service a usable identifier.
    except psycopg2.errors.UniqueViolation as exc:  # Email or username already taken.
        raise DuplicateUser(_duplicate_field(exc)) from exc  # Tell the service which one.
    except psycopg2.Error as exc:  # Every other database failure.
        logger.exception("create_user failed")  # Keep the traceback.
        raise RepositoryError("create_user failed") from exc  # Surface as a domain error.


def mark_user_verified(email: str) -> bool:  # Flip the confirmation flag after a successful OTP check.
    """Set ``is_verified`` for an account. Returns ``True`` when a row was updated."""
    sql = "UPDATE users SET is_verified = TRUE WHERE email = %s"  # Single, parameterised statement.
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor() as cur:  # No rows are returned, so a plain cursor is enough.
                cur.execute(sql, (email,))  # Run the update.
                updated = cur.rowcount == 1  # Exactly one account should match.
            conn.commit()  # Persist the change.
            return updated  # Tell the service whether anything changed.
    except psycopg2.Error as exc:  # Any driver-level failure.
        logger.exception("mark_user_verified failed")  # Log with traceback.
        raise RepositoryError("mark_user_verified failed") from exc  # Re-raise as a domain error.


def update_user_password(email: str, password_hash: str) -> bool:  # Replace an account's password digest.
    """Store a new password hash. Returns ``True`` when a row was updated."""
    sql = "UPDATE users SET password = %s WHERE email = %s"  # Never store plaintext.
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor() as cur:  # No rows are returned.
                cur.execute(sql, (password_hash, email))  # Bind the hash first, then the address.
                updated = cur.rowcount == 1  # Exactly one account should match.
            conn.commit()  # Persist the change.
            return updated  # Tell the service whether anything changed.
    except psycopg2.Error as exc:  # Any driver-level failure.
        logger.exception("update_user_password failed")  # Log with traceback.
        raise RepositoryError("update_user_password failed") from exc  # Re-raise as a domain error.


# ---------------------------------------------------------------------------
# One-time passwords
# ---------------------------------------------------------------------------
def create_otp(  # Insert or replace the OTP for an address.
    email: str,  # Account the code belongs to.
    otp_hash: str,  # Argon2 digest of the six-digit code.
    ttl_minutes: int,  # How long the code stays valid.
    total_attempts: int,  # How many wrong guesses are tolerated.
) -> None:  # Nothing to return.
    """Insert or replace an OTP and reset its attempt counter.

    Requires ``UNIQUE (email)`` on ``otp_table`` so the ``ON CONFLICT`` clause
    can target the existing row instead of creating duplicates on resend.
    """
    sql = (  # Query: upsert so a resend replaces the previous code.
        """
        INSERT INTO otp_table (email, hash_otp, created_at, expired_at, attempts, total_attempts)  -- Columns.
             VALUES (%s, %s, now(), now() + (%s * interval '1 minute'), 0, %s)  -- Postgres owns the clock.
        ON CONFLICT (email) DO UPDATE  -- A resend replaces the previous code.
                SET hash_otp       = EXCLUDED.hash_otp,  -- Use the freshly generated digest.
                    created_at     = EXCLUDED.created_at,  -- Restart the validity window.
                    expired_at     = EXCLUDED.expired_at,  -- Restart the validity window.
                    attempts       = 0,  -- Give the user a clean slate.
                    total_attempts = EXCLUDED.total_attempts  -- Pick up configuration changes.
        """
    )
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor() as cur:  # No rows are returned.
                cur.execute(sql, (email, otp_hash, ttl_minutes, total_attempts))  # Bind all four values.
            conn.commit()  # Persist the insert or update.
    except psycopg2.Error as exc:  # Driver-level failure, e.g. no UNIQUE(email) on otp_table.
        logger.exception("create_otp failed")  # Log with traceback.
        raise RepositoryError("create_otp failed") from exc  # Re-raise as a domain error.


def get_otp(email: str) -> dict[str, Any] | None:  # Read the current code record for an address.
    """Return the OTP row including a server-computed ``is_expired`` flag."""
    sql = (  # Query: let Postgres decide expiry so clocks cannot disagree.
        """
        SELECT hash_otp,                          -- Digest to compare against the submitted code.
               attempts,                          -- Wrong guesses so far.
               total_attempts,                    -- Wrong guesses allowed.
               created_at,                        -- When the code was issued.
               expired_at,                        -- When it stops being valid.
               (expired_at <= now()) AS is_expired  -- Server-side comparison, no timezone guesswork.
          FROM otp_table                              -- OTP table.
         WHERE email = %s                             -- Parameterised lookup.
        """
    )
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Rows come back as dicts.
                cur.execute(sql, (email,))  # Run the query.
                return cur.fetchone()  # One row or ``None``.
    except psycopg2.Error as exc:  # Any driver-level failure.
        logger.exception("get_otp failed")  # Log with traceback.
        raise RepositoryError("get_otp failed") from exc  # Re-raise as a domain error.


def delete_otp(email: str) -> None:  # Remove the code entirely once it is used or expired.
    """Delete the OTP row for an address (no half-cleared rows left behind)."""
    sql = "DELETE FROM otp_table WHERE email = %s"  # Deleting beats NULLing: no poisoned row can survive.
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor() as cur:  # No rows are returned.
                cur.execute(sql, (email,))  # Run the delete.
            conn.commit()  # Persist the delete.
    except psycopg2.Error as exc:  # Any driver-level failure.
        logger.exception("delete_otp failed")  # Log with traceback.
        raise RepositoryError("delete_otp failed") from exc  # Re-raise as a domain error.


def increment_otp_attempts(email: str) -> int:  # Count a wrong guess and report the new total.
    """Increment the failed-attempt counter. Returns the new value.

    This intentionally **raises** on failure: silently swallowing an error here
    would hand an attacker an unlimited number of OTP guesses.
    """
    sql = (  # Query: bump the counter and read it back in one statement.
        """
        UPDATE otp_table                    -- Target the OTP row.
           SET attempts = attempts + 1      -- Count this wrong guess.
         WHERE email = %s                   -- Parameterised lookup.
     RETURNING attempts                     -- Report the new total for lockout decisions.
        """
    )
    try:  # Translate driver failures into domain errors.
        with connection() as conn:  # Borrow a pooled connection.
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # We need the returned row.
                cur.execute(sql, (email,))  # Run the update.
                row = cur.fetchone()  # Capture the ``RETURNING attempts`` row.
            conn.commit()  # Persist the counter bump.
            return int(row["attempts"]) if row else 0  # 0 means the row vanished mid-flight.
    except psycopg2.Error as exc:  # Any driver-level failure -- deliberately not swallowed.
        logger.exception("increment_otp_attempts failed")  # Log with traceback.
        raise RepositoryError("increment_otp_attempts failed") from exc  # Re-raise as a domain error.
