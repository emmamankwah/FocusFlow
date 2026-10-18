from datetime import timedelta

import pytest
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import authenticate_user, create_access_token, hash_password, verify_password
from app.database.session import Base
from app.models.email_outbox import EmailOutbox
from app.models.pending_users import PendingUser
from app.models.users import User
from app.routers import auth
from app.schemas.user import UserCreate


def test_user_timezone_defaults_to_utc():
    user = UserCreate(
        first_name="Alice",
        last_name="Example",
        email="alice@example.com",
        password="secret123",
        confirm_password="secret123",
    )

    assert user.timezone == "UTC"


def test_user_names_are_trimmed_and_allow_unicode_and_punctuation():
    user = UserCreate(
        first_name="  Zoë 李 ",
        last_name=" O'Connor-Smith ",
        email="alice@example.com",
        password="secret123",
        confirm_password="secret123",
    )

    assert user.first_name == "Zoë 李"
    assert user.last_name == "O'Connor-Smith"


def test_user_names_start_with_a_capital_letter():
    user = UserCreate(
        first_name="alice McDONALD",
        last_name="o'Connor-Smith",
        email="alice@example.com",
        password="secret123",
        confirm_password="secret123",
    )

    assert user.first_name == "Alice McDONALD"
    assert user.last_name == "O'Connor-Smith"


# Check both name fields reject blanks, overlong values, digits, and emoji.
@pytest.mark.parametrize("field", ["first_name", "last_name"])
@pytest.mark.parametrize("invalid_name", ["   ", "x" * 101, "Name2", "🙂Name"])
def test_user_names_reject_invalid_values(field, invalid_name):
    values = {
        "first_name": "Alice",
        "last_name": "Example",
        "email": "alice@example.com",
        "password": "secret123",
        "confirm_password": "secret123",
    }
    values[field] = invalid_name

    with pytest.raises(ValidationError):
        UserCreate(**values)


def test_create_access_token_round_trip():
    token = create_access_token({"sub": "alice@example.com"}, expires_delta=timedelta(minutes=5))
    assert token
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert payload["sub"] == "alice@example.com"


def test_authenticate_user_validates_password():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        user = User(
            first_name="Alice",
            last_name="Example",
            email="alice@example.com",
            hashed_password=hash_password("secret123"),
            timezone="UTC",
        )
        db.add(user)
        db.commit()

        auth_user = authenticate_user(db, "alice@example.com", "secret123")
        assert auth_user is not None
        assert auth_user.email == "alice@example.com"
        assert verify_password("secret123", auth_user.hashed_password)
        assert authenticate_user(db, "alice@example.com", "wrongpass") is None


def test_register_commits_pending_user_and_encrypted_email_job_together(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    monkeypatch.setattr(auth, "generate_otp", lambda: "012345")
    with SessionLocal() as db:
        response = auth.register(
            UserCreate(
                first_name="Alice",
                last_name="Example",
                email="alice@example.com",
                password="secret123",
                confirm_password="secret123",
            ),
            db,
        )

        assert response == {"message": "Verification code queued for email delivery"}
        pending = db.query(PendingUser).one()
        job = db.query(EmailOutbox).one()
        assert job.status == "pending"
        assert job.recipient == pending.email
        assert "012345" not in job.encrypted_otp
        assert verify_password("012345", pending.otp_code)

    engine.dispose()
