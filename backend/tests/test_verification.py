from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password, verify_password
from app.database.session import Base
from app.models.pending_users import PendingUser
from app.models.users import User
from app.routers import verification
from app.schemas.user import ResendOtpRequest, VerifyEmailRequest


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine)
    with session_local() as session:
        yield session
    engine.dispose()


def make_pending_user(otp_expires_at):
    return PendingUser(
        email="alice@example.com",
        hashed_password=hash_password("secret123"),
        first_name="Alice",
        last_name="Example",
        timezone="UTC",
        otp_code=hash_password("123456"),
        otp_expires_at=otp_expires_at,
    )


def test_resend_otp_updates_expired_pending_registration(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) - timedelta(minutes=1))
    db_session.add(pending_user)
    db_session.commit()
    sent_emails = []
    monkeypatch.setattr(
        verification,
        "send_verification_email",
        lambda email, otp: sent_emails.append((email, otp)),
    )

    response = verification.resend_otp(
        ResendOtpRequest(email="alice@example.com"),
        db_session,
    )

    assert response == {"message": "A new verification code has been sent"}
    assert len(sent_emails) == 1
    assert sent_emails[0][0] == "alice@example.com"
    assert verify_password(sent_emails[0][1], pending_user.otp_code)
    assert pending_user.otp_expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
    assert pending_user.first_name == "Alice"


def test_resend_otp_does_not_update_registration_when_email_fails(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) - timedelta(minutes=1))
    pending_user.otp_attempts = 2
    db_session.add(pending_user)
    db_session.commit()
    original_otp_hash = pending_user.otp_code
    original_expiration = pending_user.otp_expires_at

    def fail_to_send(*_):
        raise OSError("SMTP unavailable")

    monkeypatch.setattr(verification, "send_verification_email", fail_to_send)

    with pytest.raises(OSError, match="SMTP unavailable"):
        verification.resend_otp(
            ResendOtpRequest(email="alice@example.com"),
            db_session,
        )

    db_session.refresh(pending_user)
    assert pending_user.otp_code == original_otp_hash
    assert pending_user.otp_expires_at == original_expiration
    assert pending_user.otp_attempts == 2


def test_resend_otp_rejects_unexpired_code(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) + timedelta(minutes=1))
    db_session.add(pending_user)
    db_session.commit()
    original_otp_hash = pending_user.otp_code
    monkeypatch.setattr(
        verification,
        "send_verification_email",
        lambda *_: pytest.fail("Email should not be sent before the OTP expires"),
    )

    with pytest.raises(HTTPException) as error:
        verification.resend_otp(
            ResendOtpRequest(email="alice@example.com"),
            db_session,
        )

    assert error.value.status_code == 400
    assert pending_user.otp_code == original_otp_hash


def test_resend_otp_requires_pending_registration(db_session):
    with pytest.raises(HTTPException) as error:
        verification.resend_otp(
            ResendOtpRequest(email="missing@example.com"),
            db_session,
        )

    assert error.value.status_code == 404


def test_verify_email_promotes_pending_registration(db_session):
    pending_user = make_pending_user(datetime.now(timezone.utc) + timedelta(minutes=3))
    db_session.add(pending_user)
    db_session.commit()

    response = verification.verify_email(
        VerifyEmailRequest(email="alice@example.com", otp="123456"),
        db_session,
    )

    assert response == {"message": "Email verified successfully"}
    assert db_session.query(PendingUser).filter_by(email="alice@example.com").first() is None
    user = db_session.query(User).filter_by(email="alice@example.com").one()
    assert user.is_verified is True
    assert user.first_name == "Alice"


def test_verify_email_rejects_otp_at_expiration_time(db_session, monkeypatch):
    expiration = datetime(2026, 1, 1, tzinfo=timezone.utc)
    pending_user = make_pending_user(expiration)
    db_session.add(pending_user)
    db_session.commit()

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return expiration

    monkeypatch.setattr(verification, "datetime", FixedDatetime)

    with pytest.raises(HTTPException) as error:
        verification.verify_email(
            VerifyEmailRequest(email="alice@example.com", otp="123456"),
            db_session,
        )

    assert error.value.status_code == 400
    assert error.value.detail == "OTP expired, request a new one"


def test_verify_email_reports_already_verified_account(db_session):
    db_session.add(
        User(
            first_name="Alice",
            last_name="Example",
            email="alice@example.com",
            hashed_password=hash_password("secret123"),
            timezone="UTC",
            is_verified=True,
        )
    )
    db_session.commit()

    with pytest.raises(HTTPException) as error:
        verification.verify_email(
            VerifyEmailRequest(email="alice@example.com", otp="123456"),
            db_session,
        )

    assert error.value.status_code == 409
    assert error.value.detail == "Email is already verified"


@pytest.mark.parametrize("otp", ["12345", "1234567", "12a456", "１２３４５６", ""])
def test_verify_email_rejects_malformed_otp(otp):
    with pytest.raises(ValueError):
        VerifyEmailRequest(email="alice@example.com", otp=otp)
