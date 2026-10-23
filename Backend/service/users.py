"""
service/users.py
================

Business rules for accounts and email verification.

Layer rules enforced here
-------------------------
* Imports point **down** (``repository``) or **sideways** into adapters
  (``security`` for hashing, ``settings.mail`` for SMTP).  This module never
  imports ``psycopg2`` -- driver details stay in the repository.
* Failures are raised as :class:`ServiceError` subclasses.  They carry a
  ``status_code`` and a stable ``code`` so the route layer can translate them
  to HTTP in one small table instead of string-matching error messages.
* :class:`repository.user.RepositoryError` is deliberately allowed to bubble
  up: it means "the database is unavailable", which the app-level exception
  handler maps to HTTP 503.
* Addresses are normalised (trimmed + lower-cased) here, once, before they
  reach storage.
"""

from __future__ import annotations  # Allow modern type hints on every supported Python.

import logging  # Standard-library logging for diagnostics.
import os  # Read OTP configuration from the environment.
from typing import Any  # Type hint for the dictionaries returned to the route layer.

from model.user import (  # Request schemas owned by the API layer.
    ChangePassword,  # Payload for changing a password while signed in.
    ResetPassword,  # Payload for resetting a forgotten password.
    UserLogin,  # Payload for signing in.
    UserRegister,  # Payload for creating an account.
)
from repository.user import (  # Data-access functions; all take/return plain values.
    DuplicateUser,  # Raised when the database rejects a duplicate email or username.
    create_otp,  # Insert or replace an OTP for an address.
    create_user,  # Insert a new account and return its id.
    delete_otp,  # Remove an OTP once it has been used or has expired.
    get_otp,  # Read the current OTP record.
    get_user_by_email,  # Look up an account by address (includes the password hash).
    get_user_by_username,  # Look up an account by handle (no password hash).
    increment_otp_attempts,  # Count a wrong OTP guess and return the new total.
    mark_user_verified,  # Flip ``is_verified`` after a successful OTP check.
    update_user_password,  # Replace an account's password hash.
)
from security.otp import create_secure_otp, verify_otp as verify_otp_hash  # OTP crypto; renamed to avoid shadowing.
from security.users import hash_password, verify_password  # Account-password crypto.
from settings.mail import send_email  # SMTP adapter; returns ``True`` on success.

logger = logging.getLogger(__name__)  # Namespaced logger; never rebind the ``logging`` module itself.

OTP_TTL_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "3"))  # How long a code stays valid.
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))  # Wrong guesses tolerated per code.
OTP_SUBJECT = "Your FocusFlow verification code"  # Subject line for the OTP email.


# ---------------------------------------------------------------------------
# Errors the API layer can translate directly
# ---------------------------------------------------------------------------
class ServiceError(Exception):  # Base class for every expected business failure.
    """An expected failure that the route layer turns into an HTTP response."""

    status_code = 400  # Default HTTP status when nothing more specific applies.
    code = "service_error"  # Stable machine-readable identifier for the client.
    message = "The request could not be completed."  # Default human-readable text.

    def __init__(self, message: str | None = None) -> None:  # Allow callers to override the text.
        super().__init__(message or self.message)  # Store the chosen message on the exception.


class PasswordMismatch(ServiceError):  # ``password`` and ``confirm_password`` differ.
    status_code = 400  # Client sent inconsistent data.
    code = "password_mismatch"  # Machine-readable identifier.
    message = "Passwords do not match."  # Human-readable text.


class EmailTaken(ServiceError):  # The address already belongs to an account.
    status_code = 409  # Conflict with the current state of the resource.
    code = "email_taken"  # Machine-readable identifier.
    message = "An account with that email already exists."  # Deliberately does not echo the address.


class UsernameTaken(ServiceError):  # The handle already belongs to an account.
    status_code = 409  # Conflict with the current state of the resource.
    code = "username_taken"  # Machine-readable identifier.
    message = "That username is already taken."  # Human-readable text.


class InvalidCredentials(ServiceError):  # Unknown account or wrong password.
    status_code = 401  # Authentication required/failed.
    code = "invalid_credentials"  # Machine-readable identifier.
    message = "Invalid email or password."  # One message for both cases: no account enumeration.


class AccountNotVerified(ServiceError):  # Correct password, but the email was never confirmed.
    status_code = 403  # Authenticated but not permitted yet.
    code = "account_not_verified"  # Machine-readable identifier.
    message = "Please verify your email before signing in."  # Tells the client what to do next.


class OtpNotFound(ServiceError):  # No live code for this address.
    status_code = 400  # Client needs to request a new code.
    code = "otp_not_found"  # Machine-readable identifier.
    message = "That code is no longer valid. Request a new one."  # Actionable text.


class OtpExpired(ServiceError):  # The code existed but its window has closed.
    status_code = 400  # Client needs to request a new code.
    code = "otp_expired"  # Machine-readable identifier.
    message = "That code has expired. Request a new one."  # Actionable text.


