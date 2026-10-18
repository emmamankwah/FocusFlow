from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.outbox import enqueue_verification_email
from app.core.security import hash_password, verify_password
from app.database.session import Base
from app.models.email_outbox import EmailOutbox
from app.models.pending_users import PendingUser
from app.models.users import User
from app.routers import verification
from app.schemas.user import ResendOtpRequest, VerifyEmailRequest
from app.workers import email_outbox


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
        email_outbox,
        "send_verification_email",
        lambda email, otp: sent_emails.append((email, otp)),
    )

    response = verification.resend_otp(
        ResendOtpRequest(email="alice@example.com"),
        db_session,
    )

    assert response == {"message": "A new verification code has been queued for delivery"}
    job = db_session.query(EmailOutbox).one()
    assert job.recipient == "alice@example.com"
    assert job.status == "pending"
    assert job.encrypted_otp
    assert "123456" not in job.encrypted_otp
    assert sent_emails == []

    worker_sessions = sessionmaker(bind=db_session.get_bind())
    assert email_outbox.process_one_email(worker_sessions)
    assert len(sent_emails) == 1
    assert sent_emails[0][0] == "alice@example.com"
    assert verify_password(sent_emails[0][1], pending_user.otp_code)
    assert pending_user.otp_expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
    assert pending_user.first_name == "Alice"
    db_session.refresh(job)
    assert job.status == "sent"
    assert job.encrypted_otp is None


def test_resend_otp_commit_failure_rolls_back_otp_and_outbox(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) - timedelta(minutes=1))
    original_hash = pending_user.otp_code
    original_expiry = pending_user.otp_expires_at
    db_session.add(pending_user)
    db_session.commit()

    def fail_commit():
        raise RuntimeError("simulated database commit failure")

    monkeypatch.setattr(db_session, "commit", fail_commit)
    with pytest.raises(RuntimeError, match="simulated database commit failure"):
        verification.resend_otp(
            ResendOtpRequest(email="alice@example.com"),
            db_session,
        )

    db_session.refresh(pending_user)
    assert pending_user.otp_code == original_hash
    assert pending_user.otp_expires_at == original_expiry.replace(tzinfo=None)
    assert db_session.query(EmailOutbox).count() == 0


def test_outbox_worker_skips_superseded_otp(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) + timedelta(minutes=3))
    db_session.add(pending_user)
    db_session.commit()
    pending_user.otp_code = hash_password("654321")
    enqueue_verification_email(db_session, pending_user.email, "123456")
    job = db_session.query(EmailOutbox).one()
    db_session.commit()
    monkeypatch.setattr(
        email_outbox,
        "send_verification_email",
        lambda *_: pytest.fail("Superseded OTP must not be emailed"),
    )

    worker_sessions = sessionmaker(bind=db_session.get_bind())
    assert email_outbox.process_one_email(worker_sessions)

    job = db_session.query(EmailOutbox).one()
    assert job.status == "obsolete"
    assert job.encrypted_otp is None


def test_outbox_worker_retries_failed_delivery(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) + timedelta(minutes=3))
    db_session.add(pending_user)
    db_session.commit()
    enqueue_verification_email(db_session, pending_user.email, "123456")
    db_session.commit()

    def fail_send(*_):
        raise OSError("SMTP unavailable")

    monkeypatch.setattr(
        email_outbox,
        "send_verification_email",
        fail_send,
    )

    worker_sessions = sessionmaker(bind=db_session.get_bind())
    assert email_outbox.process_one_email(worker_sessions)

    job = db_session.query(EmailOutbox).one()
    assert job.status == "pending"
    assert job.attempts == 1
    assert job.last_error == "OSError"
    assert job.next_attempt_at > datetime.now(timezone.utc).replace(tzinfo=None)


def test_resend_otp_remains_retryable_when_email_delivery_fails(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) - timedelta(minutes=1))
    pending_user.otp_attempts = 2
    db_session.add(pending_user)
    db_session.commit()
    def fail_to_send(*_):
        raise OSError("SMTP unavailable")

    monkeypatch.setattr(email_outbox, "send_verification_email", fail_to_send)

    verification.resend_otp(
        ResendOtpRequest(email="alice@example.com"),
        db_session,
    )
    worker_sessions = sessionmaker(bind=db_session.get_bind())
    assert email_outbox.process_one_email(worker_sessions)

    db_session.refresh(pending_user)
    job = db_session.query(EmailOutbox).one()
    assert pending_user.otp_attempts == 0
    assert job.status == "pending"
    assert job.attempts == 1
    assert job.last_error == "OSError"
    assert job.encrypted_otp
    assert verify_password(
        email_outbox.decrypt_verification_otp(job.encrypted_otp),
        pending_user.otp_code,
    )


def test_resend_otp_rejects_unexpired_code(db_session, monkeypatch):
    pending_user = make_pending_user(datetime.now(timezone.utc) + timedelta(minutes=1))
    db_session.add(pending_user)
    db_session.commit()
    original_otp_hash = pending_user.otp_code

    with pytest.raises(HTTPException) as error:
        verification.resend_otp(
            ResendOtpRequest(email="alice@example.com"),
            db_session,
        )

    assert error.value.status_code == 400
    assert pending_user.otp_code == original_otp_hash
    assert db_session.query(EmailOutbox).count() == 0


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