class OtpLocked(ServiceError):  # Too many wrong guesses for this code.
    status_code = 429  # Rate limited / locked out.
    code = "otp_locked"  # Machine-readable identifier.
    message = "Too many incorrect attempts. Request a new code."  # Actionable text.


class InvalidOtp(ServiceError):  # The submitted code does not match.
    status_code = 400  # Client supplied the wrong value.
    code = "invalid_otp"  # Machine-readable identifier.
    message = "That code is incorrect."  # Human-readable text.


class EmailDeliveryFailed(ServiceError):  # SMTP refused or the credentials are missing.
    status_code = 503  # Upstream dependency unavailable.
    code = "email_delivery_failed"  # Machine-readable identifier.
    message = "We could not send the email. Please try again shortly."  # Actionable text.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _normalise_email(email: str) -> str:  # One definition of "the same address".
    return email.strip().lower()  # Trim whitespace and fold case so Foo@X.com == foo@x.com.


def _mask(email: str) -> str:  # Keep logs useful without storing full addresses.
    local, _, domain = email.partition("@")  # Split once; the local part may itself contain no '@'.
    return f"{local[:2]}***@{domain}" if local else "***"  # Show at most two characters.


def _otp_body(plain_otp: str) -> str:  # Single place that defines the email wording.
    return (  # Build the plain-text body.
        f"Your FocusFlow verification code is: {plain_otp}\n\n"  # The code itself.
        f"It expires in {OTP_TTL_MINUTES} minutes.\n"  # Reinforce the short lifetime.
        "If you did not request this, you can ignore this email."  # Reduce alarm for mistakes.
    )


def _deliver_otp(address: str, plain_otp: str) -> None:  # Send the code, translating adapter failures.
    try:  # ``send_email`` raises when SMTP credentials are missing.
        delivered = send_email(address, OTP_SUBJECT, _otp_body(plain_otp))  # Attempt delivery.
    except Exception:  # ValueError (no credentials) or any SMTP-level error.
        logger.exception("OTP delivery raised for %s", _mask(address))  # Log without the full address.
        delivered = False  # Treat any exception as a failed delivery.
    if not delivered:  # The adapter also reports failure by returning ``False``.
        raise EmailDeliveryFailed()  # The caller can offer a retry.


# ---------------------------------------------------------------------------
# Public operations
# ---------------------------------------------------------------------------
def register_user(user: UserRegister) -> dict[str, Any]:  # Create an account from a validated payload.
    """Create an account. Raises PasswordMismatch / EmailTaken / UsernameTaken."""
    if user.password != user.confirm_password:  # Guard against a client-side validation bypass.
        raise PasswordMismatch()  # 400: the two fields must match.
    email = _normalise_email(user.email)  # Fold case so duplicates cannot slip through.
    username = user.username.strip()  # Handles are case-sensitive, so only trim them.
    first_name = user.first_name.strip()  # Store trimmed names.
    last_name = user.last_name.strip()  # Store trimmed names.
    if get_user_by_email(email) is not None:  # Fast, friendly check before doing any hashing.
        raise EmailTaken()  # 409: stop early.
    if get_user_by_username(username) is not None:  # Fast, friendly check for the handle too.
        raise UsernameTaken()  # 409: stop early.
    try:  # The unique constraints are the real guard against a race between check and insert.
        user_id = create_user(  # Persist the account.
            first_name,  # Trimmed given name.
            last_name,  # Trimmed family name.
            email,  # Normalised address.
            username,  # Trimmed handle.
            hash_password(user.password),  # Never store plaintext.
        )
    except DuplicateUser as exc:  # A concurrent request won the race.
        if exc.field == "email":  # The email constraint fired.
            raise EmailTaken() from exc  # 409 with the matching message.
        if exc.field == "username":  # The username constraint fired.
            raise UsernameTaken() from exc  # 409 with the matching message.
        raise  # Unknown constraint: let RepositoryError/duplicate surface for the global handler.
    logger.info("Account created id=%s", user_id)  # Never log the address or the password.
    return {  # Shape the response for the route layer.
        "id": user_id,  # Primary key.
        "first_name": first_name,  # Echo what was stored.
        "last_name": last_name,  # Echo what was stored.
        "email": email,  # Normalised address.
        "username": username,  # Stored handle.
    }


def login_user(user: UserLogin) -> dict[str, Any]:  # Verify credentials and return the account.
    """Verify credentials. Raises InvalidCredentials / AccountNotVerified.

    Token minting belongs here once ``security/tokens.py`` exists; until then
    this returns the account and the route layer decides what to issue.
    """
    email = _normalise_email(user.email)  # Match how the address was stored.
    account = get_user_by_email(email)  # Fetch the row, including the password hash.
    if account is None:  # No such account.
        raise InvalidCredentials()  # Same message as a wrong password: no enumeration.
    try:  # A malformed/legacy hash must not become a 500.
        password_ok = verify_password(user.password, account["password"])  # Constant-time argon2 check.
    except Exception:  # ``passlib`` raises on an unreadable digest.
        logger.exception("Unreadable password hash for account id=%s", account.get("id"))  # Diagnose it.
        password_ok = False  # Treat it as a failed login.
    if not password_ok:  # Wrong password.
        raise InvalidCredentials()  # 401 with the same message as an unknown account.
    if not account.get("is_verified"):  # Correct password, but the address was never confirmed.
        raise AccountNotVerified()  # 403: tell the client to verify.
    logger.info("Login succeeded id=%s", account["id"])  # Log the id only.
    return {  # Shape the response for the route layer.
        "id": account["id"],  # Primary key.
        "email": account["email"],  # Normalised address.
        "username": account["username"],  # Handle.
    }


def request_otp(email: str) -> None:  # Issue (or re-issue) a verification code.
    """Issue an OTP. Silently ignores unknown addresses to prevent enumeration."""
    address = _normalise_email(email)  # Match how the address was stored.
    account = get_user_by_email(address)  # Only real accounts get a code.
    if account is None:  # Never reveal whether an address is registered.
        logger.info("OTP requested for an unknown address; ignoring")  # Log without the value.
        return  # Pretend it worked; the client sees a normal success response.
    plain_otp, otp_hash = create_secure_otp()  # Generate a six-digit code and its digest.
    create_otp(address, otp_hash, OTP_TTL_MINUTES, OTP_MAX_ATTEMPTS)  # Persist first: a stored code that was never delivered is harmless.
    try:  # Delivery can still fail.
        _deliver_otp(address, plain_otp)  # Send the plaintext code.
    except EmailDeliveryFailed:  # Keep storage consistent with reality.
        delete_otp(address)  # Remove the undelivered code so it cannot linger.
        raise  # Let the route return 503.
    logger.info("OTP issued for account id=%s", account.get("id"))  # Id only, never the code.


def verify_otp(email: str, code: str) -> None:  # Validate a submitted code and confirm the account.
    """Validate an OTP. Raises OtpNotFound / OtpExpired / OtpLocked / InvalidOtp."""
    address = _normalise_email(email)  # Match how the address was stored.
    supplied = code.strip()  # Clients often paste trailing whitespace.
    record = get_otp(address)  # Read the current code record.
    if record is None or not record["hash_otp"]:  # No live code for this address.
        raise OtpNotFound()  # 400: the user must request a new code.
    if record["is_expired"]:  # Postgres already compared ``expired_at`` with ``now()``.
        delete_otp(address)  # Clean up the dead code.
        raise OtpExpired()  # 400: request a new one.
    if record["attempts"] >= record["total_attempts"]:  # Lockout already reached.
        raise OtpLocked()  # 429: stop accepting guesses.
    if not verify_otp_hash(supplied, record["hash_otp"]):  # Compare the plaintext with the stored digest.
        attempts = increment_otp_attempts(address)  # Count the wrong guess (raises if the DB fails).
        if attempts >= record["total_attempts"]:  # That guess used up the budget.
            raise OtpLocked()  # 429: tell the client to request a new code.
        raise InvalidOtp()  # 400: ordinary mismatch, still has attempts left.
    delete_otp(address)  # Single use: consume the code before anything else can go wrong.
    mark_user_verified(address)  # Email ownership is now proven.
    logger.info("OTP verified for %s", _mask(address))  # Masked address only.


def reset_password(payload: ResetPassword) -> None:  # Complete the forgotten-password flow.
    """Verify the OTP and set a new password. Raises the same errors as verify_otp."""
    address = _normalise_email(payload.email)  # Match how the address was stored.
    verify_otp(address, payload.otp)  # Raises on a bad code and consumes it on success.
    if not update_user_password(address, hash_password(payload.new_password)):  # Persist the new digest.
        raise InvalidCredentials()  # The account vanished between verification and update.
    logger.info("Password reset for %s", _mask(address))  # Masked address only.


def change_password(payload: ChangePassword) -> None:  # Change a password for a signed-in account.
    """Verify the old password and store a new one. Raises InvalidCredentials."""
    address = _normalise_email(payload.email)  # Match how the address was stored.
    account = get_user_by_email(address)  # Fetch the row, including the hash.
    if account is None:  # No such account.
        raise InvalidCredentials()  # 401 with the standard message.
    if not verify_password(payload.old_password, account["password"]):  # Prove ownership first.
        raise InvalidCredentials()  # 401: wrong old password.
    if not update_user_password(address, hash_password(payload.new_password)):  # Persist the new digest.
        raise InvalidCredentials()  # The row disappeared mid-flight.
    logger.info("Password changed for %s", _mask(address))  # Masked address only.
